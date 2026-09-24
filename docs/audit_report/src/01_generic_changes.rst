Changes Overview
================

In relation to the previously audited version (|botan_git_base_ref|), Botan
|botan_version| brings a large number of extensions of functionality, hardening
measures, and bug fixes. The span between the base revision and the target
revision contains no intermediate upstream release; |botan_version| directly
succeeds |botan_git_base_ref|. The release announces one CVE fix, which is the
most important security update of this release:

- CVE-2026-48057: a bypass of the enforcement of Distinguished Name (DN) name
  constraints during X.509 path validation. The release notes give no pull
  request reference for this item. The upstream security advisory (in
  ``doc/security.rst``) states that the decoding of X.509 distinguished names
  lost relevant structure; this corresponds to the loss of the RDN grouping in
  ``X509_DN``, which was fixed with the DN parsing rework in
  `#5618 <https://github.com/randombit/botan/issues/5618>`__
  (see also the appendix on the review of that pull request).

Besides the CVE, the upstream security advisories for |botan_version| list six
further security fixes without CVE identifier (a blind SSRF during OCSP
processing, a seeding-state bug in ``AutoSeeded_RNG``, an integer overflow in
Scrypt parameter handling on 32-bit platforms, an integer overflow in the FFI
block-size reporting, a NUL-truncation of passwords in the Python bcrypt
binding, and the acceptance of unauthenticated OCSP responses by the
``ocsp_check`` command line utility).

Beyond the security fixes, the main thrust of this release is a broad rework
and hardening of the X.509/PKIX code (DN parsing and comparison, name
constraints, CRL and OCSP handling, key identifier extensions, CRL Distribution
Point and Authority Information Access extensions), a set of stricter input
validation rules for public key operations (RSA signature and ciphertext
lengths, Ed25519 identity encodings, EC domain parameters), and a number of
DTLS 1.2 handshake fixes and TLS policy changes. New functionality comprises
SPAKE2+ (RFC 9383), PKCS #12, GCM-SIV (RFC 8452), the RFC 9608 "No Revocation
Available" extension, and several new optimized implementations
(Salsa20, Streebog, ZFEC, SM4). Furthermore, the SM4 key schedule was converted
to constant-time code. Of particular relevance for the audited configuration,
the BSI module policy was reduced by two modules: finite field DSA and the ISO
9796-2 signature padding are no longer part of the BSI build (see
`Changes to the BSI Module Policy`_ below).

The following overview is derived from the official Botan release notes and
groups the changes into security relevant fixes, other fixes, and additions of
new features. A per-patch classification with the associated auditors is found
in the detailed change tables (see :ref:`changes`).


Security Relevant Fixes
-----------------------

This section lists the fixes of actual vulnerabilities, i.e. defects that
allowed an attacker to bypass a security check, corrupt memory, cause a denial
of service, or that led to cryptographically wrong results. Fixes of a purely
hardening or compliance nature are listed under "Other Fixes".

* CVE-2026-48057: bypass of DN name constraint enforcement. The decoding of
  X.509 distinguished names lost the grouping of attributes into relative
  distinguished names, so that a DN could be constructed which passed a name
  constraint check it should have failed. Not referenced by a dedicated pull
  request in the release notes; addressed by the DN parsing rework in
  `#5618 <https://github.com/randombit/botan/issues/5618>`__.

* Blind server-side request forgery during OCSP request processing. The OCSP
  HTTP client followed a single redirect, so a malicious OCSP responder or
  network attacker could cause the application to perform a bodyless GET
  request to an internal service; the response was not available to the
  attacker (`#5815 <https://github.com/randombit/botan/issues/5815>`__).

* ``AutoSeeded_RNG`` could be reinitialized from predictable data: calling
  ``clear`` followed by ``randomize`` into an empty buffer marked the RNG as
  seeded without consulting the configured entropy sources. On platforms
  without a system RNG the resulting state was derived only from a clock value
  and the process ID
  (`#5838 <https://github.com/randombit/botan/issues/5838>`__,
  `#5839 <https://github.com/randombit/botan/issues/5839>`__).

