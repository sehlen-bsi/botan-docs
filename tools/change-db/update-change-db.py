#!/usr/bin/env python3

"""
Builds or updates a JSON database of audit change entries from the topic
YAML files of the audit report.

By default the topic files are read from docs/audit_report/changes/topics
(relative to this script's location in the repository) and the database is
written to docs/database/botan-changes.<x.y.z>.json where <x.y.z> is the
BOTAN_VERSION configured in config/botan.env.
"""

import argparse
import json
import logging
import os
import re
import sys
from glob import glob

import yaml


def repository_root() -> str:
    this_path = os.path.dirname(os.path.realpath(__file__))
    expected_parents = ["change-db", "tools"]
    for p in expected_parents:
        if not os.path.basename(this_path) == p:
            raise RuntimeError(f"build-change-db.py resides in an unexpected location: {__file__}")
        this_path = os.path.dirname(this_path)
    return this_path


def read_botan_env(env_var: str) -> str:
    config_file = os.path.join(repository_root(), "config", "botan.env")
    cfgpattern = re.compile(r"(^[a-zA-Z_0-9]+)=\"?([^\"]+)\"?\n$")
    with open(config_file, encoding="utf-8") as cfg:
        for line in cfg.readlines():
            match = cfgpattern.match(line)
            if match and match.group(1) == env_var:
                return match.group(2)
    raise RuntimeError(f"Did not find ${env_var} in {config_file}")


def parse_categories(value) -> list[str]:
    if not isinstance(value, str):
        raise RuntimeError(f"'categories' must be a comma separated string: '{value}'")
    categories = [c.strip() for c in value.split(',') if c.strip()]
    if not categories:
        raise RuntimeError(f"'categories' must contain at least one entry: '{value}'")
    return categories


def change_key(entry: dict) -> str:
    """ Identity of a change entry used to match entries across updates """
    if 'pr' in entry:
        return f"pr:{entry['pr']}"
    if 'commit' in entry:
        return f"commit:{entry['commit']}"
    raise RuntimeError(f"Change entry is neither a Pull Request nor a Commit: {entry}")


def load_entry_annotations(topic_file_text: str) -> list[dict]:
    """ Extracts title and author from the comment lines preceding each
        top-level patch entry, in entry order. The comment block directly
        above an entry starts with the title line, followed by an
        '#   Author: ...' line. """

    author_pattern = re.compile(r"^#\s*Author:\s*(.*?)\s*$")
    meta_pattern = re.compile(r"^#\s*(Author|Approvals):")

    annotations = []
    pending_comments = []
    for line in topic_file_text.splitlines():
        if line.startswith('#'):
            pending_comments.append(line)
        elif re.match(r"^- (pr|commit):", line):
            title = None
            author = None
            for comment in pending_comments:
                if match := author_pattern.match(comment):
                    author = match.group(1)
                elif title is None and not meta_pattern.match(comment):
                    title = comment.lstrip('#').strip() or None
            annotations.append({"title": title, "author": author})
            pending_comments = []
        else:
            pending_comments = []
    return annotations


def load_changes(topics_dir: str) -> list[dict]:
    topic_files = sorted(glob(os.path.join(topics_dir, "*.yml")))
    if not topic_files:
        raise RuntimeError(f"No topic YAML files found in: {topics_dir}")

    changes = []
    for topic_file in topic_files:
        topic_reference = os.path.splitext(os.path.basename(topic_file))[0]
        with open(topic_file, encoding="utf-8") as f:
            text = f.read()
        try:
            cfg = yaml.load(text, Loader=yaml.FullLoader)
        except yaml.YAMLError as ex:
            raise RuntimeError(f"Failed to parse '{topic_file}': {ex}") from ex
        if not cfg:
            raise RuntimeError(f"Failed to load topic file: {topic_file}")

        patches = cfg.get('patches') or []
        annotations = load_entry_annotations(text)
        if len(annotations) != len(patches):
            raise RuntimeError(f"Found {len(annotations)} annotated entries for "
                               f"{len(patches)} patches in: {topic_file}")

        for patch, annotation in zip(patches, annotations):
            entry = dict(annotation)
            entry.update(patch)
            if 'categories' in entry:
                entry['categories'] = parse_categories(entry['categories'])
            else:
                entry['categories'] = [topic_reference]
            changes.append(entry)
        logging.debug("Read %d change entries from '%s'", len(patches), topic_file)

    return changes


