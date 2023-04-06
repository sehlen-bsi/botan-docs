Changelog
=========

.. table::
   :class: longtable
   :widths: 10 10 65 15

   +---------+---------+---------------------------------------------------------------------------------------------------------------------------------+-------------+
   | Version | Authors | Comment                                                                                                                         | Date        |
   +=========+=========+=================================================================================================================================+=============+
   | 0.1.0   | RK, JSo | Initial version                                                                                                                 | 2016-10-28  |
   +---------+---------+---------------------------------------------------------------------------------------------------------------------------------+-------------+
   | 1.0.0   | RK      | Added SHA-3, AES adjustments                                                                                                    | 2016-11-11  |
   +---------+---------+---------------------------------------------------------------------------------------------------------------------------------+-------------+
   | 1.1.0   | RK, DN  | - Add Botan version Fix page numbers                                                                                            | 2017-01-09  |
   |         |         | - Add public key encryption scheme tests                                                                                        |             |
   |         |         | - Add certificate store tests                                                                                                   |             |
   |         |         | - Add CTR mode tests                                                                                                            |             |
   |         |         | - Add PKCS11 Session and Slot negative tests                                                                                    |             |
   |         |         | - Add 2,048 bits DH test cases                                                                                                  |             |
   |         |         | - Add Entropy Sources tests                                                                                                     |             |
   |         |         | - Update AEAD, Block Cipher, DH, KDF, MAC, Modes, Public-key Encryption, Public-key signature, RNG, X.509 tests to Botan 2.0.0  |             |
   +---------+---------+---------------------------------------------------------------------------------------------------------------------------------+-------------+
   | 1.2.0   | RK      | - Fix CBC-CTS test vectors sizes                                                                                                | 2017-03-02  |
   |         |         | - Specify TLS cipher suites tested                                                                                              |             |
   |         |         | - Add DSA to TLS handshake and policy tests                                                                                     |             |
   |         |         | - Add ECDSA invalid public key tests                                                                                            |             |
   +---------+---------+---------------------------------------------------------------------------------------------------------------------------------+-------------+
   | 1.3.0   | SC      | Update to 2.4.0-RSCS1:                                                                                                          | 2018-05-07  |
   |         |         |                                                                                                                                 |             |
   |         |         | - Fix constraints in test cases (KDF)                                                                                           |             |
   |         |         | - Update paths to test vectors (Certstor, X.509, RNG)                                                                           |             |
   |         |         | - Add test cases for new test vectors or new test functions (X.509, RNG, Public-key signature XMSS, Certstor)                   |             |
   |         |         | - Add/Update test steps in test cases (PKCS11, MAC, KA, Hash functions, Block Ciphers)                                          |             |
   |         |         | - Add/Update description of test cases (X.509, RNG, Public-key signature)                                                       |             |
   +---------+---------+---------------------------------------------------------------------------------------------------------------------------------+-------------+
   | 1.4.0   | RK      | Update to 2.14.0-RSCS1:                                                                                                         | 2020-06-24  |
   |         |         |                                                                                                                                 |             |
   |         |         | - Add/update test cases in AEAD, block ciphers, DSA, ECDSA, RNGs, PKCS#11, TLS, X.509, cipher modes, hash functions             |             |
   +---------+---------+---------------------------------------------------------------------------------------------------------------------------------+-------------+
   | 1.5.0   | RM      | Update to 3.0.0-alpha1 (Git: a19627a):                                                                                          | 2022-07-13  |
   |         |         |                                                                                                                                 |             |
   |         |         | - First document revision in the context of Project 481                                                                         |             |
   |         |         | - Add test cases for the Certificate Store adapter to the operating system's root certificate trust store.                      |             |
   |         |         | - Add System_RNG (regression) test                                                                                              |             |
   |         |         | - Add more X.509 Subject Alternative Name constraint checks                                                                     |             |
   |         |         | - Minor adjustments in the Hash and MAC KAT test procedure (retrying calculation w/o resetting)                                 |             |
   |         |         | - Mention of the BoringSSL test suite for TLS                                                                                   |             |
   +---------+---------+---------------------------------------------------------------------------------------------------------------------------------+-------------+
   | 1.5.1   | RM, FA  | Migrate the document to reStructuredText                                                                                        | 2023-04-01  |
   +---------+---------+---------------------------------------------------------------------------------------------------------------------------------+-------------+
