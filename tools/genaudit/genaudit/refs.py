"""
References to specific Git(Hub) objects like Pull Requests and Commits
"""

from enum import IntEnum
from functools import total_ordering

import auditinfo

from github.PullRequest import PullRequest as GithubPullRequest
from github.Commit import Commit as GithubCommit

class Classification(IntEnum):
    """ Not yet decided """
    UNSPECIFIED = 0

    """ Topic is not in scope of the review """
    OUT_OF_SCOPE = 1

    """ Topic does not affect the security of the system (formerly "Kategorie III") """
    INFORMATIONAL = 2

    """ Topic may be relevant for the effictivness or efficiency of security features in the system (formerly "Kategorie II") """
    RELEVANT = 3

    """ Topic is critical for the security of the system (formerly "Kategorie I") """
    CRITICAL = 4


    @staticmethod
    def __string_mapping():
        return [
            ('unspecified', Classification. UNSPECIFIED),
            ('out of scope', Classification.OUT_OF_SCOPE),
            ('critical', Classification.CRITICAL),
            ('relevant', Classification.RELEVANT),
            ('info', Classification.INFORMATIONAL),
        ]


    @staticmethod
    def from_string(classification: str):
        for m in Classification.__string_mapping():
            if m[0] == classification:
                return m[1]
        raise RuntimeError("Unknown classification: %s" % classification)

    def to_string(self) -> str:
        for m in self.__string_mapping():
            if m[1] == self.value:
                return m[0]
        raise RuntimeError("Unknown classification: %d" % self.value)

class Patch:
    def __init__(self, commit_ref: str, classification: Classification, auditer: str = None, comment: str = None):
        if commit_ref and len(commit_ref) != 40:
            raise RuntimeError("Incomplete commit hash: %s" % commit_ref)
        self.ref = commit_ref
        self.classification = classification
        self.auditer = auditer
        self.comment = comment

    def render_patch(self, repo, yaml: bool = False, approvers: bool = False):
        if isinstance(self, PullRequest):
            return self.render(repo.pull_request_info(self), yaml, approvers)
        elif isinstance(self, Commit):
            return self.render(repo.commit_info(self), yaml)
        else:
            raise RuntimeError("Unexpected patch type")

@total_ordering
class PullRequest(Patch):
    def __init__(self, github_ref: int, merge_commit_ref: str = None, classification: Classification = Classification.UNSPECIFIED, auditer: str = None, comment: str = None):
        super().__init__(merge_commit_ref, classification, auditer, comment)
        self.github_ref = github_ref
    def __repr__(self):
        return "GH #%d (%s)" % (self.github_ref, self.ref)
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.github_ref == other.github_ref
    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.github_ref < other.github_ref

    @property
    def merge_commit(self):
        return Commit(self.ref) if self.ref else None

    def render(self, pr_info: GithubPullRequest, yaml: bool = False, render_approvers: bool = False) -> str:
        if render_approvers:
            all_approvers = list(set([auditinfo.Auditor(review.user.name, review.user.login) for review in pr_info.get_reviews() if review.state == "APPROVED"]))
            authorative_auditors = [auditor for auditor in all_approvers if auditor in auditinfo.authorative_auditors()]
            other_approvers = [approver for approver in all_approvers if approver not in auditinfo.authorative_auditors()]

        if yaml:
            out = [
                f"# {pr_info.title}",
                f"#   Author:    @{pr_info.user.login}"
            ]
            if render_approvers:
                approvers = [f'@{auditor.github_handle}' for auditor in authorative_auditors]
                approvers += [f'(@{approver.github_handle})' for approver in other_approvers]
                if approvers:
                    out += [
                        f"#   Approvals: {', '.join(approvers)}",
                    ]
            out += [
                f"- pr: {pr_info.number}  # {pr_info.html_url}",
                f"  merge_commit: {self.ref}",
                f"  classification: {self.classification.to_string()}",
            ]
            if self.auditer:
                out += [f"  auditer: {self.auditer}"]
            if self.comment:
                out += [f"  comment: |"]
                out += [f"    {line}" for line in self.comment.splitlines()]
            return '\n'.join(out)
        else:
            return '\n'.join([
                f"Pull Request: '{pr_info.title}' by @{pr_info.user.login}",
                f"              {pr_info.html_url}",
            ])


@total_ordering
class Commit(Patch):
    def __init__(self, commit_ref: str, classification: Classification = Classification.UNSPECIFIED, auditer: str = None, comment: str = None):
        super().__init__(commit_ref, classification, auditer, comment)
    def __repr__(self):
        return "%s" % self.ref
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.ref == other.ref
    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.ref < other.ref

    def render(self, co_info: GithubCommit, yaml: bool = False) -> str:
        msg = co_info.commit.message.splitlines()[0]
        author = co_info.commit.author.name
        if yaml:
            out = [
                f"# {msg}",
                f"#   Author: {author}",
                f"- commit: {co_info.sha}  # {co_info.html_url}",
                f"  classification: {self.classification.to_string()}",
            ]
            if self.auditer:
                out += [f"  auditer: {self.auditer}"]
            if self.comment:
                out += [f"  comment: |"]
                out += [f"    {line}" for line in self.comment.splitlines()]
            return '\n'.join(out)
        else:
            return '\n'.join([
                f"Commit: '{msg}' by {author}",
                f"        {co_info.html_url}",
            ])
