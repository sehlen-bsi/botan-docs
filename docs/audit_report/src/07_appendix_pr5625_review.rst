Appendix: Review of Botan PR #5625
==================================


The review in this section was entirely written by Anthropic's Fable 5 model. Please treat it with care as appropriate for AI generated content.

**"Add PKCS#12"**

- **PR:** `randombit/botan#5625 <https://github.com/randombit/botan/pull/5625>`_
  (merged as ``de22448f71``)
- **Author:** Damiano Mazzella — **Merged:** 2026-08-02, +3486 lines across 58
  files
- **First released in:** Botan 3.13.0
- **Reviewed code:** ``src/lib/pkcs12/pkcs12.{h,cpp}`` (252 + 939 lines),
  ``src/lib/pkcs12/pkcs12_pbe/`` (230 lines), additions to
  ``src/lib/pbkdf/pkcs12_kdf/``, at tag ``3.13.0``
- **Audit scope status:** the new modules ``pkcs12`` / ``pkcs12_pbe`` are
  *not* in the current audit scope (not in the BSI build policy, not in the
  additional-modules list, not a dependency of any in-scope module). This
  review is a voluntary spot check; see the scope recommendation at the end.

What the PR adds
----------------

Native parsing and generation of PKCS#12/PFX bundles (RFC 7292):

- ``Botan::PKCS12`` — parses a PFX from bytes + password, surfaces private
  keys, certificates (end-entity identified by localKeyId or SPKI match),
  friendly name, localKeyId, and a list of *unknown bag type* OIDs; also acts
  as a builder with ``export_to(PKCS12_Export_Options, RNG)``.
- ``pkcs12_pbe_{encrypt,decrypt}`` — the RFC 7292 Appendix B password-based
  encryption schemes ``PBE-SHA1-3DES`` / ``PBE-SHA1-2DES``, plus dispatch into
  the existing PBES2 implementation (``PBE-PKCS5v20`` OID on decrypt,
  ``PBES2-SHA256-AES256/-AES128`` names on encrypt).
- A small extension of the existing ``pkcs12_kdf`` module: a low-level
  ``pkcs12_kdf()`` entry point that skips the RFC 7292 password encoding, used
  for OpenSSL empty-password interoperability.
- CLI commands (``pkcs12_export``, ``pkcs12_info``), examples, and a
  1,245-line test file.

Trust model note: a PFX file is routinely **attacker-supplied input** (import
of externally provided bundles), and simultaneously a container for the most
sensitive material Botan handles (private keys). Both directions were
reviewed: hostile-input robustness and protection quality of produced files.

Positive observations
---------------------

- **Authenticate-then-parse.** When MacData is present, the HMAC over the
  authSafe content is verified *before* any SafeContents parsing or PBE
  decryption (``pkcs12.cpp:483-522``). The comparison is constant-time
  (``constant_time_compare``, ``pkcs12.cpp:145``).
- **Strict algorithm allowlists in both directions.** MAC digests are limited
  to the SHA-1/SHA-2 family (``pkcs12.cpp:54-74``); PBE decryption accepts
  only ``PBE-SHA1-3DES``, ``PBE-SHA1-2DES``, and PBES2
  (``pkcs12_pbe.cpp:34-42``) — the RC2/RC4/MD5 legacy schemes of RFC 7292 are
  *not* implemented, a deliberate and security-positive interoperability cut.
  Export validates option strings against fixed lists (``pkcs12.cpp:79-115``).
- **Iteration-count caps on every KDF path.**
  ``PKCS12_MAX_ITERATIONS = 100'000'000`` (``pkcs12_pbe.h:25``, matching
  NSS/AWS-LC/BoringSSL) is enforced for the MAC KDF (``pkcs12.cpp:500-502``),
  for PKCS#12 PBE (``pkcs12_pbe.cpp:113-115``) and on export
  (``pkcs12.cpp:80-82``). The PBES2 path has its own equivalent cap
  (``pbes2.cpp:182-189``) and scrypt parameter validation.
- **Recursion bound.** SafeContentsBag nesting is capped at depth 10
  (``pkcs12.cpp:33, 201-203``) — the one recursive construct in the format.
- **Strict end-of-structure checking.** ``verify_end()`` after essentially
  every constructed type, including a trailing-data check on the outer PFX
  (``pkcs12.cpp:603``); versions are pinned (PFX v3, EncryptedData v0).
- **Key-material hygiene on the main paths.** Decrypted shrouded-key bytes,
  plain KeyBag bytes, derived keys/IVs and MAC keys all live in
  ``secure_vector`` (``pkcs12.cpp:250-259, 907``;
  ``pkcs12_pbe.cpp:65-66, 124``).
