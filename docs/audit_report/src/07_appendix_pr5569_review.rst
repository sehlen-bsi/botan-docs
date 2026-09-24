Appendix: Review of Botan PR #5569
==================================

The review in this section was entirely written by Anthropic's Fable 5 model. Please treat it with care as appropriate for AI generated content.

**"More ASN.1 and X.509 related bug fixes and hardening"**

- **PR:** `randombit/botan#5569 <https://github.com/randombit/botan/pull/5569>`_
  (branch ``jack/more-asn1-hardening``)
- **Author:** Jack Lloyd — **Merged:** 2026-05-06 as ``5e3e3f97d``, 35 commits,
  +1022/-181 across 39 files
- **First released in:** Botan 3.12.0 (tagged 2026-05-06)
- **Scope:** BER/DER codec (``src/lib/asn1``), X.509 certificate/extension/OCSP/CRL/
  name-constraint handling (``src/lib/x509``), charset/parsing utilities, in-memory
  certificate store, plus tests.

This review covers each change (grouped by area), the compatibility or security issue it
addresses, an assessment of whether the PR introduces bugs, and a survey of security issues
that remained in these functionalities after the PR — separated into those since fixed
upstream and those still open on current master.

Change-by-change review
-----------------------

BER/DER codec core
~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Commit
     - Change
   * - ``400a21c0e``
     - Reject trailing data after PSS-Params
   * - ``cbffb9cf4``
     - Delete ``BER_Decoder`` copy constructor
   * - ``3cc416fec``
     - Simplify BER length-field parsing
   * - ``204b1934e``
     - Handle pushed-back objects in ``discard_remaining``/``end_cons``
   * - ``38f653763``
     - Fix DER encoding of context-specific tag 17

**400a21c0e — PSS-Params trailing data.** ``PSS_Params::PSS_Params(span)`` decoded the
RSASSA-PSS ``AlgorithmIdentifier`` parameters but never called ``verify_end()``, so arbitrary
trailing bytes after the parameter structure were accepted. *Security issue addressed:*
signature-parameter malleability — the same signature could be carried by many distinct DER
encodings, enabling fingerprint/blocklist evasion and cross-implementation parsing
differentials. One-line fail-closed fix; correct.

**cbffb9cf4 — copy constructor removal.** The old "copy" constructor was actually
destructive: it ``std::swap``-ed the ``mutable std::unique_ptr<DataSource>`` out of the
*const* source object. Any code that copied a ``BER_Decoder`` and then kept using the original
silently read from a drained source. *Issue addressed:* a latent misparse/UB hazard in an API
that looked value-semantic but wasn't. This is an acknowledged SemVer break (the commit
message says so); ``McEliece_PrivateKey`` decoding, the only in-tree user relying on it, was
rewritten to use named local decoders. The rewrite preserves the decode structure (verified by
reading the before/after chain: same fields, same tags, ``verify_end()`` retained). Correct
and overdue.

**3cc416fec — length parsing.** Replaces ``field_size > 5`` with the equivalent
``num_length_bytes > 4`` and removes the ``get_byte<0>(length) != 0`` "overflow" check. With
at most 4 length octets the accumulated length fits 32 bits, so the removed check was dead
code on both 32- and 64-bit ``size_t`` (on 64-bit it tested the top byte of a value that never
exceeded 2\ :sup:`32` - 1; on 32-bit the accumulation never sets the top byte before the final
shift). No behavior change; pure clarity. Verified equivalent.

**204b1934e — pushed-object bookkeeping.** ``BER_Decoder`` supports one-object pushback
(used by ``peek_next_object()`` and the ``decode_optional*`` family). Previously
``discard_remaining()`` ignored a pushed object and ``end_cons()`` only checked the underlying
source for emptiness — so an object that had been *read from the source but pushed back*
counted as consumed, and a constructed type could close successfully while smuggling an
unconsumed element. *Security issue addressed:* silent acceptance of extra elements inside
SEQUENCEs (data smuggling / non-canonical acceptance). Now ``discard_remaining()`` clears the
pushed object explicitly and ``end_cons()`` throws if one is pending. This is a behavioral
contract change for the public ``BER_Decoder`` API: external code that peeks and then calls
``end_cons()`` without consuming now gets a ``Decoding_Error``. In-tree callers were audited
within the PR itself (see ``a60dcb673`` adding the missing ``decode_null()`` consumption, and
``e74e0476b`` below, both of which this change would otherwise have broken).

