import time

from collections.abc import Mapping

from auditinfo.base import *
from auditinfo.botan import *

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


def unicode_mappings():
    mapping = {
        "200B": "\\allowbreak", # zero-width space
        "03C1": "$\\rho$",
        "00E7": "\\c{c}", # small letter "c" with cedilla
        "C4B1": "{\\i}", # dotless letter "i"
    }

    return {
        "utf8extra": (''.join(["\\DeclareUnicodeCharacter{%s}{%s}" % (codepoint, latex) for codepoint, latex in mapping.items()]))
    }