def confirm_deletion(entry: dict) -> tuple[bool, bool]:
    """ Asks the user whether to delete a database entry that is absent from
        the topic files. Returns (delete, apply_to_all). """

    print("Database entry not found in the topic files:")
    print(json.dumps(entry, indent=2, ensure_ascii=False))
    while True:
        try:
            answer = input("Delete it? [y]es / [n]o / [Y]es to all / [N]o to all: ").strip()
        except EOFError:
            raise RuntimeError("No interactive input available to confirm deletions. "
                               "Use --non-interactive to delete absent entries without confirmation.")
        if answer in ('y', 'n', 'Y', 'N'):
            return answer.lower() == 'y', answer in ('Y', 'N')
        print(f"Unrecognized answer: '{answer}'")


def update_database(database_file: str, meta: dict, changes: list[dict], non_interactive: bool):
    existing_changes = []
    if os.path.isfile(database_file):
        with open(database_file, encoding="utf-8") as f:
            existing_changes = json.load(f).get('changes', [])
        logging.info("Updating existing database with %d entries: %s",
                     len(existing_changes), database_file)

    fresh = {change_key(entry): entry for entry in changes}

    # Entries already in the database are replaced in-place by their current
    # state in the topic files; entries not (or no longer) found in the topic
    # files are deleted after user confirmation. New entries are appended in
    # source order.
    merged = []
    delete_all_decision = None
    for entry in existing_changes:
        key = change_key(entry)
        if key in fresh:
            merged.append(fresh.pop(key))
            continue

        if non_interactive:
            delete = True
        elif delete_all_decision is not None:
            delete = delete_all_decision
        else:
            delete, apply_to_all = confirm_deletion(entry)
            if apply_to_all:
                delete_all_decision = delete

        if delete:
            logging.info("Deleted absent entry from database: %s", key)
        else:
            merged.append(entry)

    merged += list(fresh.values())

    if os.path.dirname(database_file):
        os.makedirs(os.path.dirname(database_file), exist_ok=True)
    with open(database_file, 'w', encoding="utf-8") as f:
        json.dump({"meta": meta, "changes": merged}, f, indent=2, ensure_ascii=False)
        f.write('\n')
    logging.info("Wrote %d change entries to: %s", len(merged), database_file)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-t', '--topics-dir',
                        default=os.path.join(repository_root(), "docs", "audit_report", "changes", "topics"),
                        help="Directory containing the audit topic YAML files")
    parser.add_argument('-d', '--database-file',
                        default=None,
                        help="Database file to create or update (default: docs/database/botan-changes.<x.y.z>.json)")
    parser.add_argument('-n', '--non-interactive', action='store_true', default=False,
                        help="Delete database entries that are absent from the topic files without asking for confirmation")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="Enable detailed logging")
    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s %(message)s',
                        level=logging.DEBUG if args.verbose else logging.INFO)

    botan_version = read_botan_env("BOTAN_VERSION")
    meta = {
        "botan_version": botan_version,
        "botan_ref": read_botan_env("BOTAN_REF"),
        "botan_base_ref": read_botan_env("BOTAN_BASE_REF"),
    }

    database_file = args.database_file or os.path.join(
        repository_root(), "docs", "database", f"botan-changes.{botan_version}.json")

    changes = load_changes(args.topics_dir)
    update_database(database_file, meta, changes, args.non_interactive)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as ex:
        logging.error(ex)
        sys.exit(1)
