Appendix: Review of Botan PR #5618
==================================


The review in this section was entirely written by Anthropic's Fable 5 model. Please treat it with care as appropriate for AI generated content.

**"Modify DN decoding to capture RDN groupings"**

- **PR:** `randombit/botan#5618 <https://github.com/randombit/botan/pull/5618>`_
  (merged as ``e0aaa196e``, commits ``a22260c36`` and ``a73972655``)
- **Author:** Jack Lloyd — **Merged:** 2026-05-22
- **First released in:** Botan 3.13.0
- **Size:** +375/-110 across 11 files
- **Audit scope status:** module ``x509`` is in the audit scope. The PR
  changes DN equality semantics used throughout path validation, CRL
  association, name constraints, and certificate stores.

What the PR does
----------------

X.501 defines a Name as a SEQUENCE OF RelativeDistinguishedName, each
RDN being a SET SIZE(1..MAX) OF AttributeTypeAndValue (AVA). Botan
previously flattened this on decode into a single list of AVAs, losing
the RDN structure. ``X509_DN``'s internal representation becomes a
sequence of RDNs (``vector<vector<pair<OID, ASN1_String>>>``), with
decoding, encoding, comparison, printing, and parsing all rewritten
around it.

The security-relevant delta: DN equality was order-insensitive
--------------------------------------------------------------

The old ``operator==`` compared DNs via ``get_attributes()`` — a
``std::multimap`` keyed by OID — i.e., it compared the *multiset* of
attributes, ignoring both RDN order and RDN grouping. Two consequences,
both over-matching:

1. ``CN=A, O=B`` compared **equal** to ``O=B, CN=A`` — different names
   per RFC 5280 7.1, which requires RDN sequences to match positionally.
2. A multi-valued RDN ``CN=A+O=B`` compared equal to the two-RDN
   sequence ``CN=A, O=B`` — likewise distinct names.

The new ``operator==`` walks the RDN sequences positionally and applies
set-based equality only *within* an RDN (``rdn_equality``: same AVA
count, then either the single-AVA fast path via ``x500_name_cmp`` or
canonicalize-fold-and-sort for multi-AVA sets — the two paths were
verified to be consistent, and the rewritten ``operator<`` induces an
ordering consistent with the new equality, which matters for
``std::map``-based certificate stores).

The best evidence that the old behavior was a real defect: **Botan's own
test CRL** (``valid_forever.crl``) carried an issuer DN in a different
attribute order than the issuing CA's subject DN — it matched for years
only because equality ignored order, and this PR had to regenerate the
test data. Likewise the DN test vectors previously asserted that a
reordered DN was *equal*; the same byte pair now sits in the inequality
section with an RFC 5280 7.1 citation. DN equality feeds trust-relevant
decisions (issuer/subject chaining candidates, CRL-to-issuer
association, certificate-store lookups, name-constraint anchoring), so
eliminating over-matching here is a genuine tightening, not cosmetics.

Other changes verified
----------------------

- **Name constraints** (``GeneralName::matches_dn``): the directoryName
  subtree check previously did positional comparison over the *flat AVA
  list*, so any multi-valued RDN misaligned every subsequent position.
  Now it is prefix-of-RDN-sequence with ``rdn_equality``, quoting RFC
  5280 7.1 — the correct semantics. (The pre-existing test expectation
  ``dn-excluded-prefix-broken-by-rdn-reorder-valid: Verified`` documents
  that reordered-RDN evasion of excluded subtrees remains possible —
  that is inherent to the specification's matching rule, not a Botan
  gap.)
- **Stricter decoding, fail-closed:** an empty RDN (SET of size 0) is
  now a ``Decoding_Error`` per the RFC's ``SIZE (1..MAX)`` — the test
  expectation for ``dn-empty-rdn-embedded-invalid`` moves from "does not
  pass name constraint" to "failed to decode", both rejections. A new
  cap ``MAX_AVAS_PER_RDN = 32`` bounds the cost of set-based matching
  against hostile DNs (the multi-AVA path canonicalizes and sorts per
  comparison) — a sensible denial-of-service guard.
- **Encoding:** decoded DNs still round-trip via the cached original
  bytes (``m_dn_bits``), so re-encoding is byte-faithful;
  programmatically built multi-AVA RDNs (new ``add_rdn``) encode as a
  SET with multiple inner SEQUENCEs. One nit: the encoder does not
  DER-sort the SET OF elements for hand-built multi-AVA RDNs, so those
  can emit non-canonical DER — irrelevant for parsed certificates.
- **API changes:** ``dn_info()`` is deprecated and now returns a
  flattened *copy* (was a reference) — callers were updated; ``count()``
  now counts RDNs rather than AVAs (documented; differs only for
  multi-valued RDNs); ``add_attribute`` keeps its old meaning (each call
  appends a single-AVA RDN, matching previous encode behavior). The
  stream operators speak RFC 4514: ``+`` joins AVAs within an RDN on
  output and is a same-RDN separator on input (quoted values still
  protect literal ``+``/``,``) — the print/parse round-trip now
  preserves RDN structure.

Compatibility notes
-------------------

DN pairs that previously compared equal — reordered attribute
sequences, or multi-valued RDNs versus their split-apart forms — now
compare unequal. Effects surface as: certificates/CRLs with
inconsistently ordered DNs failing to chain or associate (as Botan's
own test CRL did), and certificate-store lookups keyed by DN missing
formerly-conflated entries. Every such delta is in the
strict/fail-closed direction; the only newly *rejected* inputs are
structurally invalid (empty RDNs) or absurd (more than 32 AVAs in one
RDN).

Verdict
-------

A correct and overdue structural fix: DN comparison moves from
order-insensitive multiset matching (demonstrably wrong, as the PR's own
test-data corrections show) to RFC 5280 7.1 RDN-sequence semantics, with
name-constraint matching, ordering, encoding, and the textual round-trip
all made consistent, plus fail-closed strictness and a
denial-of-service bound on hostile multi-AVA RDNs. Test coverage is good
(116 new test lines, corrected vectors distinguishing case-folding from
reordering). No defects were found.

Suggested classification: **relevant** (borderline critical: in-scope
``x509`` trust-relevant matching semantics change; all verified deltas
are tightening/fail-closed).
