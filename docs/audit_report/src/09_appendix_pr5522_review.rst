Appendix: Review of Botan PR #5522
==================================

The review in this section was entirely written by Anthropic's Fable 5 model. Please treat it with care as appropriate for AI generated content.

**"Various TLS fixes"**

- **PR:** `randombit/botan#5522 <https://github.com/randombit/botan/pull/5522>`_
  (branch ``jack/various-tls-fixes``)
- **Author:** Jack Lloyd — **Merged:** 2026-04-07 as ``5183e74ba``, 19 commits,
  +487/-218 across 31 files
- **First released in:** Botan 3.12.0 (tagged 2026-05-06)
- **Scope:** TLS 1.2 and 1.3 state machines and message parsing (``src/lib/tls``), TLS
  policy surface, the PQC hybrid key wrapper, and the BoGo shim.

This PR is the direct precursor of PR #5523 (reviewed in the previous appendix): the same
BoGo-test-driven hardening effort, merged twelve days earlier. Where #5523 centered on a
feature (RFC 9258) plus conformance fixes, #5522 is dominated by two themes:
**denial-of-service hardening** (five distinct resource-exhaustion vectors closed, several
with new policy knobs) and **protocol-conformance/robustness fixes**, two of which are
genuine security fixes (a downgrade-protection gap and a signature-scheme confusion).

Functionality added
-------------------

All feature additions are policy-surface extensions in support of the hardening below —
each a new virtual on ``TLS::Policy`` with a conservative default, overridable by
applications:

.. list-table::
   :widths: 40 15 45
   :header-rows: 1

   * - New policy option
     - Default
     - Purpose
   * - ``maximum_dh_group_size()``
     - 8192 bits
     - Upper bound on the ephemeral DH prime a TLS 1.2 client accepts (``e92900f24``)
   * - ``maximum_handshake_message_size()``
     - (policy-defined)
     - Cap on a single handshake message, enforced at TLS and DTLS reassembly
       (``4c3077695``)
   * - ``minimum_key_update_interval_ms()``
     - 1000 ms
     - Minimum interval between received TLS 1.3 KeyUpdates; 0 disables (``688355654``)
   * - ``maximum_session_tickets_per_connection()``
     - 10
     - Cap on NewSessionTicket messages a TLS 1.3 client processes; 0 disables
       (``688355654``)

In addition, ``ed13d7e8f`` and ``b37cc696f`` extend the (unstable-API) ``Extensions``
container: storage moves from a linear vector to a map keyed by extension code with a
separate insertion-order list (so lookups like ``get``/``has`` are no longer linear
scans while serialization order is preserved), and three new operations are added —
``reorder()`` (used to force the PSK extension last, see below), ``remove_extension()``
(replacing ``take()``), and ``extension_raw_bytes()``, which records each extension's
original wire bytes at deserialization time so later code can compare exact encodings.

Denial-of-service hardening
---------------------------

**KeyUpdate flooding (``688355654``).** The TLS 1.3 code carried a TODO noting that
without rate limiting a peer could force "an endless loop of key updates" — each KeyUpdate
with ``update_requested`` obligates the receiver to rekey and respond, making unbounded
CPU consumption trivially remotely triggerable. A received-KeyUpdate interval check
(default: at most one per second) now terminates offending connections with
``unexpected_message``. Trade-off worth noting: RFC 8446 does not forbid frequent
KeyUpdates, so a legitimately fast-rekeying peer trips the default limit — the PR
deliberately prefers a policy-tunable hard line over unbounded work. (The BoGo suite
models throttling as counter-based rather than time-based; #5523's description notes this
mismatch and leaves the time-based approach in place.)

**Session-ticket flooding (same commit).** A TLS 1.3 server may send arbitrarily many
NewSessionTicket messages; each one costs the client callback invocations and session-store
writes. The client now silently ignores tickets beyond the policy cap (default 10) rather
than terminating — correct choice, since many tickets are legitimate server behavior.

**PSK-identity lookup amplification (same commit).** ``choose_from_offered_tickets`` in
the server's session manager iterated *all* client-offered PSK identities, each one a
session-store lookup (potentially a database query). A client could offer thousands of
bogus identities per ClientHello. Lookups are now capped at 5. Note the graceful-degradation
semantics: a valid ticket at position 6 or later now results in a full handshake instead of
resumption — a performance, not correctness, regression for pathological-but-legitimate
clients.

