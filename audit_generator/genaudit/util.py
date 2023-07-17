import subprocess


def run(cmd, working_directory="."):
    p = subprocess.Popen(cmd, cwd=working_directory,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    errcode = p.wait()
    if stderr or errcode != 0:
        raise RuntimeError("Failed to run %s: \n%s" % (cmd[0], stderr))
    return stdout


def check_keys(artefact: str, keys: list[str], expected_keys: list[str]):
    unexpected_keys = [k for k in keys if k not in expected_keys]
    if unexpected_keys:
        raise RuntimeError("Unexpected key(s) '%s' in %s" % (','.join(unexpected_keys), artefact))
