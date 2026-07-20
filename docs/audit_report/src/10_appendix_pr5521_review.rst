Appendix: Review of Botan PR #5521
==================================


The review in this section was entirely written by Anthropic's Opus 4.8 model. Please treat it with care as appropriate for AI generated content.

**"Rollup of small fixes"**

- **PR:** `randombit/botan#5521 <https://github.com/randombit/botan/pull/5521>`_
  (branch ``jack/fix-rollup``)
- **Author:** Jack Lloyd — **Merged:** 2026-04-06 as ``8a7f43563``, 72 commits,
  +1286/-456 across 100 files
- **First released in:** Botan 3.12.0 (tagged 2026-05-06)
- **Scope:** broad. Public-key math (RSA, DL/EC groups, pcurves), symmetric AEADs and
  MACs, ASN.1 codec, X.509 path building / name constraints / OCSP, the FFI and libsodium
  compatibility layers, RNG, KDF/PBE, and assorted utilities.

Unlike the other PRs reviewed in these appendices, #5521 has no unifying feature theme: it
is a large janitorial rollup of independently-discovered defects. Many are hardening
touch-ups (argument checks, exception-safety, resource caps); a meaningful minority are
real correctness or security bugs in cryptographic code. This review first summarizes the
change categories, then reports in detail on the two categories the reader asked to focus
on — **cryptographic-feature changes** and **security-vulnerability fixes**.

General summary of change types
-------------------------------

The 72 commits fall into the following broad buckets (a commit may span more than one):

.. list-table::
   :widths: 32 10 58
   :header-rows: 1

   * - Category
     - Approx. count
     - Character
   * - Input / parameter validation hardening
     - ~20
     - Reject malformed or out-of-range inputs at the earliest point (RSA/DL/McEliece key
       parameters, PBES2 KDF params, BER/DER integers, PEM label sizes, HMAC_DRBG hash
       size, SHAKE/MGF1 output length).
   * - Cryptographic correctness bugs
     - ~8
     - Wrong results under specific conditions: Poly1305 final reduction, OCB 64-bit block
       index, redc_crandall asm offset, DER negative-integer minimality, concatenated-stream
       decompression.
   * - Security-relevant fixes (see detail below)
     - ~12
     - X.509 name-constraint / OCSP validation gaps, AEAD plaintext-release-on-failure,
       constant-time / side-channel corrections, DoS resource caps.
   * - Robustness / exception-safety / DoS caps
     - ~15
     - Prevent crashes, unbounded buffering, or hangs on adversarial input (path-building
       DFS iteration cap, AEAD/GHASH length limits, argon2/roughtime guards, getrandom
       EOF, thread-pool lock).
   * - FFI / libsodium compat layer
     - ~6
     - Missing nullptr checks, buffer clearing on reset, a batch of libsodium-emulation
       bug fixes, missing ``ffi_guard_thunk``.
   * - Memory hygiene / state reset
     - ~6
     - Ensure cipher modes and GHASH fully reset state on ``clear``/``start``; zeroize
       buffers; ``Memory_Pool`` off-by-one.
   * - Key-consistency and self-test
     - ~2
     - Fill in missing ``check_key`` public/private consistency checks (Ed25519, Ed448,
       FrodoKEM, DH, ML-DSA/-KEM, XMSS documented).
   * - Performance / refactor / build
     - ~10
     - Montgomery-parameter caching in prime generation, HOTP constant-divisor reduction,
       constexpr fixes, CLI/perf, comments.

The remainder of this report details the two requested categories.

Cryptographic-feature changes
------------------------------