* Heap overflow in Scrypt on 32-bit platforms: an unchecked multiplication in
  the parameter handling led to an undersized buffer, with approximately 4 GB
  of output written past its end when hostile parameters were supplied, for
  example via a malicious encrypted private key
  (`#5629 <https://github.com/randombit/botan/issues/5629>`__,
  `#5820 <https://github.com/randombit/botan/issues/5820>`__).

* Integer overflow in the FFI function ``botan_block_cipher_block_size``,
  which reported the block size as ``int``; with the variable length block
  cipher Lion and attacker-controlled cipher specifiers this could lead to
  memory corruption when using the raw block cipher (ECB) FFI APIs
  (`#5805 <https://github.com/randombit/botan/issues/5805>`__).

* Python binding: data passed to the signing API was silently truncated due
  to a confusion of Unicode code points and byte counts, so that only a prefix
  of the intended message was signed
  (`#5807 <https://github.com/randombit/botan/issues/5807>`__); strings
  containing NUL characters were truncated at the C string boundary, which in
  the ``bcrypt`` and ``check_bcrypt`` functions allowed bypassing application
  password policies with a weaker equivalent password
  (`#5814 <https://github.com/randombit/botan/issues/5814>`__).

* The ``ocsp_check`` command line utility accepted OCSP responses without
  verifying their signature or authorizing the signer, so a malicious responder
  or network attacker could return an accepted "good" response for a revoked
  certificate (`#5825 <https://github.com/randombit/botan/issues/5825>`__;
  not referenced in the release notes, listed in the upstream advisories).

* A delegated OCSP responder certificate was accepted based on DN equality
  with the CA rather than on being signed by the CA's key, as required by
  RFC 6960. Wherever two CA keys share a subject DN (key rollover, cross
  signing, an unrelated trusted hierarchy with the same name), the holder of
  the other key could produce accepted OCSP responses, including "good"
  answers for revoked certificates. In the same pull request, critical name
  constraints of a form Botan cannot evaluate were previously silently ignored
  and now fail closed
  (`#5593 <https://github.com/randombit/botan/issues/5593>`__).

* URI and email address name constraints were previously not evaluated at all
  during path validation and are now enforced
  (`#5598 <https://github.com/randombit/botan/issues/5598>`__).

* By default OCSP no longer accepts soft-fail conditions: previously an
  unreachable responder or a certificate without an OCSP URL satisfied a
  configured revocation requirement, so an attacker able to block the OCSP
  connection could disable revocation checking
  (`#5785 <https://github.com/randombit/botan/issues/5785>`__,
  `#5804 <https://github.com/randombit/botan/issues/5804>`__).

* Denial of service in certificate path building: the work limit of the path
  search was reset on every call, so the total effort grew with the number of
  candidate paths, and an attacker supplying many intermediate certificates
  could cause excessive CPU consumption. Iteration limits were added to the
  path building functions
  (`#5633 <https://github.com/randombit/botan/issues/5633>`__,
  `#5698 <https://github.com/randombit/botan/issues/5698>`__).

* TLS 1.2 sessions that were terminated with a fatal alert remained resumable,
  contrary to RFC 5246; ticket-based sessions and the freshly negotiated
  resumption handle were not invalidated
  (`#5810 <https://github.com/randombit/botan/issues/5810>`__).

* DTLS 1.2 servers now require the cookie exchange bound to the peer address,
  unless the application explicitly opts out, closing the use of the server as
  an amplification vector for spoofed handshake requests
  (`#5792 <https://github.com/randombit/botan/issues/5792>`__).

* Diffie-Hellman accepted the peer public value p-1, the generator of the
  order-2 subgroup. Such a value confines the shared secret to two values and
  leaks the parity of the victim's private exponent; the accepted range is now
  2 <= y <= p-2 as required by NIST SP 800-56A
  (`#5581 <https://github.com/randombit/botan/issues/5581>`__).

