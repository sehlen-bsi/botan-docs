Appendix: Review of Botan PR #5593
==================================


The review in this section was entirely written by Anthropic's Fable 5 model. Please treat it with care as appropriate for AI generated content.

**"Various PKIX hardening and bug fixes"**

- **PR:** `randombit/botan#5593 <https://github.com/randombit/botan/pull/5593>`_
  (merged as ``33a803748``, 8 commits)
- **Author:** Jack Lloyd — **Merged:** 2026-05-10
- **First released in:** Botan 3.13.0
- **Size:** +334/-30 across 16 files
- **Audit scope status:** the changed modules ``x509`` and ``asn1``
  (including OCSP) are in the audit scope.
- **Release-notes placement:** cited only in the general "Various
  X509/PKIX hardenings, optimizations, bug fixes, and additional sanity
  checks" bullet (GH #5593 et al.), *not* among the security-relevant
  items — although one fix here has genuine security character.

The standout: delegated OCSP responder must be signed by the same key
----------------------------------------------------------------------

RFC 6960 4.2.2.2: a delegation certificate counts as issued by the CA in
question "only if the delegation certificate and the certificate being
checked for revocation were signed by the **same key**." Pre-PR,
``verify_ocsp_signing_cert`` established the delegation relationship by
**DN comparison** (``signing_cert.issuer_dn() == ca.subject_dn()``) plus
ordinary path validation of the responder's chain. DN equality is not
key equality: in any deployment where two different CA keys share a
subject DN — CA key rollover, cross-signed hierarchies, or an unrelated
trusted hierarchy containing a same-named CA — a responder certificate
issued by the *other* key passed the check, allowing that key's holder
to produce accepted OCSP responses (including "good" answers for revoked
certificates) for certificates the victim CA issued. The fix
(``4bf7a3c69``) adds a direct
``signing_cert.check_signature(ca.subject_public_key())``, fail-closed
on every failure path including exceptions
(``OCSP_ISSUER_NOT_TRUSTED``). This is the RFC's MUST, previously
unimplemented — the most security-relevant change in the PR, and notably
*not* called out in the release notes' security section.

Name-constraint fixes
---------------------

- **Uninterpretable constraint forms now fail closed** (``cb8533b42``):
  a critical NameConstraints extension restricting a GeneralName form
  Botan cannot evaluate (``NameType::Unknown``, e.g. x400Address
  constraints) was previously *silently ignored* — a constraint bypass
  by unevaluability. Now, under ``reject_unknown``, such a
  permitted-subtree makes ``is_permitted`` false and such an
  excluded-subtree makes ``is_excluded`` true. The code comment is
  admirably honest: the RFC neither defines nor encourages these forms,
  the rejection is deliberately broader than necessary (it triggers even
  when the constrained form does not appear in the certificate), and
  users hitting it with real chains are invited to file an issue.
  Conservative and correct.
- **matches_dn empty-constraint semantics:** an empty directoryName
  constraint previously matched *nothing*
  (``return !constraint_info.empty()``); now it matches *everything*
  (``return true``) — the X.501-correct reading (a zero-RDN subtree is
  the DIT root, a prefix of every DN). Note the direction differs by
  side: an empty excluded-subtree now excludes all DNs (tightening), an
  empty permitted-subtree now permits all DN-form names (per
  specification — previously it nonsensically rejected everything).
- A dead branch in ``matches_dns`` was removed — verified to have
  compared strings of unequal length (always false), so no behavior
  change.

OtherName / registeredID decoding
---------------------------------

Previously, otherName values were captured only when the inner ANY was a
universal string type (anything else silently dropped), and
``registeredID`` (``[8] IMPLICIT OID``) SAN entries were **ignored
entirely**. Now both are decoded (raw-BER ``OtherNameValue`` for
arbitrary otherName payloads; new ``decode_implicit``/``encode_implicit``
helpers, whose hand-rolled TLV-header skip in ``add_object_tlv``
operates only on self-generated encodings and is assert-bounded), both
round-trip on encode, and — the subtle security point — **both now count
toward** ``AlternativeName::count()``. Since ``count() == 0`` is the
gate for the CN fallback and the name-constraint DN fallbacks, a
certificate whose SAN contained *only* a registeredID or a non-string
otherName previously looked SAN-less and got CN-based name matching
despite having a SAN. That gap is closed, and the constraint checks on
otherNames now see all of them, not just string-typed ones.

OCSP and ASN.1 strictness
-------------------------

- ``OCSPResponseStatus`` **4 (undefined in RFC 6960) is rejected**
  (``d391747a8``), and ``responseBytes`` presence must now be consistent
  with the status (``a723471cf``): a successful response without
  responseBytes, or an error status *with* responseBytes, are decode
  errors per RFC 6960 4.2.1. Previously a "successful" response with no
  body produced an empty-but-successful Response object — an unhealthy
  shape for callers.
- **Missing verify_end calls added** (``af8f20284``) in five decoders
  (PSS MGF parameters, SAN directoryName entries, GeneralName DN
  constraints, TNAuthList entries, the OCSP certs list): trailing bytes
  after these substructures were silently ignored — the usual
  BER-laxness/smuggling surface — and now throw.
- **Empty BMPString/UniversalString round-trip fixed** (``bbf8074b9``):
  re-encoding a decoded empty BMP/Universal string previously tripped a
  ``BOTAN_ASSERT`` (internal-error denial of service on re-encode
  paths); the encoder now dispatches on tag type, using the preserved
  wire form for BMP/Universal/Teletex and the UTF-8 string for
  UTF-8-subset types.
- The CN-fallback condition in ``matches_dns_name`` gained an explicit
  ``issued_names.empty()`` conjunct plus an explanatory comment —
  verified behaviorally equivalent (without a SAN, the DNS list is
  necessarily empty); pure clarification, later superseded textually by
  PR #5601's rewrite.

Tests
-----

Good coverage: +71 lines of ASN.1 tests (implicit encode/decode,
empty-string round-trip), +33 OCSP (status-4, responseBytes
consistency), +24 alt-name (registeredID/otherName round-trip); one
Limbo-suite exclusion removed (a previously failing conformance case now
passes).

Verdict
-------

An early-cycle hardening batch whose headline — cryptographic
key-binding for delegated OCSP responder certificates per RFC 6960
4.2.2.2, replacing DN-equality trust — is a genuine security fix that
the upstream release notes only file under generic PKIX hardening. The
remainder is uniformly fail-closed: unevaluable name constraints reject,
previously invisible SAN entry types now count and are constrained, OCSP
response framing is specification-checked, and several trailing-garbage
acceptances are closed. The one loosening (empty permitted directoryName
subtree now permits) is the specification-correct semantics. No defects
were found.

Suggested classification: **relevant** (in-scope ``x509``/OCSP:
delegation key-binding fix with real forgery-resistance impact in
same-DN scenarios, plus fail-closed constraint and decoder hardening).
