Changes Overview
================

Since the previously audited version (|botan_git_base_ref|), Botan
|botan_version| brings some extensions and fixes. The most relevant changes are outlined below.

HSS/LMS
-------

An implementation of Hierarchical Signature System (HSS) with Leighton-Micali
Hash-Based Signatures (LMS) was introduced in Botan |botan_version|. This
algorithms is similar to the already-implemented XMSS signatures and resists
quantum attacks by nature. The algorithm is stateful and it is therefore not
recommendable to create signatures in a software implementation.

See :ref:`changes/hss_lms` for a list of relevant patches that landed in Botan |botan_version|.

New Elliptic Curve Cryptography Implementation
----------------------------------------------

Botan |botan_version| introduces an entirely new implementation of elliptic
curve cryptography for prime-order curves that is much more friendly for modern
compiler optimizations. In a future release of the library it has the potential
to roughly double the throughput of ECC-based algorithms.

In this release, the new implementation is not used for ECDH or ECDSA but rather
only for the ``ec_h2c`` module that allows hashing data to an underlying ECC
point.

See :ref:`changes/ecc` for a list of relevant patches that landed in Botan |botan_version|.

X.509
-----

Apart from some :ref:`minor additions to the X.509 implementation
<changes/x509>` this release :ref:`fixes two vulnerabilities in the handling of
X.509 certificates <chapter/vulnerabilities>`. See the linked sections for more
details.

Side Channel Mitigations
------------------------

As originally reported by `PQShield
<https://pqshield.com/pqshield-plugs-timing-leaks-in-kyber-ml-kem-to-improve-pqc-implementation-maturity>`_,
the Kyber reference implementation was vulnerable to a secret-dependent branch
side channel introduced by a compiler optimization in Clang with certain
optimization flags.

Botan |botan_version| introduces a system-wide "value barrier" that aims to
prevent the compiler from reasoning about possible value ranges of variables.
This both mitigates the described vulnerability in Kyber and applies the same
to the rest of the code base where applicable.

See :ref:`changes/side_channel_mitigation` for a list of relevant patches that
landed in Botan |botan_version|.

Module Deprecations
-------------------

This release deprecates various outdated or superseded modules. Most notably,
this includes the modules ``kyber_90s`` and ``dilithium_aes`` which are variants
of Kyber and Dilithium (NIST competition round 3) that utilize SHA-2 and AES as
their underlying primitives. Neither of those variants is considered for
standardization by NIST and will therefore be removed in a future release.

Additionally, the now-deprecated module ``mce`` implements a variant of the
McEliece cryptosystem that will be replaced by an implementation of "Classic
McEliece" in a future release of the library.
