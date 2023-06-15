Public Key-based Signature Algorithms
=====================================

Public Key-based Signature Algorithms are tested using (1) a known
answer test that generates a signature on a test message, and (2) checks
that a manipulated signature does not verify. Some algorithms also
contain a third test (3), a known answer test that checks that an
invalid signature does not verify and/or a fourth test (4), a known
answer test that verifies a given signature. Additional tests may be
implemented for specific algorithms, e.g., for public key validation.
All public key-based signature algorithms use test classes implemented
in :srcref:`src/tests/test_pubkey.cpp`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-1                                                                 |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Sign a test message                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Hash Function: The hash function used for hashing the message, e.g., |
   |                        |    SHA-1                                                                |
   |                        |                                                                         |
   |                        | -  Public Parameters:                                                   |
   |                        |                                                                         |
   |                        |    -  Group: The DL group, e.g., modp/ietf/1024 or                      |
   |                        |                                                                         |
   |                        |    -  Curve: The elliptic curve, e.g., secp192r1 or                     |
   |                        |                                                                         |
   |                        |    -  P, Q, E: DSA/RSA parameters                                       |
   |                        |                                                                         |
   |                        | -  Private Parameters: Algorithm-specific Private Key Parameters        |
   |                        |                                                                         |
   |                        | -  Msg: The test message (varying length)                               |
   |                        |                                                                         |
   |                        | -  Padding: The padding scheme used (optional)                          |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | -  Signature: The expected signature (varying length depending on the   |
   |                        |    algorithm)                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the PrivateKey object from *Group/Curve/P,Q,E* and *Private   |
   |                        |    Parameters*                                                          |
   |                        |                                                                         |
   |                        | #. Verify the signature *Signature* on the *Msg*                        |
   |                        |                                                                         |
   |                        | #. Sign the *Msg* with the PrivateKey object and compare with the       |
   |                        |    expected output *Signature*                                          |
   |                        |                                                                         |
   |                        | #. Verify the generated signature on the *Msg*                          |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-2                                                                 |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Manipulated signature should not verify                                 |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Group: The DL group, e.g., modp/ietf/1024 or                         |
   |                        |                                                                         |
   |                        | -  Curve: The elliptic curve, e.g., secp192r1 or                        |
   |                        |                                                                         |
   |                        | -  P, Q, E: RSA parameters                                              |
   |                        |                                                                         |
   |                        | -  Private Parameters: Algorithm-specific Private Key Parameters        |
   |                        |                                                                         |
   |                        | -  Msg: The test message (varying length)                               |
   |                        |                                                                         |
   |                        | -  Padding: The padding scheme                                          |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | |                                                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the PrivateKey object from *Group/Curve/P,Q,E* and *Private   |
   |                        |    Parameters*                                                          |
   |                        |                                                                         |
   |                        | #. Sign the *Msg* with the PrivateKey object                            |
   |                        |                                                                         |
   |                        | #. Check that a signature with all zeros (of the length of that of the  |
   |                        |    generated signature) does not verify                                 |
   |                        |                                                                         |
   |                        | #. Create a modified version of the generated signature by changing the |
   |                        |    length of it or by flipping random bits in it                        |
   |                        |                                                                         |
   |                        | #. Check that this modified signature does not verify                   |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-3                                                                 |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Invalid signature should not verify                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Group: The DL group, e.g., modp/ietf/1024 or                         |
   |                        |                                                                         |
   |                        | -  Curve: The elliptic curve, e.g., secp192r1 or                        |
   |                        |                                                                         |
   |                        | -  P, Q, E: RSA parameters                                              |
   |                        |                                                                         |
   |                        | -  Private Parameters: Algorithm-specific Private Key Parameters        |
   |                        |                                                                         |
   |                        | -  Msg: The test message (varying length)                               |
   |                        |                                                                         |
   |                        | -  Padding: The padding scheme                                          |
   |                        |                                                                         |
   |                        | -  InvalidSignature: The invalid signature                              |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | |                                                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the PrivateKey object from *Group/Curve/P,Q,E* and *Private   |
   |                        |    Parameters*                                                          |
   |                        |                                                                         |
   |                        | #. Check that the signature *InvalidSignature* does not verify          |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-4                                                                 |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Verify a given signature                                                |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Group: The DL group, e.g., modp/ietf/1024 or                         |
   |                        |                                                                         |
   |                        | -  Curve: The elliptic curve, e.g., secp192r1 or                        |
   |                        |                                                                         |
   |                        | -  P, Q, E: RSA parameters                                              |
   |                        |                                                                         |
   |                        | -  Public Parameters: Algorithm-specific Public Key Parameters          |
   |                        |                                                                         |
   |                        | -  Msg: The test message (varying length)                               |
   |                        |                                                                         |
   |                        | -  Padding: The padding scheme                                          |
   |                        |                                                                         |
   |                        | -  Signature: The signature to be verified                              |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | |                                                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the PublicKey object from *Group/Curve/P,Q,E* and *Public*    |
   |                        |    *Parameters*                                                         |
   |                        |                                                                         |
   |                        | #. Check that the signature *Signature* verifies                        |
   +------------------------+-------------------------------------------------------------------------+

