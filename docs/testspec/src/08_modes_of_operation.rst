Modes of Operation
==================

Block cipher modes of operation are tested using known answer tests that
(1) encrypt a message and (2) decrypt a message. All the tests are
implemented in :srcref:`src/tests/test_modes.cpp`. The test cases are described
in the following.

.. table::
   :class: longtable
   :widths: 20 80

   +---------------------+----------------------------------------------------------------------------+
   | **Test Case No.:**  | MODE-1                                                                     |
   +=====================+============================================================================+
   | **Type:**           | Positive Test                                                              |
   +---------------------+----------------------------------------------------------------------------+
   | **Description:**    | Known Answer Test that verifies the correctness of encryption under the    |
   |                     | mode of operation                                                          |
   +---------------------+----------------------------------------------------------------------------+
   | **Preconditions:**  | None                                                                       |
   +---------------------+----------------------------------------------------------------------------+
   | **Input Values:**   | -  Block Cipher: The underlying block cipher, e.g., AES-128 or AES-256     |
   |                     |                                                                            |
   |                     | -  Key: The encryption/decryption key used for the block cipher (varying   |
   |                     |    length depending on the block cipher)                                   |
   |                     |                                                                            |
   |                     | -  Nonce: The nonce used to initialize the mode of operation (varying      |
   |                     |    length)                                                                 |
   |                     |                                                                            |
   |                     | -  In: The test message to be encrypted (varying length)                   |
   +---------------------+----------------------------------------------------------------------------+
   | **Expected          | -  Out: Ciphertext (varying length depending on the block cipher)          |
   | Output:**           |                                                                            |
   +---------------------+----------------------------------------------------------------------------+
   | **Steps:**          | #. Create a Cipher_Mode encryption object                                  |
   |                     |                                                                            |
   |                     | #. Test the name of the mode                                               |
   |                     |                                                                            |
   |                     | #. Test that the mode is not an authenticated mode                         |
   |                     |                                                                            |
   |                     | #. Test that calculating the ciphertext before setting a key throws an     |
   |                     |    exception                                                               |
   |                     |                                                                            |
   |                     | #. Test that large nonce sizes are rejected by throwing an exception       |
   |                     |                                                                            |
   |                     | #. Set the key *Key* on the Cipher_Mode encryption object                  |
   |                     |                                                                            |
   |                     | #. Set the nonce *Nonce* on the Cipher_Mode encryption object              |
   |                     |                                                                            |
   |                     | #. Calculate the ciphertext of input value *In* and compare the result     |
   |                     |    with the expected output value *Out*                                    |
   |                     |                                                                            |
   |                     | #. If *In* is longer than the block size of the mode, calculate the        |
   |                     |    ciphertext of input value *In* by encrypting *In* in block size blocks  |
   |                     |    and comparing the result with the expected output value *Out*           |
   |                     |                                                                            |
   |                     | #. If *In* is longer than the block size of the mode, calculate the        |
   |                     |    ciphertext of input value *In* by encrypting *In* in multiples of block |
   |                     |    size blocks and comparing the result with the expected output value     |
   |                     |    *Out*                                                                   |
   |                     |                                                                            |
   |                     | #. Calculate the ciphertext of input value *In* in one go on a buffer      |
   |                     |    with a non-zero offset and check that the bytes before the offset       |
   |                     |    remain untouched and the ciphertext equals the expected output *Out*    |
   |                     |                                                                            |
   |                     | #. Calculate the ciphertext of input value *In* incrementally on           |
   |                     |    buffers with a non-zero offset and check that the bytes before the      |
   |                     |    offset remain untouched and the ciphertext equals the expected          |
   |                     |    output *Out*                                                            |
   |                     |                                                                            |
   |                     | #. Clear the Cipher_Mode encryption object                                 |
   |                     |                                                                            |
   |                     | #. Test that calculating the ciphertext after clearing throws an exception |
   +---------------------+----------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +---------------------+----------------------------------------------------------------------------+
   | **Test Case No.:**  | MODE-2                                                                     |
   +=====================+============================================================================+
   | **Type:**           | Positive Test                                                              |
   +---------------------+----------------------------------------------------------------------------+
   | **Description:**    | Known Answer Test that verifies the correctness of decryption under the    |
   |                     | mode of operation                                                          |
   +---------------------+----------------------------------------------------------------------------+
   | **Preconditions:**  | None                                                                       |
   +---------------------+----------------------------------------------------------------------------+
   | **Input Values:**   | -  Block Cipher: The underlying block cipher, e.g., AES-128 or AES-256     |
   |                     |                                                                            |
   |                     | -  Key: The encryption/decryption key used for the block cipher (varying   |
   |                     |    length depending on the block cipher)                                   |
   |                     |                                                                            |
   |                     | -  Nonce: The nonce used to initialize the mode of operation (varying      |
   |                     |    length)                                                                 |
   |                     |                                                                            |
   |                     | -  Out: Ciphertext (varying length depending on the block cipher)          |
   +---------------------+----------------------------------------------------------------------------+
   | **Expected          | -  In: The original plaintext (varying length)                             |
   | Output:**           |                                                                            |
   +---------------------+----------------------------------------------------------------------------+
   | **Steps:**          | #. Create a Cipher_Mode decryption object                                  |
   |                     |                                                                            |
   |                     | #. Test the name of the mode                                               |
   |                     |                                                                            |
   |                     | #. Test that the mode is not an authenticated mode                         |
   |                     |                                                                            |
   |                     | #. Test that calculating the ciphertext before setting a key throws an     |
   |                     |    exception                                                               |
   |                     |                                                                            |
   |                     | #. Test that large nonce sizes are rejected by throwing an exception       |
   |                     |                                                                            |
   |                     | #. Set the key *Key* on the Cipher_Mode decryption object                  |
   |                     |                                                                            |
   |                     | #. Set the nonce *Nonce* on the Cipher_Mode decryption object              |
   |                     |                                                                            |
   |                     | #. Calculate the plaintext of input value *Out* and compare the result     |
   |                     |    with the expected output value *In*                                     |
   |                     |                                                                            |
   |                     | #. If *Out* is longer than the block size of the mode, calculate the       |
   |                     |    plaintext of input value *Out* by decrypting *Out* in block size blocks |
   |                     |    and comparing the result with the expected output value *In*            |
   |                     |                                                                            |
   |                     | #. If *Out* is longer than the block size of the mode, calculate the       |
   |                     |    plaintext of input value *Out* by decrypting *Out* in multiples of      |
   |                     |    block size blocks and comparing the result with the expected output     |
   |                     |    value *In*                                                              |
   |                     |                                                                            |
   |                     | #. Calculate the plaintext of input value *Out* in one go on a buffer      |
   |                     |    with a non-zero offset and check that the bytes before the offset       |
   |                     |    remain untouched and the plaintext equals the expected output *In*      |
   |                     |                                                                            |
   |                     | #. Calculate the plaintext of input value *Out* incrementally on           |
   |                     |    buffers with a non-zero offset and check that the bytes before the      |
   |                     |    offset remain untouched and the plaintext equals the expected           |
   |                     |    output *In*                                                             |
   |                     |                                                                            |
   |                     | #. Clear the Cipher_Mode decryption object                                 |
   |                     |                                                                            |
   |                     | #. Test that calculating the plaintext after clearing throws an exception  |
   +---------------------+----------------------------------------------------------------------------+

