"""
Checks that all relevant patches are referenced in at least one topic
"""

import logging

from genaudit import Audit, GitRepo
from genaudit.refs import *

def find_unreferenced_patches(audit: Audit, repo: GitRepo) -> list[PullRequest|Commit]:
    def remove_from_list(list, value):
        try:
            list.remove(value)
        except ValueError:
            pass

    prs = repo.merged_pull_requests_between(audit.git_ref_from, audit.git_ref_to)
    commits = repo.commits_to_main_branch_between(audit.git_ref_from, audit.git_ref_to)
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

    return prs + commits + merges
