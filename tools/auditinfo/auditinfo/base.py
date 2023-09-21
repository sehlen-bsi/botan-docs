import os
import subprocess

def repository_root() -> str:
    """ The absolute root path of this git repository """
    this_path = os.path.dirname(os.path.realpath(__file__))
    expected_parents = ["auditinfo", "auditinfo", "tools"]
    for p in expected_parents:
        if not os.path.basename(this_path) == p:
            raise RuntimeError(f"base.py resides in an unexpected location: {__file__}")
        this_path = os.path.dirname(this_path)
    return this_path

def repository_gitsha() -> str:
    p = subprocess.Popen(["git", "rev-parse", "HEAD"], cwd=repository_root(),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    errcode = p.wait()
    if stderr or errcode != 0:
        raise RuntimeError(f"Failed to find git revision:\n{stderr}")
    return stdout.decode("utf-8")

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