CBC
---

CBC is tested with the following constraints:

-  Number of test cases: 281

-  Block Cipher: AES-128, AES-192, AES-256, ARIA-256, Blowfish, CAST-128,
   DES, TripleDES and Noekeon
-  Padding: NoPadding, PKCS7 and OneAndZeros
-  Key: 64 bits to 256 bits (depending on the block cipher)
-  Nonce: 64 bits or 128 bits (matching the block size of the block cipher)
-  In: 0 bits to 1280 bits
-  Out: 64 bits to 1280 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/modes/cbc.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +---------------------+----------------------------------------------------------------------------+
   | **Test Case No.:**  | MODE-CBC-1                                                                 |
   +=====================+============================================================================+
   | **Type:**           | Positive Test                                                              |
   +---------------------+----------------------------------------------------------------------------+
   | **Description:**    | Known Answer Test that verifies the correctness of encryption under CBC    |
   +---------------------+----------------------------------------------------------------------------+
   | **Preconditions:**  | None                                                                       |
   +---------------------+----------------------------------------------------------------------------+
   | **Input Values:**   | .. code-block:: none                                                       |
   |                     |                                                                            |
   |                     |    Block Cipher = AES-128                                                  |
   |                     |    Key = 0x2B7E151628AED2A6ABF7158809CF4F3C (128 bits)                     |
   |                     |    Nonce = 0x000102030405060708090A0B0C0D0E0F (128 bits)                   |
   |                     |    In = 0x6BC1BEE22E409F96E93D7E117393172AAE2D8A571E03AC9C9EB76FAC45AF8E51 |
   |                     |    30C81C46A35CE411E5FBC1191A0A52EFF69F2445DF4F9B17AD2B417BE66C3710        |
   |                     |    (512 bits)                                                              |
   +---------------------+----------------------------------------------------------------------------+
   | **Expected          | .. code-block:: none                                                       |
   | Output:**           |                                                                            |
   |                     |    Out = 0x7649ABAC8119B246CEE98E9B12E9197D5086CB9B507219EE95DB113A917678B |
   |                     |    273BED6B8E3C1743B7116E69E222295163FF1CAA1681FAC09120ECA307586E1A7       |
   |                     |    (512 bits)                                                              |
   +---------------------+----------------------------------------------------------------------------+
   | **Steps:**          | #. Create a CBC_Encryption object                                          |
   |                     |                                                                            |
   |                     | #. Test the name of the mode                                               |
   |                     |                                                                            |
   |                     | #. Test that the mode is not an authenticated mode                         |
   |                     |                                                                            |
   |                     | #. Test that calculating the ciphertext before setting a key throws an     |
   |                     |    exception                                                               |
   |                     |                                                                            |
   |                     | #. Test that large nonce sizes are rejected by throwing an exception       |
   |                     |                                                                            |
   |                     | #. Set the key *Key* on the CBC_Encryption object                          |
   |                     |                                                                            |
   |                     | #. Set the nonce *Nonce* on the CBC_Encryption object                      |
   |                     |                                                                            |
   |                     | #. Calculate the ciphertext of input value *In* and compare the result     |
   |                     |    with the expected output value *Out*                                    |
   |                     |                                                                            |
   |                     | #. Clear the CBC_Encryption object                                         |
   |                     |                                                                            |
   |                     | #. Test that calculating the ciphertext after clearing throws an exception |
   +---------------------+----------------------------------------------------------------------------+

