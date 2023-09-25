import os
import re

from auditinfo.base import repository_root

def __get_from_config(env_var: str) -> str:
    cfgpath = os.path.join(repository_root(), "config", "botan.env")
    cfgpattern = re.compile(r"(^[a-zA-Z_0-9]+)=(.+)\n$")
    with open(cfgpath, encoding="utf-8") as cfg:
        for line in cfg.readlines():
            match = cfgpattern.match(line)
            if match and match.group(1) == env_var:
                return match.group(2)
    raise RuntimeError(f"Did not find ${env_var} in the environment or config")

def __get_or_throw(env_var: str) -> str:
    return os.environ[env_var] if env_var in os.environ else __get_from_config(env_var)

def botan_version() -> str:
    """ The targeted version of the Botan library """
    return __get_or_throw("BOTAN_VERSION")

def botan_github_handle() -> str:
    """ The repository handle of the main code base on GitHub """
    return __get_or_throw("BOTAN_REPO")

def botan_main_branch() -> str:
    """ The name of the main branch of the main code base on GitHub """
    return __get_or_throw("BOTAN_MAIN_BRANCH")

def botan_git_ref() -> str:
    """ The git reference of the currently targeted Botan source revision """
    return __get_or_throw("BOTAN_REF")

def botan_git_base_ref() -> str:
    """ The git reference of the previously audited Botan source revision """
    return __get_or_throw("BOTAN_BASE_REF")

def auditdoc_github_handle() -> str:
    """ The repository handle  of the audit documentation on GitHub """
    return __get_or_throw("AUDITDOC_REPO")

def auditdoc_main_branch() -> str:
    """ The name of the main branch of the auditdoc repo on GitHub """
    return __get_or_throw("AUDITDOC_MAIN_BRANCH")

def auditdoc_autoupdate_branch() -> str:
    """ The branch on the audit documentation repo managed by the nightly auto-update check """
    return __get_or_throw("AUDITDOC_AUTO_UPDATE_BRANCH")