* Memory corruption and wrong-arithmetic defects in the multiprecision layer:
  ``BigInt`` left shift computed the result size with a wrapping addition, so
  a hostile shift count produced an out-of-bounds heap write
  (`#5586 <https://github.com/randombit/botan/issues/5586>`__); the P-521
  field reduction missed the value equal to the modulus, several inline
  assembly blocks lacked ``volatile`` or ``"memory"`` clobbers and could be
  miscompiled into silently wrong results, a ``BigInt`` self-assignment and a
  shrinking resize produced wrong values, and a carry could be dropped in a
  constant-time conditional addition
  (`#5592 <https://github.com/randombit/botan/issues/5592>`__); the
  ``pcurves`` backend accepted an off-curve generator for explicitly specified
  EC domain parameters, and ``verify_group`` skipped the base point checks in
  builds without the legacy EC backend, enabling invalid-curve attacks against
  applications that load untrusted domain parameters
  (`#5588 <https://github.com/randombit/botan/issues/5588>`__); division with
  two negative operands returned a wrong quotient
  (`#5585 <https://github.com/randombit/botan/issues/5585>`__).

* One-time key reuse in stateful hash-based signatures: an exhausted XMSS or
  LMS key would eventually wrap its counter and reuse a leaf, and a corrupted
  HSS-LMS private key with an out-of-range index was accepted and reused leaf
  zero on the second signing attempt
  (`#5662 <https://github.com/randombit/botan/issues/5662>`__). The stateful
  key index now detects ``fork`` and refuses to issue further indices, since
  both processes would otherwise sign with the same one-time key
  (`#5723 <https://github.com/randombit/botan/issues/5723>`__).

* The CTR mode counter could wrap around, leading to keystream reuse, and
  stream ciphers could seek or read past the defined keystream
  (`#5628 <https://github.com/randombit/botan/issues/5628>`__). Message
  authentication code objects failed to reset their state when ``start`` was
  called a second time or when the object was re-keyed
  (`#5672 <https://github.com/randombit/botan/issues/5672>`__). Related
  state transition errors in cipher modes were fixed in
  `#5610 <https://github.com/randombit/botan/issues/5610>`__.


Other Fixes
-----------

Hardening and compliance fixes without an associated vulnerability:

* Reject RSA signature and ciphertext values which are not exactly the length
  of the modulus, as required by RFC 8017
  (`#5592 <https://github.com/randombit/botan/issues/5592>`__,
  `#5630 <https://github.com/randombit/botan/issues/5630>`__,
  `#5675 <https://github.com/randombit/botan/issues/5675>`__).

* Fix several bugs in ISO 9796-2 signature verification, and deprecate the
  ``iso9796`` module. The verifier accepted either trailer format regardless
  of the configured implicit/explicit mode, and it rejected roughly one in 128
  valid signatures due to mishandling of leading zero bytes in the recovered
  message representative. Since the verifier always uses its configured hash,
  the trailer confusion did not enable a hash substitution. The module is
  removed from the BSI module policy
  (`#5680 <https://github.com/randombit/botan/issues/5680>`__).

* In Ed25519 verification also reject the non-canonical encoding of the
  identity element, as required by RFC 8032. This only matters where a
  signature under an attacker-supplied public key is given meaning
  (`#5731 <https://github.com/randombit/botan/issues/5731>`__).

* When decoding an HSS public key reject L = 0
  (`#5666 <https://github.com/randombit/botan/issues/5666>`__).

* Improve input validation in the McEliece implementations, and avoid using
  ``bool`` for secret data in Classic McEliece
  (`#5667 <https://github.com/randombit/botan/issues/5667>`__,
  `#5676 <https://github.com/randombit/botan/issues/5676>`__).

* The hash to curve and hash to scalar functions now enforce RFC 9380's rules
  on hash function security
  (`#5758 <https://github.com/randombit/botan/issues/5758>`__).

* Various further BigInt and number-theoretic hardening
  (`#5650 <https://github.com/randombit/botan/issues/5650>`__,
  `#5688 <https://github.com/randombit/botan/issues/5688>`__).

* Various X509/PKIX hardenings, optimizations, bug fixes, and additional sanity
  checks, such as restricting the OCSP nocheck extension to responder
  certificates, rejecting extensions in objects for which they are not
  defined, and stricter parsing of algorithm identifiers and dates
  (`#5605 <https://github.com/randombit/botan/issues/5605>`__,
  `#5611 <https://github.com/randombit/botan/issues/5611>`__,
  `#5637 <https://github.com/randombit/botan/issues/5637>`__,
  `#5643 <https://github.com/randombit/botan/issues/5643>`__,
  `#5660 <https://github.com/randombit/botan/issues/5660>`__,
  `#5668 <https://github.com/randombit/botan/issues/5668>`__,
  `#5670 <https://github.com/randombit/botan/issues/5670>`__,
  `#5682 <https://github.com/randombit/botan/issues/5682>`__,
  `#5685 <https://github.com/randombit/botan/issues/5685>`__,
  `#5689 <https://github.com/randombit/botan/issues/5689>`__).