- **Sound export defaults.** ``modern()``: PBES2 AES-256-CBC with
  PBKDF2-HMAC-SHA-256, 100,000 iterations, SHA-256 MAC; fresh random salts
  (8 bytes PBE / digest-length MAC salt) from the caller's RNG. Legacy 3DES +
  SHA-1 + 2,048 iterations only via the explicit ``legacy_compat()``
  constructor.
- **Negative tests** cover corrupted files, wrong password, zero and
  over-limit iteration counts, nesting depth, trailing bytes, unsupported
  algorithms, and key/cert mismatch; test data includes hand-crafted edge-case
  PFX files (nested SafeContentsBag, unknown bags, version-2 PFX rejection).

No memory-safety issue, integer overflow, or unbounded allocation was found;
buffer growth is linear in the input size throughout.

Findings
--------

F1 (Medium) — Integrity verification is silent: MAC-stripping is undetectable through the API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MacData is OPTIONAL in the PFX syntax, and the parser accordingly verifies the
MAC only ``if(pfx_seq.more_items())`` (``pkcs12.cpp:483``). A file whose
MacData an attacker has removed parses successfully, and **nothing in the**
``PKCS12`` **API tells the caller whether integrity was verified**. Since the
MAC is password-based, anyone *without* the password can strip it but not
forge it — so stripping is exactly the attack this bit of state would catch.

Consequences of a stripped MAC:

- certificates are typically stored unencrypted (this implementation even
  defaults to that on export); an attacker who can modify a bundle in transit
  or at rest can **substitute CA certificates** in an imported bundle without
  the password, and the import succeeds silently;
- the PBE ciphertexts become unauthenticated, enabling F2.

Recommendation: add an accessor such as ``bool integrity_protected() const``
(and/or a parse option requiring a valid MAC), and document that applications
importing PFX files from external sources should reject MAC-less ones.
Worth reporting upstream.

**Comparison with other implementations.** Verify-if-present is the ecosystem
norm, but the major implementations differ in what they let the application do
about a missing MAC. OpenSSL's ``PKCS12_parse()``
(``crypto/pkcs12/p12_kiss.c``) behaves exactly like this code — a MAC-less
file parses silently — but exposes ``PKCS12_mac_present()`` /
``PKCS12_get0_mac()`` as public API, so callers can enforce strictness
themselves. NSS hard-fails: ``SEC_PKCS12DecoderVerify()``
(``lib/pkcs12/p12d.c``) is a mandatory import stage that verifies the MAC if
present, otherwise attempts RFC 7292's public-key integrity mode, and returns
``SEC_ERROR_PKCS12_INVALID_MAC`` if neither verifies. OpenJDK is the most
lenient: MacData absent is accepted silently, a present MAC is skipped
entirely when the caller passes a null password, and the public ``KeyStore``
API surfaces no integrity signal. Botan 3.13.0 parses like OpenSSL but offers
neither OpenSSL's presence query nor NSS's strict mode, so an application
cannot implement the stricter policies on top of the current API at all —
which is the substance of this finding.

F2 (Low/Medium, application-dependent) — Unauthenticated CBC decryption when the MAC is absent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With no (or a stripped) MAC, EncryptedData and PKCS8ShroudedKeyBag contents
are decrypted (3DES-CBC or AES-CBC) without any authentication
(``pkcs12_pbe.cpp:120-127``). Distinct failure modes are observable to the
caller: CBC padding errors surface from ``cipher->finish()``, whereas
well-padded but garbled plaintext fails later in BER/PKCS#8 parsing with
``Decoding_Error``, and a valid parse succeeds. An application that repeatedly
opens attacker-supplied modifications of a victim file *using the correct
password* therefore provides a classic CBC padding oracle against the file's
encrypted contents (i.e. the private key). This is an inherent weakness of the
PKCS#12 format rather than of this implementation, and it is fully mitigated
whenever the MAC is present and verified — which is why F1 (making MAC
presence visible/enforceable) is the practical fix. Application guidance:
treat all parse failures uniformly; do not run repeated parse attempts on
externally modified files.

