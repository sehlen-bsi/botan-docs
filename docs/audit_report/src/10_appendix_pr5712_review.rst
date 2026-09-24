Appendix: Review of Botan PR #5712
==================================


The review in this section was entirely written by Anthropic's Fable 5 model. Please treat it with care as appropriate for AI generated content.

**"Improve CDP, AIA and IDP extension decoding and handling"**

- **PR:** `randombit/botan#5712 <https://github.com/randombit/botan/pull/5712>`_
  (merged as ``545a0ac24``, single commit ``dcd92d811``)
- **Author:** Jack Lloyd — **Merged:** 2026-07-09
- **First released in:** Botan 3.13.0
- **Size:** +2662/-124 overall; ~1120 lines in ``src/lib`` (``x509_ext``,
  ``x509_crl``, ``x509path``, ``pkix_enums``, a ``ber_dec.h`` helper), a new
  1199-line test file, and 20 crafted test certificates/CRLs
- **Audit scope status:** the changed modules ``x509`` and ``asn1`` are in
  the audit scope. This is one of the most semantically significant X.509
  changes of the 3.13 cycle: it rewrites CRL applicability logic in path
  validation.

What the PR does
----------------

**1. Full decoding of three previously half-parsed extensions.**
CRLDistributionPoints, AuthorityInformationAccess, and
IssuingDistributionPoint used to be partially decoded with many fields
silently dropped (DP ``reasons``, ``cRLIssuer``, the IDP booleans
``onlyContainsUserCerts``/``CACerts``/``AttributeCerts``,
``onlySomeReasons``, ``indirectCRL``). New public types model the ASN.1
faithfully: ``DistributionPointName`` (fullName CHOICE;
``nameRelativeToCRLIssuer`` explicitly unsupported -> ``Decoding_Error``)
and ``ReasonFlags`` (9 defined bits; the constructor rejects undefined bits
and the empty mask, matching RFC 5280's requirement that at least one bit
be set). Decoding is strict throughout: ``SIZE (1..MAX)`` on GeneralNames,
empty directoryNames rejected, ``decode_optional_field`` plus
``end_cons()`` enforcing at-most-once/in-order tagged fields, and
GeneralName encoding validation in AIA.

**2. RFC 5280 6.3.3-conformant CRL applicability in check_crl.** The new
``crl_applicability_for()`` computes two answers in one pass — can this CRL
be *searched* for a revocation entry (``usable``), and can it additionally
serve as *non-revocation evidence* (``full_coverage``):

- **Name/issuer matching per (b)(1)/(b)(2)(i):** a DP ``cRLIssuer`` must
  match the CRL issuer *and* the CRL must assert ``indirectCRL``; otherwise
  the CRL issuer must equal the certificate issuer; IDP names must overlap
  DP names (or ``cRLIssuer`` names when the DP omits its name). The RFC's
  trailing-paragraph *implicit DP* (issuer DN plus issuerAltName, no
  reasons) is implemented both for certificates without a CDP and as a
  fallback for same-issuer complete CRLs.
- **Scope per (b)(2)(ii)–(iv):** a CA-certs-only CRL is inapplicable to an
  end-entity certificate and vice versa (deliberately keyed on the raw
  basicConstraints cA flag, not Botan's stricter ``is_CA_cert()`` — the
  right choice, since the CRL issuer partitions on the extension, and noted
  in a code comment); attribute-cert-only CRLs are never applicable.
- **Indirect CRLs are rejected as unusable** — see the dedicated section
  below.
- **Reason partitioning per (d)(3), conservatively:** a CRL reason-limited
  on either side (DP ``reasons`` or IDP ``onlySomeReasons``) still *proves
  revocation* if the certificate is listed, but is never accepted as proof
  of *non*-revocation, since reason-mask accumulation across CRLs
  ((d)–(l)) is unimplemented. This one-way asymmetry is exactly right.