Correctness bugs in primitives
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Poly1305 final reduction (``6126a83ee``).** The most consequential crypto bug in the PR.
In ``poly1305_finish`` the final conditional subtraction of the prime *p* selected the
reduced or unreduced limbs using a mask derived from the wrong quantity (the carry ``c``
via ``Mask::expand(c)``) rather than the top-bit of the trial subtraction result ``g2``.
The commit states this produced an incorrect MAC "with probability ~1/2^85" — i.e. for
inputs where the accumulator lands in the narrow window requiring the final reduction. As
Poly1305 underlies ChaCha20Poly1305 (TLS, and widely elsewhere), a wrong tag means a valid
message is rejected, or — symmetrically at the verifier — a tag computed by a correct peer
mismatches. Not a forgery or key-recovery issue, but a rare interoperability/authentication
failure in a very widely used MAC. Fixed to select on ``expand_top_bit(g2)``.

**OCB with messages > 64 GiB (``b3d4a317e``).** OCB's offset computation indexed the
per-block ``L`` values with a 32-bit block counter (``var_ctz32``), overflowing after 2^32
blocks (~64 GiB at 16-byte blocks) and thereafter producing wrong offsets — hence wrong
ciphertext and tags. Widened to a 64-bit index (``var_ctz64``), the ``L`` table reserve
raised accordingly, and the mode's ``m_block_index`` promoted to ``uint64_t``. Correctness
bug for very large single messages; no security impact below the threshold.

**redc_crandall inline-asm offset (``14ce29974``) and constexpr path (``852c7fb7b``).**
Two bugs in the secp256k1 Crandall-prime reduction. The x86-64 asm read the wrong word of
the ``hi`` limb array (``16(%[x])`` instead of ``8(%[x])``); it happened to be harmless
only because, for secp256k1's specific prime, the two words involved were always equal when
the result was used. The second fixes an all-zeros result when the same routine runs in a
constexpr context under GCC (a ``return`` sat outside the ``#if`` asm block). Both are
latent — the constexpr path is not yet exercised — but they are genuine defects in
field-arithmetic that would corrupt secp256k1 (Bitcoin-curve) operations if the
preconditions changed. Reviewed both; the corrected asm reads the intended word and the
constexpr control flow is now inside the guarded block.

**DER encoding of negative integers (``e5b8295aa``).** The BigInt DER encoder did not
always produce the *minimal* two's-complement encoding for negative values (the redundant
leading ``0x00``/``0xFF`` byte was not stripped when unnecessary). A non-minimal DER integer
violates DER and can cause signature/structure re-encoding mismatches and cross-implementation
parsing differentials. Botan rarely encodes negative ASN.1 integers, but the encoder is
general-purpose. Rewritten to emit the leading byte only when the sign bit requires it, with
an assertion on the buffer length.

**Concatenated compression streams (``0e9983cea``).** Decompression of multiple
back-to-back streams (valid for gzip/zlib members) left a gap of unused output buffer
between members and mishandled re-initialization after a clean stream end. Data-integrity
bug in the compression utility (not a cryptographic primitive, but affects any protocol
layering compression under crypto).

Key-parameter validation and generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**RSA parameter tightening (``3904fccd1``, ``fc0aa5ef5``, ``0c501ae46``).** Public-key
``init`` previously accepted absurd parameters (any odd ``n`` with ``>= 5`` bits, any odd
``e``). It now enforces ``n`` in [384, 16384] bits, odd, positive, and ``1 < e < n`` with
``e`` odd and ``<= 256`` bits — rejecting degenerate keys (tiny moduli, ``e = 1`` which
makes "encryption" the identity, ``e >= n``) at decode. Key *generation* gains an upper
bound (16384) and a multiple-of-8 requirement in addition to the existing 1024-bit floor.
``generate_another`` now always uses ``e = 65537`` instead of copying a possibly-hostile
``e`` from the template key. And RSA ``AlgorithmIdentifier`` parameters are now required to
be NULL or empty (``0c501ae46``), rejecting smuggled data in the params field. Collectively
these close a class of "malicious/nonsense RSA key is accepted and misbehaves later"
problems.

