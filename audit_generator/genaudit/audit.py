"""
Audits are full document description for an individual code audit. They
typically consist of several topics.
"""

import os
import logging
from glob import iglob

import yaml

from genaudit.topic import Topic
from genaudit.refs import PullRequest, Commit


class Audit:
    def __init__(self, audit_dir: str):
        self.config_file = os.path.join(audit_dir, "config.yml")
        strm = open(self.config_file, 'r')
        cfg = yaml.load(strm, Loader=yaml.FullLoader)

        self.project_name = cfg['project']
        logging.info("Found configuration for '%s'", self.project_name)

        self.cache_location = cfg['cache'] if 'cache' in cfg else None

        self.github_handle = cfg['repo']['github_handle']
        self.local_checkout = cfg['repo']['local_checkout']
        self.git_ref_from = cfg['repo']['audit_ref_from']
        self.git_ref_to = cfg['repo']['audit_ref_to']

        self.ignore_list = self._load_ignore_list(cfg['ignore']) if 'ignore' in cfg else []
        self.topics = self._load_topics(os.path.join(audit_dir, cfg['topics']))
        logging.info("Read %d topic files for '%s'",
                     len(self.topics), self.project_name)


    def patch_ignored(self, patch: PullRequest|Commit) -> bool:
        return patch in self.ignore_list


    def _load_ignore_list(self, ignore_list) -> list[PullRequest|Commit]:
        def load_list_entry(key_value: dict):
            if pr := key_value.get('pr', None):
                return PullRequest(pr)
            if commit := key_value.get('commit', None):
                return Commit(commit)
            raise RuntimeError("Unexpected patch type in ignore list: %s" % str(key_value))
        return [load_list_entry(kv) for kv in ignore_list] if ignore_list else []


    def _load_topics(self, topics_dir) -> list[Topic]:
        topic_files = iglob(os.path.join(topics_dir, "*.yml"))
        topics = []
        for tf in sorted(topic_files):
            try:
                topics.append(Topic(tf))
            except RuntimeError as ex:
                logging.error("Failed to parse topic: %s" % ex)
                continue
        return topics
