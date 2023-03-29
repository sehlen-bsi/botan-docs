"""
Audits are full document description for an individual code audit. They
typically consist of several topics.
"""

import yaml
import os
import logging

from glob import iglob

from genaudit.topic import Topic


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

        self.topics = self._load_topics(os.path.join(audit_dir, cfg['topics']))
        logging.info("Read %d topic files for '%s'",
                     len(self.topics), self.project_name)

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
