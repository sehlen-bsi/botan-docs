"""
Checks that all relevant patches are referenced in at least one topic
"""

import logging

from genaudit import Audit, GitRepo, Topic
from genaudit.refs import *

from auditinfo import authorative_auditors

def find_unreferenced_patches(audit: Audit, repo: GitRepo) -> list[PullRequest|Commit]:
    def remove_from_list(list, value):
        try:
            list.remove(value)
        except ValueError:
            pass

    prs = repo.merged_pull_requests_between(audit.git_ref_from, audit.git_ref_to)
    commits = repo.maintainance_commits_to_main_branch_between(audit.git_ref_from, audit.git_ref_to)
    merges = repo.manual_merge_commits_to_main_branch_between(audit.git_ref_from, audit.git_ref_to)

    patches_before = len(prs) + len(commits) + len(merges)
    for topic in audit.topics:
        for patch in topic.patches:
            if isinstance(patch, PullRequest):
                remove_from_list(prs, patch)
            if isinstance(patch, Commit):
                remove_from_list(commits, patch)
                remove_from_list(merges, patch)
    patches_after = len(prs) + len(commits) + len(merges)
    logging.debug("Found %d referenced patches and %d unreferenced" % (patches_before - patches_after, patches_after))

    return filter(lambda patch: not audit.patch_ignored(patch), prs + commits + merges)


def find_misreferenced_pull_request_merges(audit: Audit, repo: GitRepo) -> list[tuple[PullRequest,str]]:
    def reference_in_repo(yaml_patch: PullRequest, repo_patches: list[PullRequest]) -> bool:
        try:
            idx = repo_patches.index(yaml_patch)
            return repo_patches[idx].ref
        except ValueError:
            raise RuntimeError("Pull Request #%d not found in repo history" % yaml_patch.github_ref)

    result = []
    prs = repo.merged_pull_requests_between(audit.git_ref_from, audit.git_ref_to)
    for topic in audit.topics:
        for patch in topic.patches:
            if not isinstance(patch, PullRequest):
                continue

            ref = reference_in_repo(patch, prs)
            if ref != patch.ref:
                result.append((patch, ref))

    logging.debug("Found %d pull request references with inconsistent merge commit hashes" % len(result))

    return result


def find_insufficiently_audited_patches(audit: Audit, repo: GitRepo) -> list[tuple[PullRequest|Commit, Topic, str]]:
    auditers = [auditor.github_handle for auditor in authorative_auditors()]

    def extract_contributors(patch: PullRequest|Commit) -> set[str]:
        result = set()

        if patch.auditer:
            result.add(patch.auditer)

        if isinstance(patch, PullRequest):
            pr_info = repo.pull_request_info(patch)
            review_info = repo.review_info(patch)
            result.add(pr_info.user.login)
            result.update([review.user.login for review in review_info if review.state == "APPROVED"])

        elif isinstance(patch, Commit):
            commit_info = repo.commit_info(patch)
            result.add(commit_info.author.login)

        else:
            raise LookupError("Unknown patch type encountered")

        return result

    def audit_status(patch: PullRequest|Commit) -> str:
        contribs = extract_contributors(patch)
        if patch.classification == Classification.UNSPECIFIED:
            return "Not classified"
        if not set(auditers) & contribs:
            return "No registered authorative auditor was involved in this patch"
        return None

    evaluated_patches = [(patch, topic, audit_status(patch)) for topic in audit.topics for patch in topic.patches]
    return [(patch, topic, error_message) for patch, topic, error_message in evaluated_patches if error_message]