**38f653763 — context tag 17 vs. SET.** ``DER_Encoder::DER_Sequence`` decided "am I a SET
(sort members per DER)?" by comparing only the type tag against ``ASN1_Type::Set`` (= 17),
ignoring the class. A context-specific constructed tag ``[17]`` was therefore silently sorted
like a universal SET, corrupting the element order, and ``start_explicit(17)`` was outright
prohibited. *Issue addressed:* encoding correctness for structures using tag number 17
(compatibility, and canonical-encoding correctness). Fix checks ``m_class_tag ==
ASN1_Class::Universal`` in all three places and removes the ``start_explicit`` prohibition.
Correct. Note this changes emitted bytes for any (out-of-tree) user who previously encoded
``[17]`` — but the previous bytes were simply wrong.

String validation and case folding
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**2eb2c5dc3 (+ tests in 5d0ae91f9) — ASN.1 string charset validation.** The centerpiece of
the PR. Adds a constexpr 256-entry table validating NumericString, PrintableString, IA5String
and VisibleString character sets, and full UTF-8 well-formedness checking
(``is_valid_utf8``) for UTF8String — enforced both when *constructing* an ``ASN1_String`` for
encoding and when *decoding* one (``asn1_str.cpp``).

*Security issues addressed:*

- **Embedded-NUL spoofing** (the classic ``CN=www.good.com\0.evil.com`` class of attack):
  NUL is now rejected in PrintableString (not in the charset) and explicitly excluded from
  IA5String ("Don't allow embedded null in IA5 even if technically valid"). The PR even had
  to fix its own test vectors (``x509_dn.vec``), which previously contained NUL bytes inside
  PrintableStrings.
- **Invalid UTF-8** reaching applications (over-long encodings, surrogates, truncated
  sequences) — a well-known source of downstream comparison/normalization bugs.
- **Parser differentials**: strict charset enforcement narrows the gap between what Botan and
  other strict stacks accept.

*Compatibility impact (deliberate, but worth flagging):* the charset check runs during DN
decoding, which is part of the main TBSCertificate parse — a single out-of-charset character
(e.g. ``*``, ``@``, ``_``, ``&`` in a PrintableString attribute, all seen in legacy CA
output) makes the entire certificate unparseable, with no lenient mode for inspection. Old
wildcard certificates carrying ``CN=*.example.com`` as PrintableString are the most likely
real-world casualty. Upstream has not relaxed the table since merge, so this strictness is
intentional policy. Also note: ``choose_encoding`` now additionally treats ``'``
(apostrophe) as PrintableString-safe, which it is per X.680 — a minor encode-side behavior
change (strings with apostrophes previously encoded as UTF8String now encode as
PrintableString).

**54dd18247 — locale-independent case folding.** Replaces ``std::tolower``/``toupper``
(locale-sensitive) with explicit ASCII folds in ``tolower_string`` (DNS name
canonicalization), X.500 DN canonicalization (``x509_dn.cpp``), and the macOS certstore DN
normalizer. *Security issue addressed:* under e.g. a Turkish locale, ``tolower('I')`` does
not yield ``'i'``, so DN matching and DNS name comparison could disagree between processes
with different locales — canonicalization mismatch is a real certificate-matching hazard,
not just cosmetics. Correct; the affected inputs are ASCII-only by RFC (1035 / 5280).

**86ab37de4 — ASN1_Time exception type.** ``set_to()`` throws ``Invalid_Argument`` for
out-of-range dates; during BER decoding this escaped as the wrong exception type, bypassing
``catch(Decoding_Error&)`` recovery paths (notably the extension-decode fallback). Now
wrapped into ``Decoding_Error``. Small but load-bearing: several fail-closed paths key on the
exception type.

X.509 extension decoding strictness
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 15 55 30
   :header-rows: 1

   * - Commit
     - Rule enforced
     - RFC basis
   * - ``6683c047d``
     - No duplicate extension OIDs
     - RFC 5280 §4.2
   * - ``1ed2913ce``
     - SAN/IAN/EKU/CertificatePolicies/AIA/CRLDP lists non-empty
     - SEQUENCE SIZE (1..MAX)
   * - ``7f8814fe0``
     - KeyUsage must have at least one bit set
     - RFC 5280 §4.2.1.3
   * - ``d11a953e6``
     - No pathLenConstraint when cA=FALSE
     - RFC 5280 §4.2.1.9
   * - ``38cfb766a``
     - GeneralSubtree ``maximum`` must be absent
     - RFC 5280 §4.2.1.10
   * - ``b9c3414db``
     - CRLReason must be a defined enum value (not 7, at most 10)
     - RFC 5280 §5.3.1
   * - ``ef065669a``
     - SKID/AKID keyIdentifier length in [1, 64]
     - heuristic cap