Additionally, for each algorithm unit tests make sure that encoding and
decoding private and public keys works correctly. These test cases are
described here in the following.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-KEY-1                                                             |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encode and decode a public key as PEM                                   |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Group: The DL group, e.g., modp/ietf/1024 or                         |
   |                        |                                                                         |
   |                        | -  Curve: The elliptic curve, e.g., secp192r1 or                        |
   |                        |                                                                         |
   |                        | -  P, Q, E: RSA parameters                                              |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random keypair on the *Group*/*Curve/RSA parameters*      |
   |                        |                                                                         |
   |                        | #. Encode the public key as PEM-encoded string                          |
   |                        |                                                                         |
   |                        | #. Create a PublicKey object from the PEM-encoded string, decoding the  |
   |                        |    PEM-encoded key                                                      |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid                                   |
   |                        |                                                                         |
   |                        | #. Check that the key object algorithm name equals that of the          |
   |                        |    generated keypair                                                    |
   |                        |                                                                         |
   |                        | #. Check that the key is valid [#sig_mechanism]_                        |
   +------------------------+-------------------------------------------------------------------------+

.. [#sig_mechanism] The exact mechanism depends on the key type and is explained in the
                    corresponding public key signature scheme section

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-KEY-2                                                             |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encode and decode a public key as BER                                   |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Group: The DL group, e.g., modp/ietf/1024 or                         |
   |                        |                                                                         |
   |                        | -  Curve: The elliptic curve, e.g., secp192r1 or                        |
   |                        |                                                                         |
   |                        | -  P, Q, E: RSA parameters                                              |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random keypair on the *Group/Curve/RSA parameters*        |
   |                        |                                                                         |
   |                        | #. Encode the public key as BER-encoded byte array                      |
   |                        |                                                                         |
   |                        | #. Create a PublicKey object from the BER-encoded byte array, decoding  |
   |                        |    the BER-encoded key                                                  |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid\ :sup:`1`                         |
   |                        |                                                                         |
   |                        | #. Check that the key object algorithm name equals that of the          |
   |                        |    generated keypair                                                    |
   |                        |                                                                         |
   |                        | #. Check that the key is valid (see PKSIG-KEY-1)                        |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-KEY-3                                                             |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encode and decode a private key as PEM                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Group: The DL group, e.g., modp/ietf/1024 or                         |
   |                        |                                                                         |
   |                        | -  Curve: The elliptic curve, e.g., secp192r1 or                        |
   |                        |                                                                         |
   |                        | -  P, Q, E: RSA parameters                                              |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random keypair on the *Group/Curve/RSA parameters*        |
   |                        |                                                                         |
   |                        | #. Encode the private key as PEM-encoded string                         |
   |                        |                                                                         |
   |                        | #. Create a PrivateKey object from the PEM-encoded string, decoding the |
   |                        |    PEM-encoded key                                                      |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid                                   |
   |                        |                                                                         |
   |                        | #. Check that the key object algorithm name equals that of the          |
   |                        |    generated keypair                                                    |
   |                        |                                                                         |
   |                        | #. Check that the key is valid (see PKSIG-KEY-1)                        |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-KEY-4                                                             |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encode and decode a private key as BER                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Group: The DL group, e.g., modp/ietf/1024 or                         |
   |                        |                                                                         |
   |                        | -  Curve: The elliptic curve, e.g., secp192r1 or                        |
   |                        |                                                                         |
   |                        | -  P, Q, E: RSA parameters                                              |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random keypair on the *Group/Curve/RSA parameters*        |
   |                        |                                                                         |
   |                        | #. Encode the private key as BER-encoded byte array                     |
   |                        |                                                                         |
   |                        | #. Create a PrivateKey object from the BER-encoded byte array, decoding |
   |                        |    the BER-encoded key                                                  |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid                                   |
   |                        |                                                                         |
   |                        | #. Check that the key object algorithm name equals that of the          |
   |                        |    generated keypair                                                    |
   |                        |                                                                         |
   |                        | #. Check that the key is valid (see PKSIG-KEY-1)                        |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-KEY-5                                                             |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encode and decode a private key as PEM, protected with a password       |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Group: The DL group, e.g., modp/ietf/1024 or                         |
   |                        |                                                                         |
   |                        | -  Curve: The elliptic curve, e.g., secp192r1 or                        |
   |                        |                                                                         |
   |                        | -  P, Q, E: RSA parameters                                              |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random password string of length between 1-32 characters  |
   |                        |                                                                         |
   |                        | #. Generate a random keypair on the *Group/Curve/RSA parameters*        |
   |                        |                                                                         |
   |                        | #. Encode the private key as PEM-encoded string, protected with the     |
   |                        |    password                                                             |
   |                        |                                                                         |
   |                        | #. Create a PrivateKey object from the PEM-encoded string, decoding the |
   |                        |    PEM-encoded key                                                      |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid                                   |
   |                        |                                                                         |
   |                        | #. Check that the key object algorithm name equals that of the          |
   |                        |    generated keypair                                                    |
   |                        |                                                                         |
   |                        | #. Check that the key is valid (see PKSIG-KEY-1)                        |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-KEY-6                                                             |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encode and decode a private key as BER, protected with a password       |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Group: The DL group, e.g., modp/ietf/1024 or                         |
   |                        |                                                                         |
   |                        | -  Curve: The elliptic curve, e.g., secp192r1 or                        |
   |                        |                                                                         |
   |                        | -  P, Q, E: RSA parameters                                              |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random password string of length between 1-32 characters  |
   |                        |                                                                         |
   |                        | #. Generate a random keypair on the *Group/Curve/RSA parameters*        |
   |                        |                                                                         |
   |                        | #. Encode the private key as BER-encoded byte array, protected with the |
   |                        |    password                                                             |
   |                        |                                                                         |
   |                        | #. Create a PrivateKey object from the BER-encoded byte array, decoding |
   |                        |    the BER-encoded key                                                  |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid (see PKSIG-KEY-1)                 |
   |                        |                                                                         |
   |                        | #. Check that the key object algorithm name equals that of the          |
   |                        |    generated keypair                                                    |
   |                        |                                                                         |
   |                        | #. Check that the key is valid (see PKSIG-KEY-1)                        |
   +------------------------+-------------------------------------------------------------------------+

Dilithium
---------

The implementation is tested for correctness using the Known Answer Test vectors
demanded by the NIST submission and provided by the reference implementation.

Additionally, Botan has implementation-specific test cases. Those ensure the
interoperability of the algorithm when using Botan's generic API for public key
algorithms. These test cases are equal for all public key schemes and are
therefore not discussed in detail in this chapter.

All Dilithium-specific test code can be found in
:srcref:`src/tests/test_dilithium.cpp`. Relevant test data vectors for the KAT tests
are in *src/tests/data/pubkey/dilithium\_\*.vec* where *\** is a placeholder for
the algorithm parameters, namely *4x4\_Deterministic*, *6x5\_Deterministic*,
*8x7\_Deterministic*, *4x4\_Randomized*, *6x5\_Randomized*, *8x7\_Randomized*,
*4x4\_AES\_Deterministic*, *6x5\_AES\_Deterministic*, *8x7\_AES\_Deterministic*,
*4x4\_AES\_Randomized*, *6x5\_AES\_Randomized* and *8x7\_AES\_Randomized*.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-DILITHIUM-1                                                       |
   +========================+=========================================================================+
   | **Type:**              | Known Answer Tests                                                      |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Uses the KAT vectors of Dilithium's reference implementation as         |
   |                        | specified in the NIST submission. Also implements a negative test by    |
   |                        | randomly pertubing the generated signatures before validation.          |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Test Vectors with RNG seed and test messages inputs in:                 |
   |                        |                                                                         |
   |                        | * :srcref:`src/tests/data/pubkey/dilithium_4x4_Deterministic.vec`       |
   |                        | * :srcref:`src/tests/data/pubkey/dilithium_6x5_Deterministic.vec`       |
   |                        | * :srcref:`src/tests/data/pubkey/dilithium_8x7_Deterministic.vec`       |
   |                        | * :srcref:`src/tests/data/pubkey/dilithium_4x4_Randomized.vec`          |
   |                        | * :srcref:`src/tests/data/pubkey/dilithium_6x5_Randomized.vec`          |
   |                        | * :srcref:`src/tests/data/pubkey/dilithium_8x7_Randomized.vec`          |
   |                        | * :srcref:`src/tests/data/pubkey/dilithium_4x4_AES_Deterministic.vec`   |
   |                        | * :srcref:`src/tests/data/pubkey/dilithium_6x5_AES_Deterministic.vec`   |
   |                        | * :srcref:`src/tests/data/pubkey/dilithium_8x7_AES_Deterministic.vec`   |
   |                        | * :srcref:`src/tests/data/pubkey/dilithium_4x4_AES_Randomized.vec`      |
   |                        | * :srcref:`src/tests/data/pubkey/dilithium_6x5_AES_Randomized.vec`      |
   |                        | * :srcref:`src/tests/data/pubkey/dilithium_8x7_AES_Randomized.vec`      |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Above described test vector files contain expected values for:          |
   |                        |                                                                         |
   |                        | * Dilithium Public Key                                                  |
   |                        | * Dilithium Private Key                                                 |
   |                        | * Signature                                                             |
   |                        |                                                                         |
   |                        | to save disk space, these are stored as their SHA-3 digests only.       |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | For each KAT vector:                                                    |
   |                        |                                                                         |
   |                        | #. Seed a AES-256-CTR-DRBG with the specified RNG seed                  |
   |                        |                                                                         |
   |                        | #. Use the seeded RNG to generate a Dilithium key pair and compare it   |
   |                        |    to the expected public and private key in the test vector. This uses |
   |                        |    the key encoding as implemented in the reference implementation and  |
   |                        |    first hashes the keys with SHA-3 to save space in the test data.     |
   |                        |                                                                         |
   |                        | #. Sign the message provided in the test vector with the just-generated |
   |                        |    private key and validate that the SHA-3 digest of the calculated     |
   |                        |    signature is equal to the test vector's expectation.                 |
   |                        |                                                                         |
   |                        | #. Decode the public key from the encoding mentioned above and verify   |
   |                        |    the just-calculated signature.                                       |
   |                        |                                                                         |
   |                        | #. Randomly alter the signature output by pertubing a single byte and   |
   |                        |    ensure that the signature verification fails.                        |
   |                        |                                                                         |
   |                        | #. Retry validation of the original (valid) signature.                  |
   +------------------------+-------------------------------------------------------------------------+


.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-DILITHIUM-2                                                       |
   +========================+=========================================================================+
   | **Type:**              | Positive and Negative Tests                                             |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Generate random key pairs, encode/decode and sign/verify messages with  |
   |                        | various combinations of encoded/decoded keys.                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | For each combination of the algorithm parameters [4x4, 6x5, 8x7],       |
   |                        | [Randomized, Determinstic] and [AES, modern]:                           |
   |                        |                                                                         |
   |                        | #. Generate a random key pair                                           |
   |                        |                                                                         |
   |                        | #. Sign the message *The quick brown fox jumps over the lazy dog.* with |
   |                        |    the just-generated private key.                                      |
   |                        |                                                                         |
   |                        | #. Encode the keypair and decode them again as "another" instance of    |
   |                        |    the same keypair.                                                    |
   |                        |                                                                         |
   |                        | #. Sign the message *The quick brown fox jumps over the lazy dog.* with |
   |                        |    the private key that was obtained by the encode/decode cycle.        |
   |                        |                                                                         |
   |                        | #. Ensure that both signatures can be verified in all possible          |
   |                        |    combinations of freshly generated or encoded/decoded key pairs.      |
   |                        |                                                                         |
   |                        | #. Tamper with the initial message by replacing the first byte by *X*.  |
   |                        |                                                                         |
   |                        | #. Ensure that both signatures cannot be verified in any possible       |
   |                        |    combinations of freshly generated or encoded/decoded key pairs.      |
   |                        |                                                                         |
   |                        | #. Decode the keypair again (via Botan's generic interface)             |
   |                        |                                                                         |
   |                        | #. Ensure that these decoded keys work for signing and verifying.       |
   +------------------------+-------------------------------------------------------------------------+

DSA
---

The Digital Signature Algorithm (DSA) is tested with the following
constraints:

-  Number of test cases: 306
-  Source: NIST CAVP (NIST CAVS file 11.2), OpenSSL
-  Hash Function: SHA-1, SHA-224, SHA-256, SHA-384, SHA-512
-  Group (P, Q, G): 1024 bits, 2048 bits, 3072 bits
-  Msg: 1024 bits
-  Signature: 1024 bits, 2048 bits, 3072 bits

All the tests are implemented in :srcref:`src/tests/test_dsa.cpp`. The
following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/pubkey/dsa_prob.vec`
and :srcref:`src/tests/data/pubkey/dsa_verify.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-DSA-1                                                             |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Sign a test message                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    P = 0xa8f9cd201e5e35d892f85f80e4db2599a5676a3b1d4f190330ed3256b26d0e |
   |                        |    80a0e49a8fffaaad2a24f472d2573241d4d6d6c7480c80b4c67bb4479c15ada7ea84 |
   |                        |    24d2502fa01472e760241713dab025ae1b02e1703a1435f62ddf4ee4c1b664066eb2 |
   |                        |    2f2e3bf28bb70a2a76e4fd5ebe2d1229681b5b06439ac9c7e9d8bde283           |
   |                        |    Q = 0xf85f0f83ac4df7ea0cdf8f469bfeeaea14156495                       |
   |                        |    G = 0x2b3152ff6c62f14622b8f48e59f8af46883b38e79b8c74deeae9df131f8b85 |
   |                        |    6e3ad6c8455dab87cc0da8ac973417ce4f7878557d6cdf40b35b4a0ca3eb310c6a95 |
   |                        |    d68ce284ad4e25ea28591611ee08b8444bd64b25f3f7c572410ddfb39cc728b9c936 |
   |                        |    f85f419129869929cdb909a6a3a99bbe089216368171bd0ba81de4fe33           |
   |                        |                                                                         |
   |                        | Private Parameters:                                                     |
   |                        |                                                                         |
   |                        | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    X= 0xc53eae6d45323164c7d07af5715703744a63fc3a                        |
   |                        |    Msg = empty message                                                  |
   |                        |    Nonce = 0x98cbcc4969d845e2461b5f66383dd503712bbcfa                   |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    Signature = 0x50ed0e810e3f1c7cb6ac62332058448bd8b284c0c6aded17216b46 |
   |                        |    b7e4b6f2a97c1ad7cc3da83fde                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the DSA_PrivateKey object from *P, Q, G* and *X*              |
   |                        |                                                                         |
   |                        | #. Verify the signature *Signature* on the *Msg*                        |
   |                        |                                                                         |
   |                        | #. Sign the *Msg* with the DSA_PrivateKey object and compare with the   |
   |                        |    expected output *Signature*                                          |
   |                        |                                                                         |
   |                        | #. Verify the generated signature on the *Msg*                          |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-DSA-2                                                             |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Invalid signatures should not verify                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | P =                                                                     |
   |                        | 0xa8f9cd201e5e35d892f85f80e4db2599a5676a3b1d4                           |
   |                        | f190330ed3256b26d0e80a0e49a8fffaaad2a24f472d2573241d4d6d6c7480c80b4c67b |
   |                        | b4479c15ada7ea8424d2502fa01472e760241713dab025ae1b02e1703a1435f62ddf4ee |
   |                        | 4c1b664066eb22f2e3bf28bb70a2a76e4fd5ebe2d1229681b5b06439ac9c7e9d8bde283 |
   |                        |                                                                         |
   |                        | Q = 0x0xf85f0f83ac4df7ea0cdf8f469bfeeaea14156495                        |
   |                        |                                                                         |
   |                        | G =                                                                     |
   |                        | 0x2b3152ff6c62f14622b8f48e59f8af46883b38e79b8                           |
   |                        | c74deeae9df131f8b856e3ad6c8455dab87cc0da8ac973417ce4f7878557d6cdf40b35b |
   |                        | 4a0ca3eb310c6a95d68ce284ad4e25ea28591611ee08b8444bd64b25f3f7c572410ddfb |
   |                        | 39cc728b9c936f85f419129869929cdb909a6a3a99bbe089216368171bd0ba81de4fe33 |
   |                        |                                                                         |
   |                        | Private Parameters:                                                     |
   |                        |                                                                         |
   |                        | X= 0xc53eae6d45323164c7d07af5715703744a63fc3a                           |
   |                        |                                                                         |
   |                        | Msg = empty message                                                     |
   |                        |                                                                         |
   |                        | Nonce = 0x98cbcc4969d845e2461b5f66383dd503712bbcfa                      |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Signatures do not verify                                                |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the DSA_PrivateKey object from *P, Q, G* and *X*              |
   |                        |                                                                         |
   |                        | #. Sign the *Msg* with the DSA_PrivateKey object                        |
   |                        |                                                                         |
   |                        | #. Check that a signature with all zeros (of the length of that of the  |
   |                        |    generated signature) does not verify                                 |
   |                        |                                                                         |
   |                        | #. Create a modified version of the generated signature by changing the |
   |                        |    length of it or by flipping random bits in it                        |
   |                        |                                                                         |
   |                        | #. Check that this modified signature does not verify                   |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-DSA-4                                                             |
   +========================+=========================================================================+
   | **Type:**              | Postive Test                                                            |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Verify a given signature                                                |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    P = 0xe6793d8a212fe151fe077d76183388c201521ffff76b966aeba9f7fc94adee |
   |                        |    f752933897ed8e599c94c705afd111ba33b36329fdc5090e918f28c59ba06943492a |
   |                        |    1381de0a4d90603dfe705b6a89d6099cdd2e9581e82bf34957eb048c178e2468df8b |
   |                        |    443e58081fe04b78dd2ab98e2bd939f3ec348d612d9622f6b8d9cd0c5f           |
   |                        |    Q = 0xf8af4ef46d9a0881bd01c70f969870b05580f499                       |
   |                        |    G = 0x9427dc62cbf9461fbf58d415d9a33974a15aa30114d93a54d5e06bee6c34af |
   |                        |    19d2e70fa763ca0a361b6f4f47a0e8773ff2624ac6d973a316ecc10de18218ad7bbf |
   |                        |    fecbaf01a4840d40d42b59f6bdb5e722127597b24b495e93bc7e500497fdbc17319a |
   |                        |    8c8dbbfa711fa0898bccab3f83c3bcfcbde5e18c23b9573d3dd24bfdb5           |
   |                        |                                                                         |
   |                        | Public Parameters:                                                      |
   |                        |                                                                         |
   |                        | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    Y = 0xcea7c9120eb8d8bc17cbe015cad32fc349140c7018af2445c6686bbbb2e572 |
   |                        |    05fe7412a40e196d57cf5ac924855ad25b79c6140cfe2dece79b907c37cf9a74eaef |
   |                        |    9597b73d55655b30843b9025c2edd1531c11480971dd55b7462a23de611ce0be7a3f |
   |                        |    e82fd4b0c65faa4445b894212406ac608ed05ad2b3c2986efa1b8cd580a          |
   |                        |    Msg = fffdfbf9f7f5f3f1efedebe9e7e5e3e1dfdddbd9                       |
   |                        |    Signature = 3db343dc58acdebf815f85d0e55fbdeda326bea6107f10f3a2cb1fbf |
   |                        |    afb3324b3fc6076fe298ac9e                                             |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Signature verifies                                                      |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the DSA_PublicKey object from *P, Q, G* and *Y*               |
   |                        |                                                                         |
   |                        | #. Check that the signature *Signature* verifies                        |
   +------------------------+-------------------------------------------------------------------------+

The following example shows a DSA-specific PKSIG-KEY-1 test case. The
constraints for this test case are:

-  Group: dsa/jce/1024, dsa/botan/2048

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-KEY-DSA-1                                                         |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encode and decode a DSA public key as PEM                               |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Group = dsa/jce/1024                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random keypair on the DSA *Group*                         |
   |                        |                                                                         |
   |                        | #. Encode the public key as PEM-encoded string                          |
   |                        |                                                                         |
   |                        | #. Create a DSA_PublicKey object from the PEM-encoded string, decoding  |
   |                        |    the PEM-encoded key                                                  |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid                                   |
   |                        |                                                                         |
   |                        | #. Check that the key object algorithm name equals that of the          |
   |                        |    generated keypair                                                    |
   |                        |                                                                         |
   |                        | #. Check that the key is valid by checking that:                        |
   |                        |                                                                         |
   |                        |    #. 1 < Y < P                                                         |
   |                        |                                                                         |
   |                        |    #. G >= 2                                                            |
   |                        |                                                                         |
   |                        |    #. P >= 3                                                            |
   |                        |                                                                         |
   |                        |    #. If Q is given:                                                    |
   |                        |                                                                         |
   |                        |       a. (P - 1) % Q = 0                                                |
   |                        |                                                                         |
   |                        |       b. G\ :sup:`Q` mod P = 1                                          |
   |                        |                                                                         |
   |                        |       c. Q is prime using a Miller-Rabin test with 50 rounds            |
   |                        |                                                                         |
   |                        |    #. P is prime using a Miller-Rabin test with 50 rounds               |
   +------------------------+-------------------------------------------------------------------------+

ECDSA
-----

The Elliptic Curve Digital Signature Algorithm (ECDSA) is tested with
the following constraints:

-  Number of test cases: 4156
-  Source: NIST CAVP (NIST CAVS file 11.2), OpenSSL, Wycheproof
-  Hash Function: SHA-1, SHA-224, SHA-256, SHA-384, SHA-512
-  Curve: secp224r1, secp256r1, secp384r1
-  Msg: 1024 bits
-  Signature: 448 bits, 512 bits, 568 bits

All the tests are implemented in :srcref:`src/tests/test_ecdsa.cpp`. The
following table shows an example test case with one test vector. All
test vectors are listed in
:srcref:`src/tests/data/pubkey/ecdsa_prob.vec`, :srcref:`src/tests/data/pubkey/ecdsa_verify.vec` and :srcref:`src/tests/data/pubkey/ecdsa_wycheproof.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-ECDSA-1                                                           |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Sign a test message                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Hash Function = SHA-224                                                 |
   |                        |                                                                         |
   |                        | Curve = secp224r1                                                       |
   |                        |                                                                         |
   |                        | Private Parameters:                                                     |
   |                        |                                                                         |
   |                        | X= 0x16797b5c0c7ed5461e2ff1b88e6eafa03c0f46bf072000dfc830d615           |
   |                        |                                                                         |
   |                        | Msg =                                                                   |
   |                        | 0x699325d6fc8fbbb4981a6ded3c3a54ad2e4e3db8a56                           |
   |                        | 69201912064c64e700c139248cdc19495df081c3fc60245b9f25fc9e301b845b3d703a6 |
   |                        | 94986e4641ae3c7e5a19e6d6edbf1d61e535f49a8fad5f4ac26397cfec682f161a5fcd3 |
   |                        | 2c5e780668b0181a91955157635536a22367308036e2070f544ad4fff3d5122c76fad5d |
   |                        |                                                                         |
   |                        | Nonce = 0xd9a5a7328117f48b4b8dd8c17dae722e756b3ff64bd29a527137eec0      |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Signature =                                                             |
   |                        | 0x2fc2cff8cdd4866b1d74e45b07d333af46b7af088                             |
   |                        | 8049d0fdbc7b0d68d9cc4c8ea93e0fd9d6431b9a1fd99b88f281793396321b11dac41eb |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the ECDSA_PrivateKey object from *Curve, X*                   |
   |                        |                                                                         |
   |                        | #. Verify the signature *Signature* on the *Msg*                        |
   |                        |                                                                         |
   |                        | #. Sign the *Msg* with the ECDSA_PrivateKey object and compare with the |
   |                        |    expected output *Signature*                                          |
   |                        |                                                                         |
   |                        | #. Verify the generated signature on the *Msg*                          |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-ECDSA-2                                                           |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Invalid signatures should not verify                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Hash Function = SHA-224                                                 |
   |                        |                                                                         |
   |                        | Curve = secp224r1                                                       |
   |                        |                                                                         |
   |                        | Private Parameters:                                                     |
   |                        |                                                                         |
   |                        | X= 0x16797b5c0c7ed5461e2ff1b88e6eafa03c0f46bf072000dfc830d615           |
   |                        |                                                                         |
   |                        | Msg =                                                                   |
   |                        | 0x699325d6fc8fbbb4981a6ded3c3a54ad2e4e3db8a56                           |
   |                        | 69201912064c64e700c139248cdc19495df081c3fc60245b9f25fc9e301b845b3d703a6 |
   |                        | 94986e4641ae3c7e5a19e6d6edbf1d61e535f49a8fad5f4ac26397cfec682f161a5fcd3 |
   |                        | 2c5e780668b0181a91955157635536a22367308036e2070f544ad4fff3d5122c76fad5d |
   |                        |                                                                         |
   |                        | Nonce = 0xd9a5a7328117f48b4b8dd8c17dae722e756b3ff64bd29a527137eec0      |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Signatures do not verify                                                |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the ECDSA_PrivateKey object from *Curve, X*                   |
   |                        |                                                                         |
   |                        | #. Sign the *Msg* with the ECDSA_PrivateKey object                      |
   |                        |                                                                         |
   |                        | #. Check that a signature with all zeros (of the length of that of the  |
   |                        |    generated signature) does not verify                                 |
   |                        |                                                                         |
   |                        | #. Create a modified version of the generated signature by changing the |
   |                        |    length of it or by flipping random bits in it                        |
   |                        |                                                                         |
   |                        | #. Check that this modified signature does not verify                   |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-ECDSA-4                                                           |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Verify a signature                                                      |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Hash Function = None                                                    |
   |                        |                                                                         |
   |                        | Curve = secp256k1                                                       |
   |                        |                                                                         |
   |                        | Private Parameters:                                                     |
   |                        |                                                                         |
   |                        | Px = 0xf3f8bb913aa68589a2c8c607a877ab05252adbd963e1be846ddeb8456942aedc |
   |                        |                                                                         |
   |                        | Py = 0xa2ed51f08ca3ef3dac0a7504613d54cd539fc1b3cbc92453cd704b6a2d012b2c |
   |                        |                                                                         |
   |                        | Msg = ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff  |
   |                        |                                                                         |
   |                        | Signature =                                                             |
   |                        | e30f2e6a0f705f4fb5f8501ba79c7c0d3fac847f1ad70b873e9797b17               |
   |                        | b89b39081f1a4457589f30d76ab9f89e748a68c8a94c30fe0bac8fb5c0b54ea70bf6d2f |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Signature verifies                                                      |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the ECDSA_PublicKey object from *Curve,* *Px, Py*             |
   |                        |                                                                         |
   |                        | #. Verify the *Signature* on the given *Msg*                            |
   +------------------------+-------------------------------------------------------------------------+

ECDSA signature verification is tested using additional positive and
negative tests from the Wycheproof [#wycheproof]_ project. The Wycheproof project
provides test vectors for detecting known weaknesses or to check for
expected behaviours of some cryptographic algorithms, e.g., signature
malleability, wrong signature length, invalid ASN.1 encoding, signature
with special case values for r and s, etc.

.. [#wycheproof] https://github.com/google/wycheproof


The following example shows an ECDSA-specific PKSIG-KEY-1 test case. The
constraints for this test case are:

-  Curve: secp256r1, secp384r1, secp521r1

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-KEY-ECDSA-1                                                       |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encode and decode an ECDSA public key as PEM                            |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Curve = secp256r1                                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random keypair on the ECDSA *Curve*                       |
   |                        |                                                                         |
   |                        | #. Encode the public key as PEM-encoded string                          |
   |                        |                                                                         |
   |                        | #. Create a ECDSA_PublicKey object from the PEM-encoded string,         |
   |                        |    decoding the PEM-encoded key                                         |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid                                   |
   |                        |                                                                         |
   |                        | #. Check that the key object algorithm name equals that of the          |
   |                        |    generated keypair                                                    |
   |                        |                                                                         |
   |                        | #. Check that the public key is valid by performing the checks from AIS |
   |                        |    46                                                                   |
   +------------------------+-------------------------------------------------------------------------+

Additional tests check that public keys are validated correctly. Test
vectors are taken from NIST CAVS file 11.0 for FIPS 186-2 and FIPS
186-4.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-PUBKEY-VAL-ECDSA-1                                                |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Validate an ECDSA public key                                            |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    Curve = secp256r1                                                    |
   |                        |    InvalidKeyX = 0xd2b419e62dc101b395401208b9868a3b3fd007ad92adb18921c0 |
   |                        |    68d416aa22e7 (256 bits)                                              |
   |                        |    InvalidKeyY = 0x17952007e021b46a2ab12f14115aafb70608a37f0c3366e7e392 |
   |                        |    1414b904d395a (256 bits)                                             |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random keypair on the ECDSA *Curve*                       |
   |                        |                                                                         |
   |                        | #. Encode the public key as PEM-encoded string                          |
   |                        |                                                                         |
   |                        | #. Create a ECDSA_PublicKey object on the curve *Curve* with the public |
   |                        |    point x coordinate InvalidKeyX and the y coordinate InvalidKeyY      |
   |                        |                                                                         |
   |                        | #. Check that the public key is valid by performing the checks from AIS |
   |                        |    46                                                                   |
   +------------------------+-------------------------------------------------------------------------+

ECGDSA
------

The Elliptic Curve German Digital Signature Algorithm (ECGDSA) is tested
with the following constraints:

-  Number of test cases: 9
-  Source: “The Digital Signature Scheme ECGDSA”, Erwin Hess, Marcus
   Schafheutle, and Pascale Serf, Siemens AG, October 24, 2006
-  Hash Function: SHA-1, SHA-224, SHA-256, SHA-384, SHA-512
-  Curve: brainpool192r1, brainpool256r1, brainpool320r1,
   brainpool384r1, brainpool512r1
-  Msg: 368 bits, 384 bits, 408 bits
-  Signature: 384 bits, 512 bits, 640 bits, 768 bits, 1024 bits

All the tests are implemented in :srcref:`src/tests/test_ecgdsa.cpp`. The
following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/pubkey/ecgdsa.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-ECGDSA-1                                                          |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Sign a test message                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Hash Function = SHA-224                                                 |
   |                        |                                                                         |
   |                        | Curve = secp224r1                                                       |
   |                        |                                                                         |
   |                        | Private Parameters:                                                     |
   |                        |                                                                         |
   |                        | X= 0x16797b5c0c7ed5461e2ff1b88e6eafa03c0f46bf072000dfc830d615           |
   |                        |                                                                         |
   |                        | Msg =                                                                   |
   |                        | 0x699325d6fc8fbbb4981a6ded3c3a54ad2e4e3db8a56                           |
   |                        | 69201912064c64e700c139248cdc19495df081c3fc60245b9f25fc9e301b845b3d703a6 |
   |                        | 94986e4641ae3c7e5a19e6d6edbf1d61e535f49a8fad5f4ac26397cfec682f161a5fcd3 |
   |                        | 2c5e780668b0181a91955157635536a22367308036e2070f544ad4fff3d5122c76fad5d |
   |                        |                                                                         |
   |                        | Nonce = 0xd9a5a7328117f48b4b8dd8c17dae722e756b3ff64bd29a527137eec0      |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Signature =                                                             |
   |                        | 0x2fc2cff8cdd4866b1d74e45b07d333af46b7af088                             |
   |                        | 8049d0fdbc7b0d68d9cc4c8ea93e0fd9d6431b9a1fd99b88f281793396321b11dac41eb |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the ECGDSA_PrivateKey object from *Curve, X*                  |
   |                        |                                                                         |
   |                        | #. Verify the signature *Signature* on the *Msg*                        |
   |                        |                                                                         |
   |                        | #. Sign the *Msg* with the ECGDSA_PrivateKey object and compare with    |
   |                        |    the expected output *Signature*                                      |
   |                        |                                                                         |
   |                        | #. Verify the generated signature on the *Msg*                          |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-ECGDSA-2                                                          |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Invalid signatures should not verify                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Hash Function = SHA-224                                                 |
   |                        |                                                                         |
   |                        | Curve = secp224r1                                                       |
   |                        |                                                                         |
   |                        | Private Parameters:                                                     |
   |                        |                                                                         |
   |                        | X= 0x16797b5c0c7ed5461e2ff1b88e6eafa03c0f46bf072000dfc830d615           |
   |                        |                                                                         |
   |                        | Msg =                                                                   |
   |                        | 0x699325d6fc8fbbb4981a6ded3c3a54ad2e4e3db8a56                           |
   |                        | 69201912064c64e700c139248cdc19495df081c3fc60245b9f25fc9e301b845b3d703a6 |
   |                        | 94986e4641ae3c7e5a19e6d6edbf1d61e535f49a8fad5f4ac26397cfec682f161a5fcd3 |
   |                        | 2c5e780668b0181a91955157635536a22367308036e2070f544ad4fff3d5122c76fad5d |
   |                        |                                                                         |
   |                        | Nonce = 0xd9a5a7328117f48b4b8dd8c17dae722e756b3ff64bd29a527137eec0      |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Signatures do not verify                                                |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the ECGDSA_PrivateKey object from *Curve, X*                  |
   |                        |                                                                         |
   |                        | #. Sign the *Msg* with the ECGDSA_PrivateKey object                     |
   |                        |                                                                         |
   |                        | #. Check that a signature with all zeros (of the length of that of the  |
   |                        |    generated signature) does not verify                                 |
   |                        |                                                                         |
   |                        | #. Create a modified version of the generated signature by changing the |
   |                        |    length of it or by flipping random bits in it                        |
   |                        |                                                                         |
   |                        | #. Check that this modified signature does not verify                   |
   +------------------------+-------------------------------------------------------------------------+

The following example shows an ECGDSA-specific PKSIG-KEY-1 test case.
The constraints for this test case are:

-  Curve: secp256r1, secp384r1, secp521r1

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-KEY-ECGDSA-1                                                      |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encode and decode an ECGDSA public key as PEM                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Curve = secp256r1                                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random keypair on the ECGDSA *Curve*                      |
   |                        |                                                                         |
   |                        | #. Encode the public key as PEM-encoded string                          |
   |                        |                                                                         |
   |                        | #. Create a ECGDSA_PublicKey object from the PEM-encoded string,        |
   |                        |    decoding the PEM-encoded key                                         |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid                                   |
   |                        |                                                                         |
   |                        | #. Check that the key object algorithm name equals that of the          |
   |                        |    generated keypair                                                    |
   |                        |                                                                         |
   |                        | #. Check that the public key is valid by performing the checks from AIS |
   |                        |    46                                                                   |
   +------------------------+-------------------------------------------------------------------------+

ECKCDSA
-------

The Elliptic Curve Korean Certificate Digital Signature Algorithm
(ECKCDSA) is tested with the following constraints:

-  Number of test cases: 3
-  Sources for KAT tests:

   - TTAK.KO-12.0015/R2 "Digital Signature Mechanism with Appendix
     - Part 3: Korean Certificate-based Digitial Signature Algorithm using
     Elliptic Curves (EC-KCDSA)"
   - ISO/IEC 14888-3:2006, with corrections from ISO/IEC 14888-3:2006/Cor.2:2009
   - ISO/IEC 14888-3:2018
   - https://github.com/libecc/libecc

-  Hash Function: SHA-1, SHA-224, SHA-256, SHA-384, SHA-512
-  Curve: secp192r1, secp224r1, secp256r1, secp384r1, secp521r1,
   brainpool256r1, brainpool384r1, brainpool512r1, frp256v1
-  Msg: 24 bits, 120 bits, 512 bits,
-  Signature: 352 bits, 448 bits, 512 bits, 768 bits, 1024 bits, 1040 bits

All the tests are implemented in :srcref:`src/tests/test_eckcdsa.cpp`. The
following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/pubkey/eckcdsa.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-ECKCDSA-1                                                         |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Sign a test message                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    Hash Function = SHA-224                                              |
   |                        |    Curve = secp224r1                                                    |
   |                        |                                                                         |
   |                        | Private Parameters:                                                     |
   |                        |                                                                         |
   |                        | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    X = 0x9051A275AA4D98439EDDED13FA1C6CBBCCE775D8CC9433DEE69C59848B3594 |
   |                        |    DF                                                                   |
   |                        |    Msg = 0x5468697320697320612073616D706C65206D65737361676520666F722045 |
   |                        |    432D4B4344534120696D706C656D656E746174696F6E2076616C69646174696F6E2E |
   |                        |    Nonce = 0x76A0AFC18646D1B620A079FB223865A7BCB447F3C03A35D878EA4CDA   |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    Signature = 0xEEA58C91E0CDCEB5799B00D2412D928FDD23122A1C2BDF43C2F8DA |
   |                        |    FAAEBAB53C7A44A8B22F35FDB9DE265F23B89F65A69A8B7BD4061911A6           |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the ECKCDSA_PrivateKey object from *Curve, X*                 |
   |                        |                                                                         |
   |                        | #. Verify the signature *Signature* on the *Msg*                        |
   |                        |                                                                         |
   |                        | #. Sign the *Msg* with the ECKCDSA_PrivateKey object and compare with   |
   |                        |    the expected output *Signature*                                      |
   |                        |                                                                         |
   |                        | #. Verify the generated signature on the *Msg*                          |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-ECKCDSA-2                                                         |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Invalid signatures should not verify                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    Hash Function = SHA-224                                              |
   |                        |    Curve = secp224r1                                                    |
   |                        |                                                                         |
   |                        | Private Parameters:                                                     |
   |                        |                                                                         |
   |                        | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    X = 0x9051A275AA4D98439EDDED13FA1C6CBBCCE775D8CC9433DEE69C59848B3594 |
   |                        |    DF                                                                   |
   |                        |    Msg = 0x5468697320697320612073616D706C65206D65737361676520666F722045 |
   |                        |    432D4B4344534120696D706C656D656E746174696F6E2076616C69646174696F6E2E |
   |                        |    Nonce = 0x76A0AFC18646D1B620A079FB223865A7BCB447F3C03A35D878EA4CDA   |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Signatures do not verify                                                |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the ECKCDSA_PrivateKey object from *Curve, X*                 |
   |                        |                                                                         |
   |                        | #. Sign the *Msg* with the ECKCDSA_PrivateKey object                    |
   |                        |                                                                         |
   |                        | #. Check that a signature with all zeros (of the length of that of the  |
   |                        |    generated signature) does not verify                                 |
   |                        |                                                                         |
   |                        | #. Create a modified version of the generated signature by changing the |
   |                        |    length of it or by flipping random bits in it                        |
   |                        |                                                                         |
   |                        | #. Check that this modified signature does not verify                   |
   +------------------------+-------------------------------------------------------------------------+

The following example shows an ECKCDSA-specific PKSIG-KEY-1 test case.
The constraints for this test case are:

-  Curve: secp256r1, secp384r1, secp521r1

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-KEY-ECDSA-1                                                       |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encode and decode an ECKCDSA public key as PEM                          |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Curve = secp256r1                                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random keypair on the ECDSA *Curve*                       |
   |                        |                                                                         |
   |                        | #. Encode the public key as PEM-encoded string                          |
   |                        |                                                                         |
   |                        | #. Create a ECKCDSA_PublicKey object from the PEM-encoded string,       |
   |                        |    decoding the PEM-encoded key                                         |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid                                   |
   |                        |                                                                         |
   |                        | #. Check that the key object algorithm name equals that of the          |
   |                        |    generated keypair                                                    |
   |                        |                                                                         |
   |                        | #. Check that the public key is valid by performing the checks from AIS |
   |                        |    46                                                                   |
   +------------------------+-------------------------------------------------------------------------+

RSA
---

The RSA algorithm is tested with the following constraints:

-  Number of test cases: 77
-  Source: ISO 9796-2:2010, Project Wycheproof, others
-  Hash Function: SHA-1, SHA-224, SHA-256, SHA-384, SHA-512
-  E: 3, 5, 7, 17, 79, 28609, 29115, 65537
-  P: 192 bits, 256 bits, 384 bits, 512 bits, 768 bits, 1024 bits, 1536
   bits, 2048 bits
-  Q: 192 bits, 256 bits, 384 bits, 512 bits, 768 bits, 1024 bits, 1536
   bits, 2048 bits
-  Msg: 0 bits – 1864 bits
-  Padding: EMSA1(SHA-1), EMSA2(SHA-1), EMSA2(SHA-224), EMSA2(SHA-256),
   EMSA2(SHA-384), EMSA2(SHA-512), EMSA3(Raw), EMSA3(SHA-1),
   EMSA3(SHA-224), EMSA3(SHA-256), EMSA3(SHA-384), EMSA3(SHA-512),
   EMSA4(SHA-1), EMSA4(SHA-1), ISO 9796-2 DS2(SHA-1), ISO 9797-2
   DS3(SHA-1)
-  Signature: 384 bits – 2048 bits

All the tests are implemented in :srcref:`src/tests/test_rsa.cpp`. The
following table shows an example test case with one test vector. Test
vectors for test cases PKSIG-RSA-1 and PKSIG-RSA-2 are listed in
:srcref:`src/tests/data/pubkey/rsa_sig.vec`. Test vectors for test case
PKSIG-RSA-3 are listed in :srcref:`src/tests/data/pubkey/rsa_invalid.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-RSA-1                                                             |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Sign a test message                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    Hash Function = SHA-1                                                |
   |                        |    E = 5                                                                |
   |                        |    P = 2932597160139455343587654517786101586715937059620256574803271522 |
   |                        |    4855053574888335295064118595233157878850644746476053                 |
   |                        |    Q = 3634072611698581074958455627374959034665880003838661976815530888 |
   |                        |    2211829358443758608966414537457415767576889158645019                 |
   |                        |    Msg = 0x4161436445664768496A4B                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    Signature = 0x3A3B7502D85F05128CFB74608205031339753DA50D0DB7E268C395 |
   |                        |    1F04A1981EDE22613BFC38DB9FFEBE183A4F11B0B0F8D7BEB668F7C1C385A801C2DD |
   |                        |    D7C08CB2E56082F80AD1105E930ED96DB6A0309639A51F5379B682C7F75C601BD4AD |
   |                        |    E5                                                                   |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the RSA_PrivateKey object from *P, Q, E*                      |
   |                        |                                                                         |
   |                        | #. Verify the signature *Signature* on the *Msg*                        |
   |                        |                                                                         |
   |                        | #. Sign the *Msg* with the RSA_PrivateKey object and compare with the   |
   |                        |    expected output *Signature*                                          |
   |                        |                                                                         |
   |                        | #. Verify the generated signature on the *Msg*                          |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-RSA-2                                                             |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Invalid signatures should not verify                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Hash Function = SHA-1                                                   |
   |                        |                                                                         |
   |                        | E = 5                                                                   |
   |                        |                                                                         |
   |                        | P =                                                                     |
   |                        | 293259716013945534358765451778610158671593705                           |
   |                        | 96202565748032715224855053574888335295064118595233157878850644746476053 |
   |                        |                                                                         |
   |                        | Q =                                                                     |
   |                        | 363407261169858107495845562737495903466588000                           |
   |                        | 38386619768155308882211829358443758608966414537457415767576889158645019 |
   |                        |                                                                         |
   |                        | Msg = 0x4161436445664768496A4B                                          |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Signatures do not verify                                                |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the RSA_PrivateKey object from *P*, *Q*, *E*                  |
   |                        |                                                                         |
   |                        | #. Sign the *Msg* with the RSA_PrivateKey object                        |
   |                        |                                                                         |
   |                        | #. Check that a signature with all zeros (of the length of that of the  |
   |                        |    generated signature) does not verify?                                |
   |                        |                                                                         |
   |                        | #. Create a modified version of the generated signature by changing the |
   |                        |    length of it or by flipping random bits in it                        |
   |                        |                                                                         |
   |                        | #. Check that this modified signature does not verify                   |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-3                                                                 |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Invalid signature should not verify                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Group: The DL group, e.g., modp/ietf/1024 or                         |
   |                        |                                                                         |
   |                        | -  Curve: The elliptic curve, e.g., secp192r1 or                        |
   |                        |                                                                         |
   |                        | -  P, Q, E: RSA parameters                                              |
   |                        |                                                                         |
   |                        | -  Private Parameters: Algorithm-specific Private Key Parameters        |
   |                        |                                                                         |
   |                        | -  Msg: The test message (varying length)                               |
   |                        |                                                                         |
   |                        | -  Padding: The padding scheme                                          |
   |                        |                                                                         |
   |                        | -  InvalidSignature: The invalid signature                              |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | |                                                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the RSA_PrivateKey object from *P, Q, E*                      |
   |                        |                                                                         |
   |                        | #. Check that the signature *InvalidSignature* does not verify          |
   +------------------------+-------------------------------------------------------------------------+

The following example shows an RSA-specific PKSIG-KEY-1 test case. The
constraints for this test case are:

-  Key Length: 1024 bits, 1280 bits

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-KEY-RSA-1                                                         |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encode and decode an RSA public key as PEM                              |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Key Length = 1024 bits                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random *Key Length* bits RSA keypair with E = 65537       |
   |                        |                                                                         |
   |                        | #. Encode the public key as PEM-encoded string                          |
   |                        |                                                                         |
   |                        | #. Create a RSA_PublicKey object from the PEM-encoded string, decoding  |
   |                        |    the PEM-encoded key                                                  |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid                                   |
   |                        |                                                                         |
   |                        | #. Check that the key object algorithm name equals that of the          |
   |                        |    generated keypair                                                    |
   |                        |                                                                         |
   |                        | #. Check that the public key is valid by checking that:                 |
   |                        |                                                                         |
   |                        |    #. N >= 35                                                           |
   |                        |                                                                         |
   |                        |    #. N is uneven                                                       |
   |                        |                                                                         |
   |                        |    #. E >= 2                                                            |
   +------------------------+-------------------------------------------------------------------------+

SPHINCS+
--------

The implementation is tested for correctness using the Known Answer Test vectors
demanded by the NIST submission and provided by the reference implementation.
Given SPHINCS+' performance characteristics, each supported algorithm
parameterization gets just a single KAT test.

Along with those integration tests Botan comes with a number of unit tests whose
vectors were also extracted from intermediate results of the reference
implementation. Particularly, the SPHINCS+-specific implementation of WOTS+ and
FORS is covered by those unit tests.

Additionally, Botan has implementation-specific test cases. Those ensure the
interoperability of the algorithm when using Botan's generic API for public key
algorithms. These test cases are equal for all public key schemes and are
therefore not discussed in detail in this chapter.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-SPHINCS+-1                                                        |
   +========================+=========================================================================+
   | **Type:**              | Known Answer Tests                                                      |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Uses the KAT vectors of SPHINCS+' reference implementation as           |
   |                        | specified in the NIST submission.                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Test Vectors with RNG seed and test messages inputs in:                 |
   |                        |                                                                         |
   |                        | * :srcref:`src/tests/data/pubkey/sphincsplus.vec`                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Above described test vector files contain expected values for:          |
   |                        |                                                                         |
   |                        | * SPHINCS+ Public Key                                                   |
   |                        | * SPHINCS+ Private Key                                                  |
   |                        | * Signature                                                             |
   |                        |                                                                         |
   |                        | to save disk space, the expected signature is stored as a digest only.  |
   |                        | We use the same hash function of the respective SPHINCS+ instantiation. |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | For each KAT vector:                                                    |
   |                        |                                                                         |
   |                        | #. Seed a AES-256-CTR-DRBG with the specified RNG seed and pull the     |
   |                        |    entropy bits needed for generating a SPHINCS+ keypair from it.       |
   |                        |                                                                         |
   |                        | #. Generate a SPHINCS+ key pair and validate that it corresponds to the |
   |                        |    expected key pair in the test vector.                                |
   |                        |                                                                         |
   |                        | #. Sign the message provided in the test vector with the just-generated |
   |                        |    private key and validate that the digest of the calculated           |
   |                        |    signature is equal to the test vector's expectation.                 |
   |                        |                                                                         |
   |                        | #. Verify the calculated signature using the generated public key.      |
   |                        |                                                                         |
   |                        | For a subset of combinations (namely when the "128bit fast" parameters  |
   |                        | are used), run those additional tests:                                  |
   |                        |                                                                         |
   |                        | #. Deserialize the key pair from the encodings provided in the test     |
   |                        |    vector and exercise the signing/validation cycle again.              |
   |                        |                                                                         |
   |                        | #. Randomly alter the signature and ensure that the verification fails. |
   |                        |                                                                         |
   |                        | #. Retry the verification using the same key object with the valid      |
   |                        |    signature.                                                           |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-SPHINCS+-2                                                        |
   +========================+=========================================================================+
   | **Type:**              | Known Answer Test                                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Ensures that the WOTS+ sub-component of SPHINCS+ works as expected.     |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Test Vectors in:                                                        |
   |                        |                                                                         |
   |                        | * :srcref:`src/tests/data/pubkey/sphincsplus_wots.vec`                  |
   |                        |                                                                         |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Hashed WOTS+ signatures and keys as defined in the test vector.         |
   |                        |                                                                         |
   |                        | To save disk space, the WOTS+ public keys and signatures in the test    |
   |                        | vector are stored as digests only. The WOTS+ public key is hashed just  |
   |                        | as it would be when creating an XMSS leaf node.                         |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | For each test vector entry:                                             |
   |                        |                                                                         |
   |                        | #. Recreate the WOTS+ signature and hashed public key from the          |
   |                        |    given input values and validate it against the provided values.      |
   |                        |    The signature is hashed for comparison.                              |
   |                        |                                                                         |
   |                        | #. Extract and validate the WOTS+ public key from the computed          |
   |                        |    signature. The WOTS+ public key is hashed for comparison.            |
   |                        |                                                                         |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-SPHINCS+-3                                                        |
   +========================+=========================================================================+
   | **Type:**              | Known Answer Test                                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Ensures that the FORS sub-component of SPHINCS+ works as expected.      |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Test Vectors in:                                                        |
   |                        |                                                                         |
   |                        | * :srcref:`src/tests/data/pubkey/sphincsplus_fors.vec`                  |
   |                        |                                                                         |
   |                        | To save disk space, the FORS signatures in the test vector are stored   |
   |                        | as digests only.                                                        |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | FORS signatures and keys as defined in the test vector                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | For each test vector entry:                                             |
   |                        |                                                                         |
   |                        | #. Generate a FORS signature and public key for the provided message    |
   |                        |    and secret seed and validate those against the ones provided.        |
   |                        |                                                                         |
   |                        | #. From the generated FORS signature, recreate the FORS public key and  |
   |                        |    validate it against the one provided in the test data.               |
   +------------------------+-------------------------------------------------------------------------+

Extended Hash-Based Signatures (XMSS)
-------------------------------------

Signature Generation
~~~~~~~~~~~~~~~~~~~~

The XMSS signature generation algorithm [XMSS] is tested with the
following constraints:

-  Hash Function: SHA-256, SHA-512
-  w: 16
-  h: 10
-  Msg: 0 bits – 400 bits
-  Signature: 20032 bits - 72768 bits

All the tests are implemented in :srcref:`src/tests/test_xmss.cpp`. All test
vectors are listed in :srcref:`src/tests/data/pubkey/xmss_sig.vec`. Currently 4
test vectors are tested. Optional additional test vectors are present
within *xmss_sig.vec* but commented out by default to reduce the test
bench run time. The hash function and algorithm parameters “w”, “h” are
provided through the algorithm oid, which is part of the private key.
The following table shows an example test case with one test vector.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-XMSS-1                                                            |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Sign a test message                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    Hash Function = SHA-256                                              |
   |                        |    h = 10                                                               |
   |                        |    PrivateKey = 0x01000001A020196CDE3A20C13477CE56DE3A7A4381821EA50BF07 |
   |                        |    F0670048A0E1736D22876575FA4F5404B393828F74776A9B9C73B0962069652B0884 |
   |                        |    32242E12CF75E170000000000000000CE1994BC37AEDD7E21851001EC0F4296ECC3D |
   |                        |    389263E4E720D05EFFD60A20A41B90B7E2CC1647319B4B143CEDDADADFB3E571BE68 |
   |                        |    F36ACC8D6C0A0ADD41266F2                                              |
   |                        |    Msg = 0x078A87923DEC59CE843149F5E642A3F921E2E78543132F88BA637A09DF0C |
   |                        |    16552A3037E3EEB3A30FDA5DF73AE2E0DD3821D1                             |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    Signature = 0x0000000000000000D3A842202DB1812F8DC93387EA6A78D01211D0 |
   |                        |    0911D37678CAD55CBC228B2DA495C0B88593D505696EF3BE99A6742B75A12555BBED |
   |                        |    E5F788D4F4B7DAE4E6C7DA82FAA2D7E60F836673BC0BAE8CB75A6A94480970C90A41 |
   |                        |    2E49AE7B0CFA63025C1444A746C5BDCF9D8618CECE33549043A98D05CBA7673FB7E4 |
   |                        |    F835E624B482E85B3B2AFF7613CD58F1C8FF2B0E6011E02F5A3387708E8E99970EB0 |
   |                        |    [...]                                                                |
   |                        |    880DC8C51FC850354AACB05BD175542080D0C87CEA99081ADF901920EA6327B761DE |
   |                        |    A28B61951EAEC23BC9DC30D32DD0ED4FCFE39F575803F874D72D71D48CE8F26D47B0 |
   |                        |    CC74881C54F80F41DB4718EC04FAAADFD93AF8B8A258527024658FB28D4F6983DAA0 |
   |                        |    1558F85BF8C6120D355388C302516D1FDA5480961799AC8B5E9B485BC579675F03CE |
   |                        |    604A103DF21CD31ADD951AD0A3AE1AD1788444997EB12F78BA96E909C74543EB6D0D |
   |                        |    CAFAE60796632E6888E3B3D2EB6D6B733AA53C455C04473C2213494570F6C8AE04FE |
   |                        |    F4307419A7D84C87EF8A9CA8DC62177D2BC09FB1362ECF7A6E879B51B0B27B535835 |
   |                        |    6689289D09BAEC2F204ADBA0A20C05A5E7C59F10D4C9F0C349ED71B2D08CFAFC96CB |
   |                        |    97DE01FBC0484B2                                                      |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the XMSS_PrivateKey object from the byte sequence provided    |
   |                        |    through input value “PrivateKey”                                     |
   |                        |                                                                         |
   |                        | #. Verify the signature *Signature* on the *Msg*                        |
   |                        |                                                                         |
   |                        | #. Sign the *Msg* with the XMSS_PrivateKey object and compare with the  |
   |                        |    expected output *Signature*                                          |
   |                        |                                                                         |
   |                        | #. Verify the generated signature on the *Msg*                          |
   +------------------------+-------------------------------------------------------------------------+

Signature Verification
~~~~~~~~~~~~~~~~~~~~~~

The XMSS signature verification is tested with the following
constraints:

-  Hash Function: SHA-256, SHA-512
-  w: 16
-  h: 10, 16, 20
-  Msg: 0 bits – 2640 bits
-  Signature: 20032 bits - 77888 bits

The hash function and algorithm parameters “w”, “h” are provided through
the algorithm oid, which is part of the private key. Test vectors for
the test case PKSIG-XMSS-2 and PKCS-XMSS-3 are listed in
:srcref:`src/tests/data/pubkey/xmss_verify.vec` and in
:srcref:`src/tests/data/pubkey/xmss_invalid.vec`, correspondingly.The following
table shows an example test case with one test vector.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-XMSS-2                                                            |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Valid signatures should verify                                          |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    Hash Function = SHA-512                                              |
   |                        |    h=10                                                                 |
   |                        |    PublicKey = 0x04000004E0489566FE62275CF1BE38B809F0F959717848A76D26B2 |
   |                        |    392793BC6523FC57AA78B3EBBEB74462990EAF2E2FB89F988B804EF9A31556413471 |
   |                        |    24F7728040C1EF60BF55B84746D9B9232F0221A3EF11728BF25E797985607C06432E |
   |                        |    A5B4122574923583E7127424B4304D01F90DE74E2C81ACA71E6721805B70E9C77FA1 |
   |                        |    9C5C0F                                                               |
   |                        |    Msg = 0x426E562AB69A03A893F56910A2AED2A0618DA1E365167749E78BEB4997D3 |
   |                        |    6DC054F34225797478A5153037D4154A90C88836EAB69A7F6783237143FDEDBDB6FB |
   |                        |    A8AEDFD98D3AF16FA293660640163C0936AE072C0D38772013B0BBF97CF44B64C44A |
   |                        |    CB62803A7B2B374DA627E47A1135782F09537E873AAF5BB54676BB5195AADDF73B64 |
   |                        |    FB9B32                                                               |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Signatures verifies                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | |                                                                       |
   |                        |                                                                         |
   |                        | #. Create the XMSS_PublicKey object from the byte sequence provided     |
   |                        |    through input value “Public”                                         |
   |                        |                                                                         |
   |                        | #. Check that the is modified signature does not verifies               |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PKSIG-XMSS-3                                                            |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Invalid signatures should not verify                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    Hash Function = SHA-256                                              |
   |                        |    h=10                                                                 |
   |                        |    PublicKey = 0x01000001c9802b0c3dfa2596ffde21b7b9abfed5094d7e936a9690 |
   |                        |    0ad7ca634ad7bffeade07f1a46e940a2630bb8da78dfeae742d5a9712e15459d9d51 |
   |                        |    f2a22145f25be0                                                       |
   |                        |    Msg = 0x0d8a2b78908b8a2537a194af3b98de9355384accdd7d2e3b542e37dab55f |
   |                        |    0fbd8fe163e261d37074f7fcc3f4e7d1774cddc6                             |
   |                        |    InvalidSignature = 0x00000000000000001762b20507b3bf51231e50aa3bed990 |
   |                        |    b93493fdec8040ae24043fc7d5a0e0d8744611ec5f883282695c4a181de84d3fd993 |
   |                        |    e24749f6d855453a1507bc0703cc5645bfb281687fa9c9a8375c19dd51b0a62a5036 |
   |                        |    e570a45fc1f3c89bdd1147dd200f3756b6c04634f7d2abb37da79555cd209975824d |
   |                        |    0363cebbab14d3419e0e99233413c6226e811a1cdedacce918c467cd468ba21a3bf2 |
   |                        |    f3c549bf0d93a87cb0a7f6574d3db01dbfc5d61c8eb60b8b3adc4ff5d8d63d9f9e91 |
   |                        |    [...]                                                                |
   |                        |    0d84f26ceb28a7a340f36f0bbf91451b4dd5a599eb661018dd6dd3870c510b251d65 |
   |                        |    006f4e51d1909283c87e086ab3cbeed325a628fb8b885890bdc3062bbd6bbb3ebc59 |
   |                        |    da5a906f347192d69fbb76333099d809456ad7a5fd4dc4e0e23f4473ca9167065ccd |
   |                        |    60a526fa88e550c                                                      |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Signatures do not verify                                                |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the XMSS_PublicKey object from the byte sequence provided     |
   |                        |    through input value “Public”                                         |
   |                        |                                                                         |
   |                        | #. Check that the signature *InvalidSignature* does not verify          |
   +------------------------+-------------------------------------------------------------------------+
