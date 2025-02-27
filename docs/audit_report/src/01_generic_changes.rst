Changes Overview
================

Since the previously audited version (|botan_git_base_ref|), Botan
|botan_version| brings some extensions and fixes. The most relevant changes are outlined below.

Introduction of Standardized Post-Quantum Algorithms
----------------------------------------------------

Additionally to the existing implementations of the round 3 candidates Kyber,
Dilithium and SPHINCS+, Botan |botan_version| introduces implementations for the
standards FIPS 203, 204 and 205.

   * ML-KEM (FIPS 203)
   * ML-DSA (FIPS 204)
   * SLH-DSA (FIPS 205)

Note that the signature algorithms lack support for pre-hash mode and the
application-defined context string. Those features were introduced with the
final standards and can't be implemented without an API extension that was
postponed to a future minor release of the library.

Jitterentropy RNG Wrapper
-------------------------

This is a small wrapper around the jitterentropy-library. This library provides
a high-quality entropy source based on jitter measured in CPU execution times.
It comes with extensive documentation and estimates on the entropy's quality.

TPM 2.0 Wrapper
---------------

The TPM 2.0 wrapper provides a high-level interface to TPM-hosted asymmetric key
material as well as an adapter to the TPM's random number generator.
Additionally, Botan implements the crypto callbacks introduced with TPM2-TSS
4.0, which allow to communicate with the TPM without a dependency on a
third-party crypto library such as OpenSSL or mbedTLS.

New (internal) Elliptic Curve Math Library
------------------------------------------

Botan |botan_git_base_ref| already introduced a new elliptic curve math library,
which is now (starting with Botan |botan_version|) used for all elliptic curve
algorithms, such as ECDH and ECDSA. Apart from a major performance gain,
applications should not notice this change. The new library uses fixed-length
data types (instead of the previously used ``BigInt``) and is designed to better
leverage compiler optimizations.
