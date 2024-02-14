import requests
import re
from docutils import nodes
from docutils.nodes import Node, system_message
from sphinx.roles import ReferenceRole

class SourceReferenceRole(ReferenceRole):
    """A role to create a reference to a source file.

    The reference will link to ``<src_ref_base_url>/<src_ref_reference>/<target>``.

    The text of the role will be the ``<target>``.
    The reference role can also accept ``link title <target>`` style as a text for
    the role.
    Alternativeley, the target can be displayed truncated. For example:
    ``[src/lib/hash]/sha1/sha1.cpp`` is displayed as ``.../sha1/sha1.cpp``.

    Options:

    - ``src_ref_base_url``: Base URL for the link.
    - ``src_ref_reference``: Name of a branch, a tag or an SHA-1 hash to link to.
    - ``src_ref_check_url``: If true, check that the URL is reachable.

    Example:

    - ``src/lib/hash/sha1/sha1.cpp``
    - ``src/lib/pubkey/xmss/``
    - ``XMSS <src/lib/pubkey/xmss/>``
    - ``[src/lib/hash]/sha1/sha1.cpp``
    """

    truncated_target_re = re.compile(r"\[(.*)(/\]|\]/)(.*)")

    def run(self) -> tuple[list[Node], list[system_message]]:
        self.parse_target()
        ref_uri = self.build_uri()

        if self.env.app.config.src_ref_check_url:
            if result := self.check_url(ref_uri):
                return result

        ref_node = nodes.reference('', '', internal=False, refuri=ref_uri, **self.options)
        if self.has_explicit_title:
            ref_node += nodes.Text(self.title)
        else:
            ref_node += nodes.literal(self.text, self.text)

        return [ref_node], []

    def parse_target(self) -> None:
        """ Check if the target is marked as truncated and adapt the target and text accordingly."""
        match = self.truncated_target_re.match(self.target)
        if match:
            self.target = f"{match.group(1)}/{match.group(3)}"
            self.text = f".../{match.group(3)}"

    def build_uri(self) -> str:
        return f'{self.env.app.config.src_ref_base_url}/{self.env.app.config.src_ref_reference}/{self.target}'

    def check_url(self, url: str) -> tuple[list[Node], list[system_message]] | None:
        ret = requests.head(url)
        if ret.status_code < 400:
            return None

        msg = self.inliner.reporter.error(f'invalid source reference to path "{self.target}", GitHub said: {ret.status_code} - {ret.reason} (requested: {url})',
                                          line=self.lineno)
        prb = self.inliner.problematic(self.rawtext, self.rawtext, msg)
        return [prb], [msg]

