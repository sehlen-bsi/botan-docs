import requests
import re
from docutils import nodes
from docutils.nodes import Node, system_message
from sphinx.roles import ReferenceRole

class LinkTarget:
    extended_target_regex = re.compile(r"^(?:\[(?P<to_be_truncated>[^\]\s:]+)\])?(?P<path>[^\s:]+)(?::(?P<line_number>\d+)\|(?P<validation_search_string>[^\n]*))?$")

    @property
    def uri(self) -> str:
        line_extension = f"#L{self.line}" if self.has_line else ''
        target_url = ''.join([self._truncated, self._path, line_extension])
        return '/'.join([self._base_url, "blob", self._github_reference, target_url])

    @property
    def uri_to_raw_file(self) -> str:
        target_url = ''.join([self._truncated, self._path])
        return '/'.join([self._base_url, "raw", self._github_reference, target_url])

    @property
    def text_suggestion(self) -> str:
        truncation_mark = '...' if self.is_truncated else ''
        line_extension = f":{self.line}" if self.has_line else ''
        return f"{truncation_mark}{self._path}{line_extension}"

    @property
    def has_line(self) -> bool:
        return self._line != ''

    @property
    def is_truncated(self) -> bool:
        return self._truncated != ''

    @property
    def line(self) -> int:
        if not self.has_line:
            raise ValueError("No line number was provided")
        return int(self._line)

    def check(self) -> str |  None:
        if self.has_line:
            ret = requests.get(self.uri_to_raw_file)
        else:
            ret = requests.head(self.uri)

        if ret.status_code >= 400:
            return f"Failed to fetch target URL '{self.uri}' : {ret.status_code} {ret.reason}"

        if self.has_line:
            lines = ret.text.splitlines()
            if len(lines) < self.line:
                return f"Target file '{self.uri}' only has {len(lines)} lines, but line {self.line} was requested."
            line = lines[self.line - 1]
            if self.search_string not in line:
                return f"Target file '{self.uri}' does not contain the expected string '{self.search_string}' in line {self.line}."

        return None

    def __init__(self, target_string: str, base_url: str, reference: str):

        m = self.extended_target_regex.match(target_string)
        if not m:
            raise ValueError(f"Invalid target string: {target_string}")

        self._base_url = base_url
        self._github_reference = reference
        self._truncated = m['to_be_truncated'] or ''
        self._path = m['path']
        self._line = m['line_number'] or ''
        self.search_string = m['validation_search_string'] or ''


class SourceReferenceRole(ReferenceRole):
    """A role to create a reference to a source file.

    The reference will link to ``<src_ref_base_url>/<src_ref_reference>/<target>[:<line number>|<expected line content>]``.

    The text of the role will be the ``<target>``.
    The reference role can also accept ``link title <target>`` style as a text for
    the role.
    Alternatively, the target can be displayed truncated. For example:
    ``[src/lib/hash]/sha1/sha1.cpp`` is displayed as ``.../sha1/sha1.cpp``.

    The target may optionally include a line number. For instance, to deep-link
    to a specific function in a source file. Note that the line number MUST be
    followed by a search string that must match the line's content. That way, CI
    can verify that the line number still points to the expected content even if
    the upstream source file changes.

    Options:

    - ``src_ref_base_url``: Base URL for the link.
    - ``src_ref_reference``: Name of a branch, a tag or an SHA-1 hash to link to.
    - ``src_ref_check_url``: If true, check that the URL is reachable.

    Example:

    - ``src/lib/hash/sha1/sha1.cpp``
    - ``src/lib/pubkey/xmss/``
    - ``XMSS <src/lib/pubkey/xmss/>``
    - ``[src/lib/hash]/sha1/sha1.cpp``
    - ``TLS 1.3 key export <src/lib/tls/tls13/tls_cipher_state.cpp:400|CipherState::export_key>``
    """

    def run(self) -> tuple[list[Node], list[system_message]]:
        link_target = LinkTarget(self.target, self.env.app.config.src_ref_base_url, self.env.app.config.src_ref_reference)

        # Check that the linked code is reachable and seems up-to-date
        if self.env.app.config.src_ref_check_url and (errormsg := link_target.check()):
            msg = self.inliner.reporter.error(errormsg, line=self.lineno)
            prb = self.inliner.problematic(self.rawtext, self.rawtext, msg)
            return [prb], [msg]

        ref_node = nodes.reference('', '', internal=False, refuri=link_target.uri, **self.options)
        if self.has_explicit_title:
            ref_node += nodes.Text(self.title)
        else:
            text = link_target.text_suggestion
            ref_node += nodes.literal(text, text)

        return [ref_node], []
