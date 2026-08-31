#!/usr/bin/env python3

"""
Watches the audit topic YAML files and rebuilds the change database and its
HTML view whenever they change.

On every detected change update-change-db.py is invoked, followed by
render-changes-db.py. If update-change-db.py fails, the view is not rendered
and the watcher simply waits for the next change of the topic files.
"""

import argparse
import logging
import os
import subprocess
import sys
import time
from glob import glob

POLL_INTERVAL = 1.0
SETTLE_INTERVAL = 0.5
RELOAD_SECONDS = 5.0

UPDATE_SCRIPT = "update-change-db.py"
RENDER_SCRIPT = "render-changes-db.py"


def repository_root() -> str:
    this_path = os.path.dirname(os.path.realpath(__file__))
    expected_parents = ["change-db", "tools"]
    for p in expected_parents:
        if not os.path.basename(this_path) == p:
            raise RuntimeError(f"watch-changes-db.py resides in an unexpected location: {__file__}")
        this_path = os.path.dirname(this_path)
    return this_path


def script_path(script: str) -> str:
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), script)


def snapshot(topics_dir: str) -> dict:
    """ State of all topic YAML files, used to detect any change """
    state = {}
    for topic_file in glob(os.path.join(topics_dir, "*.yml")):
        try:
            stat = os.stat(topic_file)
        except FileNotFoundError:
            continue  # removed while we were looking at it
        state[topic_file] = (stat.st_mtime_ns, stat.st_size)
    return state


def describe_changes(before: dict, after: dict) -> str:
    def names(files):
        return ', '.join(sorted(os.path.basename(f) for f in files))

    parts = []
    if added := after.keys() - before.keys():
        parts.append(f"added: {names(added)}")
    if removed := before.keys() - after.keys():
        parts.append(f"removed: {names(removed)}")
    if modified := {f for f in before.keys() & after.keys() if before[f] != after[f]}:
        parts.append(f"modified: {names(modified)}")
    return '; '.join(parts)


def wait_for_change(topics_dir: str, before: dict, interval: float) -> dict:
    """ Blocks until the topic files change and settled down again """
    while True:
        time.sleep(interval)
        after = snapshot(topics_dir)
        if after == before:
            continue

        # Editors may write files in several steps; wait for a stable state so
        # that we don't read a half-written file.
        while True:
            time.sleep(SETTLE_INTERVAL)
            settled = snapshot(topics_dir)
            if settled == after:
                break
            after = settled

        logging.info("Detected change (%s)", describe_changes(before, after) or "no-op")
        return after


def run(script: str, arguments: list[str]) -> bool:
    """ Runs one of the change database scripts, inheriting the terminal so
        that interactive prompts keep working. Returns True on success. """
    command = [sys.executable, script_path(script)] + arguments
    logging.debug("Running: %s", ' '.join(command))
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        logging.error("%s failed with exit code %d", script, result.returncode)
        return False
    return True


def rebuild(update_arguments: list[str], render_arguments: list[str]):
    if not run(UPDATE_SCRIPT, update_arguments):
        logging.warning("Skipping %s, waiting for the next change of the topic files", RENDER_SCRIPT)
        return
    run(RENDER_SCRIPT, render_arguments)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-t', '--topics-dir',
                        default=os.path.join(repository_root(), "docs", "audit_report", "changes", "topics"),
                        help="Directory of the watched topic YAML files")
    parser.add_argument('-d', '--database-file', default=None,
                        help="Database file to create or update (passed on to update-change-db.py)")
    parser.add_argument('-i', '--database-dir', default=None,
                        help="Directory of the database files to render (passed on to render-changes-db.py, "
                             "defaults to the directory of --database-file)")
    parser.add_argument('-o', '--output', default=None,
                        help="HTML output file (passed on to render-changes-db.py)")
    parser.add_argument('-n', '--non-interactive', action='store_true', default=False,
                        help="Let update-change-db.py delete absent entries without asking for confirmation")
    parser.add_argument('-r', '--reload', type=float, default=RELOAD_SECONDS, metavar='SECONDS',
                        help="Let the rendered page reload itself every SECONDS, so that it picks up "
                             f"the rebuilt view on its own (default: {RELOAD_SECONDS}, 0 disables it)")
    parser.add_argument('--interval', type=float, default=POLL_INTERVAL,
                        help=f"Interval in seconds between checks for changes (default: {POLL_INTERVAL})")
    parser.add_argument('--no-initial-run', action='store_true', default=False,
                        help="Don't build and render once on startup, wait for the first change instead")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="Enable detailed logging")
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG if args.verbose else logging.INFO)

    if not os.path.isdir(args.topics_dir):
        raise RuntimeError(f"Not a directory: {args.topics_dir}")

    update_arguments = ['--topics-dir', args.topics_dir]
    if args.database_file:
        update_arguments += ['--database-file', args.database_file]
    if args.non_interactive:
        update_arguments += ['--non-interactive']
    if args.verbose:
        update_arguments += ['--verbose']

    render_arguments = ['--reload', str(args.reload)]
    database_dir = args.database_dir or (os.path.dirname(args.database_file) if args.database_file else None)
    if database_dir:
        render_arguments += ['--database-dir', database_dir]
    if args.output:
        render_arguments += ['--output', args.output]
    if args.verbose:
        render_arguments += ['--verbose']

    state = snapshot(args.topics_dir)
    logging.info("Watching %d topic files in: %s", len(state), args.topics_dir)

    if not args.no_initial_run:
        rebuild(update_arguments, render_arguments)

    while True:
        state = wait_for_change(args.topics_dir, state, args.interval)
        rebuild(update_arguments, render_arguments)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as ex:
        logging.error(ex)
        sys.exit(1)
    except KeyboardInterrupt:
        logging.info("Stopped watching")
        sys.exit(0)