**DL_Group validation (``2086d4526``, ``89fecf072``).** Cheap structural checks (``p``
odd/positive/size-bounded, ``2 <= g < p``, ``q`` odd with ``q.bits() < p.bits()``) are
moved to a ``DL_Group_Data::create`` factory run at *deserialization* time rather than
being deferred to the expensive ``verify_group``. Combined with ``89fecf072``, which
switches DL/EC-group, TLS-name and OCSP decoding to require **DER** (not lenient BER),
this rejects malformed group parameters and non-canonical encodings up front. A malformed
group reaching the math layer is a classic source of hard-to-diagnose failures and
potential small-subgroup exposure.

**McEliece parameter validation (``bfb66d25e``).** HyMES McEliece key decoding validated
its ``n``/``t`` parameters only implicitly, accepting invalid combinations that then failed
"in more opaque ways later". Now checked at decode.

**EC scalar / point checks (``ac03ac4c6``, ``39ed02365``).** ``pcurves_generic`` scalar
deserialization now rejects zero scalars (a zero private key / signature-nonce component is
invalid and dangerous). ``base_point_mul_x_mod_order`` — used in ECDSA/SM2-style
``r = x(k*G) mod n`` computations — now asserts the result is not the identity point, which
can only occur if the caller passed a zero scalar; producing ``r`` from the identity would
be a catastrophic nonce failure.

**SM2 zero r/s guard (``2d5908c6c``).** SM2 signing now checks for ``r == 0`` or ``s == 0``
(throwing ``Internal_Error``, since with overwhelming probability these indicate a bug, not
genuine zeros). Standard defensive check mandated by the SM2/ECDSA signing algorithms;
their absence could yield a malformed or trivially-invalid signature.

**check_key completeness (``3d7119818``).** Several private keys skipped the
public/private consistency check: Ed25519, Ed448, FrodoKEM and DH now recompute the public
key (or run a signature round-trip for Dilithium/ML-DSA under ``strong``) and compare;
ML-DSA/-KEM and XMSS gain comments explaining that decoding already guarantees consistency.
This strengthens ``check_key``, the routine applications call to validate imported keys.

Side-channel / constant-time corrections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**CT::poison ordering (``b61e92e06``, ``cd5701137``).** Two cases where the taint-tracking
annotation used for constant-time verification (valgrind/ctgrind) was applied in the wrong
order relative to a memory write, defeating the check. In bitsliced AES decrypt the buffer
was poisoned *before* the input was loaded into it, so the loaded secret was treated as
initialized (unpoisoned) and its subsequent use would not be flagged. In
``inverse_mod_odd_modulus`` (modular inversion, used in RSA/ECDSA) the poison call sat
before the setup writes. These do not change runtime behavior but restore the integrity of
Botan's constant-time test harness for two security-critical routines — without them, a
future timing regression in AES or modular inversion could pass CI unnoticed.

**HOTP constant-divisor reduction (``d9d6f01c5``).** The final ``code % m_digit_mod`` used
a runtime modulus, which many compilers lower to a variable-time hardware division. Rewritten
to switch on the digit count so the divisor is a compile-time constant (multiply-shift),
avoiding a data-dependent division on the OTP value. Minor, but OTP codes are secret-adjacent.

**timing_test alignment (``14ffe04fc``).** Updates the ECDSA timing self-test to exercise
the same code path as production ECDSA, so the side-channel regression test actually covers
the shipped implementation.

Security-vulnerability fixes
----------------------------

X.509 name constraints
~~~~~~~~~~~~~~~~~~~~~~~

These are the highest-impact security fixes in the PR: name-constraint processing is a
direct authorization boundary (a constrained sub-CA must not be able to vouch for names
outside its delegation).

**Wildcard SAN bypassing excludedSubtrees (``47c74ba23``).** If a certificate carried a
wildcard SAN (e.g. ``*.example.com``) and a name-constraints ``excludedSubtrees`` entry
named a specific host the wildcard could match (``secret.example.com``), Botan's exclusion
check compared literally and did **not** treat the wildcard as matching the excluded name —
so the certificate was accepted. Because the wildcard cert can then authenticate the
excluded host, this is a name-constraint **bypass**. The fix adds a wildcard-vs-constraint
check (``host_wildcard_match``) in ``is_excluded``. RFC 5280 is ambiguous here; Botan takes
the safe (reject) interpretation.

