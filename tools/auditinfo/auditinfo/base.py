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