* Various ASN.1 hardening and decoder strictness improvements
  (`#5693 <https://github.com/randombit/botan/issues/5693>`__,
  `#5703 <https://github.com/randombit/botan/issues/5703>`__,
  `#5710 <https://github.com/randombit/botan/issues/5710>`__,
  `#5720 <https://github.com/randombit/botan/issues/5720>`__).

* During path validation, by default require that OCSP responses are no more
  than seven days old
  (`#5623 <https://github.com/randombit/botan/issues/5623>`__).

* The default policy for TLS no longer lists finite field Diffie-Hellman
  (`#5782 <https://github.com/randombit/botan/issues/5782>`__).

* TLS 1.3 handshake hardening and various minor TLS fixes
  (`#5664 <https://github.com/randombit/botan/issues/5664>`__,
  `#5721 <https://github.com/randombit/botan/issues/5721>`__,
  `#5767 <https://github.com/randombit/botan/issues/5767>`__).

* Fix DTLS 1.2 handshake edge cases, including pacing of repeated timeout
  checks, replay of final flights after local activation, partial server-flight
  delivery, and delayed server-side flight handling
  (`#2310 <https://github.com/randombit/botan/issues/2310>`__,
  `#2498 <https://github.com/randombit/botan/issues/2498>`__,
  `#4022 <https://github.com/randombit/botan/issues/4022>`__,
  `#4036 <https://github.com/randombit/botan/issues/4036>`__,
  `#5696 <https://github.com/randombit/botan/issues/5696>`__,
  `#5790 <https://github.com/randombit/botan/issues/5790>`__,
  `#5791 <https://github.com/randombit/botan/issues/5791>`__,
  `#5793 <https://github.com/randombit/botan/issues/5793>`__,
  `#5800 <https://github.com/randombit/botan/issues/5800>`__,
  `#5801 <https://github.com/randombit/botan/issues/5801>`__,
  `#5802 <https://github.com/randombit/botan/issues/5802>`__,
  `#5803 <https://github.com/randombit/botan/issues/5803>`__,
  `#5811 <https://github.com/randombit/botan/issues/5811>`__,
  `#5829 <https://github.com/randombit/botan/issues/5829>`__,
  `#5834 <https://github.com/randombit/botan/issues/5834>`__,
  `#5835 <https://github.com/randombit/botan/issues/5835>`__,
  `#5836 <https://github.com/randombit/botan/issues/5836>`__).

* Fix various further edge case bugs in AEAD, cipher mode, stream cipher,
  MAC, and KDF implementations
  (`#5642 <https://github.com/randombit/botan/issues/5642>`__,
  `#5659 <https://github.com/randombit/botan/issues/5659>`__,
  `#5665 <https://github.com/randombit/botan/issues/5665>`__,
  `#5674 <https://github.com/randombit/botan/issues/5674>`__,
  `#5742 <https://github.com/randombit/botan/issues/5742>`__,
  `#5743 <https://github.com/randombit/botan/issues/5743>`__).

* Improve OCSP request and response serialization
  (`#5678 <https://github.com/randombit/botan/issues/5678>`__,
  `#5741 <https://github.com/randombit/botan/issues/5741>`__).

* Improve handling of the authority and subject key identifier extensions
  (`#5735 <https://github.com/randombit/botan/issues/5735>`__,
  `#5737 <https://github.com/randombit/botan/issues/5737>`__).

* Properly decode and handle the X.509 CRL Distribution Point and Authority
  Information Access extensions
  (`#5712 <https://github.com/randombit/botan/issues/5712>`__).

* Improve CRL decoding and encoding, including support for CRL numbers larger
  than 32 bits
  (`#5687 <https://github.com/randombit/botan/issues/5687>`__,
  `#5694 <https://github.com/randombit/botan/issues/5694>`__,
  `#5697 <https://github.com/randombit/botan/issues/5697>`__).

