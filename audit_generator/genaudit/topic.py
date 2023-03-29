"""
Topics are individual audit categories and typically refer to one or more GitHub
patches.
"""

import os
import yaml
import logging
import re

from genaudit import refs

class Topic:
    def __init__(self, topic_file: str):
        self.file = topic_file
        with open(topic_file, 'r') as f:
            cfg = yaml.load(f, Loader=yaml.FullLoader)
            if not cfg or 'title' not in cfg:
                raise RuntimeError("Failed to load Topic in '%s'" % topic_file)

            self.title = cfg['title']
            self.patches = self._load_patches(cfg)
            self._classification = self._load_classification(cfg)
            self.description = self._load_description(cfg)

            logging.debug("Found %s topic '%s' with %d patch references",
                          self._classification, self.title, len(self.patches))

    def _load_patches(self, cfg) -> list[refs.PullRequest|refs.Commit]:
        is_pr = re.compile(r'^\d+$')
        is_commit = re.compile(r'^[0-9a-f]{40}$')

        def load(patch):
            def get_ref():
                if isinstance(patch, dict):
                    ref = [m for m in patch if str(m) not in ['classification', 'comment']]
                    if len(ref) != 1:
                        raise RuntimeError("Failed to read patch: '%s'" % patch)
                    return ref[0]
                else:
                    return patch

            def get_comment():
                return patch.get("comment", None)

            ref = get_ref()
            if isinstance(ref, int) or is_pr.search(ref):
                return refs.PullRequest(int(ref), self._load_classification(patch), get_comment())
            elif is_commit.search(ref):
                return refs.Commit(ref, self._load_classification(patch), get_comment())
            else:
                raise RuntimeError("Patch is neither a Pull Request nor a Commit: %s" % patch)

        if 'patches' not in cfg:
            return []

        return [load(patch) for patch in cfg['patches']]

    def _load_classification(self, cfg):
        if not isinstance(cfg, dict) or 'classification' not in cfg:
            return refs.Classification.UNSPECIFIED

        classification = cfg['classification'].lower()

        try:
            return refs.Classification.from_string(classification)
        except KeyError:
            raise RuntimeError("unexpected classification '%s' in topic '%s'" % (
                classification, self.title))

    def _load_description(self, cfg) -> str:
        return cfg.get('description', None)

    @property
    def classification(self) -> refs.Classification:
        if self._classification != refs.Classification.UNSPECIFIED or not self.patches:
            return self._classification

        # If no specific classification was set on the topic, we take the
        # highest classification on any of the patches.
        return max([patch.classification for patch in self.patches])

    @property
    def reference(self) -> str:
        return os.path.splitext(os.path.basename(self.file))[0]
