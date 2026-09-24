Appendix: Review of Botan PR #5602
==================================


The review in this section was entirely written by Anthropic's Fable 5 model. Please treat it with care as appropriate for AI generated content.

**"Fix various bugs in the PKCS11 wrapper"**

- **PR:** `randombit/botan#5602 <https://github.com/randombit/botan/pull/5602>`_
  (merged as ``a09371704``, single commit ``9e0dd103d``)
- **Author:** Jack Lloyd — **Merged:** 2026-05-26
- **First released in:** Botan 3.13.0
- **Size:** +330/-127 across 17 files, entirely within
  ``src/lib/prov/pkcs11``
- **Audit scope status:** the ``pkcs11`` provider is explicitly in the
  audit scope. This is a dense collection of real fixes; several are
  security-relevant, not just cosmetic.

Security-relevant fixes
-----------------------

- **ECDH peer-point validation before the token sees it.** ``agree()``
  now deserializes the peer's public point against the curve and rejects
  not-on-curve and identity points *before* ``C_DeriveKey``. Previously
  the raw bytes went straight to the token — and many tokens do not
  validate peer points, which is the classic invalid-curve attack setup
  against hardware-held keys. This is the single most important fix in
  the PR, and it directly addresses one of the permissive-decoder gaps
  noted in the review of PR #5725 (see
  `randombit/botan#5913 <https://github.com/randombit/botan/issues/5913>`_).
- **RSA raw-decrypt range check per RFC 8017 5.1.2.** The blinded raw
  path previously fed any input to ``Blinder::blind``, which reduces mod
  n — so a ciphertext outside [1, n-1] was silently accepted as its
  reduction. Now zero, larger-than-n, and over-length inputs return empty
  with ``valid_mask = 0``. (The early return is value-dependent, but
  ciphertext range validity is public — same as the software provider.)
- **Token decrypt errors mapped to** ``valid_mask`` **instead of
  exceptions.** ``C_Decrypt`` failures (e.g. the token's own PKCS#1
  unpad rejection, ``CKR_ENCRYPTED_DATA_INVALID``) previously propagated
  as exceptions out of ``PK_Ops::Decryption::decrypt`` — a
  distinguishable error path where the API contract expects the
  constant-time-friendly ``valid_mask`` convention. Now caught and mapped
  to mask 0/empty. A genuine padding-oracle-surface reduction for
  hardware-unpadded mechanisms.
- **Software-EME decrypt path fixed.** This path serves tokens that can
  only do raw RSA (``CKM_RSA_X_509``), with Botan's software PKCS#1/OAEP
  unpadder removing the padding in constant time.
  ``PKCS11_RSA_Decryption_Operation_Software_EME`` previously
  implemented its ``raw_decrypt()`` in terms of the *public API class*
  ``PK_Decryptor_EME(key, rng, "Raw")``, which dispatched back down into
  a second, inner PKCS#11 operation. That middle layer is exactly wrong
  in this position, for two manifest reasons. First, failure semantics:
  ``PK_Decryptor::decrypt`` discards the inner ``valid_mask`` and
  *throws* on invalid input, and token errors from ``C_Decrypt`` threw
  ``PKCS11_ReturnError`` — either exception escaped from inside
  ``raw_decrypt``, aborting the constant-time unpadder before it ran and
  giving the application a distinguishable error path instead of the
  uniform mask-0 behavior the ``PK_Ops::Decryption`` contract promises
  (this also silently defeats ``PK_Decryptor::decrypt_or_random``, whose
  oracle mitigation assumes the operation returns with a mask rather
  than throwing). Second, lifetime: neither the wrapper nor the inner
  operation kept the key alive (the inner operation held a ``const``
  reference), so a decryptor outliving its key object dereferenced
  freed memory. The rewrite holds the raw PKCS#11 operation — and,
  inside it, the key — by value. A new comment additionally pins the
  pre-existing width contract: the raw decrypt returns the fixed-width
  I2OSP encoding, preserving the leading 0x00 byte that the outer
  software unpadder frames its input on (this documents an invariant the
  old code already upheld, so refactoring cannot silently lose it).
- **Derived/generated objects no longer linger on the token.** The ECDH
  shared-secret object (created with ``Extractable=true``!) and the
  public-key halves created during RSA/EC key generation are now
  destroyed via ``scoped_cleanup`` once read. Previously they persisted
  on the token until session close — for the ECDH secret, a sensitive
  extractable object left lying around.
- **Dangling-reference fixes: operations own their keys.** RSA
  encrypt/decrypt and ECDH agreement operations held ``const Key&``; a
  ``PK_Decryptor``/``PK_Key_Agreement`` outliving the key object
  dereferenced freed memory. Now held by value (cheap handle-wrapper
  copies), matching the signature operation which already did this.