CBC-CTS (CBC-CS3)
-----------------

CBC-CTS is tested with the following constraints:

-  Number of test cases: 48 (6 with AES-128, 42 with DES)
-  Source: RFC 3962 (AES-128 test cases)

-  Block Cipher: AES-128, DES
-  Key: 128 bits (AES-128), 64 bits (DES)
-  Nonce: 128 bits (AES-128), 64 bits (DES)
-  In: 136 bits - 512 bits (AES-128), 72 bits - 400 bits (DES)
-  Out: 136 bits - 512 bits (AES-128), 72 bits - 400 bits (DES)

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/modes/cbc.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +---------------------+----------------------------------------------------------------------------+
   | **Test Case No.:**  | MODE-CTS-1                                                                 |
   +=====================+============================================================================+
   | **Type:**           | Positive Test                                                              |
   +---------------------+----------------------------------------------------------------------------+
   | **Description:**    | Known Answer Test that verifies the correctness of encryption under CTS    |
   +---------------------+----------------------------------------------------------------------------+
   | **Preconditions:**  | None                                                                       |
   +---------------------+----------------------------------------------------------------------------+
   | **Input Values:**   | Block Cipher = AES-128                                                     |
   |                     |                                                                            |
   |                     | Key = 0x636869636b656e207465726979616b69 (128 bits)                        |
   |                     |                                                                            |
   |                     | Nonce = 0x00000000000000000000000000000000 (128 bits)                      |
   |                     |                                                                            |
   |                     | In = 0x4920776f756c64206c696b652074686520 (136 bits)                       |
   +---------------------+----------------------------------------------------------------------------+
   | **Expected          | Out = 0xc6353568f2bf8cb4d8a580362da7ff7f97 (136 bits)                      |
   | Output:**           |                                                                            |
   +---------------------+----------------------------------------------------------------------------+
   | **Steps:**          | #. Create a CTS_Encryption object                                          |
   |                     |                                                                            |
   |                     | #. Test the name of the mode                                               |
   |                     |                                                                            |
   |                     | #. Test that the mode is not an authenticated mode                         |
   |                     |                                                                            |
   |                     | #. Test that calculating the ciphertext before setting a key throws an     |
   |                     |    exception                                                               |
   |                     |                                                                            |
   |                     | #. Test that large nonce sizes are rejected by throwing an exception       |
   |                     |                                                                            |
   |                     | #. Set the key *Key* on the CTS_Encryption object                          |
   |                     |                                                                            |
   |                     | #. Set the nonce *Nonce* on the CTS_Encryption object                      |
   |                     |                                                                            |
   |                     | #. Calculate the ciphertext of input value *In* and compare the result     |
   |                     |    with the expected output value *Out*                                    |
   |                     |                                                                            |
   |                     | #. Clear the CTS_Encryption object                                         |
   |                     |                                                                            |
   |                     | #. Test that calculating the ciphertext after clearing throws an exception |
   +---------------------+----------------------------------------------------------------------------+

