import time

from collections.abc import Mapping

from auditinfo.base import *
from auditinfo.botan import *

def coverpage_resources(language: str) -> list[str]:
    """ Returns a list of absolute paths to files needed for the coverpage """
    if language not in ["en", "de"]:
        raise RuntimeError(f"Unknown language: {language}")
    return [
        os.path.join(global_resources(), f"coverpage_{language}", "custom_coverpage.sty"),
        os.path.join(global_resources(), "logos", "rscs.png"),
    ]


def rst_substitutions(custom_substitutions : Mapping[str, str] = {}) -> str:
    """ An rST prolog containing a number of useful substitutions.

        Example: In rST, just write |document_gitsha| to render the
                 current git revision of repository.
    """

    substitutions = {
        "document_gitsha": repository_gitsha(),
        "document_gitsha_short": repository_gitsha()[:7],
        "document_datestamp": time.strftime("%d.%m.%Y"),
        "botan_version": botan_version(),
        "botan_git_base_ref": botan_git_base_ref(),
        "botan_git_ref": botan_git_ref(),
        **custom_substitutions
    }

    return '\n'.join([f".. |{subst}| replace:: {value}" for subst, value in substitutions.items()])
