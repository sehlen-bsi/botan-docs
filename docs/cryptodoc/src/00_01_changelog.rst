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
   |         |          | | Add introductary text and                 |            |
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
   |         |          | - Hash trunction in ECKCDSA                 |            |
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
