Appendix: Review of Botan PR #5737
==================================


The review in this section was entirely written by Anthropic's Fable 5 model. Please treat it with care as appropriate for AI generated content.

**"Support decoding of X509 authority key ID fields with a DN + serial"**

- **PR:** `randombit/botan#5737 <https://github.com/randombit/botan/pull/5737>`_
  (merged as ``af7d17a771``, single commit ``c7cfd8b1a``)
- **Author:** Jack Lloyd — **Merged:** 2026-07-18, +121/-32 lines across 6
  files
- **First released in:** Botan 3.13.0
- **Reviewed code:** ``src/lib/x509/x509_ext.{h,cpp}``,
  ``src/lib/asn1/ber_dec.{h,cpp}``, ``src/scripts/run_limbo_tests.py``,
  ``src/tests/unit_x509.cpp``, at tag ``3.13.0``
- **Audit scope status:** the changed modules ``x509`` and ``asn1`` are in
  the audit scope; the change affects the parsing of attacker-controlled
  certificate data.

What the PR does
----------------

The AuthorityKeyIdentifier (AKI) extension has three fields per RFC 5280:
``keyIdentifier [0]``, ``authorityCertIssuer [1]`` (GeneralNames), and
``authorityCertSerialNumber [2]``. Botan previously decoded only the key
identifier and silently discarded the other two fields via
``discard_remaining()``, and could encode only the key identifier. With this
patch:

- **Decoding** parses all three fields (``decode_optional_field`` per tag;
  the IMPLICIT-tagged GeneralNames and INTEGER are decoded by re-tagging via
  ``decode_implicit``), exposing issuer and serial through a new
  ``Authority_Cert_Identifier`` accessor. The parser reuses the existing,
  heavily exercised ``AlternativeName`` GeneralNames machinery rather than
  introducing a new parser.
- **New validations**, all mandated by RFC 5280: ``authorityCertIssuer``
  must contain at least one GeneralName (``SIZE (1..MAX)``); issuer and
  serial must *both* be present or *both* absent (Appendix A.2); and since
  the old ``discard_remaining()`` is gone, trailing or unknown content
  inside the AKI sequence now fails ``end_cons()``. A malformed AKI
  therefore rejects the certificate at parse time — fail-closed, consistent
  with the strict-decoding posture of this release (see also GH #5689 and
  GH #5741).
- **Encoding** can now emit issuer plus serial (refusing empty GeneralNames
  and empty directoryNames via the relocated ``emit_general_names_implicit``
  helper), ``should_encode()`` accounts for the new field, and ``copy()``
  was fixed to copy the whole object (the old version, harmless before this
  patch, would have dropped the new field).
- Per the PR description, the decoded issuer/serial are **not used for path
  building** — chain construction and validation logic are unchanged; this
  is parse-and-expose only.

The BER_Decoder change: closure of a silent footgun
---------------------------------------------------

``BER_Decoder::decode(ASN1_Object&, type, class)`` previously *ignored its
tag arguments entirely* — any caller passing implicit tags for an
``ASN1_Object`` got default decoding with no error. It now throws
``Not_Implemented`` for non-default tags, and
``decode_implicit``/``decode_optional`` route ``ASN1_Object``-derived types
through the tagless overload (``if constexpr`` on
``std::is_base_of_v<ASN1_Object, T>``), relying on the object re-tagging
performed beforehand.

That this footgun was real is demonstrated within the PR itself: the
in-tree ``String_Extension`` test helper called ``decode(str, Utf8String)``
— the tag was silently ignored — and had to be rewritten to
decode-then-check-tag. Third-party code making the same mistake now gets a
loud error instead of unchecked decoding.

External validation
-------------------

The change is corroborated by the x509-limbo corpus: the entries
``webpki::aki::root-with-aki-authoritycertissuer`` and
``webpki::aki::root-with-aki-authoritycertserialnumber`` were removed from
the test runner's "tests that succeed unexpectedly" list — these are exactly
the certificates violating the both-or-neither rule that Botan previously
accepted and now correctly rejects. (``root-with-aki-all-fields`` rightly
remains listed: a well-formed AKI with all fields is only objectionable
under CA-profile rules that a verifier need not enforce.)

Security assessment
-------------------

- The attacker-facing surface (certificate parsing) becomes *stricter*, and
  the newly reachable parsing code is the existing GeneralNames parser
  already exposed via SAN/IAN/CRL-DP — no new parser; DER limits are
  enforced (``BER_Decoder::Limits::DER()``) and the pre-existing 64-byte
  key-identifier bound is kept.
- Interoperability risk of the new rejections is low: certificates with only
  one of issuer/serial violate a MUST and are rare (the x509-limbo suite
  tracks them as pathological); mis-ordered or trailing AKI content
  likewise.
- Because the decoded fields are not used for path building, there is no
  behavioral change to chain validation — and no risk of the classic
  AKI-issuer/serial-matching pitfalls, which RFC 5280 path building
  deliberately avoids relying on.
- One minor round-trip caveat, not a defect: a re-encoded serial passes
  through ``BigInt``, so a non-canonical original INTEGER encoding would not
  survive byte-for-byte — irrelevant for verification, only for hypothetical
  re-emission.

Verdict
-------

The patch completes AKI parsing with RFC-mandated validation, closes a
genuine silently-ignored-argument footgun in ``BER_Decoder``, is externally
validated by the x509-limbo corpus, and changes no path-validation
behavior. No security gaps were found.

Suggested classification: **relevant** (in-scope ``x509``/``asn1`` parsing
of attacker-controlled certificate data; strictness increase, fail-closed).
