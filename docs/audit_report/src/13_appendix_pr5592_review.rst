Appendix: Review of Botan PR #5592
==================================


The review in this section was entirely written by Anthropic's Fable 5 model. Please treat it with care as appropriate for AI generated content.

**"Various BigInt/mp related hardenings and bug fixes"**

- **PR:** `randombit/botan#5592 <https://github.com/randombit/botan/pull/5592>`_
  (merged as ``c5930e708``, 25 commits)
- **Author:** Jack Lloyd — **Merged:** 2026-05-10
- **First released in:** Botan 3.13.0
- **Size:** +319/-115 across 25 files
- **Audit scope status:** the changed modules ``math/bigint``, ``mp``,
  ``numbertheory``, ``pcurves_secp521r1``, ``rsa``, ``dsa``, ``dl_group``
  and ``ec_group`` are in the audit scope; ``srp6``, ``fpe_fe1`` and
  ``elgamal`` fall outside the BSI policy build.

Wrong-arithmetic fixes (the serious class)
------------------------------------------

- **P-521 reduction incomplete** (``3d2f52515``): ``P521Rep::redc``
  subtracted the modulus only when the folded value *exceeded*
  P = 2^521 - 1, missing the value **equal to** P — so a quantity
  congruent to 0 (mod p) could emerge as the non-canonical
  representative P instead of 0. The fix adds a constant-time all-ones
  detection (masked to the 9 valid top-word bits) and folds it into the
  subtract condition. Reachability is, as far as could be determined,
  negligible: a product of canonical nonzero inputs can never be
  congruent to 0 modulo a prime, and wide reductions (hash-to-curve
  style) hit the case with probability 2^-521 — but an incomplete
  modular reduction in a BSI-recommended curve's field arithmetic is
  precisely the kind of latent defect an audit must record, and the
  constant-time repair is correct.
- **Inline-asm miscompilation hazards** (``6b7d4af9f``, ``bf30db5b3``):
  ``word8_sub2`` lacked ``volatile`` (a compiler could legally elide or
  reorder the block), and ``word8_linmul3``/``word8_madd3`` wrote
  ``z[]`` through pointers without declaring a ``"memory"`` clobber —
  the optimizer could cache ``z`` across the asm block and compute with
  stale words. These are silent-wrong-bignum-arithmetic bugs whose
  manifestation depends on optimizer behavior; exactly the failure mode
  that produces exploitable fault-like conditions (compare the known
  RSA-CRT fault attacks). The ``divq`` block also gains its missing
  ``"cc"`` clobber.
- **BigInt internal invariants:** self-assignment ``x += x`` / ``x -= x``
  read the source data while ``add``/``sub`` may reallocate the same
  buffer — now special-cased (doubling/zeroing); a shrinking ``resize``
  failed to invalidate the cached significant-word count (stale
  ``sig_words`` -> wrong values downstream); ``ct_cond_add`` sized its
  output by the addend only, so when ``*this`` was wider the carry could
  be silently dropped — now ``max(size, v_words) + 1``;
  ``from_s32(INT32_MIN)`` negated an ``int32_t`` (undefined behavior) —
  now widened first; new ``static_assert`` s close zero-shift and
  empty-literal corners in ``mp_core.h``.
- **DL_Group::power_b_p(b, x) with x > p** silently truncated the
  exponent to ``p_bits`` — incorrect results; now sized by
  ``max(x.bits, p_bits)`` with an honest comment about the
  (exceptional-case) leak. The companion SRP6 fix (``db6a330e2``)
  corrects the ``a + u*x`` bit-bound (``max(a, 2H) + 1`` instead of
  ``max(a + 1, 2H)``), whose understatement could trip exactly that
  truncation.

Side-channel hardening
----------------------

- **ct_divide / ct_modulo size leaks** (``763204efd``): the working
  remainder used growable ``BigInt`` operations (``r <<= 1``,
  ``ct_cond_swap`` via sized operations) whose memory behavior tracked
  the intermediate value's magnitude. Now fixed-width ``y_words + 1``
  buffers driven by ``bigint_shl1``/``bigint_cnd_swap`` at constant
  length — the loop's footprint no longer depends on secret
  intermediates. These functions underlie constant-time inversions and
  reductions across in-scope algorithms.
- **Montgomery layer misuse-proofing:** ``mul``/``sqr`` now reject
  output aliasing an input (previously silent corruption; the overlap
  check pedantically uses ``std::less<const word*>`` to keep the pointer
  comparison well-defined, with an explanatory comment), the zero-value
  ``Montgomery_Int`` constructor now allocates ``p_words`` (was empty,
  breaking later fixed-width operations), and negative bases and scalars
  are rejected at exponentiation entry (previously the magnitude was
  silently used).

