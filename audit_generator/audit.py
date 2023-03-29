#!/usr/bin/env python3

from github.PullRequest import PullRequest
from github.Commit import Commit

import argparse
import os
import sys
import logging

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


def find_unrefed(args: argparse.Namespace):
    audit, repo = _init(args)

    def render_pull_request(info: PullRequest):
        issue = info.number
        title = info.title
        author = info.user.login
        url = info.html_url

        if args.yaml:
            print("# %s  (@%s)" % (title, author))
            print("- %d:  # %s" % (issue, url))
            print("  classification: unspecified")
            print()
        else:
            print("Pull Request: '%s' by @%s              \n%s" % (title, author, url))

    def render_commit(info: Commit):
        sha = info.sha
        msg = info.commit.message.splitlines()[0]
        author = info.commit.author.name
        url = info.html_url

        if args.yaml:
            print("# %s  (@%s)" % (msg, author))
            print("- %s:  # %s" % (sha, url))
            print("  classification: unspecified")
            print()
        else:
            print("Commit: '%s' by %s\n        %s" % (msg, author, url))

    if args.yaml:
        print("patches:")

    prs = 0
    cos = 0
    for unrefed in genaudit.find_unreferenced_patches(audit, repo):
        if isinstance(unrefed, genaudit.refs.PullRequest):
            info = repo.pull_request_info(unrefed)
            render_pull_request(info)
            prs += 1
        if isinstance(unrefed, genaudit.refs.Commit):
            info = repo.commit_info(unrefed)
            render_commit(info)
            cos += 1

    if not args.yaml:
        print()
        print(
            "Found %d unreferenced Pull Requests and %d unreferenced Commits" % (prs, cos))


def render_audit_report(args: argparse.Namespace):
    audit, repo = _init(args)
    renderer = genaudit.Renderer(audit, repo)
    if args.out_dir:
        if renderer.render_to_files(args.out_dir, args.update):
            print("Rendered files were put in '%s'" % args.out_dir)
        else:
            print("Rendered nothing. Everything up-to-date")
    else:
        print(renderer.render())


def main():
    parser = argparse.ArgumentParser(
        description='This is a tool to generate audit reports based on GitHub information and YAML annotations')
    parser.add_argument('-t', '--token', help='GitHub access token (pulled from $BASIC_GH_TOKEN by default)',
                        default=os.environ.get('BASIC_GH_TOKEN'))
    parser.add_argument('-v', '--verbose', help='Enable detailed logging',
                        default=False, action='store_true')
    parser.add_argument('-c', '--cache-location',
                        help='Path to a directory that should be used as disk cache (overrides config.yml and defaults to AUDIT_CACHE_LOCATION)',
                        default=os.environ.get('AUDIT_CACHE_LOCATION'))
    parser.add_argument('-r', '--repo-location',
                        help='Path to a local checkout of the Botan repository (overrides config.yml and defaults to AUDIT_REPO_LOCATION)',
                        default=os.environ.get('AUDIT_REPO_LOCATION'))

    subparsers = parser.add_subparsers(title='Subcommands', required=True)

    unrefed = subparsers.add_parser(
        'unrefed', help='Find patches that are not referenced in the topic files.')
    unrefed.add_argument('--yaml', action='store_true', default=False,
                         help='print the result as a YAML document compatible with the topic.yml format')
    unrefed.add_argument('audit_config_dir',
                         help='the audit directory to be used')
    unrefed.set_defaults(func=find_unrefed)

    renderer = subparsers.add_parser(
        'render', help='Render the audit document')
    renderer.add_argument('audit_config_dir',
                          help='the audit directory to be used')
    renderer.add_argument( '-o', '--out-dir',
                          help='will be populated with rST document files')
    renderer.add_argument('-u', '--update', default=False, action='store_true',
                          help='generate rST file only if the associated YAML file is newer')
    renderer.set_defaults(func=render_audit_report)

    args = parser.parse_args(sys.argv[1:])

    loglevel = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=loglevel)
    args.func(args)


if __name__ == "__main__":
    main()
