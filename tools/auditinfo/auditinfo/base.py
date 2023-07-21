import os

def repository_root() -> str:
    """ The absolute root path of this git repository """
    this_path = os.path.dirname(os.path.realpath(__file__))
    expected_parents = ["auditinfo", "auditinfo", "tools"]
    for p in expected_parents:
        if not os.path.basename(this_path) == p:
            raise RuntimeError(f"base.py resides in an unexpected location: {__file__}")
        this_path = os.path.dirname(this_path)
    return this_path