Parameter-validation hardening (hostile or degenerate domain parameters)
------------------------------------------------------------------------

- **DSA:** q is now required (all constructors funnel through one check)
  *and* at least 160 bits ("all versions of FIPS 186") — tiny-q
  parameters make discrete log and nonce bias trivial. Verification now
  also rejects the case where ``inverse_mod_q(s)`` returns 0 (s not
  invertible — reachable with a hostile composite q), which previously
  flowed s^-1 = 0 into the verification equation.
- **DL_Group estimated strength is now min(NFS(p), q_bits/2)** —
  previously only p counted, so a large-p/small-q group overstated its
  strength. Consequence worth flagging: certificates and keys over
  160-bit-q groups now evaluate to 80-bit strength and **fail the
  default 110-bit minimum-key-strength check in path validation** — a
  fail-closed behavior change aligned with TR-02102-1 (which demands
  q of at least 250 bits anyway).
- **ElGamal** (out of policy): encrypt rejects m = 0; decrypt validates
  a as a proper public element and rejects b in {0, >= p} — degenerate
  ciphertexts previously passed into the arithmetic. **FPE_FE1** (out of
  policy): inputs now range-checked against n, and the
  impossible-factorization error became a proper ``Invalid_Argument``
  with documented modulus requirements.
- **RSA:** verification's length check tightened to the RFC 8017
  exact-k rule (``829760b99``) — this is the check PR #5596 temporarily
  relaxed the next day (TLS-Anvil tooling bug) and PR #5630 restored on
  2026-05-31; the released 3.13.0 has it strict. The private-operation
  early exits gained a comment justifying why they are side-channel-safe
  (public inputs only) — accurate.
- **Prime generation** (``fd464898e``): ``random_prime`` unconditionally
  applied the safe-prime ``2p+1`` sieve filter, which for some
  ``equiv``/``modulo`` combinations (e.g. equivalent to 1 mod 3) rejects
  *every* candidate — an availability bug. The filter is now applied
  only from ``random_safe_prime``. Also ``EC_Group`` alias-OID lookups
  no longer register duplicate group data (``dcc5dca46``), keeping group
  identity consistent when a curve is referenced by a non-canonical OID.

Coverage in the 3.13.0 release notes
------------------------------------

PR #5592 appears **twice** in the 3.13.0 release notes, both times in
*general* (non-security-headline) entries:

- "Various BigInt and number-theoretic hardening and bug fixes.
  (GH #5581 #5585 #5586 #5588 **#5592** #5650 #5688)" — this generic
  bullet subsumes the P-521 reduction fix, the inline-asm clobber fixes,
  the BigInt invariant fixes, the side-channel hardening, and the
  DSA/DL-group parameter hardening, none of which are called out
  individually.
- "Reject RSA signature and ciphertext values which are not exactly the
  length of the modulus (GH **#5592** #5630 #5675)" — the RSA
  strict-length arc (introduced here, temporarily relaxed by #5596,
  restored by #5630).

**None of the fixes in this PR are listed among the release notes'
security-relevant items.** The security-relevant entries at the top of
the 3.13.0 notes are limited to: the blind OCSP SSRF (GH #5815), the
``AutoSeeded_RNG`` unseeded-after-clear bug (GH #5839 #5838), the Scrypt
32-bit integer overflow (GH #5820 #5629), the DN name-constraint
enforcement bug, and the FFI integer overflow (GH #5805). Upstream thus
classifies everything in #5592 — including the P-521 incomplete
reduction and the asm-clobber fixes — as hardening rather than as
vulnerabilities, presumably on reachability grounds (see the
reachability discussion above).

Tests
-----

Modest relative to the fix count: new powmod vectors, +9 lines in
``test_bigint``, +49 in ``test_ec_group`` (alias-OID behavior). Many of
the fixes are internal invariants exercised indirectly by the existing
corpus; the P-521 case and the asm clobbers are the ones a regression
vector would most be wanted for, and only the former plausibly is
covered (via the powmod vectors).

Verdict
-------

A high-value hardening sweep of the arithmetic core: several genuine
silent-wrong-result fixes (incomplete P-521 reduction, asm
clobber/volatile omissions, dropped carries, stale cached word counts,
exponent truncation), real side-channel tightening in the constant-time
division/modulo primitives, and a coherent set of hostile-parameter
defenses for DSA/DL groups with one report-worthy behavior change
(small-q groups now fail default path-validation strength checks). No
defects were found in the fixes themselves.

Suggested classification: **relevant** (borderline critical: in-scope
bignum/curve arithmetic correctness fixes including a BSI-recommended
curve's reduction, plus DSA/DL parameter hardening with
validation-outcome changes).