**Handshake-message size (``4c3077695``).** A new policy cap enforced in both the TLS 1.2
stream reassembly (``Stream_Handshake_IO::get_next_record``) and the DTLS defragmenter
(``Datagram_Handshake_IO::add_record``, checked *before* buffering fragments). The wire
format allows 24-bit (16 MiB) messages; without a cap, a peer can force large allocations
per connection. TLS 1.3 already had ``maximum_certificate_chain_size``; this extends
protection to all message types and to the 1.2 stack.

**Sequence-number overflow (``473ddfdb7``).** RFC 8446 §5.3: "Sequence numbers MUST NOT
wrap." None of the three counters (TLS 1.2 stream read/write, DTLS 48-bit per-epoch write,
TLS 1.3 read/write) was checked. Wrapping a 64-bit counter is not reachable in practice
(2^64 records), but the DTLS write counter is 48 bits — large yet less absurd — and a
wrapped sequence number means nonce reuse under the same AEAD key, a catastrophic failure
mode for GCM/ChaCha20-Poly1305. All four sites now throw ``Invalid_State`` instead of
wrapping. Cheap, fail-closed insurance against the worst-case outcome.

**DH group size bounds (``e92900f24``).** The TLS 1.2 client checked
``minimum_dh_group_size`` only *after* running ``DL_Group::verify_group`` — and had no
upper bound at all. A malicious server could send an enormous prime (e.g. 100k bits) and
make the client burn CPU on primality testing before any policy check. The size window
(policy minimum, new 8192-bit maximum) is now enforced *before* group verification.
Ordering matters here; this is the actual fix, not the new knob.

Security fixes
--------------

**TLS 1.2 resumption omitted the downgrade-protection sentinel (``72f96b459``).**
RFC 8446 §4.1.3 requires a TLS 1.3-capable server negotiating TLS 1.2 to embed the
``DOWNGRD`` sentinel in the last 8 bytes of ``ServerHello.random``, so a 1.3-capable
client can detect a downgrade attack. Botan's TLS 1.2 server did this on full handshakes
(via ``make_server_hello_random``) but the *resumption* ServerHello constructor used plain
``make_hello_random`` — no sentinel. A downgrade forced onto the resumption path was
therefore undetectable by conforming clients. I verified ``make_server_hello_random``
embeds the sentinel exactly when ``offered_version.is_pre_tls_13() &&
policy.allow_tls13()``; the fix routes the resumption constructor through it with the
resumed session's version. Real, if narrow, downgrade-protection gap closed.

**Signature-scheme confusion via string comparison (``93685b08c``).** The TLS 1.2
``parse_sig_format`` check "was the scheme the peer signed with actually offered?"
compared schemes by their *name pair* (algorithm name, hash name). But
``Signature_Scheme::algorithm_name()`` returns ``"RSA"`` for both the PKCS#1 v1.5 *and*
the RSA-PSS code points, and the hash names also coincide (both families use "SHA-256"
etc.). Consequence: a peer that signed ServerKeyExchange or CertificateVerify with
``rsa_pkcs1_sha256`` would pass the offered-scheme check even if only
``rsa_pss_rsae_sha256`` had been offered (and vice versa) — the padding-scheme dimension
of the negotiation was simply invisible to the check. Verification itself used the
received scheme's padding, so this was not a signature forgery, but it allowed a peer to
substitute PKCS#1 v1.5 where policy/negotiation admitted only PSS: a policy-enforcement
bypass along exactly the axis (PSS vs. v1.5) that modern configurations care about.
Schemes are now compared by code point. The error message also becomes precise
(``scheme.to_string()``).

**Policy-forbidden schemes influenced ciphersuite choice (``9cd1da61a``).** In the TLS
1.2 server's ``choose_ciphersuite``, the "does the client support a usable hash for this
suite's signature algorithm" probe iterated the client's offered schemes without
intersecting them with the server's own ``allowed_signature_schemes()``. The server could
thus commit to a signature ciphersuite for which every mutually-known scheme was forbidden
by its policy. The signing path (``choose_sig_format``) draws only from policy-allowed
schemes, so the outcome was a later handshake failure rather than a forbidden signature —
a negotiation-correctness/availability fix that also keeps policy reasoning in one place.

