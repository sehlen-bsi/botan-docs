Public Key-based Encryption Algorithms
======================================

Public Key-based Encryption Algorithms are divided into hybrid
encryption schemes and public key encryption schemes. Some public
key-based encryption algorithms use test classes implemented in
*src/tests/test\_pubkey.cpp*.

Hybrid Encryption Schemes
-------------------------

DLIES
~~~~~

The Discrete Logarithm Integrated Encryption Scheme (DLIES) is tested
with the following constraints:

-  Number of test cases: 37
-  Source: Generated with BouncyCastle
-  KDF: KDF1-18033
-  Hash Function: SHA-1, SHA-256, SHA-512
-  MAC: HMAC-SHA1, HMAC-SHA256, HMAC-SHA512
-  IV: 128 bits
-  X1: 232 bits
-  X2: 232 bits
-  Group (P, Q, G): 2048 bits (MODP Group, RFC 3526)
-  Cipher: XOR, AES-256/GCM
-  Msg: 256 bits
-  Ciphertext: 2432 bits - 2944 bits

All the tests are implemented in *src/tests/test\_dlies.cpp*. The
following table shows an example test case with one test vector. All
test vectors are listed in *src/tests/data/pubkey/dlies.vec*.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKENC-DLIES-1                                                           |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encrypt and decrypt a secret                                            |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    KDF = KDF1-18033(SHA-512)                                            |
   |                        |    MAC = HMAC(SHA-512)                                                  |
   |                        |    Group = modp/ietf/2048                                               |
   |                        |    IV = 0x00112233445566778899aabbccddeeff                              |
   |                        |    X1 = 0x4316760088048858173826993660634587631078362099236037980378049 |
   |                        |    883427191                                                            |
   |                        |    X2 = 0x3824157470039532100357278938102046076290169354062923298804711 |
   |                        |    018976423                                                            |
   |                        |    Msg = 0x75dad921764736e389c4224daf7b278ec291e682044742e2e9c7a025b54d |
   |                        |    d62f                                                                 |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    Ciphertext = 0x57DFAFA0D81AC3AACA2570AD13CCCD127239F4EE04843BB738234 |
   |                        |    588F0DAEA53CCD8AF65A5A00ED19FBB6F2EB57779FF2E38E3D5D27986253A1193DAB |
   |                        |    F14D2402E1A33527866FA21F23F7ABBEE5F454AAD762FC90139C8377BF6CC77AF7F9 |
   |                        |    82404BAEA5CA4831DD8ED28BABF2D43B1F65EFF42167B82F020DFD4928D8E96DCB78 |
   |                        |    45ECF8F560FBBF5646FAE5BC4EDA6D978E5FB333843A1F4525CFBDDE756842A1E353 |
   |                        |    F4DE1503738EEC6C9D901A78CDEFEDF8DAAA49631DA674B44CAB2193C778BF297667 |
   |                        |    30A656B42E96F84698F77913C718067048263034CF2A2F34572AB662E4B1C5B04CD7 |
   |                        |    1183433C591ABD5613820544D46F7462BEA57E44F23AB06E0FB9A0B0CAB5C285FB0C |
   |                        |    B1F788213B6B82A2C2E485C1D514BAEF7FC241D57DB031D9E80361C55B562232759A |
   |                        |    660C89E0DE0E11BB8C807142C1C98C07C9BD08BFC7A3D9977133AD07DDED60728B46 |
   |                        |    D668444A74BC001CFBFB8E8FE0BACF6A4078DD4212DC7CDC3291CB3F02AC0B7CDF6E |
   |                        |    65D                                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create a DH_PrivateKey object *P1* from *P, Q, G* and *X1*           |
   |                        |                                                                         |
   |                        | #. Create a DH_PrivateKey object *P2* from *P, Q, G* and *X2*           |
   |                        |                                                                         |
   |                        | #. Use P1, P2, the *KDF*, *MAC* and *IV* to encrypt the *Msg* and       |
   |                        |    compare with *Ciphertext*                                            |
   |                        |                                                                         |
   |                        | #. Use P2, P1, the *KDF*, *MAC* and *IV* to decrypt the *Ciphertext*    |
   |                        |    and compare with *Msg*                                               |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKENC-DLIES-2                                                           |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Invalid signatures should not verify                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    KDF = KDF1-18033(SHA-512)                                            |
   |                        |    MAC = HMAC(SHA-512)                                                  |
   |                        |    Group = modp/ietf/2048                                               |
   |                        |    IV = 0x00112233445566778899aabbccddeeff                              |
   |                        |    X1 = 0x4316760088048858173826993660634587631078362099236037980378049 |
   |                        |    883427191                                                            |
   |                        |    X2 = 0x3824157470039532100357278938102046076290169354062923298804711 |
   |                        |    018976423                                                            |
   |                        |    Msg = 0x75dad921764736e389c4224daf7b278ec291e682044742e2e9c7a025b54d |
   |                        |    d62f                                                                 |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Invalid ciphertexts should not decrypt correctly                        |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create a DH_PrivateKey object *P1* from *P, Q, G* and *X1*           |
   |                        |                                                                         |
   |                        | #. Create a DH_PrivateKey object *P2* from *P*, *Q*, *G* and *X2*       |
   |                        |                                                                         |
   |                        | #. Use P2, P1, the *KDF*, *MAC* and *IV* to decrypt the *Ciphertext*    |
   |                        |    and compare with *Msg*                                               |
   +------------------------+-------------------------------------------------------------------------+