**IPv4 constraints with non-normalized network address (``304d88db7``).** IPv4
name-constraint matching used the stored network address without masking off host bits. A
constraint encoded with a non-zero host portion (``10.1.2.3/24`` instead of ``10.1.2.0/24``)
would then fail to match addresses it should have covered — meaning an *excluded* subnet
could be evaded, or a *permitted* subnet spuriously fail. Now the network address is masked
(``net & mask``) at construction, decode, and every comparison site, giving correct
CIDR semantics.

**Constraints wrongly applied to self-issued intermediates (``9362e85c1``).** RFC 5280
§6.1.4(b) says name constraints are *not* applied to self-issued CA certificates in the
middle of a path (only to the final certificate). Botan applied them unconditionally,
causing valid chains through a re-keyed / self-issued intermediate to be **wrongly
rejected** (availability, matching the Limbo ``rfc5280::nc::permitted-self-issued`` test
that was previously xfail). Fixed to skip self-issued non-leaf certificates.

OCSP validation
~~~~~~~~~~~~~~~

**Delegated-responder issuer not verified (``4274164a1``).** When an OCSP response was
signed by a delegated responder certificate, Botan did not verify that the responder was
issued by the same CA that issued the certificate under check. The fix requires the
responder's issuer DN to equal the CA's subject DN, and — when both key identifiers are
present — that they match (handling shared-DN re-keyed/cross-certified CAs). Without this, a
responder legitimate for one CA could be accepted for another sharing a DN: a revocation
integrity gap.

**Weak OCSP-responder key silently accepted (``a5b1a0e9b``).** An off-by-one
(``>`` vs ``>=`` against ``FIRST_ERROR_STATUS``) in ``evaluate_ocsp_response`` meant an
error status returned by responder-cert verification — specifically the "signing key is too
weak for local policy" status, which sits exactly at the boundary — was treated as success.
So an OCSP response signed with a policy-forbidden weak key was accepted. Corrected to
``>=``.

**Restrict OCSP hashes to SHA-1/SHA-256 (``59923f6fd``).** ``CertID::is_id_for`` now
refuses OCSP CertIDs using any hash other than SHA-1 or SHA-256 (the only algorithms real
responders use), rather than instantiating whatever the response names. This narrows an
attacker-influenced-algorithm surface in revocation checking.

AEAD plaintext-release-on-verification-failure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Zeroize decrypted output when the tag check fails (``daec09b28``).** Across all one-shot
AEAD decryptors (GCM, ChaCha20Poly1305, EAX, OCB, SIV, CCM, Ascon), a failed authentication
tag threw ``Invalid_Authentication_Tag`` but left the *decrypted-but-unauthenticated*
plaintext sitting in the caller's output buffer. An application that ignored the exception
(or caught it carelessly) could read and act on forged plaintext — the canonical
release-of-unverified-plaintext hazard. Each decryptor now clears the output span before
throwing. The commit explicitly notes the residual limitation: the *incremental* update
interface still exposes unauthenticated data, which cannot be fully mitigated in that API
shape.

**NIST key-unwrap padding not verified (``c1f01384e``).** ``nist_key_unwrap_padded`` (SP
800-38F KWP) failed to verify that the padding bytes of the recovered plaintext were zero —
a check that had been lost in an earlier refactor (the commit names the culprit). Without
it, KWP unwrapping accepts inputs it should reject, weakening the integrity guarantee of the
key-wrap. Restored.

Denial-of-service resource caps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Certificate-path build/verify bounds (``ce5759473``, ``e9e8e6e7d``).** Path *building*
is a DFS over the supplied certificate pool; a crafted set of certificates (many sharing
subjects/issuers) can make it explore exponentially. A hard cap of 1000 DFS steps is added,
and the per-validation limits are tightened from 128 paths to 50 paths **and** a new 200
total-certificate-verification budget. These bound CPU against a hostile certificate bundle.

