"""
Topics are individual audit categories and typically refer to one or more GitHub
patches.
"""

import os
import yaml
import logging

from genaudit import refs, util

class Topic:
    def __init__(self, topic_file: str):
        self.file = topic_file
        # Topic files whose patches were relocated into this topic via their
        # 'categories' field. Rendered output depends on those files as well.
        self.extra_source_files = []
        with open(topic_file, 'r') as f:
            cfg = yaml.load(f, Loader=yaml.FullLoader)
            if not cfg:
                raise RuntimeError("Failed to load Topic in '%s'" % topic_file)

            util.check_keys("Topic", cfg.keys(), ['classification', 'title', 'patches', 'description'])

            self.title = cfg['title']
            self.patches = self._load_patches(cfg)
            self._classification = self._load_classification(cfg)
            self.description = self._load_description(cfg)

            logging.debug("Found %s topic '%s' with %d patch references",
                          self._classification, self.title, len(self.patches))

    def __repr__(self):
        return "%s" % self.title

    def _load_patches(self, cfg) -> list[refs.PullRequest|refs.Commit]:
        def load(patch):
            def get_ref():
                ref = [(k,v) for k,v in patch.items() if str(k) in ['pr', 'commit']]
                if len(ref) != 1:
                    raise RuntimeError("Failed to read patch: '%s'" % patch)
                return ref[0]

            def get_comment():
                return patch.get("comment", None)

            def get_auditer():
                return patch.get("auditer", None)

            def get_categories():
                if 'categories' not in patch:
                    return None
                value = patch['categories']
                if not isinstance(value, str):
                    raise RuntimeError("'categories' must be a comma separated string in patch: '%s'" % patch)
                categories = [c.strip() for c in value.split(',') if c.strip()]
                if not categories:
                    raise RuntimeError("'categories' must contain at least one entry in patch: '%s'" % patch)
                return categories

            util.check_keys("Patch", patch.keys(), ['pr', 'commit', 'merge_commit', 'classification', 'comment', 'auditer', 'categories'])

            ref_type, value = get_ref()
            if ref_type == "pr":
                return refs.PullRequest(int(value), patch.get('merge_commit', None), self._load_classification(patch), get_auditer(), get_comment(), get_categories())
            elif ref_type == "commit":
                return refs.Commit(value, self._load_classification(patch), get_auditer(), get_comment(), get_categories())
            else:
                raise RuntimeError("Patch is neither a Pull Request nor a Commit: %s" % patch)

        if 'patches' not in cfg or cfg['patches'] is None:
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