Protocol-conformance and robustness fixes
-----------------------------------------

- **Reject sentinel handshake types on decode (``f2b62dd09``).** Botan's
  ``Handshake_Type`` enum contains internal sentinel values (``HelloRetryRequest``,
  ``HandshakeCCS``, ``None``) that are not legitimate TLS 1.2 wire values. Only ``None``
  was rejected, and only in the stream path. A peer sending e.g. the byte that maps to the
  internal CCS sentinel inside a handshake record could inject a value the state machine
  treats as a different kind of event — classic type-confusion surface. Both the stream
  and (newly) the datagram paths now reject all sentinels immediately on decode with
  ``unexpected_message``.
- **PSK extension forced last after HRR (``718d40439``).** RFC 8446 §4.2.11 requires
  ``pre_shared_key`` to be the last ClientHello extension (its binders cover the hello
  prefix). In the HelloRetryRequest retry path, extensions added during ``retry()`` (e.g.
  cookie) could land after PSK. The new ``Extensions::reorder()`` guarantees the
  invariant. Without this, a resuming client that received an HRR with a cookie produced a
  malformed ClientHello — an interop failure with strict servers.
- **Verify ClientHello immutability across HRR (``b37cc696f``).** RFC 8446 §4.1.2 allows
  the client to change only a named set of extensions (key_share, pre_shared_key,
  early_data, cookie, padding) between CH1 and CH2; the server-side check previously
  compared only extension *presence* and had a TODO for contents. Using the new
  ``extension_raw_bytes()``, the server now compares exact wire encodings of all other
  extensions and aborts with ``illegal_parameter`` on mutation. This closes a
  transcript-manipulation gap: CH1 is bound into the transcript hash, and mutations the
  server fails to detect are exactly the kind of ambiguity downgrade-style attacks feed
  on. Residual leniency (extensions Botan does not implement were still exempt) was
  removed in the follow-up ``a472079bb`` (2026-04-26, also in 3.12.0).
