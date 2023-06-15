"""
Provides a wrapper for a github-hosted repository.
"""

import re
import logging

from github.PullRequest import PullRequest
from github.PullRequestReview import PullRequestReview
from github.Commit import Commit
from github.NamedUser import NamedUser
from github import Github

from genaudit import util
from genaudit import refs
from genaudit.cache import CachingRequester

class CachingGithub(Github):
    def __init__(self, login_or_token, cache_location = None):
        super().__init__(None)
        self._Github__requester = CachingRequester(login_or_token, cache_location)

class GitRepo:
    def __init__(self, github_token: str, cache_location: str, local_repo_root: str, github_handle: str, main_branch: str = "master"):
        self.local_repo_root = local_repo_root
        self.github_handle = github_handle
        self.main_branch = main_branch
        self.connection = CachingGithub(github_token, cache_location)

        self.repo = self.connection.get_repo(self.github_handle)

    def _run_git(self, cmd):
        logging.info("running git: `git %s`" % ' '.join(cmd))
        return util.run(["git"] + cmd, self.local_repo_root).decode("utf-8")

    def _extract_commit_ref_from_log_output(self, output):
        regex = re.compile(r"^([0-9a-f]+) .*$")

        def extract_commit_ref(line):
            match = regex.match(line)
            if not match:
                raise RuntimeError(
                    "Failed to interpret git log output line: %s" % line)
            return refs.Commit(match.group(1))

        return [extract_commit_ref(line) for line in output.splitlines()]

    def _extract_pull_request_number(self, line):
        regex = re.compile(r"^([0-9a-f]+) [^#]+#(\d+) .*$")
        match = regex.match(line)
        if not match:
            raise RuntimeError(
                "Failed to interpret git log output line: %s" % line)
        return refs.PullRequest(int(match.group(2)))

    def merged_pull_requests_between(self, start_ref, end_ref) -> list[refs.PullRequest]:
        out = self._run_git(["log", "--merges",
                                    "--no-decorate",
                                    "--oneline",
                                    "--grep=^Merge pull request",
                                    "--grep=^Merge GH",
                                    "%s..%s" % (start_ref, end_ref)])

        return [self._extract_pull_request_number(line) for line in out.splitlines()]

    def manual_merge_commits_to_main_branch_between(self, start_ref, end_ref) -> list[refs.Commit]:
        out = self._run_git(["log", "--merges",
                                    "--no-decorate",
                                    "--oneline",
                                    "--no-abbrev-commit",
                                    "--grep=^Merge pull request",
                                    "--grep=^Merge GH",
                                    "--invert-grep",
                                    "%s..%s" % (start_ref, end_ref)])

        return self._extract_commit_ref_from_log_output(out)

    def commits_to_main_branch_between(self, start_ref, end_ref) -> list[refs.Commit]:
        # To select for commits that were applied straight to the main branch we use
        # `--first-parent`. Unfortunately, this seems to interfere with the commit
        # range selection: I.e. `start_ref..end_ref` doesn't work properly. It always
        # returns main-branch commits all the way to the tip of the main branch.
        #
        # To work around that, we list all non-merge commits between start_ref and
        # end_ref and intersect both sets to obtain the commits on the main branch
        # between start_ref and end_ref.
        commits_to_main_since_start_ref = self._extract_commit_ref_from_log_output(
            self._run_git(["log", "--first-parent", self.main_branch,
                           "--no-decorate",
                           "--oneline",
                           "--no-abbrev-commit",
                           "--no-merges",
                           "^%s" % start_ref]))
        all_commits_between_start_and_end_ref = self._extract_commit_ref_from_log_output(
            self._run_git(["log",
                           "--no-decorate",
                           "--oneline",
                           "--no-abbrev-commit",
                           "--no-merges",
                           "%s..%s" % (start_ref, end_ref)]))
        return [sha for sha in all_commits_between_start_and_end_ref if sha in commits_to_main_since_start_ref]

    def pull_request_info(self, pr_number: refs.PullRequest) -> PullRequest:
        return self.repo.get_pull(pr_number.ref)

    def review_info(self, pr_number: refs.PullRequest) -> list[PullRequestReview]:
        return self.repo.get_pull(pr_number.ref).get_reviews()

    def commit_info(self, commit_hash: refs.Commit) -> Commit:
        assert len(commit_hash.ref) == 40
        return self.repo.get_commit(commit_hash.ref)

    def user_info(self, login_name: str) -> NamedUser:
        return self.connection.get_user(login_name)