* Improve the HTTP 1.0 client used for OCSP and CRL fetching
  (`#5609 <https://github.com/randombit/botan/issues/5609>`__).

* Various fixes and improvements for SLH-DSA
  (`#5730 <https://github.com/randombit/botan/issues/5730>`__).

* Various fixes for SM2 signatures and encryption
  (`#5713 <https://github.com/randombit/botan/issues/5713>`__).

* Fix various bugs in the PKCS #11 wrapper
  (`#5602 <https://github.com/randombit/botan/issues/5602>`__).

* Fix various bugs in the Pipe/Filter library
  (`#5724 <https://github.com/randombit/botan/issues/5724>`__,
  `#5809 <https://github.com/randombit/botan/issues/5809>`__).

* Fix several issues in the compression wrappers
  (`#5733 <https://github.com/randombit/botan/issues/5733>`__).

* Fix further errors in the Python binding
  (`#5722 <https://github.com/randombit/botan/issues/5722>`__,
  `#5796 <https://github.com/randombit/botan/issues/5796>`__).

* Add missing, or correct erroneous, documentation comments in many headers
  (`#5760 <https://github.com/randombit/botan/issues/5760>`__,
  `#5761 <https://github.com/randombit/botan/issues/5761>`__,
  `#5762 <https://github.com/randombit/botan/issues/5762>`__,
  `#5763 <https://github.com/randombit/botan/issues/5763>`__,
  `#5764 <https://github.com/randombit/botan/issues/5764>`__,
  `#5766 <https://github.com/randombit/botan/issues/5766>`__,
  `#5774 <https://github.com/randombit/botan/issues/5774>`__).

* On MSVC, deprecation warnings now include the file and line number
  (`#5749 <https://github.com/randombit/botan/issues/5749>`__).

* Upgrade to TLS-Anvil 1.5
  (`#5630 <https://github.com/randombit/botan/issues/5630>`__).


Changes to the BSI Module Policy
--------------------------------

The audited configuration is built with the BSI module policy
(``src/build-data/policy/bsi.txt``). Two modules were removed from that policy
in this release; neither change is mentioned in the release notes.

* The finite field ``dsa`` module is removed from the BSI policy. DSA had
  already been documented as deprecated in |botan_git_base_ref| (the
  deprecation notice states that finite field DSA is slow, rarely used, and no
  longer approved by NIST), but the module itself lacked the deprecation
  annotation and was still listed among the recommended signature algorithms
  of the policy. The pull request aligns the module annotations with the
  documented deprecations and comments ``dsa`` out of the policy file
  (`#5780 <https://github.com/randombit/botan/issues/5780>`__). As a
  consequence, DSA is no longer available in the audited build.

* The ``iso9796`` module (ISO 9796-2 DS2/DS3 RSA signature padding) is
  deprecated and removed from the BSI policy together with the verification
  fixes described under "Other Fixes"
  (`#5680 <https://github.com/randombit/botan/issues/5680>`__).


New Features and Additions
--------------------------

New and refactored X.509 / PKIX functionality:

* Add ``DNSName``, ``URI``, and ``EmailAddress`` types
  (`#5598 <https://github.com/randombit/botan/issues/5598>`__,
  `#5601 <https://github.com/randombit/botan/issues/5601>`__,
  `#5622 <https://github.com/randombit/botan/issues/5622>`__,
  `#5663 <https://github.com/randombit/botan/issues/5663>`__,
  `#5683 <https://github.com/randombit/botan/issues/5683>`__,
  `#5750 <https://github.com/randombit/botan/issues/5750>`__).

* Add ``X509_DN::parse`` and improve the parsing and printing of Distinguished
  Name strings, including capturing RDN groupings and escaping control
  characters
  (`#5618 <https://github.com/randombit/botan/issues/5618>`__,
  `#5657 <https://github.com/randombit/botan/issues/5657>`__,
  `#5658 <https://github.com/randombit/botan/issues/5658>`__).

* Optimize ``X509_DN`` comparison and name constraint checks using precomputed
  canonical encodings
  (`#5652 <https://github.com/randombit/botan/issues/5652>`__).

