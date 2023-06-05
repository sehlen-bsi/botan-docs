import subprocess


def run(cmd, working_directory="."):
    p = subprocess.Popen(cmd, cwd=working_directory,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    errcode = p.wait()
    if stderr or errcode != 0:
        raise RuntimeError("Failed to run %s: \n%s" % (cmd[0], stderr))
    return stdout
