#!/usr/bin/env python3

import argparse
import os
import sys
import logging
import io

from datetime import datetime

from github.PullRequest import PullRequest
from github.Commit import Commit

import genaudit

def _get_directory(config_file_dir, cfg_location, cli_location):
    location = cli_location if cli_location else cfg_location
    return location if os.path.isabs(location) else os.path.join(config_file_dir, location)

def _init(args: argparse.Namespace):
    audit = genaudit.Audit(args.audit_config_dir)
    cache = _get_directory(args.audit_config_dir, audit.cache_location, args.cache_location)
    checkout = _get_directory(args.audit_config_dir, audit.local_checkout, args.repo_location)
    repo = genaudit.GitRepo(args.token, cache, checkout, audit.github_handle)
    return audit, repo


def _render_pull_request(info: PullRequest, yaml_info: genaudit.PullRequest, yaml: bool, stream: io.StringIO):
    issue = info.number
    title = info.title
    author = info.user.login
    url = info.html_url
    classification = yaml_info.classification.to_string()

    if yaml:
        print("# %s  (@%s)" % (title, author), file=stream)
        print("- pr: %d  # %s" % (issue, url), file=stream)
        print("  merge_commit: %s" % yaml_info.ref, file=stream)
        print("  classification: %s" % classification, file=stream)
        if(yaml_info.auditer):
            print("  auditer: %s" % yaml_info.auditer, file=stream)
        if(yaml_info.comment):
            print("  comment: |", file=stream)
            print("    %s" % '    '.join(yaml_info.comment.splitlines(True)), file=stream)

        print(file=stream)
    else:
        print("Pull Request: '%s' by @%s\n              %s" % (title, author, url), file=stream)


def find_unrefed(audit: genaudit.Audit, repo: genaudit.GitRepo, args: argparse.Namespace):
    def _render_commit(info: Commit, stream: io.StringIO):
        sha = info.sha
        msg = info.commit.message.splitlines()[0]
        author = info.commit.author.name
        url = info.html_url

        if args.yaml:
            print("# %s  (@%s)" % (msg, author), file=stream)
            print("- commit: %s  # %s" % (sha, url), file=stream)
            print("  classification: unspecified", file=stream)
            print(file=stream)
        else:
            print("Commit: '%s' by %s\n        %s" % (msg, author, url), file=stream)

    output = io.StringIO()
    if args.yaml:
        print("patches:", file=output)

    prs = 0
    cos = 0
    for unrefed in genaudit.find_unreferenced_patches(audit, repo):
        if isinstance(unrefed, genaudit.refs.PullRequest):
            info = repo.pull_request_info(unrefed)
            _render_pull_request(info, unrefed, args.yaml, output)
            prs += 1
        if isinstance(unrefed, genaudit.refs.Commit):
            info = repo.commit_info(unrefed)
            _render_commit(info, output)
            cos += 1

    logging.info("Found %d unreferenced Pull Requests and %d unreferenced Commits", prs, cos)

    if prs+cos > 0:
        print()
        print(output.getvalue())
        return 1
    else:
        return 0


def verify_merge_commits(audit: genaudit.Audit, repo: genaudit.GitRepo, args: argparse.Namespace):
    inconsistent_prs = genaudit.find_misreferenced_pull_request_merges(audit, repo)
    logging.info("Found %d Pull Requests with misreferenced commits", len(inconsistent_prs))

    if args.yaml:
        output = io.StringIO()
        print("patches:", file=output)
        for pr in inconsistent_prs:
            pr_ref = pr[0]
            pr_commit_ref  = pr[1]
            pr_ref.ref = pr_commit_ref
            _render_pull_request(repo.pull_request_info(pr_ref), pr_ref, args.yaml, output)

        print()
        print(output.getvalue())

    return 0 if not inconsistent_prs else 1


def render_audit_report(audit: genaudit.Audit, repo: genaudit.GitRepo, args: argparse.Namespace):
    renderer = genaudit.Renderer(audit, repo)
    if args.out_dir:
        if renderer.render_to_files(args.out_dir, args.update):
            print("Rendered files were put in '%s'" % args.out_dir)
        else:
            print("Rendered nothing. Everything up-to-date")
    else:
        print(renderer.render())

    return 0


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

    subparsers = parser.add_subparsers(title='Subcommands', required=True)

    unrefed = subparsers.add_parser(
        'unrefed', help='Find patches that are not referenced in the topic files.')
    unrefed.add_argument('--yaml', action='store_true', default=False,
                         help='print the result as a YAML document compatible with the topic.yml format')
    unrefed.add_argument('audit_config_dir',
                         help='the audit directory to be used')
    unrefed.set_defaults(func=find_unrefed)

    merge_commits = subparsers.add_parser(
        'verify_merges', help='Find pull requests that are not referenced with their respective merge commit hash')
    merge_commits.add_argument('--yaml', action='store_true', default=False,
                               help='print the correction as a YAML document compatible with the topic.yml format')
    merge_commits.add_argument('audit_config_dir',
                               help='the audit directory to be used')
    merge_commits.set_defaults(func=verify_merge_commits)

    renderer = subparsers.add_parser(
        'render', help='Render the audit document.')
    renderer.add_argument('audit_config_dir',
                          help='The audit directory to be used.')
    renderer.add_argument( '-o', '--out-dir',
                          help='Will be populated with rST document files.')
    renderer.add_argument('-u', '--update', default=False, action='store_true',
                          help='Generate rST file only if the associated YAML file is newer.')
    renderer.set_defaults(func=render_audit_report)

    args = parser.parse_args(sys.argv[1:])

    loglevel = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=loglevel)

    audit, repo = _init(args)
    try:
        rate_limit = repo.rate_limit()
        reset_time_h = int((rate_limit.reset - datetime.now()).seconds / 60 / 60)
        reset_time_m = (rate_limit.reset - datetime.now()).seconds / 60 % 60
        logging.info("Current GitHub API rate limit: %d/%d (will reset in: %d hours %d minutes)", rate_limit.remaining, rate_limit.limit, reset_time_h, reset_time_m)

        return args.func(audit, repo, args)
    finally:
        logging.info("Performed %d API requests (%.1f%% cache hits)", repo.api_request_count(), repo.api_cache_hit_rate() * 100)


if __name__ == "__main__":
    sys.exit(main())
