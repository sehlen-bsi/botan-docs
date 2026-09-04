Appendix: Review of Botan PR #5588
==================================


The review in this section was entirely written by Anthropic's Fable 5 model. Please treat it with care as appropriate for AI generated content.

**"Improve verification of EC group generators"**

- **PR:** `randombit/botan#5588 <https://github.com/randombit/botan/pull/5588>`_
  (merged as ``fbb82b80c``, 3 commits)
- **Author:** Jack Lloyd — **Merged:** 2026-05-09
- **First released in:** Botan 3.13.0
- **Size:** +99/-12 across 5 files
- **Audit scope status:** modules ``ec_group`` and ``pcurves_generic``
  are the core of all in-scope ECC (ECDSA/ECDH over the BSI curves).
- **Release-notes placement:** cited in the general "Various BigInt and
  number-theoretic hardening and bug fixes" bullet (GH #5581 #5585 #5586
  #5588 #5592 #5650 #5688), not among the security-relevant items.

The gap being closed
--------------------

Validation of EC *domain parameters* — the values an application may
receive from untrusted sources via the deprecated explicit-parameter
``EC_Group`` constructors, DER groups with explicit parameters, or TLS
custom-curve callbacks — had backend-dependent holes:

- **The pcurves (modern) backend accepted an off-curve generator.**
  ``PCurveInstance::from_params`` performed no on-curve check at all;
  only the legacy ``EC_Point``-based path checked it. An off-curve
  generator is the invalid-curve attack applied to the *group itself*:
  all arithmetic silently runs on some other curve (potentially of
  smooth order), voiding the discrete-logarithm assumption for every
  operation under that group.
- **verify_group was partially a no-op in pcurves-only builds**: the
  base-point on-curve and order checks sat inside
  ``#if BOTAN_HAS_LEGACY_EC_POINT``, so in builds without the legacy
  backend an explicit ``verify_group()`` call — the API whose entire
  purpose is vetting untrusted parameters — skipped exactly those
  checks.

What the PR does
----------------

1. **Chokepoint check in EC_Group_Data**: the constructor every
   group-creation path funnels through now verifies
   y^2 = x^3 + a*x + b (mod p) via Barrett arithmetic and throws
   ``Invalid_Argument`` otherwise — backend-independent, so off-curve
   generators are rejected at group construction regardless of build
   configuration (including parse-time rejection for DER-supplied
   explicit groups).
2. **pcurves_generic from_params** independently performs the same
   check and returns null — defense in depth at the backend boundary.
3. **The deprecated explicit constructor** gains full parameter
   validation: range checks (0 <= a < p, 0 < b < p, coordinates in
   [0, p)), **Baillie-PSW primality of both p and the order**, non-zero
   discriminant 4a^3 + 27b^2 (rejecting singular curves, on which the
   "DLP" collapses to the additive or multiplicative group), and the
   generator-on-curve check. Two minor observations: ``b > 0`` excludes
   b = 0 curves, a slight over-restriction (such curves always carry
   2-torsion, so no prime-order-generator group loses anything real —
   no standardized curve is affected), and Baillie-PSW is
   probable-prime only, though with no known counterexamples it is the
   accepted practice for parameter vetting.
4. **verify_group rewritten backend-independently**: the on-curve check
   uses plain modular arithmetic, and the order check is replaced by an
   identity-free formulation — compute [n-1]G through the (blinded)
   scalar-multiplication machinery and require it to equal -G, which
   holds if and only if [n]G is the identity element (the point at
   infinity). This works within pcurves, which cannot represent the
   identity as an affine point; the side condition that G itself is not
   the identity is guaranteed because G is constructed from affine
   coordinates. The cofactor check ([cofactor]G not the identity)
   correctly remains legacy-only, with a comment noting that pcurves
   supports only cofactor 1.
5. Test-infrastructure tweak (``test_throws`` substring matching) plus a
   targeted test: secp256r1 parameters with the generator's y low bit
   flipped, asserted rejected through both deprecated constructor
   variants.

Assessment
----------

All changes are fail-closed strengthening of hostile-parameter
validation at exactly the right layers: the universal ``EC_Group_Data``
chokepoint, the backend factory, the deprecated public constructor, and
the explicit verification API. The new order-verification logic
([n-1]G = -G if and only if [n]G is the identity, given G is not the
identity) and the discriminant/on-curve arithmetic were checked and are
correct. Behavior change to record: previously accepted degenerate
parameter sets (composite p or order, singular curves, off-curve
generators) now throw from the deprecated constructor — any user of that
constructor with non-conforming toy curves breaks, which is the intent.

Verdict
-------

A clean closing of backend-dependent validation gaps for EC domain
parameters, eliminating the accepted-off-curve-generator case in the
modern backend and restoring ``verify_group``'s guarantees in
pcurves-only builds, with sensible extra vetting (primality,
discriminant) at the deprecated entry point. No defects were found; the
``b > 0`` exclusion is the only (harmless) over-restriction.

Suggested classification: **relevant** (in-scope ``ec_group``
hostile-parameter hardening affecting all ECC; verified fail-closed).