An inapplicable CRL is now **skipped as if absent** — the caller's policy
decides (required revocation -> ``NO_REVOCATION_DATA``; soft-fail ->
validates) — instead of the old behavior of inserting
``VALID_CRL_CHECKED`` plus an advisory ``NO_MATCHING_CRLDP``.
``merge_revocation_status`` correspondingly counts ``CERT_IS_REVOKED`` as
revocation evidence, so a reason-limited CRL listing the certificate no
longer also surfaces a spurious "no revocation data".

Why indirect CRLs are not supported
-----------------------------------

An *indirect CRL* is one issued by a different entity than the CA that
issued the certificates it covers — the certificate's DP names that other
party in ``cRLIssuer``, and the CRL asserts ``indirectCRL`` in its IDP to
confirm it plays that role (e.g. a CA outsourcing CRL publication to a
dedicated revocation service, or one CRL aggregating revocations for
several CAs). Supporting them correctly requires machinery Botan's
``check_crl`` does not have; RFC 5280 6.3.3 spells out what is missing:

1. **A different signature-verification key, with its own path validation
   (steps (f)–(g)).** For a normal CRL, the verifier checks the CRL
   signature with the certificate issuer's key, which it already has and
   whose trust was just established as part of the chain. For an indirect
   CRL the signer is the ``cRLIssuer`` — a different entity whose key must
   first be obtained and validated through its own certification path to
   the same trust anchor, including a check that this entity is authorized
   to sign CRLs (cRLSign key usage). Botan's ``check_crl`` is structured
   around the chain at hand: it verifies ``crls[i]`` against
   ``cert_path[i+1]``'s key only. There is no mechanism to discover, build,
   and validate a second chain for a third-party CRL signer inside that
   loop.

2. **Per-entry issuer attribution — the** ``certificateIssuer`` **CRL entry
   extension.** Serial numbers are only unique *per issuer*, and an
   indirect CRL can list certificates from multiple CAs. RFC 5280
   disambiguates via an entry-level ``certificateIssuer`` extension with
   sticky semantics: an entry without it inherits the issuer from the most
   recent preceding entry that has one (defaulting to the CRL issuer).
   Botan's ``is_revoked()`` matches purely on serial number within one CRL.
   Against an indirect CRL this would be wrong in both directions: a
   certificate with serial 1234 from CA-A could be flagged revoked because
   a different CA-B's certificate with serial 1234 is listed (false
   revocation), or an entry could fail to be attributed correctly (false
   non-revocation). In practice a second, independent mechanism catches
   this case: ``certificateIssuer`` is a *critical* entry extension that
   Botan does not recognize, and since PR #5611 (also in 3.13.0) unknown
   critical extensions at the CRL *entry* level render the whole CRL
   unusable (``CRL_HAS_UNKNOWN_CRITICAL_EXTENSION``), per RFC 5280 5.3.
   So an indirect CRL that actually uses per-entry issuer attribution is
   rejected twice over — by the IDP ``indirectCRL`` applicability check
   reviewed here, and by the entry-level critical-extension gate.

3. **Authorization/trust scoping.** Even with (1) and (2) in place, the
   verifier must decide that *this* cRLIssuer is legitimately entitled to
   speak about *that* CA's certificates — the DP's ``cRLIssuer`` name, the
   CRL's IDP, and the validated path all have to be cross-checked. Getting
   this wrong would let anyone holding a CRL-signing-capable certificate
   under the same root publish "revocation" data for arbitrary CAs.

Since the preconditions for evaluating an indirect CRL are absent —
``check_crl`` would verify the signature against the wrong key and match
entries with the wrong semantics — the PR's choice is the only safe one:
an indirect CRL is declared **inapplicable**, treated as if no CRL was
supplied, and the caller's revocation policy takes over. That is
fail-closed: a wrong "not revoked" or a wrong "revoked" is worse than an
honest "I can't use this."

