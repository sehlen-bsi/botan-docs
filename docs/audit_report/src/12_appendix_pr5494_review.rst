Appendix: Review of Botan PR #5494
==================================


The review in this section was entirely written by Anthropic's Fable 5 model. Please treat it with care as appropriate for AI generated content.

**"Address various minor TLS 1.3 issues"**

- **PR:** `randombit/botan#5494 <https://github.com/randombit/botan/pull/5494>`_
  (branch merged as ``839b455636``)
- **Author:** Jack Lloyd — **Merged:** 2026-03-31 as ``839b455636``,
  +121/-40 across 11 files in the TLS stack
- **First released in:** Botan 3.11.1 (tagged 2026-03-31, the same rapid patch
  release that shipped PR #5499)
- **Scope:** TLS 1.2 and TLS 1.3 handshake and record handling, plus SNI
  extension parsing shared by both versions

The question examined here is whether this PR — presented as a rollup of "minor"
TLS 1.3 issues — closes any *real* vulnerability. The conclusion is that it
closes **one**: a non-constant-time PSK binder comparison, which is a
MAC-verification timing side channel. The remaining changes are RFC-conformance
and state-machine/robustness hardening; several touch real attack classes as
defense-in-depth, but none of them is by itself a demonstrably exploitable flaw
given Botan's existing checks.

The real vulnerability: non-constant-time PSK binder comparison
---------------------------------------------------------------

``PSK::validate_binder`` in ``tls_extensions_psk.cpp`` previously compared the
two binder values with ``std::vector``'s ``operator==``:

.. code-block:: cpp

   return psks[index].binder() == binder;                              // before
   return CT::is_equal<uint8_t>(binder, expected_binder).as_bool();    // after

This is the classic constant-time-comparison vulnerability class applied to a
MAC check. On the **server** — the exploitable direction, at the call site in
``tls_server_impl_13.cpp`` — ``validate_binder`` compares the
**attacker-supplied** binder taken from the ClientHello against the
**secret, server-computed** expected binder (``psk_binder_mac``, derived from
the PSK key and the handshake transcript). ``std::vector::operator==``
short-circuits at the first differing byte, so its running time leaks the
position of the first mismatch.

Because the attacker controls the ClientHello, they can hold the transcript —
and therefore the expected binder value — constant across connection attempts.
That is exactly the precondition that makes byte-by-byte timing recovery of the
expected binder theoretically possible. A recovered binder is a forged PSK
proof-of-possession: it authenticates the attacker as a party that knows the
PSK without the attacker actually possessing the PSK secret — i.e. a **PSK /
session-resumption authentication bypass**.

The fix was verified for correctness against attacker-controlled input:

- The client-supplied binder length is attacker-controlled (0..255 bytes; the
  PSK extension parser deliberately accepts any length here and defers rejection
  to ``validate_binder``, yielding a ``bad_record_mac`` alert).
- ``CT::is_equal`` on spans (``ct_utils.h``) first compares lengths and returns
  "not equal" on mismatch. This length-dependent early return is **safe**: the
  expected binder length is public information (fixed by the negotiated
  ciphersuite's hash function), not a secret, so leaking a length mismatch
  reveals nothing sensitive and cannot read out of bounds.
- When the lengths match, the comparison accumulates byte differences into a
  ``volatile`` value with no data-dependent branch, giving a genuine
  constant-time result.

**Severity: real, but low practical exploitability.** Network-observable timing
differences of a ``std::vector`` byte comparison are on the order of
nanoseconds and extremely noisy, and each guess requires a full handshake round
trip. However, this is precisely the bug pattern behind real MAC-comparison
timing CVEs, and constant-time comparison of authentication tags is mandatory
for a defensible TLS implementation. The fix is correct and belongs in the
library regardless of how difficult exploitation would be in practice. This is
the single change in the PR that closes a genuine vulnerability.

The remaining changes: conformance and robustness hardening
-----------------------------------------------------------

None of the following is, on its own, a demonstrably exploitable vulnerability,
but two of them harden against real attack classes and are worth recording.

**CCS-skip enforcement (TLS 1.2, ``tls_handshake_io.cpp``).** The previously
ignored ``expecting_ccs`` parameter of ``get_next_record`` is now honored: if a
handshake message arrives at a point where a ChangeCipherSpec is required, the
connection aborts with an ``unexpected_message`` alert. This hardens the TLS 1.2
state machine against a peer sending an encrypted Finished without the preceding
CCS (whereupon the encrypted bytes would otherwise be misinterpreted as a
plaintext handshake message) — the SMACK "SKIP" / early-Finished family of
message-skipping attacks. It is meaningful defense-in-depth, but the actual
security boundary (the Finished MAC verification) was already enforced
elsewhere, so this strengthens strictness rather than closing an independent
hole.

**``handshake_finished()`` now requires the peer Finished to be verified
(``tls_handshake_state_13.h``).** Previously the predicate returned true as soon
as both Finished *messages existed*; it now additionally requires the flag set
by ``confirm_peer_finished_verified()``, which is only called after the peer's
Finished MAC has successfully verified (in the client and server
``handle(Finished_13)`` paths). This tightens ``is_handshake_complete()``.
Because verification happens synchronously in the same handler and throws on
failure, the previous code exhibited only a transient inconsistency with no path
to treating an unverified handshake as complete; this is semantic hardening, not
the closure of an exploitable state.

**SNI extension parsing rewrite (``tls_extensions.cpp``).** Adds RFC 6066
validation: a server-sent SNI must be empty, a client-sent SNI must be
non-empty, a duplicate ``host_name`` entry is rejected, and unknown name types
are correctly skipped via their 16-bit length prefix instead of discarding the
remainder of the list. The old length arithmetic (``name_bytes -= 2 + size``)
was fragile, but every read went through a bounds-checked reader, so this is a
conformance and robustness improvement, not a memory-safety fix.

**Certificate_13 missing ``signature_algorithms`` (``msg_certificate_13.cpp``).**
Replaces a ``BOTAN_ASSERT_NOMSG`` with a proper ``missing_extension`` alert when
a client that omits ``signature_algorithms`` reaches server certificate
selection. ``BOTAN_ASSERT`` throws rather than aborting the process, so this was
a wrong-alert / internal-error issue on a malformed ClientHello rather than a
crash; the change brings the behavior in line with RFC 8446 4.2.3.

**HelloRetryRequest ciphersuite check (``tls_client_impl_13.cpp``).** The client
now rejects a HelloRetryRequest that selects a ciphersuite not usable in
TLS 1.3, with an ``illegal_parameter`` alert (RFC 8446 4.1.4 / Appendix B.4).
Conformance.

**Empty inner-plaintext rejection (``tls_record_layer_13.cpp``).** Rejects a
protected record whose ``TLSInnerPlaintext.content`` is empty for Handshake or
Alert types, per RFC 8446 5.4, with an ``unexpected_message`` alert. Conformance
and minor DoS hygiene.

**Record-version check relaxation (``tls_record.cpp``).** The record-layer
version check is *loosened* to accept any ``{03,XX}`` value, dropping the former
upper bound on the minor byte, to comply with RFC 7568's requirement that
servers accept any ``{03,XX}`` as the ClientHello record version. This is a
deliberate, more-permissive conformance change, not a security fix.

**bogo_shim error mapping.** A single BoGo error-string mapping was added for
the new CCS-skip check; test plumbing only.

Verdict
-------

PR #5494 closes **one real vulnerability**: the non-constant-time PSK binder
comparison, a MAC-verification timing side channel whose worst-case consequence
is a PSK / session-resumption authentication bypass. Its practical
exploitability over a network is low, but the fix (a ``volatile`` constant-time
compare) is correct, safe against the attacker-controlled binder length, and
appropriate for a TLS library. Every other change in the PR is legitimate
RFC-conformance or state-machine and robustness hardening. Two of those — the
TLS 1.2 CCS-skip enforcement and the verified-peer-Finished tightening — harden
against real attack classes as defense-in-depth, but neither is independently
exploitable given Botan's existing Finished-MAC verification. All of the changes
shipped together in Botan 3.11.1.
