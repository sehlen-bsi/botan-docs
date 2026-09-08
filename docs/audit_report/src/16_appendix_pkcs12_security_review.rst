Appendix: Security Review and Test Campaign for the PKCS#12 Implementation
==========================================================================


The review in this section was written by Anthropic's Fable 5 model under the
direction of the auditor. Please treat it with care as appropriate for AI
generated content. All measurements quoted below were produced by the test
programs described in :ref:`pkcs12-review-tests`, which are archived with the
report.

**Subject:** the PKCS#12/PFX support added in Botan 3.13.0 by
`#5478 <https://github.com/randombit/botan/pull/5478>`__ (PKCS#12 KDF) and
`#5625 <https://github.com/randombit/botan/pull/5625>`__ (parser, exporter,
PBE schemes, CLI). Modules ``pkcs12``, ``pkcs12_pbe`` and ``pkcs12_kdf``;
reviewed at tag ``3.13.0`` and cross-checked against upstream ``master``
(commit ``9bce628ff``, 2026-09-06), which additionally contains
`#5902 <https://github.com/randombit/botan/pull/5902>`__ (``mac_protected()``
accessor).

This appendix complements the static review of PR #5625 in the appendix on
that pull request (findings F1 to F8 there). It goes deeper into the parser's
state handling, the parameter space of the exporter, the behaviour under
hostile input, interoperability, and the correctness of the reference
documentation. Findings below are numbered P1 to P9 to keep them apart from
F1 to F8.

Method
------

Four instruments were used:

1. **Source review** of ``src/lib/pkcs12/pkcs12.{h,cpp}``,
   ``src/lib/pkcs12/pkcs12_pbe/``, ``src/lib/pbkdf/pkcs12_kdf/`` and the
   relevant parts of ``pbes2``, ``cbc``, ``ecc_key`` and ``ber_dec``.
2. **A new test suite** (``test_pkcs12_audit.cpp``, 27 test groups, about
   280 assertions plus measurement notes) which builds PFX structures by hand
   with Botan's DER encoder so that every structural variant can be produced
   deliberately, and which contains an independent re-implementation of the
   RFC 7292 Appendix B password based encryption for cross-checking. The
   suite was run against a clean build of tag ``3.13.0`` and of ``master``;
   all assertions pass on both.
3. **An interoperability matrix** against OpenSSL 3.6.3 in both directions
   (338 cases; 334 pass, 4 expected failures for the RC2-40 legacy cipher
   which Botan deliberately does not implement).
4. **A stand-alone demonstration program** for the resource consumption an
   attacker-supplied file can impose (finding P1).

Summary
-------

No memory-safety defect, no key-recovery weakness and no way to bypass the
integrity MAC when it is present were found. Over 4,182 single-bit
modifications and 2,091 truncations of MAC-protected files, every single
change was rejected, and every rejection surfaced as one of the two documented
exception types. The KDF, the two legacy PBE schemes, the empty-password
conventions and all supported MAC digests interoperate with OpenSSL for
empty, short, non-ASCII and over-block-length passwords.

The substantive results concern the situation *without* a MAC, which the
format allows and the parser accepts silently (F1 of the PR #5625 appendix,
now mitigated on ``master`` by the ``mac_protected()`` accessor from #5902):

- **P1 (Low):** a 196-byte PFX file forces an 8 GiB allocation and
  13 seconds of CPU in the parser through PBES2/scrypt parameters that pass
  Botan's validation. No documented limit of Botan is violated by this;
  it is a resource-exhaustion exposure of the class the maintainer already
  considers inherent, but with a memory dimension that peers such as
  OpenSSL bound far more tightly.
- **P2 (Medium, format inherent):** in a MAC-less file, single-bit changes to
  the encrypted private key can yield a *silently altered private key that
  still matches the end-entity certificate*, because the EC key decoder takes
  the public point from the PKCS#8 structure without checking it against the
  scalar. Only ``check_key()`` detects this.

The remaining findings are robustness and documentation issues. The reference
documentation contains several factual errors (section
:ref:`pkcs12-review-docs`), the most consequential being a wrong iteration
limit and a wrong description of when export fails.

Findings
--------

P1 (Low) — Memory exhaustion through PBES2/scrypt parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PKCS#12 delegates ``PBE-PKCS5v20`` (PBES2) content to the generic PBES2
decoder (``pkcs12_pbe.cpp:98-102``), which accepts PBKDF2 and scrypt as key
derivation functions. For scrypt, ``Pbes2ScryptParameters::validate_params``
(``pbes2.cpp:269-290``) bounds ``N <= 2^22``, ``r <= 64``, ``p < 1024`` and
the product ``N*r*p <= 2^26``; this product is documented as aligning with
the 10\ :sup:`8` iteration cap of PBKDF2 and the PKCS#12 KDF. The memory
consumption of scrypt, however, is ``128 * r * (N + 1)`` bytes
(``scrypt.cpp:246-249``), which the work bound does not constrain: the
parameters ``N = 2^22, r = 16, p = 1`` pass validation and require 8 GiB.
The scrypt implementation itself refuses parameter sets above
``MAX_SCRYPT_MEMORY_GB`` (8 GiB on 64-bit, 2 GiB on 32-bit platforms,
``scrypt.cpp:25-27, 168-172``); that limit is meant for the library's own
tuner and is the only memory bound on the decode path, so an untrusted file
can drive the parser to exactly that ceiling.

The demonstration program ``scrypt_demo.cpp`` builds a MAC-less PFX with a
single ``PKCS8ShroudedKeyBag`` (32 bytes of arbitrary ciphertext) carrying
those parameters and parses it with an arbitrary password:

.. code-block:: text

   PFX size: 196 bytes; scrypt N=2^20 r=8  p=1 -> 1 GiB:  elapsed 2.5 s,  peak RSS 1.01 GiB
   PFX size: 196 bytes; scrypt N=2^22 r=16 p=1 -> 8 GiB:  elapsed 13.3 s, peak RSS 8.01 GiB
   PFX size: 197 bytes; scrypt N=2^23 r=8  p=1         -> rejected immediately (N too large)

The password is irrelevant: the KDF runs to completion before the (wrong)
key is used for decryption. The precondition is only that the parser reaches
the bag, i.e. the file has no MAC, or the MAC was computed with a password
the victim will enter (for example the empty password used by many
truststores, or a password the attacker chose and communicated with the
file). The same structure applies to PKCS#8 ``EncryptedPrivateKeyInfo``
loading outside PKCS#12; the PKCS#12 import path merely widens the exposure,
since bundles are routinely received from third parties. On a 32-bit or
memory-constrained system the allocation fails with ``std::bad_alloc`` or the
process is killed; on a server the request occupies gigabytes for tens of
seconds. Several bags in one file multiply the effect sequentially.

CPU cost is additive as well: the test suite measured 21 ms for one valid
shrouded key bag with 200,000 PKCS#12 KDF iterations and 63 ms for three
such bags, confirming the per-bag accumulation described as F3 in the
PR #5625 appendix. All per-operation caps were confirmed to be enforced
before any work is done (10\ :sup:`8`\ +1 iterations, ``N = 2^23``,
``N*r*p > 2^26``, ``r = 65``, ``p = 1024`` and non-power-of-two ``N`` are
all rejected within a millisecond).

Assessment. This does not violate any limit Botan states: the threat model
document addresses side channels only, the ``max_memory_usage_mb`` option of
the password hash API is documented as a tuning-time choice for the
*producer* of parameters, and the PBES2 code comment only claims alignment
of the scrypt *work* bound with the PBKDF2 iteration cap, which holds in CPU
terms (about 13 s either way). The CPU aspect was raised in
`#5894 <https://github.com/randombit/botan/issues/5894>`__; the maintainer
regards a decryption cost budget as "somewhat unavoidable" without a policy
mechanism and opened
`#5914 <https://github.com/randombit/botan/issues/5914>`__ for it. What
justifies recording P1 separately, at low severity, is that memory differs
from CPU: an 8 GiB request on a constrained host invokes the out-of-memory
killer rather than costing a bounded delay, Botan's own advisories treat
resource exhaustion from attacker-supplied ASN.1 (CVE-2026-44378,
CVE-2024-34702) and "decrypting a malicious private key" (the 3.13.0 Scrypt
advisory) as in scope, and OpenSSL's ``EVP_PBE_scrypt`` applies a 32 MiB
default memory cap on the same decode path, so the same file is rejected
there. A decode-side memory bound is also far simpler and less
interoperability-sensitive than a general CPU budget, because no legitimate
producer emits such parameters.

Recommendation: bound the scrypt memory in ``validate_params`` for the
decode path, independently of the work bound and far below the 8 GiB
implementation ceiling (for example ``128 * r * N <= 256 MiB``, which still
admits Botan's own defaults of ``N = 32768, r = 8``, i.e. 32 MiB); in the
longer term the budget mechanism of #5914. Applications must treat PKCS#12 import
as an expensive, attacker-influenced operation and should reject MAC-less
files (``mac_protected() == false`` on Botan 3.14).

P2 (Medium, format inherent) — Silent private key alteration in MAC-less files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Without a MAC the shrouded key is protected by unauthenticated CBC only (F2
in the PR #5625 appendix). The test suite flipped every bit of the first
byte of every ciphertext byte position of an exported ECDSA P-256 key
(144 modifications per scheme) and classified the outcome:

.. list-table::
   :header-rows: 1
   :widths: 30 20 20 30

   * - Key encryption
     - Rejections
     - Silently altered key
     - ... still matching the end-entity cert
   * - PBE-SHA1-3DES
     - 124 (8 distinct error messages)
     - 20
     - 20
   * - PBES2-SHA256-AES256
     - 140 (8 distinct error messages)
     - 4
     - 4

A "silently altered key" means the modified file parsed without any
exception and returned an ECDSA private key whose scalar differs from the
original. This happens when the garbled CBC block and the flipped bit both
fall inside the 32-byte private scalar of the ``ECPrivateKey`` structure. In
all 24 cases ``end_entity_certificate()`` still returned the matching
certificate, because ``EC_PrivateKey``'s PKCS#8 constructor
(``ecc_key.cpp:188-230``) takes the public point from the optional
``publicKey [1]`` field verbatim and does not verify that it equals
``scalar * G``. The parsed object therefore carries a public key that does
not belong to its private key. ``check_key(rng, false)`` detects every one of
the 24 cases; nothing else in the API does. The test then uses each altered
key through the ordinary signing API: ``PK_Signer`` accepts all 24 keys and
produces a signature without any error (ECDSA signing reads only the group
and the scalar, ``ecdsa.cpp:129-133``), and none of these signatures verifies
under the certificate's public key or under the key object's own public
point.

The attacker does not learn the key (the garbled block is the decryption of
an attacker-unknown value), so this is not a key-recovery attack. It is a
fault-injection primitive: an application that imports a MAC-less bundle
and signs with the key produces signatures that do not verify under its
certificate, without any error at import time. Combined with F1 (silent MAC
stripping) the precondition is a bundle the attacker can modify in transit or
at rest, and a victim that supplies the correct password.

The eight distinct error messages per scheme (CBC padding, several BER
decoder errors, "Failed to deserialize elliptic curve point", PEM and OID
errors) are the padding-oracle side of F2; they are visible to a caller that
reports ``what()`` back to the party controlling the file.

Recommendations: (a) upstream, verify scalar/point consistency when both are
present in an ``ECPrivateKey`` (one fixed-base multiplication, negligible
against the KDF), or at least call ``check_key`` on keys parsed from
MAC-less PKCS#12 files; (b) applications should reject MAC-less files, and
otherwise call ``check_key`` on every imported key; (c) treat all import
failures uniformly towards the party that supplied the file.

P3 (Low, hygiene) — Plaintext private key in a non-zeroizing buffer on the legacy export path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``pkcs12_pbe_encrypt`` (``pkcs12_pbe.cpp:159-160``) copies the plaintext
into ``std::vector<uint8_t> ciphertext`` and encrypts in place with
``cipher->finish(ciphertext)``. For non-``secure_vector`` buffers,
``Cipher_Mode::finish`` (``cipher_mode.h:197-203``) copies the buffer into a
temporary ``secure_vector``, encrypts, and then calls ``resize`` on the
original vector; PKCS#7 padding always enlarges the buffer, so the resize
reallocates and the original block, still holding the plaintext PKCS#8
``PrivateKeyInfo``, is freed without scrubbing. The PBES2 path is not
affected (``pbes2_encrypt_shared`` works on a ``secure_vector``). This is the
export-side counterpart of F4 (parse side, unencrypted ``KeyBag``); it is
reached with ``legacy_compat()`` or any ``PBE-SHA1-3DES`` / ``PBE-SHA1-2DES``
key encryption, i.e. exactly the modes recommended for interoperability with
old software. The maintainer considered F4 academic; the export case is
somewhat stronger since the key is *not* otherwise on disk in plaintext.
Fix: make ``ciphertext`` a ``secure_vector`` (and ``unlock`` it on return).

P4 (Low) — End-entity ordering trusts the unauthenticated ``localKeyId`` over the key match
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When ordering certificates after parsing, the ``localKeyId`` attribute of
the first key is matched against the certificates' attributes *before* the
``subjectPublicKeyInfo`` comparison is tried (``pkcs12.cpp:547-573``). With
a crafted file in which the key's ``localKeyId`` equals that of a CA
certificate while the SPKI matches a different certificate, the test suite
observed:

- ``certificates().front()`` is the CA certificate (attribute match), while
- ``end_entity_certificate()`` returns the SPKI-matching certificate,
- ``ca_certificates()`` returns the CA certificate (consistent with the
  previous point), and
- ``friendly_name()`` is taken from the attribute-matched CA certificate.

The reference documentation states that the end-entity certificate "comes
first when produced by parsing"; a caller relying on that (rather than on
``end_entity_certificate()``) receives the wrong certificate. Without a MAC
this is attacker-controllable without the password; with a MAC only the
password holder can produce such a file. Recommendation: use the
``localKeyId`` only to disambiguate between SPKI-matching certificates, and
correct the documentation.

P5 (Info) — Inconsistent treatment of passwords outside the Basic Multilingual Plane
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The PKCS#12 KDF encodes the password as UCS-2, so ``utf8_to_ucs2`` throws
``Decoding_Error`` for code points above U+FFFF (``charset.cpp:144-146``)
and for invalid UTF-8. Consequently an export with such a password fails
whenever the MAC or a legacy PBE scheme is used, but *succeeds* for a
MAC-less PBES2 file, because PBKDF2 consumes the raw UTF-8 bytes. The
resulting file is readable by Botan; its interoperability with other
implementations (OpenSSL converts to UTF-16 with surrogate pairs) is
doubtful. Parsing a MAC-protected file with such a password also reports a
``Decoding_Error`` rather than an authentication failure. Recommendation:
reject non-BMP and invalid-UTF-8 passwords uniformly at the API boundary
with ``Invalid_Argument``.

P6 (Info) — Fields outside the MAC and encoding leniency
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The MAC covers only the ``authSafe`` content (as the format prescribes).
The bit-flip sweep of a MAC-protected legacy file found exactly one
accepted modification: byte 13 of the ``MacData`` structure, which turns the
``NULL`` parameter of the SHA-1 ``AlgorithmIdentifier`` into an empty
``OCTET STRING``; the digest OID is unchanged and verification succeeds.
Related observations without security impact: an indefinite-length (BER)
encoding of the outer ``PFX`` ``SEQUENCE`` is accepted; an empty MAC salt is
accepted; ``AlgorithmIdentifier`` parameters of the MAC digest are not
validated. All of these are non-canonical encodings an attacker can produce
without the password; none changes the parsed content. For a strict-DER
posture the outer structure could be decoded with
``BER_Decoder::Limits::DER()`` as the PKCS#8 decoder already does.

P7 (Info) — Export validates only the first key, order-dependently
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``export_to`` matches only ``m_private_keys.front()`` against the
certificates (``pkcs12.cpp:695-712``). The suite confirmed: a bundle with
keys ``[A, B]`` and A's certificate exports (B is written without any
attribute), whereas ``[B, A]`` with the same certificate throws
``Invalid_Argument``. A key-only bundle exports without error, contrary to
the header comment and the reference documentation ("requires the
end-entity cert to be present when a key is exported"). Unknown bag types
recorded during parsing are dropped silently on re-export. None of this is a
security issue; it should be documented or made consistent (for example
by matching every key).

P8 (Info) — Behaviour of the empty password and the OpenSSL convention
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The RFC 7292 encoding of the empty password (two zero bytes) and OpenSSL's
non-conforming encoding (empty byte string) were both produced with the
independent re-implementation. The parser accepts files that use either
convention *consistently* (MAC and bags), rejects mixed files, and never
applies the fallback for non-empty passwords. For a MAC-less file only the
RFC encoding is tried (F5 of the PR #5625 appendix); such OpenSSL-produced
files fail to import. The CLI documentation claims ``--no-mac`` is required
with an empty password; neither the library nor the CLI enforces this, and
the interop matrix shows OpenSSL reads Botan's empty-password files with MAC
for all six MAC digests.

P9 — Confirmed positive properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following properties, claimed by the code or its comments, were verified
experimentally:

- **MAC before content.** A file whose MAC is valid but whose content is
  malformed reports ``Invalid_Authentication_Tag`` for a wrong password and
  ``Decoding_Error`` for the right one; a shrouded key bag demanding
  10\ :sup:`8` KDF iterations is never reached with a wrong password.
- **Integrity.** 4,182 single-bit flips (modern and legacy profiles) and
  2,091 truncations of MAC-protected files: no modification accepted, no
  exception type other than ``Invalid_Authentication_Tag`` and
  ``Decoding_Error``, no non-Botan exception, no crash. Appended trailing
  bytes are rejected.
- **Parameter matrix.** 216 combinations of four key encryption schemes,
  three certificate encryption settings, three MAC digests and six password
  shapes (empty, one byte, non-ASCII, 70 bytes, 130 bytes, embedded NUL)
  round-trip with identical key, certificates, chain and friendly name;
  for each, a different password, a prefix and an extension of the password
  are rejected with ``Invalid_Authentication_Tag``.
- **Randomness.** Repeated exports of the same bundle differ in every salt
  and IV; all PBE salts within one file (three keys plus encrypted
  certificates) are distinct.
- **KDF contract.** ``PKCS12-KDF`` via ``PasswordHashFamily`` applies the
  RFC 7292 encoding (UCS-2 BE plus two zero bytes); ids 1, 2 and 3 produce
  unrelated outputs; shorter outputs are prefixes of longer ones; ids 0 and
  4 and zero iterations are rejected.
- **Legacy PBE.** Shrouded key bags produced by Botan with ``PBE-SHA1-3DES``
  and ``PBE-SHA1-2DES`` decrypt with the independent re-implementation
  (including the ``K1||K2||K1`` expansion for 2DES), and vice versa.
- **Cost caps** (see P1) are enforced before work; the nesting limit rejects
  exactly the tenth nested ``SafeContentsBag``; 500 sibling bags parse in
  7 ms (linear).
- **Structural strictness.** PFX versions 0, 2 and 4, ``SignedData``
  integrity mode, ``EnvelopedData`` content, ``EncryptedData`` version 1,
  non-``Data`` inner content type, all RFC 7292 Appendix C RC2/RC4 schemes
  and PBES1, MD5 and SHA-3 MAC digests, negative, zero and oversized
  iteration counts, and wrong-length or wrong-digest MAC values are all
  rejected with ``Decoding_Error`` or ``Invalid_Authentication_Tag``.

Interoperability with OpenSSL 3.6.3
-----------------------------------

The script ``interop.sh`` (archived with the report together with its log)
exercises the CLI in both directions with an OpenSSL-generated P-256 key,
end-entity certificate and CA certificate.

.. list-table::
   :header-rows: 1
   :widths: 45 15 40

   * - Direction and variation
     - Result
     - Remarks
   * - Botan export, OpenSSL import: 4 passwords (empty, short, non-ASCII,
       70 bytes) x 4 key ciphers x 3 certificate encryptions x 3 MAC
       digests x iterations {1, 2048}, plus 2 MAC-less files
     - 290 / 290
     - OpenSSL recovers the key and both certificates; the wrong password is
       rejected in every case
   * - OpenSSL export, Botan import: 4 passwords x 12 OpenSSL profiles
       (default, legacy, 3DES, 2DES, AES-128/256, MAC SHA-1/224/384/512,
       ``-iter 1``, ``-nomaciter``, ``-nomac``, 100k iterations)
     - 44 / 48
     - Botan recovers key, chain and friendly name; the 4 failures are the
       ``-legacy`` profile, whose ``PBE-SHA1-RC2-40`` certificate encryption
       Botan rejects by design with a clear error

The 70-byte password exceeds the 64-byte block size of SHA-1 and SHA-256,
which exercises the password-repetition step of the KDF; agreement with
OpenSSL confirms that step and the UCS-2 encoding of the non-ASCII password.

.. _pkcs12-review-docs:

Correctness of the reference documentation
------------------------------------------

``doc/api_ref/pkcs12.rst`` (and the header comments it mirrors) was checked
statement by statement against the code and the test results. Errors found:

1. **Wrong iteration limit.** ``with_iterations`` and ``export_to`` state
   that values above ``PKCS12_MAX_ITERATIONS`` (1 000 000) are rejected. The
   constant is 100 000 000 (``pkcs12_pbe.h:25``); an export with 1 000 001
   iterations succeeds (measured 161 ms). The same figure is wrong for the
   parser, which accepts MAC and bag iteration counts up to 10\ :sup:`8`.
2. **Non-existent public identifiers.** ``PKCS12_MAX_ITERATIONS`` lives in
   the internal header ``pkcs12_pbe.h`` and ``PKCS12_MAX_NESTING`` in an
   anonymous namespace of ``pkcs12.cpp``; neither is available to
   applications, yet both are presented as API constants.
3. **Nesting limit attributed to export.** The ``PKCS12_MAX_NESTING`` rule is
   listed under ``export_to``; it applies only when parsing.
4. **Export failure condition misstated.** ``export_to`` and the header
   comment say the call throws "if a stored private key does not match any
   stored certificate" and that the end-entity certificate is required when
   a key is exported. Only the *first* key is checked, and only if at least
   one certificate is present; key-only bundles and additional unmatched
   keys export without error (P7).
5. **Ordering claim.** ``certificates()`` "the end-entity, if any, comes
   first when produced by parsing" does not hold when the ``localKeyId``
   attributes point elsewhere (P4).
6. **``ca_certificates()``** "for a key-less bundle, returns all
   certificates after the first" also applies to bundles whose key matches
   no certificate.
7. **Exception list of the constructor** is accurate for hostile input
   (confirmed by the sweeps), but a password outside the BMP or with
   invalid UTF-8 produces ``Decoding_Error`` on parse and export alike,
   which readers would not expect (P5).
8. **``with_friendly_name`` / options constructor:** an *empty* friendly
   name passed in the options suppresses the attribute entirely instead of
   falling back to the bundle-level name.
9. **Supported-algorithms table.** ``pbes2``, ``aes`` and ``des`` are listed
   as modules "required" for individual algorithms, but all three are hard
   dependencies of ``pkcs12_pbe`` (``info.txt``); the PKCS#12 module cannot
   be built without them. Only ``sha2_64`` (SHA-384/512 MAC) is genuinely
   optional. The table also omits ``SHA-224`` and ``SHA-512-256``, which
   are supported and listed elsewhere on the page.
10. **CLI documentation** (``doc/cli.rst``): ``--no-mac`` is described as
    "required when ``--pass`` is empty". It is not; empty passwords with a
    MAC are produced, parsed and read by OpenSSL.
11. **Minor:** the header comment on ``PKCS12_Export_Options`` calls
    ``modern`` and ``legacy_compat`` "pseudo-constructors"; the wording is
    fine, but ``legacy_compat`` is documented as using "PBE-SHA1-3DES, SHA-1
    MAC, 2 048 iterations" without mentioning that certificates stay
    unencrypted, which differs from what OpenSSL's ``-legacy`` produces.

Statements verified as correct: the default and legacy parameter sets; the
list of supported key and certificate encryption names and MAC digests; the
behaviour of ``unknown_bag_types()``; the ``mac_protected()`` description on
``master``; the example programs compile against the documented API and
handle the two documented exception types.

.. _pkcs12-review-tests:

Test suite
----------

``src/tests/test_pkcs12_audit.cpp`` (about 1,600 lines) registers the test
group ``pkcs12_audit`` and is picked up automatically by ``configure.py``.
It runs in well under a second and needs the modules ``pkcs12``, ``ecdsa``,
``pbes2`` and ``x509``. Its structure:

- **State transitions** of the ``PKCS12`` object: empty bundle, key-only and
  certificate-only bundles, insertion-order dependence of key/certificate
  matching, parse-mutate-re-export, repeated export randomness and
  ``const``-ness, attribute precedence (options versus bundle, empty
  values, clearing), and password change through re-export.
- **Export option validation** including case sensitivity, unsupported
  names, MAC digest validation only when a MAC is produced, and the
  iteration boundaries (0, 1, 10\ :sup:`6`\ +1, 10\ :sup:`8`\ +1, with
  timing).
- **Parameter matrix** (216 combinations) and password edge cases (non-BMP,
  invalid UTF-8, embedded NUL, 4 KiB).
- **KDF contract** and the **independent PBE re-implementation** used in
  both directions.
- **MAC handling:** MAC-before-content ordering, 31 ``MacData`` variations
  (digests with and without ``NULL`` parameters, absent/zero/negative/huge
  iteration fields, salt lengths 0 to 200, wrong-length and wrong-digest
  values), MAC stripping with certificate tampering and substitution, error
  distinguishability without MAC (including signing with every silently
  altered key and verifying under the certificate and the key's own public
  point), and the bit-flip and truncation sweeps with outcome
  classification.
- **Hand-crafted structures** built with the DER encoder: attribute
  variants (``UTF8String`` names, multiple values, unknown attributes, empty
  sets), the ``localKeyId`` ordering case, multiple keys, duplicate
  certificates, unknown certificate and bag types, the exact nesting
  boundary and breadth, ``EncryptedData`` variants (versions, content types,
  every RFC 7292 Appendix C legacy scheme, PBKDF2 and scrypt cost caps),
  shrouded key bag cost and mismatch cases, PFX versions, ``SignedData`` and
  ``EnvelopedData`` content, BER indefinite length, and both empty-password
  conventions in all combinations.

Two assertions are version dependent and compiled only for Botan 3.14 and
later (``mac_protected()``); everything else is identical on 3.13.0 and
``master``. The suite, the interoperability script with its log, and the
demonstration program are archived under ``misc/pkcs12/`` in the report
sources.

Classification and recommendations
----------------------------------

The ``pkcs12`` modules remain outside the audited BSI policy build (see the
scope recommendation in the PR #5625 appendix). For the audit record:

- P1 violates no stated limit and belongs to the resource-exhaustion class
  the maintainer has deferred to #5914; it is nevertheless worth reporting
  upstream with the demonstration, since a decode-side memory bound in
  ``Pbes2ScryptParameters::validate_params`` is a small change that brings
  Botan in line with OpenSSL's 32 MiB default. Classification: *info*.
- P2 sharpens the known MAC-less weakness into a concrete silent-corruption
  primitive; the cheap upstream fix is a scalar/point consistency check in
  the EC private key decoder. Applications should require ``mac_protected()``
  and call ``check_key`` on imported keys.
- P3, P4 and the documentation errors (items 1 to 10) should be reported
  upstream together; P5 to P8 are suggestions.
- The implementation's handling of hostile input, its integrity protection
  when a MAC is present, and its interoperability were found to be robust;
  no finding of the PR #5625 appendix was contradicted, and F1 has been
  addressed upstream in #5902.