* Add support for encoding name constraint extensions
  (`#5734 <https://github.com/randombit/botan/issues/5734>`__).

* Add support for the RFC 9608 No Revocation Available extension
  (`#5595 <https://github.com/randombit/botan/issues/5595>`__).

* Add an explicit ``X509_Serial_Number`` type
  (`#5740 <https://github.com/randombit/botan/issues/5740>`__).

* Add support for PKCS #12
  (`#5478 <https://github.com/randombit/botan/issues/5478>`__,
  `#5625 <https://github.com/randombit/botan/issues/5625>`__).

* Add support for parsing EC keys which contain the ECC domain parameters
  within the key rather than in the algorithm identifier
  (`#5532 <https://github.com/randombit/botan/issues/5532>`__).

New algorithms and public key functionality:

* Add support for SPAKE2+ from RFC 9383
  (`#5711 <https://github.com/randombit/botan/issues/5711>`__).

* Add support for GCM-SIV from RFC 8452
  (`#5770 <https://github.com/randombit/botan/issues/5770>`__).

* Introduce ``PK_Decryptor::ciphertext_length``
  (`#5717 <https://github.com/randombit/botan/issues/5717>`__).

* Add hash to curve support for brainpool256r1, brainpool384r1, brainpool512r1,
  and numsp512d1
  (`#5754 <https://github.com/randombit/botan/issues/5754>`__).

* Extend Blowfish to support keys up to 72 bytes in length
  (`#5714 <https://github.com/randombit/botan/issues/5714>`__).

* Add ``HashFunction::security_level``
  (`#5746 <https://github.com/randombit/botan/issues/5746>`__).

TLS:

* In the default TLS policy, prefer ECDSA over RSA signatures
  (`#5727 <https://github.com/randombit/botan/issues/5727>`__).

* Add support for the Brainpool ECDH/ECDSA groups in TLS 1.3 as specified in
  RFC 8734
  (`#5691 <https://github.com/randombit/botan/issues/5691>`__,
  `#5771 <https://github.com/randombit/botan/issues/5771>`__,
  `#5772 <https://github.com/randombit/botan/issues/5772>`__).

* Add ``TLS::Policy::record_padding_bytes``, which allows padding TLS 1.3
  records, for example out to a minimum plaintext size or to a multiple of some
  block size
  (`#5752 <https://github.com/randombit/botan/issues/5752>`__,
  `#5843 <https://github.com/randombit/botan/issues/5843>`__).

APIs, bindings, and build system:

* Improve the ``Database`` abstraction type, make it easier to support
  databases other than SQLite, and validate SQL table names
  (`#5607 <https://github.com/randombit/botan/issues/5607>`__,
  `#5673 <https://github.com/randombit/botan/issues/5673>`__).

* Add getters for the RFC 3779 extensions to the FFI interface and Python
  binding
  (`#5491 <https://github.com/randombit/botan/issues/5491>`__).

* Add ``PublicKey.load_x25519`` and ``PublicKey.load_x448`` to the Python
  binding
  (`#5748 <https://github.com/randombit/botan/issues/5748>`__).

* The Python binding documentation is now generated from the docstrings in
  ``botan3.py`` using Sphinx
  (`#5233 <https://github.com/randombit/botan/issues/5233>`__,
  `#5765 <https://github.com/randombit/botan/issues/5765>`__).

New optimized and constant-time algorithm implementations:

* Convert the SM4 key schedule to constant time code, including the hardware
  AES based variant
  (`#5638 <https://github.com/randombit/botan/issues/5638>`__,
  `#5639 <https://github.com/randombit/botan/issues/5639>`__).

* Add an AVX-512/GFNI implementation of the Streebog compression function
  (`#5655 <https://github.com/randombit/botan/issues/5655>`__).

* Add optimized Salsa20 implementations using 128-bit SIMD (SSSE3, NEON),
  AVX2, and AVX-512
  (`#5759 <https://github.com/randombit/botan/issues/5759>`__).

* Add an AVX-512/GFNI implementation of ZFEC, and optimize the existing vperm
  code
  (`#5747 <https://github.com/randombit/botan/issues/5747>`__).