**AEAD / GHASH input-length limits (``4cd5abcab``, ``dab6adb6d``).** GHASH/GCM now enforce
the NIST SP 800-38D maximum (2^39 - 256 bits) and ChaCha20Poly1305 the RFC 8439 maximum
(2^38 - 64 bytes), throwing rather than silently exceeding the AEAD's security bound (past
which the mode's guarantees do not hold). Counters widened to ``uint64_t`` to track this
correctly.

**Signature-padding input caps (``0edf8be5d``, ``aab82b37c``).** ``PSS_Raw`` and
``PKCS1v15(Raw)`` now reject over-long inputs during ``update`` rather than buffering
unbounded data that would be rejected only at sign/verify time — cutting off a memory-
amplification path.

**Miscellaneous robustness (``6900638fe``, ``0669dbc59``, ``d88a9c30a``, ``b1910ec67``).**
``getrandom`` returning 0 (rather than error) is now caught instead of looping/mis-seeding;
a Roughtime out-of-range shift is guarded; ``argon2_check_pwhash`` is wrapped so malformed
encoded hashes cannot throw out to the caller; and ``Thread_Pool`` no longer holds its lock
while running a task synchronously (a self-deadlock / contention hazard).

Introduced bugs
---------------

None found. Given the breadth (100 files) I focused verification on the cryptographic and
security changes:

1. **Poly1305 fix (``6126a83ee``)** — confirmed the new mask selects the unreduced value
   exactly when the trial subtraction ``g2`` did not borrow (top bit clear via
   ``expand_top_bit``), which is the correct "h >= p" condition; the previous ``c``-based
   mask was selecting on the wrong signal.
2. **AEAD zeroization (``daec09b28``)** — each ``clear_mem`` spans exactly the plaintext
   region (offset to remaining/`sz - tag`), before the throw, in all seven modes.
3. **OCSP issuer/weak-key fixes** — the DN+KeyID predicate is fail-closed (mismatch returns
   ``OCSP_ISSUER_NOT_TRUSTED``); the ``>=`` boundary change now includes the first error
   code rather than excluding it.
4. **Name-constraint IPv4 masking** — applied consistently at construction, BER decode, and
   all three match sites, so stored and compared forms agree.
5. **RSA/DL parameter bounds** — bounds are inclusive/exclusive as intended and do not
   reject any standard key size (1024-16384 RSA, standard FFDHE/DSA groups).
6. **OCB 64-bit index** — the ``L`` reserve (65) covers the widened ntz range and
   ``var_ctz64`` returns 64 on zero as the 32-bit version returned 32.

The RSA and DL_Group tightenings are the only changes with meaningful *compatibility*
fallout: a previously-loadable but degenerate key (tiny RSA modulus, ``e`` outside
``1 < e < n``, a DL group failing the new cheap checks, or a BER-rather-than-DER group
encoding) now fails to decode. These are deliberate fail-closed choices consistent with the
other hardening PRs in this series.

Verdict
-------

A large, heterogeneous hardening rollup. The cryptographically significant content is a
real correctness bug in Poly1305 (rare wrong MAC in a very widely used construction), an
OCB large-message overflow, two latent field-arithmetic defects in the secp256k1 reduction,
and a set of primitive-level parameter/key validations that move failure from "opaque later
error" to "clear rejection at decode". The security-vulnerability content is led by three
X.509 name-constraint fixes (a genuine wildcard-SAN exclusion **bypass**, an IPv4 CIDR
matching error, and an RFC 5280 self-issued-exemption error), two OCSP validation gaps
(delegated-responder issuer binding, and an off-by-one that accepted weak responder keys),
the AEAD release-of-unverified-plaintext mitigation across all one-shot modes, restored KWP
padding verification, and several DoS caps on path building and AEAD/padding input sizes.
I found no introduced bugs. All 72 commits shipped together in Botan 3.12.0, which is the
first release to contain any of them.