Two contextual notes. RFC 5280 does not mandate indirect-CRL support; it is
an optional feature that many validators skip (it is the corner where
several historical CRL-processing bugs in other stacks lived). And before
this PR, Botan did not handle indirect CRLs *correctly* either — the
``indirectCRL`` flag was among the IDP fields that failed decoding, so such
CRLs died as "unknown critical extension". The new code reaches the same
safe outcome by explicit, documented decision rather than by parser
accident, and leaves a clean hook (``idp->indirect_crl()``) should upstream
ever implement 6.3.3 (f)–(g) properly.

Points verified
---------------

- **Malformed-extension robustness:** ``Extensions::create_extn_obj``
  *catches* decode failures of recognized extensions and demotes them to
  ``Unknown_Extension(failed_to_decode=true)``. A certificate whose CDP
  uses the unsupported ``nameRelativeToCRLIssuer`` form (or has an invalid
  AIA URI) therefore still **parses**; its CDP merely becomes unusable
  (falling back to implicit-DP matching), with criticality handled through
  the standard unknown-critical machinery. On the CRL side, the IDP is
  critical, so an undecodable IDP renders the CRL unusable — fail-closed,
  as before.
- **The corrected PKITS expectation** is the best single summary of the
  security delta: NIST test76 (CA-certs-only IDP CRL, end-entity
  certificate, revocation required) previously failed with "critical
  extension could not be processed" (the IDP simply could not be decoded);
  it now fails with the semantically correct ``NO_REVOCATION_DATA`` — the
  CRL is *understood* and correctly deemed out of scope. Both are
  fail-closed; the reasoning is now real instead of accidental. Similarly
  the BSI test-suite expectations CRL_13/CRL_15 change from "No CRL with
  matching distribution point" to "No revocation data".
- **Pre-PR gap actually closed:** previously a certificate-side DP
  ``reasons`` field was *dropped entirely*, so a matching but reason-scoped
  arrangement yielded full ``VALID_CRL_CHECKED`` non-revocation evidence —
  the classic partitioned-CRL over-trust. Rare in practice, but a genuine
  correctness-of-evidence gap now handled per the RFC.
- **Test quality:** the new ``test_x509_cdp_aia.cpp`` exercises the matrix
  with purpose-built artifacts — IDP variants (user-certs, CA-certs,
  some-reasons with and without an actual revocation, indirect with and
  without the flag, dirname, fullName), multi-URI and multi-DP CDPs, DP
  reasons, ``cRLIssuer``, dirname partitions, AIA OCSP-via-dirname, and an
  unknown AIA access method (STIR TN list) — 1199 lines against 20 crafted
  certificates/CRLs, plus updated PKITS/BSI corpus expectations.

Observations (not defects)
--------------------------

- ``NO_MATCHING_CRLDP`` is no longer emitted by ``check_crl``; the status
  code remains in the public enum. Downstream consumers keying on it will
  simply stop seeing it.
- **For the audit documents:** the BSI x509 test-suite expected outputs
  changed (CRL_13/CRL_15) — if the testspec chapter reproduces those
  expected result strings, it needs a corresponding update this cycle.
- All rejections are fail-closed; the only direction in which *acceptance*
  grew is CRLs whose IDP previously failed to decode (unknown-critical ->
  unusable) and now decode fine and pass the scope checks — i.e.
  legitimate partitioned CRLs become usable, correctly.

Verdict
-------

A substantial and carefully executed upgrade of CRL scope handling from
partial/accidental to RFC 5280 6.3.3-conformant, with the two hard
sub-problems (indirect CRLs, reason-mask accumulation) explicitly and
safely declared out of scope rather than approximated, exhaustive
purpose-built tests, and corrected PKITS/BSI expectations. No security gaps
were found; every behavioral delta is fail-closed or strictly more correct.

Suggested classification: **relevant** (borderline critical: in-scope
``x509`` revocation-checking semantics change with direct effect on
path-validation outcomes; but no new cryptographic mechanism, and all
deltas were verified to be conservative).
