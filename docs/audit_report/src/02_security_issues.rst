Open Security and Compatibility Issues in the Audited Version
=============================================================

The following table lists the open security and compatibility issues in the
audited version |botan_version|, i.e. issues that are present in |botan_version|
and were not fixed within the range covered by this audit. The ``Type`` column
indicates whether an issue affects security and/or compatibility. The ``Source``
column records where the issue was identified: issues drawn from the upstream
Botan release notes are marked *Botan release notes*, issues identified during
this project's audit are marked *P663 Audit*, and issues that were found and
fixed upstream after the release of |botan_version| without a corresponding
release note yet are marked *Botan master*. For issues that have been fixed
upstream, the ``Fixed in Version`` column names the upstream release that
resolves them.

At the time of writing (2026-09-07), |botan_version| is the most recent upstream
release; no subsequent release has been published. The draft release notes of
the upcoming version 3.14.0 on the upstream ``master`` branch do not list any
fix for a defect present in |botan_version|, and the upstream security
advisories (``doc/security.rst``) contain no entry beyond those fixed in
|botan_version|. Fixes merged to ``master`` after the release that address
defects present in |botan_version| are listed below with the fixed-in version
3.14.0 (unreleased). The entries carried over from the previous audit were
re-validated against the |botan_version| sources and the state of the
respective GitHub issues.

.. list-table::
   :class: longtable
   :widths: 12 11 10 15 10 42
   :header-rows: 1

   * - Reference
     - Source
     - Type
     - Affected versions
     - Fixed in Version
     - Description
   * - `#5614 <https://github.com/randombit/botan/issues/5614>`__
     - P663 Audit
     - security
     - up to and including 3.13.0
     -
     - Problematic behaviour of ``Stateful_RNG::force_reseed()`` with respect to the resulting RNG state with possible side effects to SCA countermeasures in ECC operations. The function still only resets the reseed counter in 3.13.0, i.e. it marks the RNG as unseeded instead of reseeding it. The issue is still open upstream.
   * - `#5615 <https://github.com/randombit/botan/issues/5615>`__
     - P663 Audit
     - security
     - up to and including 3.13.0
     -
     - Control of SCA countermeasures in ECC operations depends implicitly on RNG seeding state. This is an obscure and error prone mechanism to control relevant security measure. The maintainer closed the issue on 2026-05-20 without a code change, arguing that scalar blinding is not required in the cache/timing side channel model and that resorting to an implicit fallback RNG would violate the caller-chooses-the-RNG policy. The behaviour is unchanged in 3.13.0: the ECC scalar multiplication code (both the ``pcurves`` and the legacy ``EC_Point`` backend) still enables blinding only if ``rng.is_seeded()`` returns true.
   * - `#5909 <https://github.com/randombit/botan/issues/5909>`__
     - P663 Audit
     - security
     - 3.13.0 (Ascon-AEAD128 was added in 3.13.0; the ``Sponge`` base class also underlies SHA-3, SHAKE and Keccak)
     - 3.14.0 (unreleased), fixed by `#5919 <https://github.com/randombit/botan/issues/5919>`__, merged 2026-09-04
     - The destructor of ``Ascon_AEAD128_Mode`` scrubs the key copy but not the key-derived permutation state held in the ``Sponge`` object, so key-dependent state could remain in freed memory. Identified in the review of `#5742 <https://github.com/randombit/botan/issues/5742>`__ (see the corresponding appendix). The fix scrubs the sponge state on destruction for all ``Sponge`` based primitives.
   * - `#5913 <https://github.com/randombit/botan/issues/5913>`__
     - P663 Audit
     - compatibility
     - 3.13.0
     - 3.14.0 (unreleased), partially addressed by `#5920 <https://github.com/randombit/botan/issues/5920>`__, merged 2026-09-04
     - The strict EC point deserialization introduced with `#5725 <https://github.com/randombit/botan/issues/5725>`__ rejects the hybrid point encoding that the encoder can still be configured to emit (round-trip break), changes TLS 1.2 interoperability for peers sending hybrid points without a release note, and leaves several decoding paths (ECIES, FFI raw point loaders, PKCS #11 ``CKA_EC_POINT``, ECDH ``raw_agree``) permissive, so that the C and C++ APIs disagree on accepted encodings.
   * - `#5924 <https://github.com/randombit/botan/issues/5924>`__
     - P663 Audit
     - security (low severity)
     - 3.13.0
     -
     - Information loss in ``RandomNumberGenerator::randomize_with_ts_input()``: on the fallback path taken in builds without a System_RNG, the expression computing the length of the additional input (``8 + (pid != 0) ? 4 : 0``) is affected by an operator precedence error and always yields 4. Only the least significant 32 bits of the timestamp are passed to the DRBG and the process ID is dropped, which weakens the hedge against duplicated generator states after a ``fork()`` or a virtual machine rollback. Introduced by `#5839 <https://github.com/randombit/botan/issues/5839>`__. Seeding and the security of a correctly seeded generator are not affected, and default builds with a System_RNG do not take this path; the severity is therefore rated low. Identified during the update of the cryptographic documentation for 3.13.0. The issue is still open upstream.
   * - `#5921 <https://github.com/randombit/botan/issues/5921>`__
     - Botan master
     - security
     - up to and including 3.13.0
     - 3.14.0 (unreleased), merged 2026-09-06
     - Incomplete validation of EC domain parameters: for explicitly encoded curve parameters neither the Hasse bound nor the curve discriminant was checked, the deprecated ``EC_Group`` constructor checked the discriminant but not the Hasse bound, no setup path verified that the generator lies on the curve (this was left to ``verify_group``), anomalous curves (``p == n``) were accepted, and a cofactor of zero was accepted. Additionally, registering a group under a name known to ``pcurves`` but with different parameters selected the curve specific implementation for the wrong curve. Relevant only for applications that load explicit or custom EC parameters from untrusted input.
   * - `#5002 <https://github.com/randombit/botan/issues/5002>`__
     - P663 Audit
     - compatibility
     - All versions featuring ML-DSA, up to and including 3.13.0
     - Fix is pending. PR exists (`#5307 <https://github.com/randombit/botan/issues/5307>`__, still open, last updated 2026-08-12).
     - RFC 9881 specifies three alternative encodings of the ML-DSA private key. Botan still reads and writes the "pure seed" format (the raw 32-byte seed as content of the PKCS #8 ``privateKey`` octet string, without the ``CHOICE`` structure), which is not compatible to any of those specified in RFC 9881. Confirmed for 3.13.0 in ``ML_DSA_Expanding_Keypair_Codec``.
   * - `#5540 <https://github.com/randombit/botan/issues/5540>`__
     - P663 Audit
     - compatibility
     - All versions featuring ML-KEM, up to and including 3.13.0
     - Fix is pending. The issue is deliberately kept on hold until the approach for ML-DSA (`#5307 <https://github.com/randombit/botan/issues/5307>`__) is agreed upon.
     - RFC 9935 specifies three alternative encodings of the ML-KEM private key. Botan still reads and writes the "pure seed" format (the raw 64-byte seed, or alternatively the raw expanded key, as content of the PKCS #8 ``privateKey`` octet string, without the ``CHOICE`` structure), which is not compatible to any of those specified in RFC 9935. Confirmed for 3.13.0 in ``Kyber_PrivateKey::private_key_bits``.
