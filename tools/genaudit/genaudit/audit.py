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
from genaudit import util

import auditinfo

class Audit:
    def __init__(self, audit_dir: str):
        self.config_file = os.path.join(audit_dir, "config.yml")
        strm = open(self.config_file, 'r')
        cfg = yaml.load(strm, Loader=yaml.FullLoader)
        if not cfg:
            raise RuntimeError("Failed to load configuation: %s" % self.config_file)

        util.check_keys("Configuration", cfg.keys(), ['rst_ref', 'project', 'repo', 'topics', 'cache', 'fail_on_load_error', 'ignore'])

        self.rst_ref = cfg['rst_ref']
        self.project_name = cfg['project']
        logging.info("Found configuration for '%s'", self.project_name)

        self.cache_location = cfg['cache'] if 'cache' in cfg else None
        self.fail_on_load_error = cfg.get('fail_on_load_error', False)

        util.check_keys("Repo", cfg['repo'].keys(), ['local_checkout'])

        self.github_handle = auditinfo.botan_github_handle()
        self.main_branch = auditinfo.botan_main_branch()
        self.local_checkout = cfg['repo']['local_checkout']
        self.git_ref_from = auditinfo.botan_git_base_ref()
        self.git_ref_to = auditinfo.botan_git_ref()

        self.ignore_list = self._load_ignore_list(cfg['ignore']) if 'ignore' in cfg else []
        self.topics_dir = os.path.join(audit_dir, cfg['topics'])
        self.topics = self._load_topics(self.topics_dir)
        logging.info("Read %d topic files for '%s'",
                     len(self.topics), self.project_name)


    def patch_ignored(self, patch: PullRequest|Commit) -> bool:
        return patch in self.ignore_list


    def get_topic_file_path(self, topic_file_name: str) -> str:
        if os.path.split(topic_file_name)[0]:
            raise RuntimeError("topic_file_name must be a file name, not a path")
        return os.path.join(self.topics_dir, topic_file_name)


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
                if self.fail_on_load_error:
                    raise ex
                else:
                    continue
        return topics
