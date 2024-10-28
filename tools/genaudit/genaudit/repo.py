"""
Provides a wrapper for a github-hosted repository.
"""

import re
import subprocess

from github.PullRequest import PullRequest
from github.PullRequestReview import PullRequestReview
from github.Commit import Commit
from github.NamedUser import NamedUser
from github.Auth import Token
from github import Github, Rate

from genaudit import refs
from genaudit.cache import CachingRequester

import auditutils

from datetime import datetime

class CachingGithub(Github):
    def __init__(self, login_or_token, cache_location = None):
        super().__init__(None)
        self.requester = CachingRequester(login_or_token, cache_location)
        self._Github__requester = self.requester

class GitRepo:
    # see https://github.com/web-flow.gpg
    GITHUB_WEBFLOW_KEY_FINGERPRINT = "4aee18f83afdeb23"

    def __init__(self, github_token: str, cache_location: str, local_repo_root: str, github_handle: str, main_branch: str = "master"):
        self.local_repo_root = local_repo_root
        self.github_handle = github_handle
        self.main_branch = main_branch
        self.connection = CachingGithub(Token(github_token), cache_location)

        self.repo = self.connection.get_repo(self.github_handle)

        self._ensure_gpg_key_availability(self.GITHUB_WEBFLOW_KEY_FINGERPRINT)

    def _ensure_gpg_key_availability(self, key_fingerprint):
        # will throw if gpg is not available or the key is not known
        auditutils.run(["gpg", "--list-key", key_fingerprint])

    def _run_git(self, cmd):
        return auditutils.run_git(cmd, self.local_repo_root)

    def _extract_commit_ref_from_log_output(self, output):
        regex = re.compile(r"^([0-9a-f]+) .*$")

        def extract_commit_ref(line):
            match = regex.match(line)
            if not match:
                raise RuntimeError(
                    "Failed to interpret git log output line: %s" % line)
            return refs.Commit(match.group(1))

        return [extract_commit_ref(line) for line in output.splitlines()]

    def _get_oneline_commit_message(self, commit: refs.Commit) -> str:
        return self._run_git(["show", "--oneline",
                                      "--no-decorate",
                                      "--no-patch",
                                      commit.ref])

    def _commit_created_by_github(self, commit: refs.Commit) -> bool:
        """ Check if the commit was signed by the GitHub webflow GPG key """
        p = subprocess.Popen(["git", "verify-commit", "--raw", commit.ref],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             cwd=self.local_repo_root)
        _, stderr = p.communicate()
        errcode = p.wait()
        sstderr = stderr.decode("utf-8")

        if errcode == 0:
            m = re.search(r'GOODSIG ([a-zA-Z0-9]+) (.*)$', sstderr, re.MULTILINE)
            return (m and m.group(1).lower() == self.GITHUB_WEBFLOW_KEY_FINGERPRINT)

        return False

    def _extract_pull_request_info_from_commit(self, line):
        regex = re.compile(r"^([0-9a-f]+) [^#]+#(\d+)(?: .*)?$")
        match = regex.match(line)
        if not match:
            raise RuntimeError(
                "Failed to interpret git log output line: %s" % line)
        return refs.PullRequest(int(match.group(2)), match.group(1))

    def _extract_pull_request_info_from_squash_commit(self, commit: refs.Commit):
        match = re.match(r"^.* \(#([0-9]+)\)$", self._get_oneline_commit_message(commit))
        if not match:
            raise RuntimeError("Commit %s does not seem to be a squash-merged PR" % commit.ref)
        return refs.PullRequest(int(match.group(1)), commit.ref)

    def merged_pull_requests_between(self, start_ref, end_ref) -> list[refs.PullRequest]:
        out = self._run_git(["log", "--merges",
                                    "--no-decorate",
                                    "--oneline",
                                    "--no-abbrev-commit",
                                    "--grep=^Merge pull request",
                                    "--grep=^Merge GH",
                                    "%s..%s" % (start_ref, end_ref)])

        squashed_pr_merges = self._squashed_pull_requests_on_main_branch_between(start_ref, end_ref)

        return [self._extract_pull_request_info_from_commit(line) for line in out.splitlines()] + \
               [self._extract_pull_request_info_from_squash_commit(commit) for commit in squashed_pr_merges]

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

    def _commits_to_main_branch_between(self, start_ref, end_ref) -> list[refs.Commit]:
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

    def _squashed_pull_requests_on_main_branch_between(self, start_ref, end_ref) -> list[refs.Commit]:
        """ Find commits that indicate a squash-rebased pull request """
        # Assumption: pull requests merged with the "squash-rebase" strategy are
        #             always signed by the GitHub webflow key and feature the
        #             pull request reference in parenthesis at the end of the
        #             commit message.
        commits_to_main = self._commits_to_main_branch_between(start_ref, end_ref)
        ends_with_a_pr_ref = lambda c: re.search(r"\(#[0-9]+\)$", self._get_oneline_commit_message(c)) is not None
        return [c for c in commits_to_main if self._commit_created_by_github(c) and ends_with_a_pr_ref(c)]

    def maintainance_commits_to_main_branch_between(self, start_ref, end_ref) -> list[refs.Commit]:
        """ All commits added straight to the main branch (typically by the maintainer) """
        commits_to_main = self._commits_to_main_branch_between(start_ref, end_ref)
        squashed_prs = self._squashed_pull_requests_on_main_branch_between(start_ref, end_ref)
        return [c for c in commits_to_main if c not in squashed_prs]

    def tip_of_main_branch(self) -> Commit:
        return self.repo.get_branch(self.main_branch).commit

    def resolve_reference(self, gitref) -> Commit:
        return self.repo.get_commit(gitref)

    def pull_request_info(self, pr_number: refs.PullRequest) -> PullRequest:
        return self.repo.get_pull(pr_number.github_ref)

    def review_info(self, pr_number: refs.PullRequest) -> list[PullRequestReview]:
        return self.repo.get_pull(pr_number.github_ref).get_reviews()

    def commit_info(self, commit_hash: refs.Commit) -> Commit:
        assert len(commit_hash.ref) == 40
        return self.repo.get_commit(commit_hash.ref)

    def user_info(self, login_name: str) -> NamedUser:
        return self.connection.get_user(login_name)

    def rate_limit(self) -> Rate:
        return self.connection.get_rate_limit().core

    def api_cache_hit_rate(self):
        return self.connection.requester.cache_hit_rate()

    def api_request_count(self):
        return self.connection.requester.request_count()