- **DTLS handshake fragment truncation (``0de116f4d``).** ``format_fragment`` took the
  fragment offset and total message length as ``uint16_t``, silently truncating messages
  over 64 KiB (the DTLS wire format allows 24 bits). A large outgoing message — entirely
  plausible with post-quantum certificate chains — was fragmented with corrupted
  offset/length fields, producing garbage the peer cannot reassemble. Parameters widened
  to ``uint32_t``. Sending-side correctness bug, silent data corruption class; no
  security impact (the peer's reassembly fails).
- **``Hybrid_KEM_PublicKey::algo_name()`` (``1d8c27937``).** Classic
  ``std::ostringstream`` misuse: constructing with ``("Hybrid(")`` sets the initial
  buffer but leaves the write position at 0, so subsequent output *overwrites* the prefix
  instead of appending — yielding names like ``x25519(`` instead of
  ``Hybrid(x25519,ML-KEM-768)``. Diagnostic-value bug affecting the PQC hybrid wrapper;
  fixed by streaming the prefix.
- **Correct member in ``derive_read_traffic_key`` (``4653b8e7a``).** The read-side key
  derivation asserted and queried ``m_encrypt`` (the write cipher) for the key length
  instead of ``m_decrypt``. Latent rather than live — both directions of a TLS 1.3
  connection always use the same AEAD, so the lengths coincide — but the code was wrong
  and would break under any future asymmetric-cipher scenario, and the assert guarded the
  wrong object.
- **Documented spec deviation (``e6aad6582``).** RFC 8446 declares PSK
  ``identity<1..2^16-1>`` (non-empty), but Botan accepts empty identities because the
  BoGo reference tests themselves send them. Comment-only commit; the deviation is now
  explicit and intentional rather than accidental. (Consistent with the RFC-vectors-vs-RFC
  conflict noted for SNI in the #5523 review: the reference ecosystem is not always
  self-consistent.)

Performance and refactoring
---------------------------

- **``83087c2d7``** replaces quadratic duplicate detection in ``key_share`` and
  ``supported_groups`` parsing with an ``unordered_set`` — with maximum-size hellos the
  old ``O(n^2)`` scans were themselves a small parsing-cost amplification.
- **``ed13d7e8f``** — the ``Extensions`` map refactor described above; also switches
  serialization to explicit insertion order, a prerequisite for ``reorder()``.
- **``e140927c3`` / ``d42cf7d01``** replace repeated ``vector::erase``-from-front
  (an ``O(n)`` shift per message/record) in the TLS 1.3 handshake and record layers with a
  read-offset plus compaction on refill; the record layer also releases the buffer
  entirely once drained. I reviewed the offset bookkeeping (invariant asserts at each
  step, offset reset in ``copy_data`` compaction and ``clear_read_buffer``,
  ``has_pending_data`` updated to compare offset against size) and found it consistent.
- **``eafc80e36``** updates the BoGo shim's error-message mappings (test infrastructure).

Introduced bugs
---------------

None found. Points specifically checked:

1. The offset-based buffer refactors (``e140927c3``, ``d42cf7d01``) — the highest-risk
   changes in the PR, since record/handshake reassembly is attacker-facing. All reads go
   through the offset-adjusted span, every mutation reasserts the offset invariant, and
   the partial-message predicate was updated along with the representation.
2. The KeyUpdate limiter's first-message case (sentinel ``m_last_key_update_ms == 0``)
   and its interaction with the mandated KeyUpdate *response* (rate limit applies to
   received updates only; the obligated reply is sent before the next receive can occur).
3. ``validate_updates`` raw-bytes comparison: wire bytes exist only for deserialized
   hellos, which is precisely the server-side CH1/CH2 case; the client's
   programmatically-built hellos skip the comparison rather than spuriously failing.
4. The sentinel-type rejection cannot mis-fire on the genuine CCS path: the
   ``expecting_ccs`` branch is taken before the wire-type check in the stream reader.
5. The 48-bit DTLS overflow guard triggers at the correct bound and before the increment.

Behavioral trade-offs to be aware of (deliberate, policy-tunable, but visible):
peers sending KeyUpdates faster than 1/s are disconnected; only the first 5 offered PSK
identities are considered for resumption; at most 10 session tickets per connection are
processed; DH groups above 8192 bits are rejected. Each changes observable behavior
against unusual-but-conforming peers, and each is overridable via ``TLS::Policy``.

Follow-ups in the same hardening campaign
-----------------------------------------

The BoGo-driven work continued directly in PR #5523 (merged 2026-04-19, previous appendix)
and a further batch on 2026-04-26. Follow-ups touching the areas changed here:

.. list-table::
   :widths: 20 60 20
   :header-rows: 1

   * - Commit
     - Change
     - In Botan 3.12?
   * - ``a472079bb``
     - Removes the unimplemented-extension exemption from the CH1/CH2 mutation check
       added by ``b37cc696f`` — unknown extensions are now held to RFC 8446 §4.1.2 too
     - Yes
   * - ``17ed96fb6`` (PR #5523)
     - ``extension_types()`` excludes never-serialized (empty) extensions, refining the
       offered-set semantics this PR's refactor centralized
     - Yes
   * - ``46d8ac4a1``, ``138148ccf``, ``f686a285c``
     - Guards against sending invalid extensions, ``tls_modify_extensions`` misuse, and
       tightened extension-parser validation
     - Yes

All of PR #5522, PR #5523, and the 2026-04-26 batch shipped together in Botan 3.12.0;
there is no released/unreleased split for any change discussed here.

Verdict
-------

A substantial hardening PR whose common thread is bounding attacker-driven resource
consumption and tightening TLS 1.2/1.3 negotiation exactness. The two changes with
genuine security weight are the downgrade-sentinel fix for TLS 1.2 resumption
(``72f96b459`` — a conforming client could not detect a downgrade forced onto the
resumption path) and the signature-scheme code-point comparison (``93685b08c`` — PKCS#1
v1.5/PSS were interchangeable in the offered-scheme check). The DoS batch (KeyUpdate rate
limiting, ticket and PSK-lookup caps, message-size cap, pre-verification DH size bounds,
sequence-number overflow guards) closes several cheap remote resource-exhaustion vectors,
each with a policy escape hatch. The riskiest refactors (buffer-offset management in the
attacker-facing record/handshake layers) are implemented with explicit invariants and
survived scrutiny; I found no introduced bugs. Residual leniencies left by this PR — the
unimplemented-extension exemption in the HRR check and the empty-extension offered-set
semantics — were both closed within three weeks and shipped in the same release (3.12.0),
so no released version carries them.