**6683c047d — duplicate extensions.** Previously duplicates were caught only as a special
case during *path validation*; a consumer using ``X509_Certificate`` accessors directly (or
any non-path-validated use: CRLs, PKCS#10, OCSP single-extensions) saw whichever copy
``std::map::emplace`` happened to keep (the first), while other stacks may honor the last.
*Security issue addressed:* extension-shadowing/parser-differential attacks. Rejecting at
decode is the right layer. The BSI test expectation change (``ext_05``) documents the visible
behavior shift: the certificate now fails to *parse* rather than failing validation.

**6e9afc74b — broadened catch.** ``Extensions::create_extn_obj`` now converts *any*
``Botan::Exception`` (not just ``Decoding_Error``) from ``decode_inner`` into an
``Unknown_Extension(failed_to_decode=true)``. Rationale: any escaping exception means the
extension didn't parse; letting ``Invalid_Argument``, ``BER_Decoding_Error`` subtype quirks,
etc. propagate made whole-certificate parsing fail unpredictably. Combined with the existing
critical-extension tracking this is fail-closed where it matters: a *critical* extension that
fails to decode still causes ``UNKNOWN_CRITICAL_EXTENSION`` in validation. Minor hygiene
concern: this also swallows ``Internal_Error``, so genuine library bugs get downgraded to
"extension failed to decode" — acceptable for parsing robustness, slightly unfortunate for
debugging.

I specifically checked the interaction that this leniency could have created for hostname
verification: if a SAN extension fails its now-stricter decode and is non-critical, the
certificate still parses, the SAN list is empty — but CN fallback is correctly suppressed
because ``m_subject_alt_name_exists`` is set from OID *presence*, not decode success
(``x509cert.cpp:279``), and ``matches_dns_name`` checks that flag (``x509cert.cpp:831``). So
a malformed SAN makes the certificate match *nothing* (fail-closed) rather than falling back
to CN. Good design; no differential introduced.

**ef065669a — key-identifier size limits.** Rejects empty and >64-byte
SubjectKeyIdentifier / AuthorityKeyIdentifier keyIdentifier values. *Issue addressed:*
memory-amplification (key IDs are indexed and compared during path building) and nonsense
inputs. 64 bytes covers every real generation scheme (SHA-1 = 20, SHA-256 = 32, RFC 7093
methods). The AKI rewrite also makes the keyIdentifier-presence check explicit via
``peek_next_object().is_a(0, ContextSpecific)``; I verified this predicate is exactly the one
``decode_optional_string`` uses internally (``ber_dec.h:510``), so the "present" flag and the
consumed value cannot disagree. The ``authorityCertIssuer``/``authorityCertSerialNumber``
fields were still ``discard_remaining()``-ed (see "remaining issues" — addressed upstream
later).

**RPKI: 6f54074c6, a60dcb673, 65ac4a3ea, 3ec3dc115 (+ tests in test_x509_rpki.cpp).**

- ``6f54074c6``: an ASIdentifiers extension with neither ``asnum`` nor ``rdi`` previously
  survived decoding and then tripped ``BOTAN_ASSERT_NOMSG`` during validation — i.e.
  **remotely triggerable abort (DoS)** on a crafted RPKI certificate. Now a
  ``Decoding_Error`` at parse, plus a defensive status-code path (instead of the assert) in
  ``validate()``.
- ``a60dcb673``: adds ``verify_end()`` after decoding each ASIdentifierChoice
  (trailing-garbage rejection) and — importantly — adds the missing ``from.decode_null()``
  when the choice is NULL. Before, the NULL object was peeked but never consumed; the new
  ``verify_end`` / ``end_cons`` strictness from ``204b1934e`` would have turned that into a
  spurious failure, so this is both a hardening and a required companion fix. Consistent.
- ``65ac4a3ea``: ``static_cast<Type>(obj.type_tag())`` changed to ``static_cast<uint32_t>(...)`` —
  casting an arbitrary attacker-controlled tag into a small enum before comparing is
  UB-adjacent (out-of-range enum values); now compared as integer. Correctness fix.
- ``3ec3dc115``: ``BER_Decoder(obj, limits).start_sequence()`` called ``start_sequence()``
  on a temporary; the returned child decoder holds a parent pointer, which dangles once the
  temporary dies at end of statement. The child was used across the following loop — latent
  use-after-free the moment anything touches the parent (e.g. ``end_cons``). Rebound to a
  named local. Real (if unexploited) lifetime bug, correctly fixed.

Name constraints
~~~~~~~~~~~~~~~~

**7a23ec9f4 — empty subject DN exemption (+ new test chain
x509/name_constraint_empty_subject/).** Per RFC 5280 §4.2.1.10, directoryName constraints
apply to the subject field only "when the certificate includes a non-empty subject field"
(the subject identity then lives in the — required-critical — SAN). Botan applied
permitted-directoryName subtrees to the empty DN, which can never match a non-empty required
subtree, so RFC-conformant SAN-only certificates below a directoryName-constrained CA were
wrongly rejected. *Compatibility issue addressed*, matching the RFC. Security
considerations: this is not a bypass in practice — the empty DN carries no identity to
abuse, and SAN entries (DNS, IP, email, directoryNames inside SAN) are still fully
constrained. One leniency worth noting: Botan does not enforce the RFC's companion
requirement that when the subject DN is empty the SAN must be present and critical; that
requirement binds CAs, not validators, so this is defensible.

**38cfb766a** — explicit rejection of the ``maximum`` field (previously rejected only as an
opaque tag-mismatch error downstream). Diagnostic improvement, no semantic change.

OCSP
~~~~

**73aa7ed9d — byKey ResponderID length (+ test 60498c1c7 with new ocsp/byKey_responder*
data).** RFC 6960 defines ``KeyHash`` as *exactly* the SHA-1 of the responder key (20
bytes). Unvalidated lengths made responder matching ambiguous (prefix/empty hashes). Now
rejected at parse. Note the PR also *added the first test coverage ever* for byKey responder
matching — previously this code path was untested.

**160fffb0a + 1ab9fe9b2 — out-of-range times.** OCSP responses with times not representable
by the platform clock (e.g. year 2200, or pre-epoch) threw out of ``Response::status_for``
and **propagated an exception out of** ``x509_path_validate`` — a DoS/availability bug for
any application that didn't expect path validation to throw. Now caught and mapped to
``OCSP_RESPONSE_INVALID``. The revocation check deliberately stays *before* the time checks,
and ``1ab9fe9b2`` documents why: otherwise an attacker could staple an expired response that
indicates revocation and have it reported as a benign "expired" (easily dismissed as clock
skew) instead of "revoked". Correct ordering, now explained in-source. Also fixes the absurd
status string ``"OCSP parsing valid"``, replacing it with a real message.

**61b45486c — per-certificate stapled-OCSP tracking.** The real security fix of the OCSP
group. Previously ``x509_path_validate`` used stapled OCSP *all-or-nothing*: if the stapled
set produced *any* status entry, online fetching was skipped entirely (and ``check_ocsp``
popped trailing empty entries, masking which certificates actually had responses).
Concretely: a TLS server (or an attacker able to influence stapling) that stapled a response
only for an intermediate would **suppress online revocation checking of the end-entity
certificate**. Now each position in the chain is tracked; online lookup fills only the gaps
(``x509path.cpp``, the ``need_online`` loop). I verified the index conventions line up:
``check_ocsp`` builds ``status[i]`` for ``cert_path[i]`` (EE = 0), the fill-in loop merges by
the same index, and ``merge_revocation_status`` treats empty per-index sets as "no data" — so
retaining empty entries (the removed ``pop_back`` loop) is safe. The ``#else`` (no-HTTP)
branch correctly marks only the positions that needed online data with ``OCSP_NO_HTTP``.
Behavior change: configurations that previously made zero network requests (because any
staple was present) may now perform online lookups — intended, but a latency/privacy-visible
change.

**375f23a62** — hash into ``std::vector`` directly instead of ``unlock()`` round-trips, plus
an RFC 6960 quotation. Refactor only; no functional change (verified the hashed inputs are
unchanged).

Certificate store
~~~~~~~~~~~~~~~~~

**85aa1db18 — pimpl for Certificate_Store_In_Memory.** ABI-insulation refactor (members
move behind ``unique_ptr<Impl>``). Functionally equivalent — with one **unannounced API
break**: the class previously had an implicitly-defined copy *assignment* operator; the PR
deletes it (``operator=(const&) = delete``) while keeping a deep-copying copy constructor.
Code doing ``store_a = store_b;`` no longer compiles. Unlike the ``BER_Decoder`` break this
one is not called out in the commit message or deprecation notes. Minor, but it is a
SemVer-relevant regression in API surface.

**9d315e92f — CRL index.** Adds ``map<X509_DN, size_t>`` issuer-DN-to-CRL index, replacing
linear scans in ``add_crl``/``find_crl_for``. I checked the semantic edge: the old code
could in principle scan past an AKID-mismatched CRL to find another with the same issuer
DN — but the old ``add_crl`` already guaranteed at most one stored CRL per issuer DN, so the
loop could never hit that case, and the new early-return is equivalent. Performance fix for
large CRL stores (path validation does this lookup per certificate); no behavior change.

Miscellaneous
~~~~~~~~~~~~~

- **45d307bb0 — IPv6 SAN enumeration.** ``AlternativeName::contents()`` and
  ``subject_info("IPv6")`` previously *silently omitted* IPv6 iPAddress entries (IPv4
  only) — applications enumerating names for display or policy never saw them.
  Compatibility/completeness fix; matching (``matches_ip(IPv6Address)``) already existed.
- **906ed12ae — PKCS10 accessors.** Replaces ``dynamic_cast<T&>`` (which throws
  ``std::bad_cast`` — a non-Botan exception — if the extension OID mapped to an
  ``Unknown_Extension`` because its body failed to decode) with the null-checked
  ``get_extension_object_as<T>()``. Minor DoS/robustness fix on attacker-supplied CSRs.
- **4fc39edb3 — X509_Object accessors.** ``signature()``, ``signed_body()``,
  ``signature_algorithm()`` dereferenced ``m_signed_data`` unconditionally; certain API
  sequences (not reachable via decoding) left it null, leading to a crash. Now ``Invalid_State``.
  Defensive fix.
- **e74e0476b — EC group seed class tag.** ``decode_optional_string(seed, BitString,
  BitString)`` defaulted the class to ContextSpecific, so a genuine universal BIT STRING
  seed never matched — it was read, pushed back, and (pre-``204b1934e``) silently dropped at
  ``end_cons``. With the new pushed-object strictness this would instead have *broken*
  decoding of explicit EC parameters carrying a seed, so this companion fix was mandatory.
  Now decodes the seed correctly. Good example of the PR's internal consistency auditing.
- **b00af6861** — comment documenting why basicConstraints criticality is not enforced on
  validation (RFC 5280 binds CAs, not validators). Documentation only.
- **doc/deprecated.rst** — deprecates TeletexString encode/decode support (see the
  remaining-issues section).
- **Tests**: new ``asn1_string_validation.vec`` (invalid charset/UTF-8/NUL cases),
  ``x509_dn.vec`` corrections, byKey OCSP data, empty-subject name-constraint chain, RPKI
  invalid-encoding tests, unit_x509 additions. Coverage is added for essentially every
  behavior-changing commit — notably including previously untested code paths (byKey OCSP).

Does the PR introduce bugs?
---------------------------

I found **no functional bug in the merged result**. Specific risk points I checked:

1. **OCSP fill-in indexing** (``61b45486c``): index conventions between ``check_ocsp``,
   ``check_ocsp_online``, the fill-in loop, and ``merge_revocation_status`` all agree (EE at
   index 0; empty set = no data). Retaining trailing empty entries is handled.
2. **AKI presence predicate vs. consumption** (``ef065669a``):
   ``peek_next_object().is_a(0, ContextSpecific)`` is exactly the match condition inside
   ``decode_optional_string`` — no disagreement possible.
3. **Length-parsing rewrite** (``3cc416fec``): limit is provably identical; removed check
   was dead on both 32- and 64-bit targets.
4. **end_cons pushed-object strictness** (``204b1934e``): all in-tree peek-then-close sites
   were fixed in the same PR (``a60dcb673`` ``decode_null``, ``e74e0476b`` seed class tag);
   ``decode_optional*`` pushback of the end-of-content object does not set ``m_pushed`` to a
   real object, so normal optional-at-end-of-sequence parsing is unaffected.
5. **CRL index** (``9d315e92f``): semantics preserved given the pre-existing
   one-CRL-per-issuer invariant.

What the PR *does* introduce, deliberately or as side effects:

- **Compatibility regressions by design.** Strict charset validation, duplicate-extension
  rejection, empty-list rejection, KeyUsage != 0, pathLen-without-CA, CRLReason range checks —
  each rejects certificates that Botan <= 3.8 and lenient stacks (OpenSSL by default) accept.
  The charset enforcement is the most likely to bite in the field (legacy PrintableString
  values containing ``*``, ``@``, ``_``; whole-certificate parse failure with no lenient
  mode). These are defensible fail-closed choices, but integrators should expect a tail of
  "certificate worked before the upgrade" reports.
- **Unannounced API break**: deletion of ``Certificate_Store_In_Memory`` copy assignment
  (``85aa1db18``), in addition to the *announced* ``BER_Decoder`` copy-constructor break.
- **Public API contract change**: ``BER_Decoder::end_cons()``/``discard_remaining()``
  behavior with pushed objects changed without documentation; out-of-tree decoders using
  peek-then-close patterns will start throwing ``Decoding_Error``.
- **Exception-masking**: the broadened ``catch(Exception&)`` in extension decoding
  (``6e9afc74b``) can hide ``Internal_Error``-class library bugs behind "extension failed to
  decode". A narrower catch list or debug logging would preserve the robustness win without
  the diagnostic loss.
- **Fragility (later fixed)**: ``is_valid_utf8`` (``2eb2c5dc3``) relied on
  ``next_utf8_codepoint``'s callers for bounds discipline; upstream added the missing
  internal length check in ``19e3653a0`` (2026-06-28), noting it "wasn't reachable due to
  how callers manage the index".

Remaining security issues in these functionalities
--------------------------------------------------

Gaps that remained after the PR — since fixed upstream
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The post-merge history of ``src/lib/asn1`` / ``src/lib/x509`` is effectively a list of what
PR #5569 did *not* yet cover; all of the following were still open at merge time and were
fixed in later PRs (evidence: the cited master commits).

**Release-timeline note:** PR #5569 itself first shipped in **Botan 3.12.0** (tagged
2026-05-06, the same day the PR was merged). Every follow-up fix below postdates the 3.12.0
tag: **none of them is contained in Botan 3.12** (verified per commit with
``git merge-base --is-ancestor <commit> 3.12.0``). As of 2026-07-21 they are all unreleased,
sitting on master (``3.12.0-424-gc3f13bc82``) for the next feature release (3.13.0). In
other words, a Botan 3.12 user has PR #5569's hardening, but every issue in this table is
still present in 3.12.

