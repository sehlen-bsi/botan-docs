Changes Overview
================

In relation to the previously audited version (|botan_git_base_ref|), Botan
|botan_version| brings some minor extensions of functionality and bug fixes.
This update spans the two upstream releases that lie between the base revision
and the target revision, namely 3.11.1 and 3.12.0. Among the bug fixes, there
are fixes for three CVEs, which probably are the most important updates in this
update:

- CVE-2026-44378: a CPU-based denial of service when decoding BER encoded data
- CVE-2026-34580: a certificate verification bypass introduced in 3.11.0
  (`#5500 <https://github.com/randombit/botan/issues/5500>`__)
- CVE-2026-34582: a TLS 1.3 client authentication bypass
  (`#5599 <https://github.com/randombit/botan/issues/5599>`__)

Furthermore, a number of code optimizations have been introduced.

The following overview is derived from the official Botan release notes and
groups the changes into security relevant fixes, other fixes, and additions of
new features. A per-patch classification with the associated auditors is found
in the detailed change tables (see :ref:`changes`); the security issues are
described in more detail in the chapter on Security and Vulnerabilities.


Security Relevant Fixes
-----------------------

* CVE-2026-44378: a CPU-based denial of service when decoding BER encoded data.
  The release notes do not reference a dedicated pull request for this
  identifier; it was addressed as part of the BER/DER decoding hardening in
  `#5545 <https://github.com/randombit/botan/issues/5545>`__,
  `#5561 <https://github.com/randombit/botan/issues/5561>`__ and
  `#5521 <https://github.com/randombit/botan/issues/5521>`__.

* CVE-2026-34580: resolve a certificate verification bypass bug introduced in
  3.11.0 (`#5500 <https://github.com/randombit/botan/issues/5500>`__).

* CVE-2026-34582: resolve a TLS 1.3 client authentication bypass
  (`#5599 <https://github.com/randombit/botan/issues/5599>`__).

* Require strict DER when decoding PKIX types such as certificates
  (`#5521 <https://github.com/randombit/botan/issues/5521>`__).

* Fix bugs in handling of indefinite length BER data, including missing EOC
  markers being silently accepted
  (`#5545 <https://github.com/randombit/botan/issues/5545>`__).

* Enforce maximum input length limits for ChaCha20Poly1305 and GHASH/GCM
  (`#5521 <https://github.com/randombit/botan/issues/5521>`__).

* Fix a bug in Ed25519 where an invalid signature checked with ``PK_Verifier``
  might cause a later valid signature to be rejected
  (`#5454 <https://github.com/randombit/botan/issues/5454>`__).

* Fix a corresponding bug in the handling of ECDSA DER-encoded signatures
  (`#5455 <https://github.com/randombit/botan/issues/5455>`__).

* Various TLS conformance and hardening fixes
  (`#5550 <https://github.com/randombit/botan/issues/5550>`__,
  `#5551 <https://github.com/randombit/botan/issues/5551>`__,
  `#5555 <https://github.com/randombit/botan/issues/5555>`__,
  `#5568 <https://github.com/randombit/botan/issues/5568>`__).


Other Fixes
-----------

* Various X509/PKIX/OCSP optimizations and bug fixes
  (`#5535 <https://github.com/randombit/botan/issues/5535>`__,
  `#5536 <https://github.com/randombit/botan/issues/5536>`__,
  `#5546 <https://github.com/randombit/botan/issues/5546>`__,
  `#5554 <https://github.com/randombit/botan/issues/5554>`__,
  `#5561 <https://github.com/randombit/botan/issues/5561>`__,
  `#5562 <https://github.com/randombit/botan/issues/5562>`__,
  `#5569 <https://github.com/randombit/botan/issues/5569>`__).

* Skip OCSP/CRL revocation checks on certificate chains which were already
  going to be rejected due to path validation errors
  (`#5512 <https://github.com/randombit/botan/issues/5512>`__).

* Improve handling of unknown X.509 certificate extensions
  (`#5518 <https://github.com/randombit/botan/issues/5518>`__).

* Skip checking the self-signature of self-signed certificates during parsing
  (`#5515 <https://github.com/randombit/botan/issues/5515>`__).

* Avoid sending the TLS ``certificate_type`` extension unless TLS 1.2 is
  disabled, since raw public keys are not currently supported in 1.2
  (`#5523 <https://github.com/randombit/botan/issues/5523>`__).

* Avoid truncation of large handshake messages in DTLS
  (`#5522 <https://github.com/randombit/botan/issues/5522>`__).

* Discard TLS handshake state once the handshake has completed, retaining only
  the data needed for the active connection
  (`#5517 <https://github.com/randombit/botan/issues/5517>`__).

* Fixes for compiling with GCC 16
  (`#5564 <https://github.com/randombit/botan/issues/5564>`__).

* Fix various minor TLS conformance issues flagged by TLS-Anvil
  (`#5494 <https://github.com/randombit/botan/issues/5494>`__,
  `#5498 <https://github.com/randombit/botan/issues/5498>`__).

* Fix a problem introduced in 3.11.0 which could cause crashes on processors
  without SSSE3 support, particularly when compiled by GCC
  (`#5460 <https://github.com/randombit/botan/issues/5460>`__,
  `#5463 <https://github.com/randombit/botan/issues/5463>`__,
  `#5469 <https://github.com/randombit/botan/issues/5469>`__).

* Fix various new warnings from ``clang-tidy`` 22
  (`#5456 <https://github.com/randombit/botan/issues/5456>`__).