F3 (Low) — CPU-exhaustion amplification across multiple KDF invocations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each individual KDF run is capped at 10\ :sup:`8` iterations, but a single
file may demand many runs before/without any authentication succeeding: one
(or, for the empty-password OpenSSL fallback, two — ``pkcs12.cpp:510-518``)
MAC KDF, plus one key+IV derivation pair *per* EncryptedData element and *per*
shrouded key bag (each bag carries its own iteration count). A small crafted
file with many bags, each at the cap, turns one ``PKCS12`` constructor call
into hours of CPU. The per-operation cap matches other implementations and the
aggregate issue exists in them too, but it deserves a documentation note
("parsing untrusted PFX files can be made expensive; impose external
limits/timeouts"), or a cumulative iteration budget per parse.

F4 (Low, hygiene) — Unencrypted key material transits non-zeroizing buffers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The per-bag buffers holding decrypted or plain private-key bytes are
``secure_vector`` (good), but when a PFX carries **unencrypted KeyBags**, the
raw PrivateKeyInfo is also embedded in the outer containers, which are plain
``std::vector<uint8_t>``: ``auth_safe_content`` (``pkcs12.cpp:463``) and
``safe_contents_data`` (``pkcs12.cpp:317``). Their contents are not zeroized
on destruction, so private-key bytes can linger in freed heap memory. Low
severity (requires a key stored unencrypted in the file, plus a memory
disclosure primitive to matter), trivially fixed by switching those two
buffers to ``secure_vector``. Worth reporting upstream.

F5 (Info) — Empty-password OpenSSL quirk only auto-detected via the MAC
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The non-conforming OpenSSL empty-password KDF encoding is detected by
retrying MAC verification (``pkcs12.cpp:506-518``) and then propagated to PBE
decryption. A MAC-less OpenSSL file with an empty password will fail to
decrypt, since no equivalent retry exists on the PBE path. Interoperability
asymmetry only; the conservative choice (no password-guessing loops around
PBE) is defensible.

F6 (Info) — Unknown certificate types are dropped silently
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unknown *bag* types are transparently surfaced via ``unknown_bag_types()``
(``pkcs12.h:207``), but an unknown certType inside a CertBag (e.g. SDSI) is
silently discarded (``pkcs12.cpp:236-238``). Inconsistent transparency; a
caller cannot tell such entries existed.

F7 (Info) — Certificates are unencrypted by default on export
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``cert_encryption_algo`` defaults to empty = plaintext SafeContents
(``pkcs12.h:94-106``, ``pkcs12.cpp:865-872``). This is documented, matches
the modern argument that certificates are public, and keeps the file readable
without the password — but differs from OpenSSL's default (encrypted cert
bags) and exposes the certificate chain and friendly-name/localKeyId metadata
to anyone holding the file. Applications with confidentiality expectations
for the *identity* contained in a bundle should set a cert encryption
algorithm.

F8 (Info) — Legacy algorithm surface and TR-02102 relevance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For interoperability the implementation accepts (decrypt) and can produce
(explicit ``legacy_compat()``/option only) ``PBE-SHA1-3DES`` and
``PBE-SHA1-2DES`` — SHA-1-based KDF, 8-byte salt, and in the 2DES case an
effective security level around 80–112 bits (2-key 3DES, expanded K1||K2||K1 at
``pkcs12_pbe.cpp:83-86``). None of these mechanisms conform to BSI TR-02102-1
recommendations; a BSI-context application must stick to the (default) PBES2
AES + SHA-256 profile for produced files and should treat legacy-encrypted
incoming files as weakly protected. The implementation's defaults already
steer this way; the note is for the audit record.

Verdict
-------

No exploitable vulnerability was identified in the implementation itself. The
code is defensively written for hostile input: algorithm allowlists,
iteration caps aligned with other major implementations, a recursion bound,
strict end-of-content checks, constant-time MAC comparison, and correct
MAC-before-parse ordering. The substantive gaps are systemic to the PKCS#12
format but actionable in the API: the caller cannot detect a stripped MAC
(F1), which in turn re-enables the format's classic unauthenticated-CBC
weakness (F2); plus a memory-hygiene slip on the unencrypted-KeyBag path (F4)
and a DoS-amplification documentation gap (F3). F1 and F4 are concrete,
low-effort improvements worth raising upstream.

Scope recommendation
--------------------

The ``pkcs12``/``pkcs12_pbe`` modules are outside the current audit scope.
Given that the parser processes attacker-supplied files, handles private
keys, and will plausibly be used by applications in BSI contexts (the PR's
motivation is replacing external tooling for PFX handling), adding ``pkcs12``
(which pulls ``pkcs12_pbe`` and ``pkcs12_kdf``) to the additional-modules
list should be considered for this or the next cycle. Note this would bring
``des`` into the audited dependency closure. If the scope stays unchanged,
the addition should still be mentioned in the Changes Overview (it is a
release-notes item), with the patch classified out-of-scope.
