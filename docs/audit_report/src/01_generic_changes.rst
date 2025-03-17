Changes Overview
================

Since the previously audited version (|botan_git_base_ref|), Botan
|botan_version| brings some extensions and fixes. The most relevant changes are outlined below.

Classic McEliece
----------------

The code-based post-quantum key-encapsulation mechanism "Classic McEliece" was
added in this release. It is implemented according to an ISO draft standard that
is currently being finalized for publication.

(Hybrid) PQC in TLS 1.3
-----------------------

This release removes the experimental support for TLS 1.3 key exchanges using
hybrid schemes based on the Kyber Round 3 specification. Instead, the default
TLS 1.3 configuration now allows hybrid key exchanges using x25519/ML-KEM-768.

Support for pure ML-KEM key exchanges without a hybridization with an elliptic
curve algorithm was added for TLS 1.3 but not enabled by default.

Elliptic Curve Cryptography
---------------------------

Various optimizations were applied to the new elliptic curve math implementation
added back in Botan 3.5.0. The existing elliptic curve implementation is now
marked as deprecated and can be disabled at build time. In Botan |botan_version|
this will remove support for user-defined curves, however. The next version of
the library (Botan 3.8.0) will add support for such curves independent of the
now-deprecated legacy elliptic curve implementation.

Wrapper for "Entropy Source and DRNG Manager" (ESDM)
----------------------------------------------------

This allows an easy integration with the [ESDM]_ to gain access to high-quality
entropy via a user-space random number generator daemon on Linux.
