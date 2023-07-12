"""
References to specific Git(Hub) objects like Pull Requests and Commits
"""

from enum import IntEnum
from functools import total_ordering

class Classification(IntEnum):
    """ Not yet decided """
    UNSPECIFIED = 0

    """ Topic is not in scope of the review """
    OUT_OF_SCOPE = 1

    """ Topic does not affect the security of the system (formerly "Kategorie III") """
    INFORMATIONAL = 2

    """ Topic may be relevant for the effictivness or efficiency of security features in the system (formerly "Kategorie II") """
    RELEVANT = 3

    """ Topic is critical for the security of the system (formerly "Kategorie I") """
    CRITICAL = 4


    @staticmethod
    def __string_mapping():
        return [
            ('unspecified', Classification. UNSPECIFIED),
            ('out of scope', Classification.OUT_OF_SCOPE),
            ('critical', Classification.CRITICAL),
            ('relevant', Classification.RELEVANT),
            ('info', Classification.INFORMATIONAL),
        ]


    @staticmethod
    def from_string(classification: str):
        for m in Classification.__string_mapping():
            if m[0] == classification:
                return m[1]
        raise RuntimeError("Unknown classification: %s" % classification)

    def to_string(self) -> str:
        for m in self.__string_mapping():
            if m[1] == self.value:
                return m[0]
        raise RuntimeError("Unknown classification: %d" % self.value)

class Patch:
    def __init__(self, commit_ref: str, classification: Classification, auditer: str = None, comment: str = None):
        if commit_ref and len(commit_ref) != 40:
            raise RuntimeError("Incomplete commit hash: %s" % commit_ref)
        self.ref = commit_ref
        self.classification = classification
        self.auditer = auditer
        self.comment = comment

    def __hash__(self):
        return hash((self.ref, self.classification, self.auditer, self.comment))


@total_ordering
class PullRequest(Patch):
    def __init__(self, github_ref: int, merge_commit_ref: str = None, classification: Classification = Classification.UNSPECIFIED, auditer: str = None, comment: str = None):
        super().__init__(merge_commit_ref, classification, auditer, comment)
        self.github_ref = github_ref
    def __repr__(self):
        return "GH #%d (%s)" % (self.github_ref, self.ref)
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.github_ref == other.github_ref
    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.github_ref < other.github_ref

    @property
    def merge_commit(self):
        return Commit(self.ref) if self.ref else None

    __hash__ = Patch.__hash__

@total_ordering
class Commit(Patch):
    def __init__(self, commit_ref: str, classification: Classification = Classification.UNSPECIFIED, auditer: str = None, comment: str = None):
        super().__init__(commit_ref, classification, auditer, comment)
    def __repr__(self):
        return "%s" % self.ref
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.ref == other.ref
    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.ref < other.ref

    __hash__ = Patch.__hash__
