# Review of cryptodoc against Botan 3.12.0

Date: 2026-08-11
Scope: all chapters under `docs/cryptodoc/src/` checked against the Botan
source delta `3.11.0..3.12.0` (tags in `/home/fstrenzke/dev/p663/botan`).
Method: per-chapter comparison of every algorithm admonition, function name,
constant and behavioral claim against the 3.12.0 sources; `:srcref:` line
numbers were *not* checked (CI covers those); typos were out of scope.

Severity legend:

- **A (doc wrong for 3.12)** — statement contradicted by 3.12.0 code due to a
  3.11.0→3.12.0 change.
- **B (new 3.12 behavior, undocumented)** — new security-relevant behavior the
  doc should probably describe; no existing statement is contradicted.
- **C (pre-existing inaccuracy)** — statement already wrong for 3.11.0,
  discovered during this pass.

---

## 09_x509.rst — X.509 / OCSP (largest impact)

### A — wrong for 3.12

1. **Revocation checks are skipped on already-rejected chains (GH #5512).**
   Doc lines 64–68 and steps 7b–7e of `x509_path_validate` claim CRL/OCSP
   checks run unconditionally on each candidate path. In 3.12.0 they only run
   if the chain status so far is below the new
   `FIRST_ERROR_STATUS_TO_SKIP_REVOCATION = 3000` (`pkix_enums.h:61`,
   `x509path.cpp:975`).

2. **Path building is now incremental/lazy (GH #5513/#5520/#5521).**
   `x509_path_validate` no longer calls `build_all_certificate_paths`; it
   pulls candidate paths one at a time from an internal
   `CertificatePathBuilder` (`x509path.cpp:50–202, 933–1039`) and validates
   each as discovered. The doc's "First, all possible certificate paths are
   built" (lines 53–54) and steps 4–7 describe the old two-phase structure.
   `build_all_certificate_paths` still exists as a public wrapper. The builder
   also honors `restrictions.require_self_signed_trust_anchors()` directly.

3. **Online-OCSP trigger is now per-certificate (commit 61b45486c).**
   Doc step 7d: online lookup only `if ocsp_status.empty()`. 3.12.0 determines
   per position (EE, or all intermediates with `ocsp_all_intermediates()`)
   which slots lack a stapled/provided response and fetches/merges only the
   missing ones (`x509path.cpp:984–1017`). Without HTTP support, `OCSP_NO_HTTP`
   is inserted into all empty required slots (3.11: slot 0 only).

4. **`check_ocsp` no longer strips empty status sets** (doc step 3, line 797).
   3.12.0 returns a fixed-size `n-1` vector including empty sets
   (`x509path.cpp:550–577`).

5. **`check_crl` gates content checks on signature validity (commit 2b246f477).**
   Doc steps 4g–4k append `VALID_CRL_CHECKED` and perform revoked/CRLDP/
   critical-extension checks unconditionally after the signature check. In
   3.12.0 all of these run only if the CRL signature verified
   (`x509path.cpp:608–633`).

6. **CRLDP matching semantics changed (GH #5546).** Doc step 4j describes URL
   string comparison. 3.12.0 uses `X509_CRL::has_matching_distribution_point()`
   (`x509_crl.cpp:298–311`): no error if the cert has no CRLDP extension;
   `NO_MATCHING_CRLDP` if the cert has one but the CRL has no IDP extension;
   otherwise structural GeneralNames overlap, not string equality. The
   unknown-critical-CRL-extension check is now a `dynamic_cast` to
   `Unknown_Extension` rather than an OID-registration test.

7. **Delegated-responder validation: new pre-checks and `>=` comparison
   (commits 4274164a1, a5b1a0e9b).** Before the criterion-c path validation,
   `verify_ocsp_signing_cert()` now requires
   `signing_cert.issuer_dn() == ca.subject_dn()` and (when both present)
   AKID(signing_cert) == SKID(ca); on mismatch it returns
   `OCSP_ISSUER_NOT_TRUSTED` **alone, without running path validation** — so
   the doc's step-3 statement that a failure always yields the two-element set
   {path-validation result, OCSP_ISSUER_NOT_TRUSTED} no longer covers this
   path. Additionally the failure test in `evaluate_ocsp_response()` changed
   from `>` to `>= FIRST_ERROR_STATUS` (`x509path.cpp:535`), so a responder
   path validation ending at `SIGNATURE_METHOD_TOO_WEAK` (1000) now rejects
   the response. Also `has_ex_constraint()` no longer accepts
   anyExtendedKeyUsage as satisfying id-kp-OCSPSigning (this makes doc step 3c
   *more* accurate than for 3.11).

8. **`status_for()` can also return `OCSP_RESPONSE_INVALID`** for
   unrepresentable thisUpdate/nextUpdate times (commit 160fffb0a,
   `ocsp.cpp:486–502`) — missing from the output list at doc lines 910–914.

9. **`matches_dns_name` matches IP addresses.** The Remark at lines 641–644
   ("does not support matching 'IPAddress' … fields") is wrong: IPv4 SAN
   matching existed already in 3.11.0 (pre-existing error), and 3.12.0 added
   IPv6 (`x509cert.cpp:707–731`, commits 45d307bb0, da7307b48). URI matching
   is still unsupported.

### B — new 3.12 behavior, undocumented

10. **Search limits + new status codes.** `x509_path_validate` aborts after
    >50 candidate paths or >200 certificates with the new hard-failure code
    `EXCEEDED_SEARCH_LIMITS = 5006`; each builder step is capped at 1000 DFS
    iterations (`x509path.cpp:955–970, 74–82`). New code
    `EXTENSION_ENCODING_ERROR = 4508`: a recognized extension whose body fails
    to decode is retained as `Unknown_Extension` with `failed_to_decode=true`
    and yields this status during `check_chain` (GH #5518,
    `x509_ext.h:965–985`).

11. **Strict DER for PKIX types (GH #5521, `BER_Decoder::Limits::DER()`).**
    Certificates, SPKI, extensions, CRLs and OCSP responses now reject
    non-DER BER encodings at parse time; OCSP parsing additionally enforces
    ResponderID exactly-one-of byName/byKey, KeyHash length 20, and defined
    OCSPResponseStatus values (`ocsp.cpp:259–342`). Security-relevant
    tightening; also the context of CVE-2026-44378 (BER decoding DoS).

12. **`OCSP::Response::verify_signature(issuer, restrictions)`** (the overload
    `evaluate_ocsp_response` calls) can now also return
    `UNKNOWN_CRITICAL_EXTENSION` (unrecognized critical extension in the
    response or any SingleResponse), `UNTRUSTED_HASH`, and
    `SIGNATURE_METHOD_TOO_WEAK` (responder key below
    `minimum_key_strength()`) — none of these OCSP outcomes are in the doc
    (`ocsp.cpp:383–425`).

13. **Self-signed detection during parsing is now heuristic (GH #5515).**
    Subject DN == issuer DN plus SKID==AKID when both present; the
    self-signature itself is only verified during path validation
    (`x509cert.cpp:285–303`).

### C — pre-existing

14. `build_all_certificate_paths` admonition mismatches the DFS: there is no
    upfront self-signed-EE rejection (doc step i, lines 263–264); any trusted
    certificate terminates a candidate path and the DFS continues extending
    through it; `CANNOT_ESTABLISH_TRUST` is recorded only for untrusted
    self-signed certs (lines 287–290; also contradicts lines 135–138).
15. `build_certificate_path` admonition (lines 322–369) describes an obsolete
    single-pass issuer walk.
16. `CHAIN_LACKS_TRUST_ROOT` is inserted only when
    `require_self_signed_trust_anchors()` is true (default true); this option
    (and `trusted_ocsp_responders`) is missing from the
    `Path_Validation_Restrictions` list at lines 100–108.
17. Minor: line 421 `SIGNATURE_ALGO_UNKNOWN` (not `SIGNATURE_ALGORITHM_...`),
    and on unknown OID the key-load/verify steps are skipped; line 425
    dangling "continue with step l)"; warnings list (126–129) omits
    `TRUSTED_CERT_HAS_EXPIRED`/`TRUSTED_CERT_NOT_YET_VALID`; step 4f
    `CRL_HAS_EXPIRED` only checked when nextUpdate is set; check_crl step 5
    removes only *trailing* empty sets.

### Consistent

`check_chain` (byte-identical 3.11↔3.12), `merge_revocation_status`,
`check_ocsp_online` admonition, `host_wildcard_match`,
`evaluate_ocsp_response` steps 1/2/5, Remark 1 (relaxed restrictions),
`allowed_usage(OCSP_RESPONDER)`, `status_for` check order, extension lists,
footnote on recursive responder revocation (GH #3124 TODO retained).

---

## 07_rng.rst / 08_entropy.rst — RNG and entropy

### A — wrong for 3.12 (new behavior contradicting or extending doc)

18. **HMAC_DRBG rejects MACs with output < 160 bits** (commit b6cb264c2):
    `hmac_drbg_security_level()` throws `Invalid_Argument` for
    `mac_output_length < 20`; runs from every constructor. SHA-1 still
    permitted; security-level table stays valid. (B-class: constructors gained
    a failure mode.)
19. **getrandom backend:** `got == 0` now throws
    `System_Error("System_RNG getrandom unexpectedly returned 0")`
    (commit 6900638fe) — missing from the getrandom Randomize steps
    (lines 772–784).
20. Minor B-class: HMAC_DRBG null-PRF and Jitter_RNG construction failures now
    throw (`Invalid_Argument` / `Internal_Error`) instead of asserting
    (commits 102ebdd62, 7d4ea22de).

### C — pre-existing (doc wrong for 3.11 and 3.12 alike)

21. **`BOTAN_RNG_RESEED_POLL_BITS` and `BOTAN_RNG_RESEED_DEFAULT_TIMEOUT` do
    not exist** (verified by grep over both tags). The actual constants are
    `RandomNumberGenerator::DefaultPollBits = 256` and
    `DefaultPollTimeout = 50ms` (`rng.h:50, 285`). Moreover the RNG reseed
    path (`Stateful_RNG::reseed_from_sources` → 2-arg
    `Entropy_Sources::poll(rng, poll_bits)`) has **no timeout logic at all**;
    the 3-arg poll overload with timeout is not used by reseeding, and
    `reseed()`'s timeout parameter is literally `/*unused_timeout*/`
    (deprecated in favor of `reseed_from_sources`). Affects lines 35–46 and
    reseed_check step 2.4.1 (lines 499–503). *Note: the earlier section-A fix
    in this doc cycle replaced one nonexistent macro name with another —
    needs re-fixing to reference the actual constants and drop the timeout
    claim.*
22. `max_number_of_bytes_per_request` bound: doc says `>= 64*1024` invalid
    (lines 140–142, 168–170, 198–200); code rejects only `> 64*1024`, and the
    default is exactly 64*1024 (`check_limits()` in hmac_drbg.cpp).
23. **`randomize_with_ts_input` misdescribed** (lines 29–34, 421–447): 3.12.0
    (and 3.11.0) always stores the 64-bit high-resolution clock at offset 0
    and 32-bit PID at offset 8 of a fixed 32-byte buffer (when os_utils
    available), then fills the remaining **20 bytes (160 bits)** — not 96
    bits — from `System_RNG` if available; there is no clock/PID fallback
    branch as described.
24. reseed_check step 2.3.3: reset criterion is the *requested* poll bits
    (`poll_bits >= security_level()`), not a returned entropy estimation;
    `reseed_from_rng()` returns nothing.
25. reseed_check step 2.4 lead-in names the wrong function/source: the branch
    calls `reseed_from_sources(*m_entropy_sources, security_level())`,
    polling the entropy sources, not "the underlying RNG" via
    `reseed_from_rng()`.
26. getrandom is a **default** Linux target feature, not "if explicitly
    enabled" (line 571); same for the getentropy availability statement in
    08_entropy.rst lines 61–63 (default on Linux; declared for many OSes).
27. `/dev/random` is opened `O_RDONLY | O_NOCTTY`, not "O_RDWD" (line 812);
    only `/dev/urandom` is opened O_RDWR.
28. Jitter_RNG construction uses `jent_entropy_init_ex(0, JENT_FORCE_FIPS)` —
    not `jent_entropy_init()` with "default flags" (lines 889–893).
    Security-relevant: JENT_FORCE_FIPS forces the SP800-90B health tests.
29. 08_entropy.rst: Intel_Rdseed retry count is `RDSEED_RETRIES = 1024`, not
    512 (lines 40–42); `BOTAN_ENTROPY_DEFAULT_SOURCES` macro does not exist —
    the list is hardcoded in `Entropy_Sources::global_sources()`
    (values themselves correct); the entropy-source enumeration omits the
    `"jitter_rng"` source (`Jitter_RNG_EntropySource`, a *counted* source,
    not in the default list) — internally inconsistent with 07_rng.rst
    line 885.

### Consistent

HMAC_DRBG update/generate/clear/security_level/reseed-interval, five-constructor
structure; `Stateful_RNG` incl. the quoted `generate_batched_output()` listing
(verbatim match at 3.12.0); AutoSeeded_RNG; System_RNG backend order and
per-backend admonitions; ESDM; Jitter Randomize; Processor_RNG; entropy-source
admonitions apart from the items above. `src/lib/entropy` and
`src/lib/prov/tpm2` have **zero diff** 3.11.0→3.12.0 (chapters 08/10 unaffected
by the release itself).

---

## 05_01_dh.rst / 05_02_dsa.rst / 05_03_ecc.rst / 05_04_rsa.rst / 04_prim_generation.rst

### A — wrong for 3.12

30. **`DH_PrivateKey::check_key` semantics changed (commit 3d7119818).** The
    doc's condition list (05_01 lines 226–244) is wrong for 3.12.0:
    private-key check is now `verify_group(rng, strong) &&
    verify_private_element(x)` — i.e. the `y` range conditions are no longer
    checked for private keys; the `x` conditions now include `x > q` (missing
    from doc); and `y != g^x mod p` is not checked (was not in 3.11 either).
    Also (pre-existing) the Miller-Rabin description "6 (65 if strong)
    iterations" doesn't match `verify_group` (always `test_prob = 128` → 65
    iterations for external groups; builtin groups skipped unless strong).
31. **RSA key generation limits (commit 3904fccd1):** besides `bits >= 1024`
    the constructor now rejects `bits > 16384` and `bits % 8 != 0`
    (05_04 lines 32–35 say only "at least 1024").
32. **RSA private operations reject zero input (commit 6202258d3):**
    `Decoding_Error` if `input == 0 || input >= n` — affects `raw_sign` step 1
    ("m < N", line 413) and the decryption admonition (no range check
    documented at all).

### B — new 3.12 behavior, undocumented

33. **Validation at key/parameter decoding time:**
    - `DL_Group`: every construction now enforces p positive/odd,
      3 ≤ p.bits() ≤ 16384, 2 ≤ g < p, q (if present) positive/odd,
      q.bits() < p.bits() (`check_dl_group_params`, commit 2086d4526); DER
      decoding is strict (`DER_decode_DL_group`).
    - `DL_PublicKey` constructors enforce 1 < y < p at load (`BOTAN_ARG_CHECK`);
      only y^q == 1 is left to `check_key` — the doc's advice that `check_key`
      must be called manually (05_01 lines 249–251) implies no load-time
      validation. Applies to DSA keys too.
    - `RSA_PublicKey::init`: n positive odd, 384 ≤ n.bits() ≤ 16384, e odd,
      1 < e < n, e.bits() ≤ 256 (keys < 384 bits can no longer be loaded).
      `RSA_PrivateKey::init`: d ≥ 2, p,q ≥ 3, p ≠ q, p·q = n — checks the doc
      lists only as manual `check_key` items (05_04 lines 58–81) now run on
      every decode.
34. **`EC_PrivateKey::check_key` pairwise consistency** (commit 3d7119818):
    recomputes the public point from the private scalar (d·G, or d⁻¹·G for
    ECKCDSA/ECGDSA via new `m_with_modular_inverse`) and compares — not
    described in 05_03 (only the public-key check is, lines 260–273).
35. Generic pcurves backend now rejects zero scalars at deserialization
    (commit ac03ac4c6) — this makes the code *match* the doc's existing
    "0 < r < n" claims for application-registered custom curves (previously
    inaccurate for that backend). No doc change needed; noteworthy for audit.

### C — pre-existing

36. 05_02 line 50–52 refers to "DH key generation check", inheriting the
    finding-30 inaccuracies; `DSA_PrivateKey::check_key` additionally does
    `x < q` and a SHA-256 sign/verify consistency check — none of which
    matches the referenced DH list.
37. 05_04 `check_key` list omits the `p == q` check the code performs.

### Consistent

Chapter 04 (prime generation) fully consistent — the 3.12 primality changes
only hoist Montgomery-parameter computation to callers. DSA module unchanged;
DSA sign/verify, DH/ECDH `raw_agree`, ECDSA/ECKCDSA/ECGDSA sign/verify, RSA
encrypt/decrypt/CRT/blinding, PKCS#1 v1.5 and OAEP admonitions all still
accurate (OAEP gained an early public length-based rejection for
`input < 2*hlen + 2`, no doc statement contradicted). Reworked DER signature
decoding (`decode_der_signature_pair`) is semantically equivalent canonical-DER
enforcement.

---

## 02_sym_enc.rst / 01_hash.rst / 03_mac.rst

### A — wrong for 3.12

38. **GCM now enforces the SP 800-38D message-length limit (GH #5521).**
    Doc lines 180–183 state "Botan does not check the plaintext length
    explicitly. It is currently up to the application developer…". 3.12.0
    `GHASH::update()` throws `Invalid_State("GCM message length limit
    exceeded")` beyond (2^39 − 256)/8 bytes = 2^32 − 2 blocks (encrypt and
    decrypt; text only, not AD; GMAC unaffected). Side note: the doc's
    "(2^32 − 1) blocks" figure doesn't match the enforced 2^32 − 2 blocks.
39. **AEAD decryption failure now zeroizes the output buffer** (commit
    daec09b28, all AEADs: CCM/GCM/EAX/SIV/ChaCha20Poly1305). The CCM remark at
    lines 119–121 ("output buffer can still contain parts of the decrypted
    ciphertext…") now states the opposite of actual behavior.
40. **SHAKE constructors reject zero output length** (commit af57d087b) —
    "allows arbitrary output lengths" (01_hash lines 95–97) is overstated
    (also pre-existing: lengths must be multiples of 8 bits).

### B / C

41. B: CCM now rejects over-long messages early in `process()`
    (`Invalid_State`, commit 377f39d22). C (pre-existing): the limit is
    2^(8L) − 1 bytes, not 2^24 (lines 110–114, off by one).
42. C: `BOTAN_HAS_GCM_CLMUL_CPU` (line 166) does not exist — the macro is
    `BOTAN_HAS_GHASH_CLMUL_CPU`.

### Consistent

AES implementation inventory and constant-time claims; CBC/CTR descriptions;
GCM `start()` description (m_y0 removal is internal); SHA-1/SHA-2/SHA-3/
BLAKE2/Keccak unchanged; HMAC/CMAC/GMAC zero diff; KMAC max-key-length 192
still correct (3.12 fixed missing-`start_msg` handling, no doc conflict);
new HW implementations of ARIA/Camellia/SEED/SM4/Twofish/Whirlpool are not
documented ciphers — no impact.

---

## 05_05_xmss.rst — XMSS

The large 3.12 refactor (parameter switch-factories, public-key pimpl,
`base_w_with_checksum` helper) is **behavior-preserving**: all 21 parameter
sets, WOTS+/XMSS algorithm steps, key/signature wire formats, and the
`Stateful_Key_Index_Registry` section verified unchanged.

43. B: key decoding now uses strict DER (`BER_Decoder::Limits::DER()` in
    `extract_raw_public_key` / `extract_raw_private_key`) — non-canonical BER
    of the OCTET STRING wrapper is rejected.
44. C: lines 145–147 name the classes `WOTS_Public_Key`/`WOTS_Private_Key`;
    actual names are `XMSS_WOTS_PublicKey`/`XMSS_WOTS_PrivateKey` (doc uses
    the correct names elsewhere).
45. C: lines 81–82 swap the Key_Mask values — actual (`xmss_address.h:42`):
    `Mask_MSB_Mode = 1, Mask_LSB_Mode = 2`.
46. Informational: `XMSS_WOTS_Parameters::base_w()`/`append_checksum()` no
    longer exist as named functions (folded into a file-local helper,
    bit-identical output); doc references the RFC algorithm, still correct.

---

## PQC chapters (05_06–05_11), 06_hpke.rst, 11_kdf.rst, 12_pbkdf.rst

No statement factually wrong for 3.12.0. Deltas worth documenting:

47. B: **ML-DSA** `Dilithium_PrivateKey::check_key(rng, strong)` added
    (strong → sign/verify roundtrip via `KeyPair::signature_consistency_check`);
    `expand_keypair` now throws `Decoding_Error("Invalid ML-DSA seed size")`
    on wrong seed length (doc line 242–244 "sanity checks … can be omitted"
    remains valid for structural checks but could mention the length check).
48. B: **FrodoKEM** `check_key(strong)` added: encaps/decaps roundtrip with
    Raw KDF, returns K == K'.
49. Cosmetic: 05_08 line 413 cites "Botan 3.6.0" for the missing context-string
    support — **the claim itself was re-verified and still holds at 3.12.0**
    (TODO comments at `dilithium.cpp:151, 267`; empty context always used), but
    the version reference is dated. Same situation for SLH-DSA context remarks
    (still true at 3.12.0).
50. Cosmetic: Argon2 gained an AVX-512 backend and constant-time modular
    helpers; doc never enumerates SIMD backends. Argon2 parameter bounds
    (p ≤ 128, M ≤ 2^23 KiB) verified correct.

Consistent by construction: HSS/LMS (zero diff), ML-KEM (`final` annotations
only), SLH-DSA (unused-member removal), Classic McEliece (`final` only),
DLIES/ECIES (zero diff), 11_kdf claims (SP800-56C one-step rewrite is
behavior-preserving except zero-length output now allowed — not documented).

---

## Front matter

- `00_01_changelog.rst` has no 3.12.0 entry yet (latest row: 3.11.0).
- `config/botan.env` already targets `BOTAN_VERSION/BOTAN_REF = 3.12.0`,
  `BOTAN_BASE_REF = 3.11.0`.

## Suggested priorities

1. 09_x509.rst items 1–13 (path-validation restructuring, revocation-skip
   logic, OCSP responder pre-checks and `>=` change, strict DER, new status
   codes) — the chapter's control flow no longer matches 3.12.0.
2. 07_rng.rst item 21 (nonexistent reseed macros / phantom timeout — includes
   re-fixing the earlier A6 edit) and items 22–29.
3. 02_sym_enc.rst items 38–39 (GCM limit, AEAD zeroization — both currently
   asserted in the doc with opposite sign).
4. 05_01/05_03/05_04 items 30–34 (check_key semantics, decode-time
   validation, RSA limits).
5. New-behavior sections (B items) as needed for audit-report coverage of the
   3.12 release; changelog entry for 3.12.0.