ECIES
~~~~~

The Elliptic Curve Integrated Encryption Scheme (ECIES) is tested with
the following constraints:

-  Number of test vectors: 2
-  Source: ISO/IEC 18033-2:2006
-  Format: uncompressed, compressed
-  P: 192 bits
-  A: 192 bits
-  B: 191 bits
-  MU: 192 bits (order)
-  NU: 8 bits (cofactor)
-  Gx: 189 bits (base point x)
-  Gy: 187 bits (base point y)
-  Hx: 189 bits (x of public point of bob)
-  Hy: 191 bits (y of public point of bob)
-  X: 192 bits (private key of bob)
-  R: 188 bits (ephemeral private key of alice)
-  C0: 200 bits, 392 bits (expected encoded ephemeral public key)
-  K: 1024 bits (expected derived secret)
-  Cofactor Mode: enabled, disabled
-  Old Cofactor Mode: enabled, disabled
-  Check Mode: enabled, disabled
-  Single Hash Mode: enabled, disabled
-  Kdf: KDF2(SHA-1)
-  Cipher: AES-256/CBC (cipher used to encrypt data)
-  CipherKeyLen: 256 bits
-  Mac: HMAC(SHA-1) (MAC used to authenticate data)
-  MacKeyLen: 160 bits

All the tests are implemented in *src/tests/test\_ecies.cpp*. All test
vectors are listed in *src/tests/data/pubkey/ecies-18033.vec*. It
contains only two test vectors, but all combinations of cofactor mode,
single hash mode, old cofactor mode, check mode and compression mode are
tested with these two test vectors, so all in all, 96 test cases are
executed, 48 tests for each test vector. As only one of the modes
cofactor mode, old cofactor mode and check mode can be enabled at a
time, the test cases where two or more of these modes are enabled do not
encrypt/decrypt, but instead only check that the combination of these
modes lead to an exception (negative test). In the following one
positive and one negative test is shown.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKENC-ECIES-1                                                           |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Derive a shared secret and encrypt/decrypt                              |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | P = 0xfffffffffffffffffffffffffffffffeffffffffffffffff                  |
   |                        |                                                                         |
   |                        | A = 0xfffffffffffffffffffffffffffffffefffffffffffffffc                  |
   |                        |                                                                         |
   |                        | B = 0x64210519e59c80e70fa7e9ab72243049feb8deecc146b9b1                  |
   |                        |                                                                         |
   |                        | MU = 0xffffffffffffffffffffffff99def836146bc9b1b4d22831                 |
   |                        |                                                                         |
   |                        | NU = 0x01                                                               |
   |                        |                                                                         |
   |                        | Gx = 0x188da80eb03090f67cbf20eb43a18800f4ff0afd82ff1012                 |
   |                        |                                                                         |
   |                        | Gy = 0x07192b95ffc8da78631011ed6b24cdd573f977a11e794811                 |
   |                        |                                                                         |
   |                        | Hx = 0x1cbc74a41b4e84a1509f935e2328a0bb06104d8dbb8d2130                 |
   |                        |                                                                         |
   |                        | Hy = 0x7b2ab1f10d76fde1ea046a4ad5fb903734190151bb30cec2                 |
   |                        |                                                                         |
   |                        | X = 0xb67048c28d2d26a73f713d5ebb994ac92588464e7fe7d3f3                  |
   |                        |                                                                         |
   |                        | Format = uncompressed                                                   |
   |                        |                                                                         |
   |                        | Cofactor Mode = enabled                                                 |
   |                        |                                                                         |
   |                        | Old Cofactor Mode = disabled                                            |
   |                        |                                                                         |
   |                        | Single Hash Mode = disabled                                             |
   |                        |                                                                         |
   |                        | Check Mode = disabled                                                   |
   |                        |                                                                         |
   |                        | Kdf = KDF2(SHA-1)                                                       |
   |                        |                                                                         |
   |                        | Cipher = AES-256/CBC                                                    |
   |                        |                                                                         |
   |                        | CipherKeyLen = 256 bits                                                 |
   |                        |                                                                         |
   |                        | Mac = HMAC(SHA-1)                                                       |
   |                        |                                                                         |
   |                        | MacKeyLen = 160 bits                                                    |
   |                        |                                                                         |
   |                        | Plaintext = 0x010203                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | K =                                                                     |
   |                        | 0x9a709adeb6c7590ccfc7d594670dd2d74fcdda3f862                           |
   |                        | 2f2dbcf0f0c02966d5d9002db578c989bf4a5cc896d2a11d74e0c51efc1f8ee784897ab |
   |                        | 9b865a7232b5661b7cac87cf4150bdf23b015d7b525b797cf6d533e9f6ad49a4c6de5e7 |
   |                        | 089724c9cadf0adf13ee51b41be6713653fc1cb2c95a1d1b771cc7429189861d7a829f3 |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create an ECDH_PrivateKey object *PR1* from *P, A, B, Gx, Gy, MU,    |
   |                        |    NU,* *X*                                                             |
   |                        |                                                                         |
   |                        | #. Create an ECDH_PublicKey object *PU1* P, A, B, Hx, Hy                |
   |                        |                                                                         |
   |                        | #. Create an ECDH_PrivateKey object *PR2* from *P, A, B, Gx, Gy, MU,    |
   |                        |    NU,* *R*                                                             |
   |                        |                                                                         |
   |                        | #. Encode the public point of *PR2* using *Format* and compare with     |
   |                        |    expected output *C0*                                                 |
   |                        |                                                                         |
   |                        | #. Use PR1 and PU1 to derive a shared secret of 128 bytes using         |
   |                        |    KDF1-18033(SHA-1) and *Format* and compare with expected output *K*  |
   |                        |                                                                         |
   |                        | #. Create an ECIES_System_Params object ESP from *P*, *A*, *B*, *Kdf*,  |
   |                        |    *Cipher*, *CipherKeyLen*, *Mac*, *MacKeyLen*, *Format* and *Cofactor |
   |                        |    Mode*, *Old Cofactor Mode*, *Single Hash Mode* and *Check Mode*      |
   |                        |                                                                         |
   |                        | #. Create an ECIES_Encryptor from PR1 and ESP                           |
   |                        |                                                                         |
   |                        | #. Set the public point of PR2 as the public key of the other party on  |
   |                        |    the ECIES_Encryptor                                                  |
   |                        |                                                                         |
   |                        | #. Create an ECIES_Decryptor from PR2 and ESP                           |
   |                        |                                                                         |
   |                        | #. Set the public point of PR2 as the public key of the other party on  |
   |                        |    the ECIES_Decryptor                                                  |
   |                        |                                                                         |
   |                        | #. Set the IV on the ECIES_Encryptor to 16 zero bytes                   |
   |                        |                                                                         |
   |                        | #. Set the IV on the ECIES_Decryptor to 16 zero bytes                   |
   |                        |                                                                         |
   |                        | #. Encrypt the *Plaintext* using the ECIES_Encryptor                    |
   |                        |                                                                         |
   |                        | #. Decrypt the ciphertext generated by the previous step using the      |
   |                        |    ECIES_Decryptor and compare the output with the *Plaintext*          |
   |                        |                                                                         |
   |                        | #. Negate the last byte of the previously generated ciphertext and      |
   |                        |    check that decryption using the ECIES_Decryptor throws an exception  |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKENC-ECIES-2                                                           |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Derive a shared secret test that encrypt/decrypt is not possible using  |
   |                        | the combination of cofactor mode, old cofactor mode and check mode      |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | P = 0xfffffffffffffffffffffffffffffffeffffffffffffffff                  |
   |                        |                                                                         |
   |                        | A = 0xfffffffffffffffffffffffffffffffefffffffffffffffc                  |
   |                        |                                                                         |
   |                        | B = 0x64210519e59c80e70fa7e9ab72243049feb8deecc146b9b1                  |
   |                        |                                                                         |
   |                        | MU = 0xffffffffffffffffffffffff99def836146bc9b1b4d22831                 |
   |                        |                                                                         |
   |                        | NU = 0x01                                                               |
   |                        |                                                                         |
   |                        | Gx = 0x188da80eb03090f67cbf20eb43a18800f4ff0afd82ff1012                 |
   |                        |                                                                         |
   |                        | Gy = 0x07192b95ffc8da78631011ed6b24cdd573f977a11e794811                 |
   |                        |                                                                         |
   |                        | Hx = 0x1cbc74a41b4e84a1509f935e2328a0bb06104d8dbb8d2130                 |
   |                        |                                                                         |
   |                        | Hy = 0x7b2ab1f10d76fde1ea046a4ad5fb903734190151bb30cec2                 |
   |                        |                                                                         |
   |                        | X = 0xb67048c28d2d26a73f713d5ebb994ac92588464e7fe7d3f3                  |
   |                        |                                                                         |
   |                        | Format = uncompressed                                                   |
   |                        |                                                                         |
   |                        | Cofactor Mode = enabled                                                 |
   |                        |                                                                         |
   |                        | Old Cofactor Mode = enabled                                             |
   |                        |                                                                         |
   |                        | Single Hash Mode = disabled                                             |
   |                        |                                                                         |
   |                        | Check Mode = disabled                                                   |
   |                        |                                                                         |
   |                        | Kdf = KDF2(SHA-1)                                                       |
   |                        |                                                                         |
   |                        | Cipher = AES-256/CBC                                                    |
   |                        |                                                                         |
   |                        | CipherKeyLen = 256 bits                                                 |
   |                        |                                                                         |
   |                        | Mac = HMAC(SHA-1)                                                       |
   |                        |                                                                         |
   |                        | MacKeyLen = 160 bits                                                    |
   |                        |                                                                         |
   |                        | Plaintext = 0x010203                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | K =                                                                     |
   |                        | 0x9a709adeb6c7590ccfc7d594670dd2d74fcdda3f862                           |
   |                        | 2f2dbcf0f0c02966d5d9002db578c989bf4a5cc896d2a11d74e0c51efc1f8ee784897ab |
   |                        | 9b865a7232b5661b7cac87cf4150bdf23b015d7b525b797cf6d533e9f6ad49a4c6de5e7 |
   |                        | 089724c9cadf0adf13ee51b41be6713653fc1cb2c95a1d1b771cc7429189861d7a829f3 |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create an ECDH_PrivateKey object *PR1* from *P, A, B, Gx, Gy, MU,    |
   |                        |    NU,* *X*                                                             |
   |                        |                                                                         |
   |                        | #. Create an ECDH_PublicKey object *PU1* P, A, B, Hx, Hy                |
   |                        |                                                                         |
   |                        | #. Create an ECDH_PrivateKey object *PR2* from *P, A, B, Gx, Gy, MU,    |
   |                        |    NU,* *R*                                                             |
   |                        |                                                                         |
   |                        | #. Encode the public point of *PR2* using *Format* and compare with     |
   |                        |    expected output *C0*                                                 |
   |                        |                                                                         |
   |                        | #. Use PR1 and PU1 to derive a shared secret of 128 bytes using         |
   |                        |    KDF1-18033(SHA-1) and *Format* and compare with expected output *K*  |
   |                        |                                                                         |
   |                        | #. Create an ECIES_System_Params ESP object from *P*, *A*, *B*, *Kdf*,  |
   |                        |    *Cipher*, *CipherKeyLen*, *Mac*, *MacKeyLen*, *Format* and *Cofactor |
   |                        |    Mode*, *Old Cofactor Mode*, *Single Hash Mode* and *Check Mode* and  |
   |                        |    check that it throws an exception                                    |
   +------------------------+-------------------------------------------------------------------------+

