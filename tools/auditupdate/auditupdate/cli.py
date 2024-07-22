#!/usr/bin/env python3

import argparse
import logging
import os
import sys
import re

import github

import auditinfo
import genaudit
import auditutils

def run_git(cmd:list[str]) -> str:
    return auditutils.run_git(cmd, auditinfo.repository_root())


def get_autoupdate_pull_request(repo) -> github.PullRequest.PullRequest | None:
    orguser = auditinfo.auditdoc_github_handle().split('/')[0]
    branch = auditinfo.auditdoc_autoupdate_branch()
    autoupdate_pr = list(repo.get_pulls(state="open", head=f"{orguser}:{branch}"))
    return autoupdate_pr[0] if autoupdate_pr else None


def target_git_ref_is_pinned():
    """ We consider a target as 'not pinned' if it is set to a bare git SHA """
    return re.match(r'^[0-9a-z]+$', auditinfo.botan_git_ref()) == None


def update_uncategorized_patches(audit: genaudit.Audit, repo: genaudit.GitRepo, topic_file: str, topic_title: str) -> bool:
    """ Finds unreferenced patches and updates the given topic YAML file accordingly """

    unrefed_patches = genaudit.find_unreferenced_patches(audit, repo)
    if not unrefed_patches:
        return False

    target_topic_file = audit.get_topic_file_path(topic_file)
    os.makedirs(os.path.dirname(target_topic_file), exist_ok=True)

    with open(target_topic_file, 'a', encoding="utf-8") as unrefed_topic:
        if unrefed_topic.tell() == 0:
            # if the file was just created, we have to add a preamble
            unrefed_topic.write('\n'.join([
                f"title: {topic_title}",
                f"",
                f"patches:",
            ]))

        # render all found unreferenced patches
        rendered_unrefed_patches = ''.join([f"\n{patch.render_patch(repo, yaml=True, approvers=True)}\n" for patch in unrefed_patches])
        unrefed_topic.write(rendered_unrefed_patches)

    return True


def create_pull_request(repo, branch):
    title = ":robot: Audit: Auto-update with latest upstream patches"
    description = '\n'.join([
        f"This pull request was created automatically and contains the latest uncategorized patches from Botan's repository.",
        f"",
        f"Typically, you will need to pull this branch (`{branch}`) to categorize and audit the newly added patches. It is perfectly fine to push into this pull request and merge it after a code review.",
        f"If not merged, this pull request will be updated with new patches continuously.",
    ])
    repo.create_pull(title=title, body=description, head=branch, base=auditinfo.auditdoc_main_branch())

def main():
    parser = argparse.ArgumentParser(
        description='This is a tool to generate audit reports based on GitHub information and YAML annotations.')
    parser.add_argument('-t', '--token', help='GitHub access token (pulled from $BASIC_GH_TOKEN by default)',
                        default=os.environ.get('BASIC_GH_TOKEN'))
    parser.add_argument('-v', '--verbose', help='Enable detailed logging',
                        default=False, action='store_true')
    parser.add_argument('-c', '--cache-location',
                        help='Path to a directory that should be used as disk cache (overrides config.yml and defaults to AUDIT_CACHE_LOCATION).',
                        default=os.environ.get('AUDIT_CACHE_LOCATION'))
    parser.add_argument('-r', '--repo-location',
                        help='Path to a local checkout of the Botan repository (overrides config.yml and defaults to AUDIT_REPO_LOCATION).',
                        default=os.environ.get('AUDIT_REPO_LOCATION'))
    parser.add_argument('-o', '--output-topic',
                        help='File name of the topic to append unreferenced patches to',
                        default='uncategorized.yml')
    parser.add_argument('-n', '--output-topic-title',
                        help='Title of the topic to append unreferenced patches to',
                        default='Uncategorized Patches')
    parser.add_argument('audit_config_dir',
                         help='the audit directory to be updated')

    args = parser.parse_args(sys.argv[1:])

    loglevel = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=loglevel)

    # Auto-updater is disabled if $BOTAN_REF is set to something that does not
    # resemble a git SHA (e.g. a git tag like 3.2.0).
    if target_git_ref_is_pinned():
        logging.info(f"No update necessary, target is pinned to: {auditinfo.botan_git_ref()}")
        return 0

    # Figure out whether we're updating an existing Auto-update Pull Request
    # or have to create a new one.
    old_target = auditinfo.botan_git_ref()
    gh = github.Github(auth=github.Auth.Token(args.token))
    docrepo = gh.get_repo(auditinfo.auditdoc_github_handle())
    pr = get_autoupdate_pull_request(docrepo)
    if pr:
        logging.info(f"Found open auto-update Pull Request (#{pr.number}), switching branch...")
        run_git(["checkout", auditinfo.auditdoc_autoupdate_branch()])
    else:
        logging.info(f"Did not find an open auto-update Pull Request, creating a branch...")
        run_git(["checkout", "-B", auditinfo.auditdoc_autoupdate_branch()])

    # Check whether new patches have landed in Botan upstream
    # (potentially compared to a currently-open Auto-update pull request)
    _, repo = genaudit.init_from_command_line_arguments(args)
    new_target = repo.tip_of_main_branch().sha
    if new_target == auditinfo.botan_git_ref():
        logging.info(f"No update necessary, target is pointing to latest commit: {auditinfo.botan_git_ref()}")
        return 0

    # Update the botan.env configuration file with the new upstream target revision.
    auditinfo.update_botan_git_ref(new_target)
    run_git(["add", auditinfo.config_file_path()])

    # Re-initialize the Audit Generator scripts with the just-updated target revision
    # and determine which patches need to be added to the audit report document.
    audit, repo = genaudit.init_from_command_line_arguments(args)
    found_patches = update_uncategorized_patches(audit, repo, args.output_topic, args.output_topic_title)
    if not found_patches:
        logging.critical(f"Upstream repo was updated (from {old_target[0:7]} to {new_target[0:7]}) but didn't find new patches. Something is wrong here!")
        return 1

    # Commit and push the new (uncategorized) patch references.
    run_git(["add", audit.get_topic_file_path(args.output_topic)])
    run_git(["commit", "--no-gpg-sign", "-m", f"Automatic update to match patches until {new_target[0:7]}"])
    run_git(["push", "--set-upstream", "origin", auditinfo.auditdoc_autoupdate_branch()])

    # If we're not updating an existing Auto-update Pull Request, we need to
    # create a new one.
    if not pr:
        logging.info(f"creating Auto-Update pull request...")
        create_pull_request(docrepo, auditinfo.auditdoc_autoupdate_branch())

    # Profit!
    return 0


if __name__ == "__main__":
    sys.exit(main())
