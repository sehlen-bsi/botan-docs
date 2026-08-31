Appendix: Review of Botan PR #5523
==================================

The review in this section was entirely written by Anthropic's Fable 5 model. Please treat it with care as appropriate for AI generated content.

**"Update BoGo shim, various TLS updates"**

- **PR:** `randombit/botan#5523 <https://github.com/randombit/botan/pull/5523>`_
  (branch ``jack/update-bogo``)
- **Author:** Jack Lloyd — **Merged:** 2026-04-19 as ``e10ad9c01``, 16 commits,
  +1074/-423 across 33 files
- **First released in:** Botan 3.12.0 (tagged 2026-05-06)
- **Scope:** TLS 1.2/1.3 protocol behavior (``src/lib/tls``), a new RFC 9258 PSK-import
  feature, the FIPS 140 build policy, and the BoGo (BoringSSL test suite) shim and its
  configuration.

The PR's nominal purpose is rebasing Botan's BoGo interoperability-test shim onto current
BoringSSL. Running the updated BoGo suite surfaced a series of protocol-conformance gaps and
small bugs in the production TLS library; the bulk of the PR fixes those. One genuinely new
piece of functionality (RFC 9258 PSK importer) is included because BoGo exercises it.

Functionality added
-------------------

RFC 9258 PSK importer (``917161cda``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The main feature addition: a new public class ``TLS::PSKImporter`` (marked
``BOTAN_PUBLIC_API(3, 12)``) in the new header ``tls_psk_13.h``, implementing the RFC 9258
"Importing External Pre-Shared Keys (PSKs) for TLS 1.3" mechanism. Given a base external
PSK, an identity, an optional context string, and the hash provisioned with the key
(SHA-256 default per RFC 9258), ``derive_imported_psk()`` derives a per-(protocol, KDF)
imported PSK:

- Builds the ``ImportedIdentity`` structure exactly per RFC 9258 §5.1
  (length-prefixed ``external_identity`` and ``context``, then ``target_protocol`` and
  ``target_kdf`` as 2-byte values); this serialized structure becomes the wire PSK identity.
- Runs ``HKDF-Extract(0, epsk)`` and ``HKDF-Expand-Label(epskx, "derived psk",
  Hash(ImportedIdentity), L)``. The implementation gets the two easily-conflated hash roles
  right, with in-source comments quoting the RFC: the HKDF itself uses the *EPSK's* hash,
  while the output length ``L`` comes from the *target* KDF.
- Supporting plumbing: ``Cipher_State::PSK_Type`` gains an ``Imported`` member so the
  binder key derivation uses the RFC 9258 ``"imp binder"`` label instead of RFC 8446's
  ``"ext binder"`` (using the wrong label would be an interoperability failure and a
  cross-protocol-derivation hygiene issue); ``ExternalPSK`` gains an ``is_imported`` flag
  (new four-argument constructor; the existing three-argument constructor keeps its
  behavior), and both the client and server PSK paths select the correct binder label from
  it. Notably, the ``External`` PSK type was previously marked "currently not implemented".
- The old header ``tls_psk_identity_13.h`` content moved into ``tls_psk_13.h``;
  the ``Ticket`` type alias remains as a deprecated name for ``PskIdentity``.

I verified the derivation logic against RFC 9258 §5.1 directly (structure layout, hash
selection, output length, label bytes ``"tls13 derived psk"`` via the standard HkdfLabel
encoding) and found no deviation. New KAT-style test vectors
(``src/tests/data/tls_13_psk_import.vec``) cover all four (EPSK hash, target hash)
combinations plus edge cases; a new test in ``test_tls.cpp`` consumes them. See the
"introduced bugs" section for input-validation gaps found and fixed after merge.

More accurate ``Group_Params::is_available()`` (``6c44108a7``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rewritten from a handful of negative ``#if`` checks into a compile-time-generated, sorted
table of actually-available group codes, searched with ``std::binary_search``. This is a
functional improvement, not just a cleanup: the old code never checked availability of the
NIST/Brainpool curves at all (it only special-cased X25519/X448, FFDHE, ML-KEM and
FrodoKEM), so a minimized build with e.g. secp384r1 compiled out would still report the
group as available, offer it, and then fail during the handshake. The new table derives
each curve's availability from the ``BOTAN_HAS_PCURVES_*`` module macros and correctly
requires *both* components for hybrid PQ groups. Unrecognized codes still return ``true``
(they may be application-defined custom groups handled via callbacks) — unchanged behavior,
explicitly commented.

BoGo shim and test infrastructure (``579f1703c``, ``b35180824``, ``badf53a03``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Not production-library code, but the enabler for everything else in the PR:

- ``579f1703c`` fixes a TCP-level race in the shim's socket teardown: closing a socket
  with unread data in the receive buffer makes the kernel send RST, which can discard a
  yet-undelivered close_notify/fatal alert, causing flaky BoGo failures. The destructor now
  does ``shutdown(SHUT_WR)``, drains pending input, then closes.
- ``b35180824`` maps BoGo's expectations for offering PQ/hybrid groups onto Botan's policy
  configuration.
- ``badf53a03`` rebases the shim onto current BoringSSL ``main``, updates the three
  ``config*.json`` disabled-test lists, bumps the pinned BoGo revision
  (``repo_config.env``), and adjusts CI.

Bug and vulnerability fixes
---------------------------

Client-side validation of server ALPN selection (``1eaaaf2aa``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The most security-relevant fix in the PR. Neither the TLS 1.2 nor the TLS 1.3 client
verified that the ALPN protocol selected by the server was actually among the protocols the
client offered (RFC 7301 §3.2 requires the selection to come "from among the list that was
advertised by the client"). A malicious or broken server could steer a Botan client into an
application protocol it never offered. Because ALPN is the security boundary that
cross-protocol attacks such as ALPACA exploit, accepting an un-offered protocol weakens the
protection ALPN is meant to provide. Both clients now abort with an ``illegal_parameter``
alert if the selected protocol was not offered. Additionally, an *empty* ALPN extension
from the peer is now a ``Decoding_Error`` instead of being silently accepted as "no
protocol".

Note the symmetric server-side gap (verifying that the protocol the *application callback*
selects was offered by the client) was not covered here; it was fixed shortly after in
``fd1e58470`` (2026-04-26), which also shipped in 3.12.0.

Do not echo SNI on TLS 1.3 resumption (``43e24fd77``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

RFC 6066 §3: "When resuming a session, the server MUST NOT include a server_name extension
in the server hello." Botan's TLS 1.3 server unconditionally echoed an empty SNI
acknowledgment in EncryptedExtensions; it now suppresses it when the handshake is a
resumption. Conformance fix (BoGo-enforced). An interesting consequence, acknowledged in
the PR: the *published RFC 8448 test vectors* include the SNI echo in the resumption
transcript and are therefore themselves in conflict with RFC 6066 — Botan's stored RFC 8448
resumption transcript (``tls_13_rfc8448/transcripts.vec``) had to be regenerated with the
extension removed. This is a deliberate, documented divergence from the (incorrect) RFC
8448 expected bytes, not a test fudge.

Reject reflected extensions that were never actually sent (``17ed96fb6``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Extensions::extension_types()`` — the set used for the "peer answered with an extension
we did not request" check — included extensions whose objects existed but whose ``empty()``
was true, i.e. extensions that ``serialize()`` never put on the wire. A server could
therefore reply with such an extension and the client would treat it as legitimately
requested and process it, despite never having sent it. The offered-set is now computed
consistently with serialization. This closes a small but real hole in the
unsolicited-extension defense (the class of issue behind several historical TLS
state-confusion attacks). Follow-ups ``46d8ac4a1``/``138148ccf``/``f686a285c``
(2026-04-26, also in 3.12.0) continued tightening this area from the sending side.

Constant-time comparison for renegotiation-info (``8acf5b23f``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The RFC 5746 secure-renegotiation verify-data comparison in both client and server
directions used ``operator==`` (short-circuiting). The commit itself notes there is no
apparent attack — any mismatch tears down the session, so an oracle cannot be iterated —
but verify-data is keyed material and comparing it in constant time
(``CT::is_equal``) is correct hygiene. Defense-in-depth, no functional change.

Fix ``PskIdentity::age()`` de-obfuscation (``44d97a6f2``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plain arithmetic bug in public API: RFC 8446 §4.2.11.1 obfuscates the ticket age by
*adding* ``ticket_age_add`` mod 2^32; recovering the age must therefore *subtract* it.
``age()`` instead called the obfuscation function again, adding the value a second time and
returning garbage. There are currently no in-tree callers (Botan's server does not yet
implement the 0-RTT ticket-freshness window where the age matters most), but any
application using this accessor to implement the RFC 8446 §8.3 freshness check got a
meaningless value — which could silently disable an anti-replay measure. Correct fix,
with the correct mod-2^32 wrapping semantics via ``uint32_t`` arithmetic.

Do not offer ``certificate_type`` when TLS 1.2 may be negotiated (``03fe5aacc``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Raw public keys (RFC 7250) are implemented in Botan only for TLS 1.3. The client offered
the ``client_certificate_type``/``server_certificate_type`` extensions unconditionally, so
a client configured for 1.2+1.3 could end up negotiating TLS 1.2 *and* RPK — a combination
the implementation cannot actually run, failing later in the handshake. The extensions are
now offered only when TLS 1.2 is disabled in policy. This is a correctness fix with a
functional trade-off: mixed 1.2+1.3 clients lose the ability to use RPK even against
1.3-only servers; strictly a conservative choice until RPK-for-1.2 exists.

Consistent alert for invalid peer key material (``fd13a60b5``, ``9289301b5``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``tls_kem_encapsulate`` and ``tls_ephemeral_key_agreement`` caught ``Decoding_Error`` from
public-key parsing (mapping it to an ``illegal_parameter`` alert) but not
``Invalid_Argument``, which several KEM/ECDH implementations throw for well-formed-but-
invalid keys (e.g. a point not on the curve, a malformed ML-KEM encapsulation key). The
uncaught exception would propagate out of the channel instead of producing a proper fatal
alert — an availability/robustness issue and a protocol-hygiene one (the peer sees a TCP
reset instead of ``illegal_parameter``). Both callbacks now map ``Invalid_Argument``
identically. Note this pattern of "internal exception type leaks out of the TLS state
machine" is the TLS-side analogue of the exception-type fixes reviewed in PR #5569.

KeyShare/supported_groups consistency check simplification (``1abd86cd0``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The server-side RFC 8446 §4.2.8 check (key_share entries must be a subset of
supported_groups, in the same order) is rewritten from a stateful lambda into a single
forward sweep with an advancing iterator. Semantics are unchanged given the (parser-
enforced) uniqueness of both lists; I verified the equivalence. Readability refactor.

FIPS 140 policy: allow HKDF (``6f3a19805``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``fips140`` module policy prohibited the ``hkdf`` module, which is inconsistent (HKDF
is NIST-approved per SP 800-56C rev. 2) and blocks TLS 1.3 entirely, since the TLS 1.3 key
schedule is built on HKDF. Removing the prohibition makes the FIPS build policy usable with
TLS 1.3. Build-configuration fix; no runtime code change.

Documentation (``b490f8e46``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adds a comment to ``Signature_Scheme::is_suitable_for`` documenting that it enforces the
TLS 1.3 curve-hash binding (e.g. ``ecdsa_secp256r1_sha256`` only with P-256 keys) and must
*not* be used for TLS 1.2 scheme selection, where RFC 5246 imposes no such binding. Comment
only, but it documents an easy-to-misuse invariant with real interop consequences.

Introduced bugs
---------------

One real, pre-release-fixed issue, and no others found:

1. **PSK importer input-validation gaps** (introduced by ``917161cda``): the constructor
   accepted an *empty* identity, although RFC 9258 §5.1 declares
   ``external_identity<1...2^16-1>`` (minimum length 1); and it validated identity and
   context lengths independently against 65535, although the assembled ``ImportedIdentity``
   (identity + context + 8 bytes of framing) itself becomes a TLS PSK identity, which is
   capped at 65535 bytes as a whole. Oversized combinations would produce a PSK identity
   that cannot be legally serialized into the ClientHello. Both gaps were fixed upstream a
   week after merge in ``35c696ef8`` (2026-04-26) — **contained in Botan 3.12.0**, so no
   released version carries the flaw. The core derivation itself was correct from the
   start.

2. Points checked without findings: the ``is_resumption`` flag threading for the SNI echo
   (server-only constructor; the deserializing constructor is unaffected); binder-label
   selection for all three PSK types on both client and server paths; the equivalence of
   the KeyShare-ordering rewrite; the ``Group_Params`` table's handling of hybrid groups
   (requires both components) and of unknown codes (permissive, as before); mod-2^32
   semantics of the ``age()`` fix; and that the regenerated RFC 8448 resumption transcript
   only changes the EncryptedExtensions contents (SNI removal) plus the consequential
   record bytes.

Also worth noting as *behavioral* (not bug) regressions: RPK can no longer be offered by
clients that also enable TLS 1.2 (``03fe5aacc``, see above), and applications relying on
Botan's former leniency (accepting a server ALPN outside the offered list, or empty ALPN
extensions) will now see handshakes abort — in both cases the previous behavior was the
defect.

Remaining gaps in the touched areas (all closed before the 3.12.0 release)
--------------------------------------------------------------------------

BoGo-driven hardening continued immediately after this PR; the direct follow-ups below were
all merged 2026-04-26 and are **included in Botan 3.12.0** together with this PR:

.. list-table::
   :widths: 20 60 20
   :header-rows: 1

   * - Commit
     - Change
     - In Botan 3.12?
   * - ``35c696ef8``
     - PSK importer length checks (fixes the gaps introduced here, see above)
     - Yes
   * - ``fd1e58470``
     - Server-side counterpart of the ALPN fix: verify the application-selected protocol
       was actually offered by the client
     - Yes
   * - ``46d8ac4a1``
     - Guard against sending accidentally invalid TLS extensions
     - Yes
   * - ``138148ccf``
     - Prevent the ``tls_modify_extensions`` callback from creating an invalid message
     - Yes
   * - ``f686a285c``
     - Tighten length and decode-time validation across TLS extension parsers
     - Yes
   * - ``66fcc7905``
     - Fix a TLS 1.3 bug relating to client certificate requests
     - Yes

Verdict
-------

A well-scoped PR that uses a test-infrastructure refresh (BoGo rebase) to drive a set of
genuine protocol-conformance and robustness fixes. The security-relevant items are the
client-side ALPN selection validation (``1eaaaf2aa`` — closes a real cross-protocol-
confusion vector), the reflected-extension check fix (``17ed96fb6``), the exception-type
mappings that keep invalid peer key material from crashing out of the state machine
(``fd13a60b5``, ``9289301b5``), and the ``PskIdentity::age()`` arithmetic fix
(``44d97a6f2`` — a latent anti-replay weakness for API consumers). The new RFC 9258
importer is a correct implementation of a subtle two-hash derivation, verified here against
the RFC; its two input-validation gaps were caught by upstream within a week and fixed
before any release shipped the feature. All 16 commits and all follow-ups land together in
Botan 3.12.0, which is the first release to contain any of this work.
