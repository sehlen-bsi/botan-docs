"""
Rendering the collected information
"""

import logging
import re
import os
import time

from jinja2 import Environment, PackageLoader

from genaudit.refs import *
from genaudit import Audit, GitRepo, Topic


class RenderError(RuntimeError):
    pass


def rst_headline(headline: str, level: int):
    # The headline underline styles are not set in stone, we're
    # going with python's guidelines:
    #
    # https://devguide.python.org/documentation/markup/#sections
    headline_underliners = ['*', '=', '-', '^', '"']
    if level >= len(headline_underliners):
        raise RenderError("Headline level too deep: %d" % level)
    return headline + '\n' + (headline_underliners[level] * len(headline))


def first_line(text: str):
    return text.splitlines()[0]


def escape_rst(text: str):
    return text.replace('_ ', '\\_ ').replace('`', '\\`')


class Renderer:
    def __init__(self, audit: Audit, repo: GitRepo):
        self.audit = audit
        self.repo = repo
        self.tmpenv = Environment(loader=PackageLoader("genaudit"))
        self.tmpenv.trim_blocks = True
        self.tmpenv.lstrip_blocks = True
        self.tmpenv.filters["rst_headline"] = rst_headline
        self.tmpenv.filters["first_line"] = first_line
        self.tmpenv.filters["escape_rst"] = escape_rst

    def render(self) -> str:
        def render_topics():
            for topic in self.audit.topics:
                yield self._render_topic(topic)

        return '\n'.join([self.tmpenv.get_template("topic.rst").render(topic) for topic in render_topics()])

    def render_to_files(self, outdir: str, update: bool = False) -> bool:
        if not os.path.isdir(outdir):
            os.makedirs(outdir)

        def needs_update(target, src):
            # if update is not explicitly requested -> render everything
            if not update:
                return True
            # if the target file doesn't exist, yet -> render it
            if not os.path.isfile(target):
                return True
            t = os.path.getmtime(target)
            return t < os.path.getmtime(src) or t < os.path.getmtime(self.audit.config_file)

        topic_files = []
        rendered = 0

        for topic in self.audit.topics:
            start = time.time()
            topic_files.append(topic.reference)
            rst_file = os.path.join(outdir, topic.reference + '.rst')
            if not needs_update(rst_file, topic.file):
                continue
            rendered += 1
            with open(rst_file, 'w') as f:
                topic_vars = self._render_topic(topic)
                f.write(self.tmpenv.get_template(
                    "topic.rst").render(topic_vars))
            end = time.time()
            logging.info("rendered '%s', took %.2f seconds" % (topic.reference, end - start))

        if rendered > 0:
            with open(os.path.join(outdir, 'index.rst'), 'w+') as f:
                f.write(self.tmpenv.get_template("index.rst").render({
                    "document_title": self.audit.project_name,
                    "topics": topic_files
                }))
            logging.info("rendered index file after %d other files were updated" % rendered)

        return rendered > 0

    def _render_topic(self, topic: Topic):
        logging.debug("collecting render variables for topic: %s" %
                      topic.title)

        def render_classification(classification):
            return {Classification.UNSPECIFIED: "Unspecified category",
                    Classification.OUT_OF_SCOPE: "Out of scope",
                    Classification.INFORMATIONAL: "Category III - Informational",
                    Classification.RELEVANT: "Category II - Relevant for security",
                    Classification.CRITICAL: "Category I - Critical for security"}[classification]

        return {
            "title": topic.title,
            "reference": topic.reference,
            "classification": render_classification(topic.classification),
            "authors": self._render_authors(topic.patches),
            "description": self._insert_smart_refs(topic, topic.description),
            "patches": self._render_patch_references(topic)
        }

    def _render_authors(self, patches):
        logging.debug("collecting render variables for authors")

        def collect_authors(patches):
            authors = set()
            for patch in patches:
                if isinstance(patch, PullRequest):
                    pr_info = self.repo.pull_request_info(patch)
                    authors.add(pr_info.user)
                if isinstance(patch, Commit):
                    commit_info = self.repo.commit_info(patch)
                    authors.add(commit_info.author)
            return authors

        return [self._render_user(author) for author in collect_authors(patches)]

    def _render_user(self, author):
        logging.debug("collecting render variables for users")
        out = {"nick": author.login,
               "url": author.html_url}
        if author.name:
            out["full_name"] = author.name
        return out

    def _render_patch_references(self, topic: Topic):
        logging.debug("collecting render variables for patch references")

        def render_approvers(patch, pr_info: PullRequest):
            assert isinstance(patch, PullRequest)
            review_info = self.repo.review_info(patch)
            approvers = {
                review.user.login: review.user for review in review_info if review.state == "APPROVED"}
            if approvers:
                return [self._render_user(approver) for approver in approvers.values()]

            # If the PR was merged by a user that is not the PR's author, the
            # merger is assumed to approve on the PR as well, despite not having
            # approved via a GitHub review explicitly.
            elif pr_info.merged_by and pr_info.user != pr_info.merged_by:
                return [self._render_user(pr_info.merged_by)]

            else:
                return []

        def render_auditer(patch):
            if not patch.auditer:
                return None
            user = self.repo.user_info(patch.auditer)
            return self._render_user(user)

        def render_classification(classification):
            return {Classification.UNSPECIFIED: "n/a",
                    Classification.OUT_OF_SCOPE: "out of scope",
                    Classification.INFORMATIONAL: "info",
                    Classification.RELEVANT: "moderate",
                    Classification.CRITICAL: "critical"}[classification]

        def render_patch(patch):
            if isinstance(patch, PullRequest):
                pr_info = self.repo.pull_request_info(patch)
                commit_url = self.repo.commit_info(patch.merge_commit).html_url if patch.merge_commit else None

                return {"type": "pull_request",
                        "merge_commit": patch.ref,
                        "merge_commit_url": commit_url,
                        "github_ref": patch.github_ref,
                        "classification": render_classification(patch.classification),
                        "title": pr_info.title,
                        "comment": self._insert_smart_refs(topic, patch.comment),
                        "author": self._render_user(pr_info.user),

                        # In rare occasions the merging user is not available, because the pull request was
                        # merged manually and GitHub cannot figure it out properly. For instance, see:
                        #   https://github.com/randombit/botan/pull/3103
                        "merger": self._render_user(pr_info.merged_by) if pr_info.merged_by else None,
                        "approvers": render_approvers(patch, pr_info),
                        "auditer": render_auditer(patch),
                        "url": pr_info.html_url}
            if isinstance(patch, Commit):
                commit_info = self.repo.commit_info(patch)
                return {"type": "commit",
                        "ref": patch.ref,
                        "classification": render_classification(patch.classification),
                        "message": commit_info.commit.message,
                        "comment": self._insert_smart_refs(topic, patch.comment),
                        "author": self._render_user(commit_info.author),
                        "committer": self._render_user(commit_info.committer),
                        "auditer": render_auditer(patch),
                        "url": commit_info.html_url}
            raise RenderError("Unknown patch type encountered")

        # render patches in descending order of relevance
        sorted_patches = sorted(
            topic.patches, key=lambda patch: patch.classification, reverse=True)
        return [render_patch(patch) for patch in sorted_patches]

    def _insert_smart_refs(self, topic: Topic, text: str):
        """ Inserts links to tickets or commits that are also referenced in the
            patches. Regex matches "GH #0000", "#0000" and lower-case git SHA. """

        def replace_pr_ref(match):
            for patch in topic.patches:
                if isinstance(patch, PullRequest) and patch.github_ref == int(match.group(1)):
                    pr_info = self.repo.pull_request_info(patch)
                    return "`%s <%s>`_" % (match.group(0), pr_info.html_url)
            return match.group(0)

        def replace_commit_ref(match):
            for patch in topic.patches:
                if isinstance(patch, Commit) and patch.ref.startswith(match.group(0)):
                    c_info = self.repo.commit_info(patch)
                    return "`%s <%s>`_" % (match.group(0), c_info.html_url)
            return match.group(0)

        if not text:
            return None

        pr_ref = re.compile(r"(?:GH )?#(\d+)", re.MULTILINE)
        commit_ref = re.compile(r"[a-f0-9]{7,40}", re.MULTILINE)

        text = pr_ref.sub(replace_pr_ref, text)
        text = commit_ref.sub(replace_commit_ref, text)

        return text