- **CK_ULONG truncation eliminated.** A new ``checked_ulong_cast``
  replaces ~30 bare ``static_cast<Ulong>`` conversions. Irrelevant on
  LP64 Linux, but on LLP64 (Windows, 32-bit ``CK_ULONG``) an oversize
  buffer silently truncated — worst case in
  ``PKCS11_RNG::fill_bytes_with_input``, where a truncated
  ``C_GenerateRandom`` length would have left the tail of the output
  span *unfilled* while the caller believed it random. The RNG now
  chunks by the ``CK_ULONG`` maximum instead of throwing; everything
  else throws ``Invalid_Argument``.

Correctness fixes
-----------------

- **C_GetInterface ABI type confusion:** the PKCS#11 v3.0 function takes
  ``CK_INTERFACE_PTR_PTR``; the wrapper declared and passed
  ``Interface*`` — the library would have written a pointer over the
  caller's struct. Fixed to ``Interface**``. Interface discovery also
  now null-checks ``pInterfaceName``/``pFunctionList`` before
  dereferencing (hostile or buggy modules previously hit an assert or a
  null dereference in ``name_of``) and enforces the "PKCS 11"
  interface-name match inside the validity predicate.
- **Empty-message sign/verify:** the old code used
  ``m_first_message.empty()`` to distinguish single- from multi-part
  operations, which conflated "no update yet" with "update with empty
  input", and ``sign()``/``is_valid_signature()`` without any
  ``update()`` called ``C_SignFinal`` on an uninitialized operation
  (``CKR_OPERATION_NOT_INITIALIZED``). A separate ``m_has_first_message``
  flag plus lazy initialization in the finishers fixes both, for ECDSA
  and RSA alike. Verification also now maps ``CKR_SIGNATURE_LEN_RANGE``
  to ``false`` (invalid signature) instead of throwing — the correct
  reading of the spec, and consistent with software providers.
- **Object::search pagination:** ``C_FindObjects`` returns batches; the
  old code called ``find()`` once, silently dropping matches beyond the
  first batch. Now loops until exhausted.
- **Lifetime/UB fixes:** ``ObjectFinder`` copy construction deleted (a
  copy triggered double ``C_FindObjectsFinal``), its move now marks the
  source terminated; ``Session``'s hand-written move prevents double
  ``C_CloseSession``/``C_Logout``; ``Module::~Module`` null-checks
  ``m_low_level`` (dereferencing a moved-from Module's null pointer was
  undefined behavior); ``Module::reload`` is now transactional (failures
  leave the module empty rather than holding a function table into a
  finalized library).
- **ECDH mechanism parsing:** the old ``"Cofactor"`` handling indexed
  ``param_parts[1]`` when ``"Cofactor"`` was the *only* part — out of
  bounds — and had order-dependent quirks; the rewrite handles both
  orders, rejects duplicates and missing KDFs. Raw-KDF agreement now
  returns the full field-size secret (matching software ``raw_agree``
  semantics, instead of asking the token to truncate to ``key_len``),
  rejects a salt when no KDF is configured (previously silently set),
  and explicitly nulls the shared-data pointer when the salt is empty
  (previously a stale pointer from a prior call could persist in the
  mechanism struct).
- **PSS alias typo:** ``PSS(SHA-224,MGF1,24)`` -> ``28`` — SHA-224's
  output is 28 bytes; the old table mapped a wrong-salt-length spec onto
  the 28-byte-salt mechanism (a cross-provider signature mismatch
  waiting to happen) while rejecting the correct spec.
- **ECDSA hash-name normalization:** ``EMSA1(SHA-256)`` unwraps to
  ``SHA-256`` so ``algorithm_identifier()`` yields a registered OID.
- **RSA encryption maximum-input-size underflow:** the old
  ``8 * (n.bytes() - padding_size()) - 1`` computation could wrap for a
  modulus smaller than the padding overhead, yielding a nonsensically
  large input limit; now guarded.

Observations (not defects)
--------------------------

- **No tests.** Understandable — PKCS#11 tests need a real token (the
  suite runs against SoftHSM only when ``--pkcs11-lib`` is given) — but
  the empty-message and pagination fixes are exercisable there and no
  test was added.
- Minor acceptance narrowing: ECDH KDF specs like ``"KDF2(SHA-256)"``
  were previously unwrapped to their hash argument; now only plain hash
  names (or ``Raw``) are accepted. Arguably right (the PKCS#11 KDFs are
  ANSI X9.63, not KDF2), but it is a silent API behavior change.
- The software-EME path discards the inner raw operation's
  ``valid_mask``; a token malfunction is thus indistinguishable from an
  unpadding failure. Harmless conflation, fail-closed.

Verdict
-------

A high-value cleanup of long-standing PKCS#11 wrapper defects. The
headline items for the audit: peer-point validation before token ECDH
(invalid-curve hardening), RFC 8017 range checking and oracle-surface
reduction in RSA decryption, sensitive derived objects no longer left on
the token, and several genuine undefined-behavior/lifetime fixes
(dangling key references, ABI type confusion in v3.0 interface loading,
double session close). All deltas were verified fail-closed or strictly
more correct; no introduced defects were found.

Suggested classification: **relevant** (in-scope ``pkcs11`` provider;
multiple security-adjacent fixes affecting RSA decryption oracle
behavior and ECDH point validation with hardware keys; no new
mechanisms).