.. list-table::
   :class: longtable
   :widths: 55 25 20
   :header-rows: 1

   * - Remaining issue at merge
     - Fixed later by
     - In Botan 3.12?
   * - Constructed OCTET/BIT STRING accepted in BER (re-encoding differentials)
     - ``838ed8ed8``, ``cf65222a4``
     - No — master only (3.13.0)
   * - DER mode accepted **unsorted SETs** (canonicalization differential, e.g. in DNs)
     - ``deea84016``
     - No — master only (3.13.0)
   * - Stray / constructed EOC markers tolerated
     - ``bf38ad87d``, ``5b971225f``
     - No — master only (3.13.0)
   * - Empty INTEGER encoding accepted in BER
     - ``a611f55ac``
     - No — master only (3.13.0)
   * - Tag numbers >= 2\ :sup:`31` mishandled in the BER decoder
     - ``949ff560e``
     - No — master only (3.13.0)
   * - No global cap on decoded object size (memory DoS)
     - ``f78f13288``
     - No — master only (3.13.0)
   * - ``AlgorithmIdentifier`` parameters not validated on decode (algorithm-confusion
       surface; the PSS fix in this PR covered only PSS)
     - ``b149e4759``
     - No — master only (3.13.0)
   * - OCSP accepted UTCTime where RFC 6960 mandates GeneralizedTime
     - ``fd52f32b6``
     - No — master only (3.13.0)
   * - Pre-1970 times unrepresentable, so whole structures were rejected as invalid rather than
       parsed (interacts with ``160fffb0a``'s guard)
     - ``6f6b35468``
     - No — master only (3.13.0)
   * - AKI ``authorityCertIssuer``/``authorityCertSerialNumber`` silently discarded
       (``ef065669a`` still ``discard_remaining()``-s them)
     - ``c7cfd8b1a``
     - No — master only (3.13.0)
   * - CRL ``removeFromCRL`` reason accepted as an ordinary revocation reason (this PR's
       ``b9c3414db`` validated the range only)
     - ``9a3bc96dc``
     - No — master only (3.13.0)
   * - Path-building work-factor limits (chain-building DoS)
     - ``081432fdc``
     - No — master only (3.13.0)
   * - Path-validation trusted-hash allow-list rejects PQ schemes with intrinsic hashes
       (SLH-DSA-SHAKE)
     - ``7f3b1b9bd`` (partial: SHAKE identifiers added to the default set)
     - No — master only (3.13.0)

The same applies to the two follow-up fixes cited elsewhere in this report: the
``next_utf8_codepoint`` bounds check (``19e3653a0``) and the control-character escaping in
``X509_Certificate::to_string`` (``b349eb3ac``) are also post-3.12.0, master-only.

The density of this follow-up list is itself a fair review conclusion: PR #5569 was one
installment in an ongoing hardening campaign, not a completion of it.

Issues still open on current master (assessment)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **IA5String control characters.** The validation table admits 0x01–0x1F in IA5String
  (spec-valid). Escaping was later added for ``X509_Certificate::to_string``
  (``b349eb3ac``), but applications consuming ``subject_info()`` / SAN strings directly
  still receive raw control characters — a display-spoofing footgun Botan only partially
  mitigates.
- **UTF8String admits embedded NUL.** NUL is well-formed UTF-8, so
  ``CN=UTF8String("a.com\0.b.com")`` still parses. Botan's own comparisons are length-aware
  (``std::string``), so internal matching is safe, but any application converting these
  values to C strings truncates — the classic vulnerability re-emerges one layer up. An
  explicit NUL rejection in UTF8String (as was done for IA5) would be cheap and consistent.
- **TeletexString decoded as Latin-1.** A pragmatic majority-behavior choice (documented
  in-source), but a canonicalization differential against T.61-strict implementations. It is
  now deprecated (``doc/deprecated.rst``, this PR) but still enabled.
- **No lenient parse mode.** The strictness added here is all-or-nothing: a certificate with
  one out-of-charset DN character cannot even be loaded for inspection (CLI dump, forensics,
  building an allow-list of a legacy peer). A "parse for inspection only" facility would
  ease the operational cost of the strict default.
- **64-byte key-ID cap is heuristic.** RFC 5280 imposes no upper bound on KeyIdentifier;
  64 bytes covers all known generation methods, but it is a Botan-invented interop line.
  Documented nowhere user-facing.
- **ocsp_all_intermediates asymmetry** (pre-existing, unchanged by ``61b45486c``): with the
  default ``false``, only the EE's missing status triggers online lookup; stapled responses
  for intermediates are *used* if present but never fetched. That is standard practice, but
  the online/stapled asymmetry is undocumented and can surprise policy authors.

Verdict
-------

A high-quality, internally consistent hardening PR. Every change addresses an identifiable
compatibility bug (EC seed decoding, empty-subject name constraints, IPv6 SAN enumeration,
tag-17 encoding), a robustness/DoS bug (RPKI assertion abort, OCSP time-range exceptions,
``bad_cast`` on CSRs, dangling decoder parent), or a parser-hygiene/differential concern
(charset validation, duplicate extensions, trailing-data rejection, pushed-object
strictness) — and the commits that tighten the ``BER_Decoder`` contract fix all in-tree
callers that the tightening would break, within the same PR. Test coverage is added for
effectively every behavior change, including previously untested paths.

I found no introduced functional bugs. The costs are deliberate: a set of strict-parsing
compatibility regressions (charset enforcement being the riskiest in the field), one
announced and one unannounced API break, and a broadened exception catch that trades
diagnosability for robustness. The most security-significant individual fixes are the
per-certificate stapled OCSP tracking (``61b45486c`` — stapling one response no longer
suppresses online revocation checks for the rest of the chain), the revoked-before-expired
OCSP check ordering (documented in ``1ab9fe9b2``), the embedded-NUL/charset validation
(``2eb2c5dc3``), and the RPKI parse-time assertion-failure fix (``6f54074c6``).
