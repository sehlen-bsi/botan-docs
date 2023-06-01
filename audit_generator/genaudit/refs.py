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
    def from_string(classification: str):
        return {'unspecified': Classification.UNSPECIFIED,
                'out of scope': Classification.OUT_OF_SCOPE,
                'critical': Classification.CRITICAL,
                'relevant': Classification.RELEVANT,
                'info': Classification.INFORMATIONAL}[classification]

@total_ordering
class Patch:
    def __init__(self, classification: Classification, comment: str):
        self.classification = classification
        self.comment = comment
    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.ref < other.ref
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.ref == other.ref

class PullRequest(Patch):
    def __init__(self, pr_ref: int, classification: Classification = Classification.UNSPECIFIED, comment: str = None):
        super().__init__(classification, comment)
        self.ref = pr_ref
    def __repr__(self):
        return "GH #%d (%s)"

class Commit(Patch):
    def __init__(self, commit_ref: str, classification: Classification = Classification.UNSPECIFIED, comment: str = None):
        super().__init__(classification, comment)
        if len(commit_ref) != 40:
            raise RuntimeError("Incomplete commit hash: %s" % commit_ref)
        self.ref = commit_ref
    def __repr__(self):
        return "%s" % self.ref