Public Key Encryption Algorithms
--------------------------------

RSA
~~~

RSA encryption and decryption are tested with the following constraints:

-  Number of test cases: 148
-  E: 3 - 2147483647
-  P: 256 bits – 1024 bits
-  Q: 256 bits – 1024 bits
-  Msg: 32 bits – 1024 bits
-  Nonce: 88 - 904 bits (optional)
-  Padding: Raw, EME1(SHA-1, SHA-256, SHA-512), EME-PKCS1-v1_5(SHA-1)
-  Ciphertext: 512 bits – 2048 bits

All the tests are implemented in *src/tests/test\_rsa.cpp*. The
following table shows an example test case with one test vector. All
test vectors are listed in *src/tests/data/pubkey/rsaes.vec* and
*src/tests/data/pubkey/rsa\_decrypt.vec*.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKENC-RSAES-1                                                           |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encrypt and decrypt                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    E = 0x3ED19                                                          |
   |                        |    P = 0xD987D71CC924C479D30CD88570A626E15F0862A9A138874F70166842169842 |
   |                        |    15                                                                   |
   |                        |    Q = 0xC5660F33AB35E41CB10A30D3A58354ADB5CC3243342C22E1A5BCCB79C391A5 |
   |                        |    33                                                                   |
   |                        |    Msg = 0x098825DEC8B4DAB5765348CEE92C4C6A527A172E4A4311399B0B02914E75 |
   |                        |    822F1789B583180ADEADE98C200B7B7670D7B9FBA19946F3D8A7FC8322F80CF67C   |
   |                        |    Padding = Raw                                                        |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    Ciphertext = 0xA54A45C5F534A6C727212802CD4B2A0B9D0069EFE32B1D239D3B1 |
   |                        |    3958BC49711E1CA5BB499FBF7402B6006E654C719C5FB7614C7C00699866B3844522 |
   |                        |    8EC7663                                                              |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the *Private\_Key* object from *P, Q, E*                      |
   |                        |                                                                         |
   |                        | #. Decrypt the *Ciphertext* with the Private_Key object and compare     |
   |                        |    with the *Msg*                                                       |
   |                        |                                                                         |
   |                        | #. Encrypt the *Msg* with the Public_Key object and compare with the    |
   |                        |    *Ciphertext*                                                         |
   |                        |                                                                         |
   |                        | #. Decrypt the generated ciphertext from the previous step and compare  |
   |                        |    with the *Msg*                                                       |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKENC-RSAES-2                                                           |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Invalid ciphertexts should not decrypt correctly                        |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    E = 0x3ED19                                                          |
   |                        |    P = 0xD987D71CC924C479D30CD88570A626E15F0862A9A138874F70166842169842 |
   |                        |    15                                                                   |
   |                        |    Q = 0xC5660F33AB35E41CB10A30D3A58354ADB5CC3243342C22E1A5BCCB79C391A5 |
   |                        |    33                                                                   |
   |                        |    Msg = 0x098825DEC8B4DAB5765348CEE92C4C6A527A172E4A4311399B0B02914E75 |
   |                        |    822F1789B583180ADEADE98C200B7B7670D7B9FBA19946F3D8A7FC8322F80CF67C   |
   |                        |    Ciphertext = 0xA54A45C5F534A6C727212802CD4B2A0B9D0069EFE32B1D239D3B1 |
   |                        |    3958BC49711E1CA5BB499FBF7402B6006E654C719C5FB7614C7C00699866B3844522 |
   |                        |    8EC7663                                                              |
   |                        |    Padding = Raw                                                        |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | |                                                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the Private_Key object from *P, Q, E*                         |
   |                        |                                                                         |
   |                        | #. Create a modified version of the *Ciphertext* by changing the length |
   |                        |    of it or by flipping random bits in it                               |
   |                        |                                                                         |
   |                        | #. Decrypt the modified *Ciphertext* compare it to the *Msg*            |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKENC-RSAES-3                                                           |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Decrypt                                                                 |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    E = 0x10001                                                          |
   |                        |    P = 0XFF9E0292F5409327E7FACC2AC663D1727F7002A9186D5F21C1E63C190A39DA |
   |                        |    43C928FD023C80ECBF1ED90810626D1B01EF78F10C784534D0479C36A780514E95CE |
   |                        |    F3E6AF9764265A7D7950950D318BC4B37B5B0BA8BEB84C6B696E1CA40F3334885AD7 |
   |                        |    9B615B7FF473346D65A277D5C8B242D5CDA4C58ADE65A89DA26D45E591           |
   |                        |    Q = 0XCEA44FACA82077997E45D4C03E313CF123291DA1BAEE2164D9842E20287D02 |
   |                        |    596B0FA4471AF95CC9526870E4C265654EAE30D79196448B1804CCF0135A4D06F477 |
   |                        |    F3BB9EFFED0697F345F4470EF566A44424F708FA86F901846ACDEA28A60180FA7446 |
   |                        |    877912FC369E90B882E24D8697329BDBF44E003D5EBA6CC2FDE71622D7           |
   |                        |    Msg = 6628194E12073DB03BA94CDA9EF9532397D50DBA79B987004AFEFE34       |
   |                        |    Padding = OAEP(SHA-256,MGF1(SHA-1))                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    Ciphertext = BEDCB1A91FD19CF7722F800F62FE5AA1D1477BEC1F6C9B46C4C0867 |
   |                        |    9684A8D104C1069292D0D6869880DDF0A1B2FAE77FC7D4F0AA9DEF102709AC47E43E |
   |                        |    FF79BF83B7A6E65EA4A2C36DBDD85D873041E39B971F17E34F1B40B22C29EBA07D49 |
   |                        |    72C62019719505D61214A577FC0A6071F5149E34FC94EAC5CA48799FB17AAFCDBF7E |
   |                        |    F3978F48974C3AD8E7BB2C960BB7421DCC16EE46E8AF90B4856A9D702097F85B774A |
   |                        |    F1814F0DCAE9A597D10E68F92CAFFB9F58FCE8627692E19F7EC9EDDB587AB2C17BC9 |
   |                        |    52FB791297895C6D08C11503C80BDBFBF8A866F3D22CFC1EFECEC0A43E1650448527 |
   |                        |    1A176AB63846E55AFA5E78AB6C86A4BF2E13AB9DAEC1E42C2                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the *Private\_Key* object from *P, Q, E*                      |
   |                        |                                                                         |
   |                        | #. Decrypt the *Ciphertext* with the Private_Key object and compare     |
   |                        |    with the *Msg*                                                       |
   +------------------------+-------------------------------------------------------------------------+
