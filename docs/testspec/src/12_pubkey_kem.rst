Public Key Encapsulation Mechanisms
-----------------------------------

Kyber
~~~~~

The implementation is tested for correctness using the Known Answer Test vectors
demanded by the NIST submission and provided by the reference implementation.

Additionally, Botan has implementation-specific test cases. Those ensure the
interoperability of the algorithm when using Botan's generic API for public key
algorithms. These test cases are equal for all public key schemes and are
therefore not discussed in detail in this chapter.

All kyber-specific test code can be found in :srcref:`src/tests/test_kyber.cpp`.
Relevant test data vectors for the KAT tests are in
*src/tests/data/pubkey/kyber\_\*.vec* where *\** is a placeholder for the
algorithm parameters, namely *512*, *512_90s*, *768*, *768_90s*, *1024* and
*1024_90s*.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKENC-KYBER-1                                                           |
   +========================+=========================================================================+
   | **Type:**              | Known Answer Tests                                                      |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Uses the KAT vectors of Kyber's reference implementation as specified   |
   |                        | in the NIST submission                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Test Vectors with RNG seed inputs in:                                   |
   |                        |                                                                         |
   |                        | * :srcref:`src/tests/data/pubkey/kyber_512_90s.vec`                     |
   |                        | * :srcref:`src/tests/data/pubkey/kyber_768_90s.vec`                     |
   |                        | * :srcref:`src/tests/data/pubkey/kyber_1024_90s.vec`                    |
   |                        | * :srcref:`src/tests/data/pubkey/kyber_512.vec`                         |
   |                        | * :srcref:`src/tests/data/pubkey/kyber_768.vec`                         |
   |                        | * :srcref:`src/tests/data/pubkey/kyber_1024.vec`                        |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Above described test vector files contain expected values for:          |
   |                        |                                                                         |
   |                        | * Kyber Public Key                                                      |
   |                        | * Kyber Private Key                                                     |
   |                        | * Ciphertext                                                            |
   |                        | * Shared Secret                                                         |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | For each KAT vector:                                                    |
   |                        |                                                                         |
   |                        | #. Seed a AES-256-CTR-DRBG with the specified RNG seed                  |
   |                        |                                                                         |
   |                        | #. Use the seeded RNG to generate a Kyber key pair and compare it to    |
   |                        |    the expected public and private key in the test vector. This uses    |
   |                        |    the key encoding as implemented in the reference implementation.     |
   |                        |                                                                         |
   |                        | #. Encapsulate a secret with the just-generted public key (using the    |
   |                        |    same RNG) and compare the resulting shared secret and ciphertext to  |
   |                        |    expected values in the test vector.                                  |
   |                        |                                                                         |
   |                        | #. Decapsulate the just-calculated ciphertext with the private key from |
   |                        |    the test vector and ensure that the resulting shared secret is equal |
   |                        |    to the expected value from the test vector                           |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKENC-KYBER-2                                                           |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Generate random key pairs, serialize and deserialize them, use the      |
   |                        | deserialized keys to encapsulate and decapsulate secrets.               |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a kyber key pair (one for each algorithm parameter          |
   |                        |    combination: [512, 768, 1024] and [90s, modern]).                    |
   |                        |                                                                         |
   |                        | #. Encode both the public and private key using the default encoding.   |
   |                        |                                                                         |
   |                        | #. Decode the public key and encapsulate a secret with the decoded key. |
   |                        |                                                                         |
   |                        | #. Decode the private key and decapsulate the above-generated           |
   |                        |    ciphertext.                                                          |
   |                        |                                                                         |
   |                        | #. Check that both resulting shared secrets are equal                   |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKENC-KYBER-3                                                           |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Generate random key pairs, serialize and deserialize them, use the      |
   |                        | deserialized keys to encapsulate secrets. Alter the ciphertext output   |
   |                        | and make sure that decapsulation fails gracefully.                      |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a kyber key pair (one for each algorithm parameter          |
   |                        |    combination: [512, 768, 1024] and [90s, modern]).                    |
   |                        |                                                                         |
   |                        | #. Encode both the public and private key using the default encoding.   |
   |                        |                                                                         |
   |                        | #. Decode the public key and encapsulate a secret with the decoded key. |
   |                        |                                                                         |
   |                        | #. Remove the last byte from a copy of the resulting ciphertext.        |
   |                        |                                                                         |
   |                        | #. Reverse the bytes of another copy of the ciphertext                  |
   |                        |                                                                         |
   |                        | #. Decode the private key and try to decapsulate both altered           |
   |                        |    ciphertexts. Expect a failure in both cases.                         |
   |                        |                                                                         |
   |                        | #. Decapsulate the original ciphertext and expect that the resulting    |
   |                        |    shared secret is equal to the one encapsulated before.               |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKENC-KYBER-4                                                           |
   +========================+=========================================================================+
   | **Type:**              | Encoding Tests                                                          |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Decode pre-defined key pairs                                            |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Pre-defined key encodings and (optional) failure modes in:              |
   |                        | * :srcref:`src/tests/data/pubkey/kyber_encodings.vec`                   |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Decode public and/or private keys as given in the test vector        |
   |                        |                                                                         |
   |                        | #. If the decoding fails: Check whether the error message matches the   |
   |                        |    vector's expected failure mode.                                      |
   |                        |                                                                         |
   |                        | #. Otherwise re-encode the public and private keys and validate that    |
   |                        |    the result is byte-compatible with the input values.                 |
   +------------------------+-------------------------------------------------------------------------+

RSA-KEM
~~~~~~~

The RSA Key Encapsulation Mechanism (RSA-KEM) is tested with the
following constraints:

-  Number of test cases: 3
-  Source: Generated with BouncyCastle
-  KDF: KDF1-18033
-  Hash Function: SHA-1, SHA-256, SHA-512
-  E: 17
-  P: 1024 bits
-  Q: 1024 bits
-  C0: 512 bits, 2048 bits
-  K: 2432 bits - 2944 bits

All the tests are implemented in :srcref:`src/tests/test_rsa.cpp`. The
following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/pubkey/rsa_kem.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKENC-RSAKEM-1                                                          |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Derive a shared secret                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    KDF= KDF1-18033                                                      |
   |                        |    Hash Function = SHA-1                                                |
   |                        |    E = 17                                                               |
   |                        |    P = 1645950186568473882341964582951551761067580585163458271143764628 |
   |                        |    50563872821063372112958430530617671033588730874556123844100607371610 |
   |                        |    22235704428221007774543857356946467542295606081624245975158122439134 |
   |                        |    09386743169797403795135840467301322375842101624289696215748957306098 |
   |                        |    32661623255469386625333399495443111996269                            |
   |                        |    Q = 1548156933394616749712012029280635537323487695558384500045530118 |
   |                        |    45712199598612461913292296568174793540787763943903927157071815682359 |
   |                        |    74852665095085448171202919729860177636423044468469111847959944718638 |
   |                        |    10981813191843193890746739216420985718840385793232935393632733929895 |
   |                        |    80933234215294363547330708372978868708523                            |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    K = 0x2879A51427541B4CDAC3AD823C75FB2B4CF895BFC8F08DF4F1355CCE27C5A5 |
   |                        |        44B3701E91D4E6A8FB9FA7762168974202D6719DA117AB506386F6BAED09F1F8 |
   |                        |        FB84620684AE4C962C05CE130D6BA770F1A54CA8C68CCEA59702DE33DDF456B0 |
   |                        |        F34813CC8BFE6999C6086B5EE96122669EAF85FD427D6EC80250FB86D39AAEA7 |
   |                        |        52A57EDE4AD5802B709B536A42F1C9285BAA73884DA2E22204C0D60404DE70E2 |
   |                        |        4D03BBA5ED3A453782D0B49800EDCE562FE2793B6C9AA59881FB29992BDA65C6 |
   |                        |        7BF2625EBCBC66EE87F734C95DDFEC808EF6D44DD9682801F26D0F91F60F85F0 |
   |                        |        1A1A3D197CD13DFC2B174F4BE14CBB14A5946F8E22E9AC492472707DB684B85E |
   |                        |        0E                                                               |
   |                        |        0x57DFAFA0D81AC3AACA2570AD13CCCD127239F4EE04843BB738234588F0DAEA |
   |                        |        53CCD8AF65A5A00ED19FBB6F2EB57779FF2E38E3D5D27986253A1193DABF14D2 |
   |                        |        402E1A33527866FA21F23F7ABBEE5F454AAD762FC90139C8377BF6CC77AF7F98 |
   |                        |        2404BAEA5CA4831DD8ED28BABF2D43B1F65EFF42167B82F020DFD4928D8E96DC |
   |                        |        B7845ECF8F560FBBF5646FAE5BC4EDA6D978E5FB333843A1F4525CFBDDE75684 |
   |                        |        2A1E353F4DE1503738EEC6C9D901A78CDEFEDF8DAAA49631DA674B44CAB2193C |
   |                        |        778BF29766730A656B42E96F84698F77913C718067048263034CF2A2F34572AB |
   |                        |        662E4B1C5B04CD71183433C591ABD5613820544D46F7462BEA57E44F23AB06E0 |
   |                        |        FB9A0B0CAB5C285FB0CB1F788213B6B82A2C2E485C1D514BAEF7FC241D57DB03 |
   |                        |        1D9E80361C55B562232759A660C89E0DE0E11BB8C807142C1C98C07C9BD08BFC |
   |                        |        7A3D9977133AD07DDED60728B46D668444A74BC001CFBFB8E8FE0BACF6A4078D |
   |                        |        D4212DC7CDC3291CB3F02AC0B7CDF6E65D                               |
   |                        |    C0 = 0xC03666B82F2E0076C9CF78056F3BE5549A2BD03349D0D52160C3D9C1C2B46 |
   |                        |    FB4E65642B340EE73EE73D301CE8DB75A5CDF5B972011490758A1E0314E0E7E4B952 |
   |                        |    A546FBA6EE8AA7370B6773D6E591D2561148FD049E571A5D8AEAF2BE9EA90F15FFE2 |
   |                        |    736D62AC13BB6C2BA0FC993E7CD72FA890E50DBF27554D3BF7F1B913107F201C6D9E |
   |                        |    A3E56C53E5683C763C0E7E23F1CD416CBCAD7A6A688AB400CBC5D87B1D6DD3612E26 |
   |                        |    15C87B398AE42B43FD5CEAF762033AC3860C38E96CEF3E5B1180C0EB5DE5D3313813 |
   |                        |    1A78D12B4E826ACE6BE2F1954CD56716D3BD7FE23C7187EE40E34BF5CD0F01B0F9A6 |
   |                        |    DE390830EC71CB9021ADBCE5AE761E6A1439E157E01                          |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create a Private_Key object from *P, Q, G*                           |
   |                        |                                                                         |
   |                        | #. Use the Private_Key and the *KDF* to derive a shared secret, compare |
   |                        |    the shared secret to expected output *K* and the encapsulated key to |
   |                        |    expected output *C0*                                                 |
   |                        |                                                                         |
   |                        | #. Use the Private_Key and the *KDF* to decrypt the input value *C0*    |
   |                        |    and compare the output to expected output *K*                        |
   +------------------------+-------------------------------------------------------------------------+
