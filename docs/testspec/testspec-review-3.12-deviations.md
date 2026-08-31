# Testspec review vs. Botan 3.12.0 — deviation log

Full verification of docs/testspec/src/*.rst against the Botan test suite at
tag 3.12.0 (all code references verified via `git show 3.12.0:<path>` /
raw.githubusercontent.com at the tag). Review performed 2026-08-18, log
consolidated 2026-08-20.

Classification legend: A = spec already wrong at the 3.7.1 baseline,
C711 = caused by a code change between 3.7.1 and 3.11.0 (documented in
testspec-changes-3.12.html, Part II), C312 = caused by a change between
3.11.0 and 3.12.0, R = error in a 3.12.0 review remark (all fixed).

Items marked [RESOLVED] were already fixed in the working tree before the
correction pass. All remaining items were corrected directly in the test
descriptions on 2026-08-20 (without review remarks). During the correction
pass every fact was re-verified against sources and test vector files
fetched from the randombit/botan repository at tag 3.12.0; several counts
turned out to have drifted further than logged (cbc.vec: 281 cases,
ctr.vec: 821 cases, dh.vec: 40 entries) and the corrections use the
re-measured values.


## Ch 17 X.509 (agent done) — 5 deviations, all A
1. A — X509-test-1 (~L153): expected output should be "CA certificate not allowed to issue certs" (x509test/expected.txt#L2).
2. A — X509-BSI-test-1 notes (~L203): dir is bsi/common_01 not cert_path_common_01 (renamed pre-3.7.1, commit f246428bb).
3. A — "All test vectors in name_constraint/" (~L246): tables 3–5 implemented in test_x509_path.cpp with data name_constraint_san/ (#L537-539), misc/name_constraint_ci/ (#L578-580), misc/nc_skip_self/ (#L617-619).
4. A — X509-name-constraint-5 notes (~L479): files are misc/nc_skip_self/{root,int,leaf}.pem not misc/name_constraint_ci/... (copy-paste error).
5. A — OCSP online test (~L538): test_online_request checks DigiCert intermediate (test_ocsp.cpp#L381-L409), not randombit.net; changed pre-3.7.1 (f7a4fcfb1). Offline tests still use randombit.net responses.
All fresh 3.12.0 remarks in ch17 verified accurate.

## Ch 01 AEAD (agent done) — 9 deviations
1.1 A — AEAD-2 step 3: default-nonce-length check only in test_enc (test_aead.cpp#L41-43), not in decryption test (#L202-235). Drop step.
1.2 A — AEAD-2 steps 8–11 wrong order/duplicate: actual = set modified AD (L242), two decrypt-before-nonce throw checks (L244-253), set modified nonce once (L255), update() random data (L256-257).
1.3 A — AEAD-1 step 15: empty message doesn't "Return"; finish() still compared and clear-steps 18–20 run; only blockwise 16–17 skipped (#L106-111, #L186-197).
1.4 A — AEAD-2 step 6: "AEAD_Encryption object" → Decryption object (#L240).
1.5 C711+C312 [RESOLVED] — gcm.vec count 43 → 47 AES (55 total incl ARIA/SM4). +1 from 03d532aa6 PR #5273 (3.11.0); +3 AES (+4 ARIA/SM4) from 5f59ae342 PR #5474 (3.11.1).
1.6 C312 [RESOLVED] — AD list missing 256 bits (from 5f59ae342/PR #5474 vectors).
1.7 A [RESOLVED] — Out length list wrong from the start; actual {128..8320} bits, no 64-bit Out.
1.8 A [RESOLVED] — Block cipher list omits AES-192 (gcm.vec#L89-153).
1.9 R [RESOLVED] — fresh 3.12.0 remark attributes new gcm.vec long-message vectors to GH #5521; actually 5f59ae342 via PR #5474 (AVX2 CTR, 3.11.1). GH #5521 doesn't touch gcm.vec. "OpenSSL 3.6" attribution correct. FIX REMARK.

## Ch 03 Block ciphers (agent done) — 7 deviations
3.1 A — BLOCK-1 step 5: parallel_bytes >= block_size*parallelism (test_block.cpp#L59), not equals.
3.2 A — BLOCK-2/BLOCK-AES-2 step 2: random key of MAXIMUM key length (#L81), not minimum.
3.3 A — BLOCK-2/BLOCK-AES-2 step 3: random plaintext of BLOCK SIZE length (#L82-83), not key length.
3.4 A — BLOCK-3 steps 3–4: decrypts Out and compares vs In (buf = expected; #L122-126), spec says encrypt In then decrypt result.
3.5 A+C711 — aes.vec count 1350 → 1353 (385/452/516). Was 1347 at 3.7.1; +6 from 69e6ae49d PR #5339 (3.11.0).
3.6 A+C711 — AES In/Out length lists: add 512 (AES-128, pre-existing) and 1152+8576 bits per key size (PR #5339, 3.11.0).
3.7 A — AES cpuid claim: add AVX2-VAES (aes.vec#L4 `#test cpuid avx2_vaes aesni ...`).

## Ch 08 Modes (agent done) — 4 deviations
8.1 A — MODE-2 step 8: decrypt Out, compare vs In (test_modes.cpp#L84-85, #L186-188).
8.2 A — MODE-2 step 6: "encryption object" → decryption object (#L180).
8.3 A — cbc.vec constraints: not 3 vectors/512 bits; AES NoPadding = 14 vectors (In 128–1280 bits), plus AES-128/CBC/PKCS7 65 vectors etc.
8.4 A — ctr.vec constraints: not 6 vectors; 185 AES vectors + 5 counter-width variants; In 8–65536 bits; nonce 120 & 128 bits. (AVX2 vector 3.11.1 covered by remark.)

## Ch 02 Cert stores (agent done) — 4 deviations
02-1 A — CERTSTOR-FAC-1 (~L145-174): missing duplicate-DN part; test_certstor.cpp#L238-258 inserts 2 certs with same subject DN from bsi/common_14/{common_14_sub_ca,common_14_wrong_sub_ca}.ca.pem.crt, expects find_all_certs == 2. Pre-3.7.1 (GH #1363, 2.4.0).
02-2 C711 — CERTSTOR-SCH-1 now test_certstor_all_finders (test_certstor.cpp#L268-320): also find_cert_by_issuer_dn_and_serial_number (L294-307); system store got same finder test (test_certstor_system.cpp#L233-253). Commit a9ebb50d1, PR GH #5072, first release 3.10.0. NOT covered by spec anywhere.
02-3 A — CERTSTOR-SYSTEM-2 step (~L307): queries by subject DN (test_certstor_system.cpp#L68-88), not "public key's SHA-1" (copy-paste).
02-4 A — CERTSTOR-SYSTEM-2 preconditions: five alternative UTF-8-DN roots (SSL.com ECC 2022, D-TRUST Class 3 CA 2 EV 2009, TrustAsia G3, T-TeleSec GlobalRoot Class 2, Atos ECC TLS 2021), at least one must be present (test_certstor_utils.cpp#L45-80); no Windows disabling. Since 3.6.0 (GH #4280).

## Ch 04 Entropy (agent done) — 2 deviations
04-1 A+C711 — default sources are {"rdseed","hwrng","getentropy","system_rng","system_stats"} hardcoded in Entropy_Sources::global_sources() (entropy_srcs.cpp#L220-224). Spec's 2.x list wrong already at 3.7.1 (A); macro BOTAN_ENTROPY_DEFAULT_SOURCES removed by 5c411c48a PR GH #4639, first release 3.8.0 (C711).
04-2 A — ENTROPY-1: "added entropy exactly once" → at least once (test_entropy.cpp#L45-48 test_sz_gte).

## Ch 15 RNG (agent done) — 6 deviations, all A
15-1 A — hmac_drbg.vec: 1680 vectors (240 × 7 hashes incl SHA-512-224), not 3360/6 hashes.
15-2 A — nonce requirement: at least FULL security strength (security_level()/8); HMAC-SHA-256 → 32 bytes not 16 (test_rng_behavior.cpp#L228-251, L241).
15-3 A — RNG-HMAC-DRBG-4 SeedData is the 16-byte pattern repeated twice = 32 bytes (#L533-535).
15-4 A — RNG-AUTO-RNG-1: name check `starts_with("HMAC_DRBG(HMAC(SHA-")` (#L728); BOTAN_AUTO_RNG_HMAC macro gone since 3.0.0 (GH #3403).
15-5 A — "SHA-160" → SHA-1 (#L506).
15-6 A — RNG-SYS-RNG-1: sizes 0..127 bytes (#L797-801); 4GiB test needs long+memory-intensive options (#L803); buffer 0xFFFFFFFF+1024 (#L807).

## Ch 10 PKCS#11 (agent done) — 9 deviations, all A
10-1 duplicate tables PKCS11-MODULE-4/5 (one test test_multiple_modules, #L145-153).
10-2 RSA-2: export only check_key(), no comparison (#L650-685).
10-3 RSA-3: set_encrypt(true) not decryption key (#L697-701).
10-4 ECDSA-4: export without comparison (#L993-1023).
10-5 ECDSA-5/6 curve lists swapped: privkey gen secp256r1 only (#L1025-1040); keypair gen secp256r1+brainpool512r1 (#L1064-1081).
10-6 RNG-3: first request 512 bits/64 bytes (#L1440), 2048 bits only after personalization (#L1447); DRBG = HMAC(SHA-512).
10-7 X509-1 path: src/tests/data/x509/nist/test01/end.crt (#L1559), not nist_x509/...
10-8 RNG-1/2/3 + X509-1 preconditions: read-WRITE session (TestSession, Session(*m_slot,false), #L97-106).
10-9 ECDH pub key label "Botan test ECDH pub key" (#L1251, #L1280).

## Ch 18 TPM (agent done) — 1 deviation
18-1 A — TPM-ECDSA-3 step 1: authenticated session via persistent ECC key (test_tpm2.cpp#L1106-1112, #L1171-1189), SRK only parent; since 3.6.0.

## Ch 16 TLS (agent done) — 14 deviations
16-1 A — handshake versions: only TLS 1.2 + DTLS 1.2 (unit_tls.cpp#L912-913, #L969-980); TLS 1.0/1.1/DTLS1.0 removed in 3.0.0.
16-2 A — AES-256 CBC suites not tested; only AES-128 CBC (SHA-1/SHA-256) RSA/ECDHE + 3DES (#L1203-1230); removed 2.5.0.
16-3 A — DHE_DSS_WITH_AES_128_CBC_SHA256 gone (only DHE_RSA, #L1236); DSA removed 3.0.0 (229ca3804).
16-4 A — GCM list: DHE_DSS entries → DHE_RSA_AES_128_GCM over FFDHE-2048 (#L1351-1359); standalone AES-256-GCM entry redundant (#L1267-1290, #L1314-1323).
16-5 A — PSK list: PSK GCM + CCM + CCM(8), ECDHE_PSK uses GCM (#L1394-1404); DHE_PSK removed 3.0.0 (43f6ccabf).
16-6 A [RESOLVED] — custom curve: numsp256d1 (OID 1.3.6.1.4.1.25258.4.1, group 0xFEE1), not secp112r1 (changed 3.5.0, GH #4089); suite ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 (#L1419-1447).
16-7 C312+R [RESOLVED] — custom-curve handshake test DISABLED at 3.12.0 (`const bool disabled = true`, #L1406-1419) by c2f97faa9 GH #5550 ("TLS 1.2 server can't negotiate application-specific group codes"). Fresh remark doesn't mention it. FIX REMARK. (Remark also silently covers ALPN test/3→test/1.)
16-8 A — policy verification: no DSA; RSA 1024/2048, ECDH 192/256, ECDSA 192/256, short-DH negative (unit_tls_policy.cpp#L47-52, #L148-165); uses raw keys not certificates.
16-9 A — TLS-ServerHello-1 AdditionalData = 000B000F00170023FF01 (server_hello.vec#L15-20), incl point formats + heartbeat.
16-10 A — TLS-CertVerify: no Protocol input (cert_verify.vec#L8-9; test_tls_messages.cpp#L106-107); dropped in 3.0.0.
16-11 A — TLS-CertVerify-2 exception: "Expected 2 bytes remaining, only 1 left" (cert_verify.vec#L14-16).
16-12 A — drop "Invalid argument Decoding error:" prefix in all negative-test exception strings (e.g. client_hello.vec#L36-38).
16-13 A — TLS-HelloVerify-2: message is "Bad length in hello verify request" (hello_verify.vec#L23-25), no "Invalid CertificateVerify:" prefix; description says CertificateVerify wrongly.
16-14 A — stream integration: 11 test cases (5 scenarios × async/sync + Test_Conversation_With_Move) (test_tls_stream_integration.cpp#L944-954); With_Move GH #2635 (3.0.0), Handshake_Failure GH #3795 (3.3.0 → C711 for that addition!).

## Ch 11 Pubkey enc (agent done) — 6 deviations, all A
11-1 A — dlies.vec: 72 vectors (42 AES-256/CBC, 22 XOR, 8 AES-256/GCM); KDF1-18033 + KDF2; HMAC + CMAC(AES-256); required MacKeyLen field (test_dlies.cpp#L26). Spec's 37 = KDF1 subset. Example missing MacKeyLen=64 + AES-256/GCM header.
11-2 A — PKENC-DLIES-2/RSAES-2: check_invalid_ciphertexts (test_pubkey.cpp#L88-119) = 5 (20 long) iterations of mutate_vec, single-byte XOR only, never length change; DLIES-2 table lacks corruption steps entirely + wrong title "Invalid signatures should not verify".
11-3 A — ECIES: no cofactor NU; vec fields p,a,b,Order,Gx,Gy,Oid,hx,hy,x,r,C0,K; EC_Group(oid,p,a,b,gx,gy,order) (test_ecies.cpp#L104,L131). mu/nu removed in 3.5.0 (PR #4038) — pre-baseline.
11-4 A — PKENC-ECIES-1 steps 5,7-10: derivation uses ephemeral PR2 vs PU1; encryptor from PR2 w/ PR1 point; decryptor from PR1; no step 10 (test_ecies.cpp#L143-149, #L52-55).
11-5 A — RSA enc constraints: 213 vectors (188 rsaes + 25 rsa_decrypt); Msg 8–1088 bits; paddings Raw, OAEP(SHA-1), EME-PKCS1-v1_5 (no hash), + OAEP SHA-224/256/512 with MGF1 variants + TCPA. 65 odd-key vectors added in 3.7.0 (PR #4467, pre-baseline).
11-6 A — PKENC-RSAES-1 step 4: base provider compares generated ciphertext vs KAT ciphertext; decrypt-generated only for other providers (test_pubkey.cpp#L458-464).

## Ch 12 Pubkey KEM (agent done) — 5 deviations, all A
12-1 A — CMCE: shared secrets stored UNhashed too (test_cmce.cpp#L296-304); only PK/SK hashed SHAKE-256(512).
12-2 A — rsa_kem.vec: 10 vectors (4 ISO 18033-2 + 6 BouncyCastle); KDF1-18033 + KDF2; E=65537 all; P/Q 256 or 1024 bits; K 160/1024/2048; required R input (test_rsa.cpp#L61).
12-3 A — PKENC-RSAKEM-1: key from E,P,Q (no G); encapsulate with PUBLIC key + Fixed_Output_RNG(R) (test_pubkey.cpp#L502-560); example E=65537 not 17.
12-4 A — PKENC-FRODO-2 step 5: mutated CT decapsulated with SECOND key pair (dec2), compared to implicit-rejection value (test_frodokem.cpp#L128-131); only truncation step uses original key.
12-5 A — ML-KEM KATs: CT_N/SS_N only in ml_kem.vec (75), not kyber_kat.vec (test_pubkey_pqc.h#L155-159); PK/SK/CT expected values are 16-byte SHAKE-256(128) digests (SHA-256 for 90s) (test_kyber.cpp#L135-149), also EK/DK/C in ACVP vecs; decapsulation uses generated key after encode/decode roundtrip, not "key from vector".

## Ch 05 Hash (agent done) — 11 deviations
05-1 A — HASH-1 loop is 3× not 5× (test_hash.cpp#L95-98).
05-2 A — chunked/copy-state part: only if input >5 bytes; random-size chunks orig, (1,n-2,1) split for copy (#L127-149); no separate HASH-2 two-chunk test.
05-3 A — HASH-4 TotalLength = total message length in bytes (#L242-283).
05-4 A — md5.vec 78 vectors, 0–128 + 1029 bytes.
05-5 A+C711 — sha1.vec 80 vectors, max 2719 bytes; +2 (211/531 bytes) via 7fef832fb GH #4852 (SHA-1 AVX2/BMI2), 3.9.0.
05-6 A — SHA-224: 3 vectors (0,1,14 bytes).
05-7 A+C711 — SHA-256: 392 vectors, up to 2638 bytes; +1 via GH #4818 (AVX2), 3.8.0.
05-8 A — SHA-512: 138 vectors up to 12800 bytes (spec's 7/896 matches SHA-384).
05-9 A — SHA-512/256: 2 vectors.
05-10 C711 — blake2b.vec REPLACED by 9459cbd71 GH #4748 (3.8.0): 224-bit output removed, now 256/384/512, 771 vectors 0–256 bytes; spec example vector gone.
05-11 A — H-PHASH-1/2 unit tests don't exist; only generic KAT over parallel.vec (4 vectors).

## Ch 06 KDF (agent done) — 8 deviations, all A
06-1 kdf1_iso18033: 4 vectors. 06-2/3/4 SP800-108 ctr/fb/pipe: 299 each, + CMAC(TripleDES) + parameterized sections, Out up to 384 bits, fb salt 128–1312 bits. 06-5 tls_prf: 32 vectors, salt 0–248 bits. 06-6 hkdf.vec 37 vectors; RFC 5869 not 5669. 06-7 example 1 is HKDF-Extract(HMAC(SHA-512)) (hkdf.vec#L88-91). 06-8 example 2 is HKDF(HMAC(SHA-1)) (#L3-7).

## Ch 07 MAC (agent done) — 5 deviations
07-1 A — MAC-2 precondition n>2 (test_mac.cpp#L115-134).
07-2 A+C711 — cmac.vec 39: + Blowfish, Threefish-512 (pre-baseline), + ARIA-128 via 19d85a798 GH #5440 (AVX-512 GFNI ARIA), 3.11.0; In up to 1336 bits.
07-3 A — hmac.vec 73 vectors, 12 hashes, keys 24–1176 bits, In 24–1216 bits.
07-4 C711 — gmac.vec 15→143 vectors (was exactly 15 at 3.7.1, spec matched!): 28e78a056 GH #5257 "more test vectors for GMAC" + 9d040fe57 GH #5418 (AVX-512 CLMUL GHASH), both 3.11.0; In 0–4992 bits; "# Generated by OpenSSL".
07-5 A — KMAC example key is 256 bits (kmac.vec#L20-24) + editorial slips.

## Ch 09 PBKDF (agent done) — 1 deviation
09-1 A — pbkdf2.vec 15 vectors incl CMAC(Blowfish); salt 32–240 bits; passphrase 0–32 chars.

## Ch 13 Pubkey agree (agent done) — 8 deviations
13.1 A — KA-KEY-2..6: check_key only for generated + PEM-public roundtrip (test_pubkey.cpp#L677,L764); others compare name+encoding; password = hex of 1–32 random bytes.
13.2 A — dh.vec: 4 entries KDF2(SHA-1); P also 256/515 bits; K also 768/2048.
13.3 A — DH keygen only modp/ietf/1024 (test_dh.cpp#L114); 2048 removed 2.3.0.
13.4 A — primality: test_prob=128 (65 MR iters + Lucas), not "MR 50 rounds" (dl_group.cpp#L466-497) — also PKSIG-KEY-DSA-1 in ch14.
13.5 A — KA-KEY-DH-INVALID-1: InvalidKey input missing; check_key must return false (test_dh.cpp#L90-110).
13.6 A — ECDH keygen: add brainpool512r1 (test_ecdh.cpp#L45-48).
13.7 A — ecdh.vec 156 entries incl 3 brainpool curves.
13.8 A — prose: 1 < Y < P.

## Ch 14 Pubkey sig (agent done) — 15 deviations
14.1 A — PKSIG-3 uses PUBLIC key (test_pubkey.cpp#L285-307; rsa_invalid E,N — test_rsa.cpp#L128-138).
14.2 A — PKSIG-KEY-2..6 validity steps (same as 13.1).
14.3 A — DSA: dsa_rfc6979.vec (21) used in default build; 302+2 vectors; sigs 320/448/512 bits (test_dsa.cpp#L24-34).
14.4 A — DSA keygen only dsa/jce/1024 (test_dsa.cpp#L107); dsa/botan/2048 removed 2.3.0.
14.5 A — DSA example Msg is 1024-bit value not empty (dsa_prob.vec#L9-16); typos double-0x Q, stray 'a' in Y.
14.6 A+C711 — ECDSA: 12146 total (251 prob + 31 verify + 11864 wycheproof); ecdsa_verify.vec 15→31 via 87eb561c6e7e "Fix ECDSA chosen-key verification forgery" GH #5211, 3.11.0. More curves/sig lengths.
14.7 A — ECDSA keygen: all known_named_groups() (test_ecdsa.cpp#L165-181).
14.8 A — PKSIG-PUBKEY-VAL-ECDSA-1: only EC_AffinePoint::from_bigint_xy construction must fail (#L238-266); no keygen/PEM; source FIPS 186-2 only.
14.9 A — ECGDSA: 12 entries, brainpool only, + RIPEMD-160; example is a copy of ECDSA example, doesn't exist.
14.10 A — ECKCDSA: 11 entries; example X wrong (eckcdsa.vec#L6-12: X=0x562A6F64...); table mislabeled PKSIG-KEY-ECDSA-1.
14.11 A — HSS/LMS: truncation to every byte length 0..len-1 (test_hss_lms.cpp#L153-177), not bits.
14.12 A — RSA sig: rsa_sig.vec 172 entries; E incl 11/65539 no 79; sigs up to 4096 bits; no EMSA1 (removed 3.0.0); example vector gone; ISO 9796-2 DS3 typo.
14.13 A — RSA check_key: E>=3 and odd (rsa.cpp#L212-217).
14.14 A — XMSS: 27 active vectors, none commented; + SHAKE/192-bit param sets; example vectors/key format obsolete (regenerated 3.0.0).
14.15 R [RESOLVED] — fresh remark: 4th malformed sig = ALL-ZERO vector one byte shorter (test_pubkey.cpp#L35-48), not "truncated by one". FIX REMARK.

## ALL AGENTS DONE. Totals: 84 deviations.

## Remark fixes to apply in RST (my own 3.12 remarks):
R1 01_aead.rst — gcm.vec long-message vectors: attribute to AVX2 CTR work GH #5474 (3.11.1), not GH #5521.
R2 16_tls.rst — unit_tls remark: mention custom-curve (numsp256d1) handshake test disabled in 3.12.0 (GH #5550; TLS 1.2 server can't negotiate application-specific groups).
R3 14_pubkey_sig.rst — "signature truncated by one byte" → "all-zero signature one byte shorter than the valid signature".

## C711 items for new HTML part "Changes between 3.7.1 and 3.11.0":
H1 aes.vec +6 long-input vectors (1152/8576 bits): 69e6ae49d, PR #5339, 3.11.0 (spec ch03 AES constraints outdated).
H2 gcm.vec +1 long AES-GCM vector: 03d532aa6, PR #5273, 3.11.0 (spec ch01 count 43→47 incl. 3.11.1 additions).
H3 Cert store issuer-DN+serial finder tests: a9ebb50d1, GH #5072, 3.10.0 (test_certstor.cpp#L268-320 test_certstor_all_finders; test_certstor_system.cpp#L233-253; spec CERTSTOR-SCH-1 covers only hashed-subject-DN).
H4 BOTAN_ENTROPY_DEFAULT_SOURCES macro removed: 5c411c48a, GH #4639, 3.8.0 (entropy_srcs.cpp#L220-224 global_sources(); spec ch04 references macro).
H5 sha1.vec +2 vectors (211/531 bytes): 7fef832fb, GH #4852 (SHA-1 AVX2/BMI2), 3.9.0. (+ SHA-256 +1 vector GH #4818, 3.8.0.)
H6 blake2b.vec replaced (224-bit dropped, 771 vectors): 9459cbd71, GH #4748, 3.8.0 (spec ch05 BLAKE2b section outdated incl. example).
H7 cmac.vec +ARIA-128: 19d85a798, GH #5440, 3.11.0.
H8 gmac.vec 15→143: 28e78a056 GH #5257 + 9d040fe57 GH #5418, 3.11.0 (spec matched exactly at 3.7.1 — cleanest case of drift).
H9 ecdsa_verify.vec 15→31: 87eb561c6e7e, GH #5211 chosen-key verification forgery fix, 3.11.0 (security-relevant regression vectors).
H10 TLS stream integration Test_Handshake_Failure/_Sync: 60cbd26d3, GH #3795, 3.3.0 (spec says 8 test cases, now 11; Test_Conversation_With_Move GH #2635 was 3.0.0 = pre-baseline).

## HTML notes
- File: docs/testspec/testspec-changes-3.12.html (committed in 0cc369c). Style: <section id>, <h2>, p.summary, figure.snippet code-snippet / doc-snippet, figcaption span.path, p.src-link. TOC nav.toc ol. 13 existing sections.
- New section to add: changes between 3.7.1 and 3.11.0 discovered via deviations. Known C711 items so far: gcm.vec +long vectors PR #5273 (3.11.0); aes.vec +6 long vectors PR #5339 (3.11.0). C312 stragglers: gcm.vec PR #5474 vectors (fix remark attribution too).

## Additional findings from the correction pass (2026-08-20, all fixed)

A1 A — 08 CBC-CTS constraints covered only the 6 AES-128 RFC 3962 vectors;
cbc.vec also contains [DES/CBC/CTS] with 42 vectors (Key 64 bits, In/Out
72-400 bits). Constraints extended to 48 test cases over AES-128 and DES.
A2 A — 13 KA-KEY-6 steps 2/3 were inverted (public-key validity check
listed before the keypair generation); order fixed to match the code
(test_pubkey.cpp: create_private_key, then check_key/strength).
A3 A — 14 PKSIG-4 input list said "P, Q, E: RSA parameters" although the
verification KAT builds a public key; actual vector keys are E,N
(test_rsa.cpp RSA_Signature_Verify_Tests, "E,N,Msg,Signature"). Inputs and
step 1 fixed to E, N.