* Fix a compilation error introduced in 3.11.0 which prevented using ``ffi``
  unless ``bcrypt`` was also enabled
  (`#5462 <https://github.com/randombit/botan/issues/5462>`__).

* Avoid a macro collision with Microsoft headers that could cause a compilation
  problem in amalgamation mode
  (`#5486 <https://github.com/randombit/botan/issues/5486>`__).

* Enable ``explicit_bzero``, ``getentropy`` and ``getrandom`` on Hurd
  (`#5488 <https://github.com/randombit/botan/issues/5488>`__).


New Features and Additions
--------------------------

New and refactored X.509 / PKIX functionality:

* Add ``BER_Decoder::Limits`` which allows controlling what DER/BER syntax is
  accepted while decoding
  (`#5507 <https://github.com/randombit/botan/issues/5507>`__,
  `#5514 <https://github.com/randombit/botan/issues/5514>`__).

* Add support for IPv6 name constraints in X.509 certificate path validation,
  and add IPv6 address parsing and formatting utilities
  (`#5534 <https://github.com/randombit/botan/issues/5534>`__,
  `#5537 <https://github.com/randombit/botan/issues/5537>`__).

* Add an index to ``X509_CRL`` for fast revocation checks
  (`#5511 <https://github.com/randombit/botan/issues/5511>`__).

* Add ``X509_Certificate::Tag`` for fast searching/indexing of certificates
  (`#5509 <https://github.com/randombit/botan/issues/5509>`__).

* Change ``X509_Object`` to share immutable state between copies
  (`#5504 <https://github.com/randombit/botan/issues/5504>`__).

* Make certificate path building DFS incremental
  (`#5513 <https://github.com/randombit/botan/issues/5513>`__,
  `#5520 <https://github.com/randombit/botan/issues/5520>`__,
  `#5521 <https://github.com/randombit/botan/issues/5521>`__).

* Refactor the Windows system certificate store and add a cache of materialized
  certificates to avoid repeated parsing
  (`#5539 <https://github.com/randombit/botan/issues/5539>`__).

* Optimize and improve certificate store search operations
  (`#5510 <https://github.com/randombit/botan/issues/5510>`__).

TLS:

* Add support for RFC 9258 PSK import in TLS 1.3
  (`#5523 <https://github.com/randombit/botan/issues/5523>`__).

* Add ALPN support to the Boost ASIO TLS stream
  (`#5428 <https://github.com/randombit/botan/issues/5428>`__).

APIs, bindings, and build system:

* Add ``BigInt::signum`` to simplify sign comparisons
  (`#5519 <https://github.com/randombit/botan/issues/5519>`__).

* Add DRBG helpers to the C89/FFI interface and Python binding
  (`#5527 <https://github.com/randombit/botan/issues/5527>`__).

* Add EC scalar and point operations to the C89/FFI interface
  (`#5404 <https://github.com/randombit/botan/issues/5404>`__,
  `#5565 <https://github.com/randombit/botan/issues/5565>`__).

* Add NIST key wrap with padding to the Python binding
  (`#5521 <https://github.com/randombit/botan/issues/5521>`__).

* Add ``configure.py --without-include-namespace`` to allow installing headers
  without the ``botan-3/`` subdirectory
  (`#5528 <https://github.com/randombit/botan/issues/5528>`__).

Test infrastructure:

* Upgrade TLS-Anvil and add client-side TLS-Anvil testing
  (`#5503 <https://github.com/randombit/botan/issues/5503>`__).

* Upgrade BoGo tests
  (`#5523 <https://github.com/randombit/botan/issues/5523>`__,
  `#5556 <https://github.com/randombit/botan/issues/5556>`__).

* Add a script for running the NIST ACVP test vectors
  (`#5527 <https://github.com/randombit/botan/issues/5527>`__).

New optimized and constant-time algorithm implementations. The constant-time
implementations additionally improve resistance against timing side channels:

* Add an optimized Argon2 implementation using AVX512
  (`#5471 <https://github.com/randombit/botan/issues/5471>`__).

* Add an optimized and constant-time Twofish implementation using AVX512/GFNI
  (`#5465 <https://github.com/randombit/botan/issues/5465>`__).

* Add an optimized and constant-time SEED implementation using AVX512/GFNI
  (`#5472 <https://github.com/randombit/botan/issues/5472>`__).

* Add optimized and constant-time Whirlpool implementations using AVX2 and
  AVX512
  (`#5453 <https://github.com/randombit/botan/issues/5453>`__,
  `#5473 <https://github.com/randombit/botan/issues/5473>`__).

* Add SSSE3/NEON and AVX2 optimized codepaths for CTR
  (`#5474 <https://github.com/randombit/botan/issues/5474>`__,
  `#5480 <https://github.com/randombit/botan/issues/5480>`__).

* Add constant time implementations of Camellia, ARIA, SEED and SM4 using AES-NI
  or ARMv8 AES instructions to implement sbox lookups
  (`#5476 <https://github.com/randombit/botan/issues/5476>`__,
  `#5477 <https://github.com/randombit/botan/issues/5477>`__,
  `#5479 <https://github.com/randombit/botan/issues/5479>`__,
  `#5481 <https://github.com/randombit/botan/issues/5481>`__,
  `#5485 <https://github.com/randombit/botan/issues/5485>`__,
  `#5492 <https://github.com/randombit/botan/issues/5492>`__).

* Improve performance of the AVX512 implementation of SHA-512, especially for
  Clang (`#5490 <https://github.com/randombit/botan/issues/5490>`__).

* Optimizations for the IDEA modular multiplication
  (`#5484 <https://github.com/randombit/botan/issues/5484>`__).