CTR
---

CTR mode is a stream cipher mode of operation in the library and thus is
tested differently than other block cipher modes of operation. All the
stream cipher modes of operation tests are implemented in
:srcref:`src/tests/test_stream.cpp`. CTR mode is tested with the following
constraints:

-  Number of test cases: 821

-  Block Cipher: AES-128, AES-192, AES-256, ARIA, Blowfish, DES, TripleDES,
   Noekeon and Serpent
-  AES-128 is additionally tested with restricted counter widths of 32 bits,
   40 bits, 48 bits and 64 bits
-  Key: 64 bits to 256 bits (depending on the block cipher)
-  Nonce: 64 bits, 120 bits or 128 bits
-  In: 8 bits to 65536 bits
-  Out: 8 bits to 65536 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/stream/ctr.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**   | MODE-CTR-1                                                               |
   +======================+==========================================================================+
   | **Type:**            | Positive Test                                                            |
   +----------------------+--------------------------------------------------------------------------+
   | **Description:**     | Known Answer Test that verifies the correctness of encryption under CTR  |
   +----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**   | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Input Values:**    | .. code-block:: none                                                     |
   |                      |                                                                          |
   |                      |    Block Cipher = AES-128                                                |
   |                      |    Key = 0x2B7E151628AED2A6ABF7158809CF4F3C (128 bits)                   |
   |                      |    Nonce = 0xF0F1F2F3F4F5F6F7F8F9FAFBFCFDFEFF (128 bits)                 |
   |                      |    In = 0x6BC1BEE22E409F96E93D7E117393172AAE2D8A571E03AC9C9EB76FAC45AF8E |
   |                      |    5130C81C46A35CE411E5FBC1191A0A52EFF69F2445DF4F9B17AD2B417BE66C3710    |
   |                      |    (384 bits)                                                            |
   +----------------------+--------------------------------------------------------------------------+
   | **Expected Output:** | .. code-block:: none                                                     |
   |                      |                                                                          |
   |                      |    Out = 0x874D6191B620E3261BEF6864990DB6CE9806F66B7970FDFF8617187BB9FFF |
   |                      |    DFF5AE4DF3EDBD5D35E5B4F09020DB03EAB1E031DDA2FBE03D1792170A0F3009CEE   |
   |                      |    (384 bits)                                                            |
   +----------------------+--------------------------------------------------------------------------+
   | **Steps:**           | #. Create a StreamCipher object                                          |
   |                      |                                                                          |
   |                      | #. Test the name of the mode                                             |
   |                      |                                                                          |
   |                      | #. Set the key *Key* on the StreamCipher object                          |
   |                      |                                                                          |
   |                      | #. Set the IV *Nonce* on the StreamCipher object                         |
   |                      |                                                                          |
   |                      | #. Clone the StreamCipher object and check that it has a different       |
   |                      |    pointer but the same name                                             |
   |                      |                                                                          |
   |                      | #. Set a random key on the cloned StreamCipher object                    |
   |                      |                                                                          |
   |                      | #. Calculate the ciphertext of input value *In* on the original          |
   |                      |    StreamCipher object and compare the result with the expected output   |
   |                      |    value *Out*                                                           |
   +----------------------+--------------------------------------------------------------------------+
