import requests
from docutils import nodes
from docutils.nodes import Node, system_message
from sphinx.application import Sphinx
from sphinx.roles import ReferenceRole


class SourceReferenceRole(ReferenceRole):
    """A role to create a reference to a source file.

    The reference will link to ``<src_ref_base_url>/<src_ref_reference>/<target>``.

    The text of the role will be the ``<target>``.
    The reference role can also accept ``link title <target>`` style as a text for
    the role.

    Options:

    - ``src_ref_base_url``: Base URL for the link.
    - ``src_ref_reference``: Name of a branch, a tag or an SHA-1 hash to link to.
    - ``src_ref_check_url``: If true, check that the URL is reachable.

    Example:

    - ``src/lib/hash/sha1/sha1.cpp``
    - ``src/lib/pubkey/xmss/``
    - ``XMSS <src/lib/pubkey/xmss/>``
    """

    def run(self) -> tuple[list[Node], list[system_message]]:
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


def setup(app: Sphinx):
    app.add_config_value('src_ref_base_url', 'https://github.com/randombit/botan/blob', 'html')
    app.add_config_value('src_ref_reference', 'master', 'html')
    app.add_config_value('src_ref_check_url', False, 'env')

    app.add_role('srcref', SourceReferenceRole())

    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
