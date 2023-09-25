
import subprocess
import logging

def run(cmd, working_directory=".", allow_stderr=False):
    """ Run a shell command and return stdout
        (or throw on non-zero return code or non-empty stderr)
    """

    p = subprocess.Popen(cmd, cwd=working_directory,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    errcode = p.wait()
    if (not allow_stderr and stderr) or errcode != 0:
        raise RuntimeError("Failed to run %s: \n%s" % (cmd[0], stderr))
    return stdout


def run_git(cmd, working_directory="."):
    logging.info("running git: `git %s`" % ' '.join(cmd))
    return run(["git"] + cmd, working_directory, True).decode("utf-8")

