Changelog
=========

.. table::
   :class: longtable
   :widths: 10 10 65 15

   +---------+----------+---------------------------------------------+------------+
   | Version | Authors  | Comment                                     | Date       |
   +=========+==========+=============================================+============+
   | 1.0.0   | JSo, RK, | Initial version                             | 2016-11-19 |
   |         | TN       |                                             |            |
   +---------+----------+---------------------------------------------+------------+
   | 1.1.0   | JSo, RK, | | Add introduction section                  | 2017-01-09 |
   |         | TN       | | Move all chapters one level up            |            |
   |         |          | | Replace top level chapter                 |            |
   |         |          |   "Certificates" by "X.509 Path             |            |
   |         |          |   Validation"                               |            |
   |         |          | | Add introductionary text and              |            |
   |         |          |   subsections to RNG chapter                |            |
   |         |          | | Fix wrong and add missing                 |            |
   |         |          |   paths to source files in RNG              |            |
   |         |          |   chapters                                  |            |
   |         |          | | Use full path to source files             |            |
   |         |          |   including src/ in all chapters            |            |
   |         |          | | SP800-90A refers to entry in              |            |
   |         |          |   bibliography                              |            |
   |         |          | | Update SP800-90A bibliography             |            |
   |         |          |   entry to revision 1                       |            |
   |         |          | | Add example for keyed hash                |            |
   |         |          |   function to HMAC_DRBG                     |            |
   |         |          | | Add note on platform                      |            |
   |         |          |   availability of System_RNG                |            |
   |         |          | | Add description of HMAC_DRBG              |            |
   |         |          |   constructors                              |            |
   |         |          | | Rework HMAC_DRBG section                  |            |
   |         |          | | Rework X.509 path validation              |            |
   |         |          |   section                                   |            |
   |         |          | | Add chapter on entropy sources            |            |
   +---------+----------+---------------------------------------------+------------+
   | 1.2.0   | RK       | | Add PKCS11_RNG                            | 2017-03-02 |
   |         |          | | Add note on requirements for              |            |
   |         |          |   seeding a DRBG                            |            |
   |         |          | | Remove System_RNG section                 |            |
   |         |          |   heading                                   |            |
   |         |          | | Added a note on the security              |            |
   |         |          |   level of HMAC_DRBG                        |            |
   |         |          | | Update DH group generation                |            |
   |         |          | | Update EC public key checks               |            |
   |         |          | | Update EC blinding                        |            |
   +---------+----------+---------------------------------------------+------------+
   | 1.2.1   | RK       | | Correct RSA blinding operation            | 2017-03-09 |
   |         |          | | Add description for HMAC_DRBG             |            |
   |         |          |   function security_level()                 |            |
   +---------+----------+---------------------------------------------+------------+
   | 1.2.2   | RK       | Correct description and add                 | 2017-04-05 |
   |         |          | default values for function                 |            |
   |         |          | random_prime()                              |            |
   +---------+----------+---------------------------------------------+------------+
   | 1.3.0   | FW, RK   | Update to 2.4.0-RSCS1:                      | 2018-05-07 |
   |         |          |                                             |            |
   |         |          | - Remove ``Win32_CAPI_EntropySource``       |            |
   |         |          | - Add ``System_RNG_EntropySource``          |            |
   |         |          | - Add ``Getentropy`` entropy source         |            |
   |         |          | - Add description of function               |            |
   |         |          |   ``Stateful_RNG::reset_reseed_counter()``  |            |
   |         |          | - Update description of function            |            |
   |         |          |   ``HMAC_DRBG::add_entropy()``              |            |
   |         |          | - Update description of function            |            |
   |         |          |   ``rdrand()``                              |            |
   |         |          | - Update description of function            |            |
   |         |          |   ``rdrand_status()``                       |            |
   |         |          | - Update set of default entropy sources     |            |
   |         |          | - Add description of ``BCryptGenRandom``    |            |
   |         |          |   and ``arc4random`` usage in               |            |
   |         |          |   ``System_RNG``                            |            |
   |         |          | - Update description of section             |            |
   |         |          |   X.509 Path Validation                     |            |
   |         |          | - Add note that maximum supported key       |            |
   |         |          |   length for HMAC is 4096 Bytes             |            |
   +---------+----------+---------------------------------------------+------------+
   | 1.3.1   | SC       | - Update AES Block Cipher                   | 2018-05-25 |
   |         |          |   (AES-ARMV8 support)                       |            |
   |         |          | - Update AES-GCM (CLMUL and PMUL support)   |            |
   +---------+----------+---------------------------------------------+------------+
   | 1.3.2   | FW       | - Update chapter 10.2                       | 2018-08-29 |
   |         |          | - Add remark on multithreaded               |            |
   |         |          |   implementation of XMSS signatures.        |            |
   |         |          | - Add remark on randomization in blinded    |            |
   |         |          |   EC point multiplication                   |            |
   +---------+----------+---------------------------------------------+------------+
   | 1.4.0   | PL       | Update to 2.14.0-RSCS1:                     | 2020-06-24 |
   |         |          |                                             |            |
   |         |          | - Add new SHA2, SHA3 hardware               |            |
   |         |          |   implementations                           |            |
   |         |          | - Add new AES hardware implementations      |            |
   |         |          | - Add AES-CCM                               |            |
   |         |          | - Update prime number generation            |            |
   |         |          | - Update random number generation for       |            |
   |         |          |   probabilistic public key algorithms       |            |
   |         |          | - Update key generation for public key      |            |
   |         |          |   algorithms                                |            |
   |         |          | - Update XMSS to RFC 8391                   |            |
   |         |          | - Update asymmetric encryption and key      |            |
   |         |          |   exchange schemes                          |            |
   |         |          | - Update signatures                         |            |
   |         |          | - Update HMAC_DRBG, systems RNGs,           |            |
   |         |          |   hardware RNGs                             |            |
   |         |          | - Update entropy sources                    |            |
   |         |          | - Update path validation                    |            |
   +---------+----------+---------------------------------------------+------------+
   | 1.5.0   | PL, RM   | Update to 3.0.0-alpha1:                     | 2022-11-03 |
   |         |          |                                             |            |
   |         |          | - AES software implementation changed       |            |
   |         |          | - Update prime number generation            |            |
   |         |          | - Update Parameter Generation for           |            |
   |         |          |   Public Key Algorithms                     |            |
   |         |          | - Update RSA-OAEP                           |            |
   |         |          | - Update RNG                                |            |
   |         |          | - Update entropy                            |            |
   |         |          | - Update X509                               |            |
   |         |          | - ``CMAC::poly_double()`` removed           |            |
   |         |          | - Adapt to file moves                       |            |
   +---------+----------+---------------------------------------------+------------+
   | 3.1.1   | FA, RM,  | Update to 3.1.1:                            | 2023-08-21 |
   |         | AT, PL   |                                             |            |
   |         |          | - Document version is now synchronized with |            |
   |         |          |   the respective Botan release version      |            |
   |         |          | - Asymmetric algorithm chapters are now     |            |
   |         |          |   structured by algorithm not by operation  |            |
   |         |          | - XMSS with NIST's keygen and parameters    |            |
   |         |          | - Hash truncation in ECKCDSA                |            |
   |         |          | - Implementation updates in the RNG and     |            |
   |         |          |   random generation of big integers         |            |
   |         |          | - New PQC algorithms                        |            |
   |         |          |   - Kyber                                   |            |
   |         |          |   - Dilithium                               |            |
   |         |          |   - SPHINCS+                                |            |
   |         |          | - New classical algorithms                  |            |
   |         |          |   - Argon2                                  |            |
   |         |          |   - Blake2b                                 |            |
   |         |          |   - SHAKE                                   |            |
   |         |          |   - HKDF                                    |            |
   +---------+----------+---------------------------------------------+------------+
   | 3.2.0   | FA, RM   | Update to 3.2.0:                            | 2023-10-09 |
   |         |          |   - Reflect Keccak permutation refactoring  |            |
   |         |          |   - Update source references                |            |
   +---------+----------+---------------------------------------------+------------+
   | 3.3.0   | FA, RM,  | Update to 3.3.0:                            | 2024-02-20 |
   |         | AT       |                                             |            |
   |         |          | - New PQC algorithms                        |            |
   |         |          |   - FrodoKEM                                |            |
   |         |          | - New classical algorithms                  |            |
   |         |          |   - Blake2s                                 |            |
   |         |          | - SHA-512 based on dedicated instructions   |            |
   |         |          |   on ARM v8.2                               |            |
   +---------+----------+---------------------------------------------+------------+
   | 3.4.0   | FA, RM   | Update to 3.4.0:                            | 2024-04-08 |
   |         |          |                                             |            |
   |         |          | - Detailed explanation of counter-measures  |            |
   |         |          |   against KyberSlash side-channel attack    |            |
   |         |          | - X.509 path validation may optionally      |            |
   |         |          |   ignore the validity interval of a trusted |            |
   |         |          |   self-signed root certificate              |            |
   +---------+----------+---------------------------------------------+------------+
   | 3.5.0   | FA, PL,  | Update to 3.5.0:                            | 2024-07-18 |
   |         | RM       |                                             |            |
   |         |          | - New PQC algorithms                        |            |
   |         |          |   - HSS/LMS                                 |            |
   |         |          | - NIST SP800-56Cr2 One-Step KDM with KMAC   |            |
   |         |          | - Mention the existing KMAC implementation  |            |
   |         |          | - Adaptions of X.509 path validation        |            |
   |         |          | - Minor updates on ECC details              |            |
   +---------+----------+---------------------------------------------+------------+
   | 3.6.1   | FA, AT,  | Update to 3.6.1:                            | 2025-02-27 |
   |         | RM       |                                             |            |
   |         |          | - Add Standardized PQC Algorithms           |            |
   |         |          |   - ML-KEM (replacing Kyber)                |            |
   |         |          |   - ML-DSA (replacing Dilithium)            |            |
   |         |          |   - SLH-DSA (replacing SPHINCS+)            |            |
   |         |          | - New implementation of internal ECC math   |            |
   |         |          | - Support for TPM 2.0                       |            |
   |         |          |   - Random number generation                |            |
   |         |          |   - Hosted RSA/ECC private keys             |            |
   |         |          | - Wrapper for "jitterentropy-library"       |            |
   +---------+----------+---------------------------------------------+------------+
   | 3.7.1   | FA, AT,  | Update to 3.7.1-RSCS1:                      | 2025-03-28 |
   |         | RM       |                                             |            |
   |         |          | - Add PQC Algorithm Classic McEliece as     |            |
   |         |          |   specified in the latest ISO draft         |            |
   |         |          | - Rework the elliptic curve documentation   |            |
   |         |          | - Update blinding mechanism of RSA decrypt  |            |
   |         |          | - DSA signing now uses additional blinding  |            |
   |         |          | - Update NIST SP.800-108 KDF description    |            |
   +---------+----------+---------------------------------------------+------------+
   | 3.11.0  | JR, FS   | Update to 3.11.0:                           | 2026-05-28 |
   |         |          |                                             |            |
   |         |          | - Support ML-KEM expanded key format.       |            |
   |         |          | - Update description of ECDSA side-         |            |
   |         |          |   channel countermeasures.                  |            |
   |         |          | - Update blinding size in                   |            |
   |         |          |   "Multiplication of Scalar k and Point P". |            |
   |         |          | - Transition to                             |            |
   |         |          | - `Stateful_Key_Index_Registry`.            |            |
   |         |          | - Annotate references to FIPS-186 due to    |            |
   |         |          |   transition to FIPS-186-5. This outdates   |            |
   |         |          |   the references to the paragraph A.1.1.2   |            |
   |         |          |   in [FIPS-186-4] about prime generation    |            |
   |         |          |   and the Lucas primality test as           |            |
   |         |          |   implemented in Botan.                     |            |
   |         |          |                                             |            |
   |         |          |                                             |            |
   +---------+----------+---------------------------------------------+------------+
   | 3.12.0  | FS       | Update to 3.12.0:                           | 2026-08-26 |
   |         |          |                                             |            |
   |         |          | - X.509: strict DER decoding of PKIX        |            |
   |         |          |   structures                                |            |
   |         |          | - X.509: reworked path building with        |            |
   |         |          |   bounded search (new status code           |            |
   |         |          |   EXCEEDED_SEARCH_LIMITS)                   |            |
   |         |          | - X.509: optional non-self-signed           |            |
   |         |          |   trust anchors and trusted OCSP            |            |
   |         |          |   responder certificates                    |            |
   |         |          | - X.509: OCSP hardening, structural         |            |
   |         |          |   CRLDP matching, IPv6 name                 |            |
   |         |          |   constraints and SAN matching              |            |
   |         |          | - Stricter public key checks at             |            |
   |         |          |   construction/decoding and extended        |            |
   |         |          |   ``check_key()`` descriptions              |            |
   |         |          | - AEAD modes zeroize output on              |            |
   |         |          |   authentication failure; GCM/CCM           |            |
   |         |          |   message length limits enforced            |            |
   |         |          | - HMAC_DRBG requires at least 160 bit       |            |
   |         |          |   MAC output                                |            |
   |         |          | - Entropy source platform defaults          |            |
   |         |          |   updated; Jitter RNG available as an       |            |
   |         |          |   entropy source                            |            |
   |         |          | - New figure on the HMAC_DRBG reseed        |            |
   |         |          |   mechanism                                 |            |
   +---------+----------+---------------------------------------------+------------+
