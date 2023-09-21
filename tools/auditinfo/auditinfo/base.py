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

def global_resources() -> str:
    """ Absolute path to the directory containing resource files """
    return os.path.join(repository_root(), "resources")

def coverpage_resources(language: str) -> list[str]:
    """ Returns a list of absolute paths to files needed for the coverpage """
    if language not in ["en", "de"]:
        raise RuntimeError(f"Unknown language: {language}")
    return [
        os.path.join(global_resources(), f"coverpage_{language}", "custom_coverpage.sty"),
        os.path.join(global_resources(), "logos", "rscs.png"),
    ]
