AEAD Modes
==========

AEAD modes are tested using known answer tests that (1) encrypt a
message, (2) decrypt a message and (3) an additional test to check
whether AEAD decryption correctly rejects manipulated ciphertexts and
manipulated nonces. All the tests are implemented in
:srcref:`src/tests/test_aead.cpp`. The test cases are described in the
following.

.. table::
   :class: longtable
   :widths: 20 80

   +----------------------+---------------------------------------------------------------------------+
   | **Test Case No.:**   | AEAD-1                                                                    |
   +----------------------+---------------------------------------------------------------------------+
   | **Type:**            | Positive Test                                                             |
   +----------------------+---------------------------------------------------------------------------+
   | **Description:**     | Known Answer Test that verifies the correctness of AEAD encryption        |
   +----------------------+---------------------------------------------------------------------------+
   | **Preconditions:**   | None                                                                      |
   +----------------------+---------------------------------------------------------------------------+
   | **Input Values:**    | -  Block Cipher: The underlying block cipher, e.g., AES-128 or AES-256    |
   |                      |                                                                           |
   |                      | -  Key: The encryption/decryption key used for the block cipher (varying  |
   |                      |    length depending on the block cipher)                                  |
   |                      |                                                                           |
   |                      | -  Nonce: The nonce used to initialize the AEAD mode (varying length)     |
   |                      |                                                                           |
   |                      | -  In: The test message to be encrypted (varying length)                  |
   |                      |                                                                           |
   |                      | -  AD: Additional data to be authenticated (varying length, optional)     |
   +----------------------+---------------------------------------------------------------------------+
   | **Expected Output:** | -  Out: Ciphertext (varying length depending on the block cipher)         |
   +----------------------+---------------------------------------------------------------------------+
   | **Steps:**           | #. Create a AEAD_Encryption object                                        |
   |                      |                                                                           |
   |                      | #. Check that the AEAD output length matches the length of *Out*          |
   |                      |                                                                           |
   |                      | #. Check that the AEAD mode accepts nonces of the default nonce length    |
   |                      |                                                                           |
   |                      | #. Check that trying to encrypt a random value before setting a key       |
   |                      |    throws an exception                                                    |
   |                      |                                                                           |
   |                      | #. If the AEAD mode requires the key to be set prior to setting           |
   |                      |    associated data, check that setting *AD* on the AEAD_Encryption object |
   |                      |    throws an exception                                                    |
   |                      |                                                                           |
   |                      | #. Set the key *Key* on the AEAD_Encryption object                        |
   |                      |                                                                           |
   |                      | #. Check that trying to encrypt a random value before setting a nonce     |
   |                      |    throws an exception                                                    |
   |                      |                                                                           |
   |                      | #. Set a modified version of associated data *AD* on the AEAD_Encryption  |
   |                      |    object                                                                 |
   |                      |                                                                           |
   |                      | #. Set a modified version of nonce *Nonce* on the AEAD_Encryption object  |
   |                      |                                                                           |
   |                      | #. Pass a random plaintext value into the AEAD_Encryption object          |
   |                      |                                                                           |
   |                      | #. Reset the AEAD_Encryption object                                       |
   |                      |                                                                           |
   |                      | #. Set the nonce *Nonce* on the AEAD_Encryption object                    |
   |                      |                                                                           |
   |                      | #. Set the associated data *AD* on the AEAD_Encryption object             |
   |                      |                                                                           |
   |                      |    #. In case it throws an exception (for some modes that don’t allow     |
   |                      |       setting AD after the nonce), reset the AEAD_Encryption object, and  |
   |                      |       set *AD* and *Nonce*                                                |
   |                      |                                                                           |
   |                      | #. Calculate the ciphertext of input value *In* and compare the result    |
   |                      |    with the expected output value *Out*                                   |
   |                      |                                                                           |
   |                      | #. If *In* is the empty message, Return                                   |
   |                      |                                                                           |
   |                      | #. If *In* is longer than the block size of the AEAD mode, calculate the  |
   |                      |    ciphertext of input value *In* by encrypting *In* in block size blocks |
   |                      |    and comparing the result with the expected output value *Out*          |
   |                      |                                                                           |
   |                      | #. If *In* is longer than the block size of the AEAD mode, calculate the  |
   |                      |    ciphertext of input value *In* by encrypting *In* in multiples of      |
   |                      |    block size blocks and comparing the result with the expected output    |
   |                      |    value *Out*                                                            |
   |                      |                                                                           |
   |                      | #. Clear the AEAD_Encryption object                                       |
   |                      |                                                                           |
   |                      | #. Check that trying to encrypt a random value after clearing throws an   |
   |                      |    exception                                                              |
   |                      |                                                                           |
   |                      | #. If the AEAD requires the key to be set prior to setting associated     |
   |                      |    data, check that setting *AD* on the AEAD_Encryption object throws an  |
   |                      |    exception                                                              |
   +----------------------+---------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +----------------------+---------------------------------------------------------------------------+
   | **Test Case No.:**   | AEAD-2                                                                    |
   +----------------------+---------------------------------------------------------------------------+
   | **Type:**            | Positive Test                                                             |
   +----------------------+---------------------------------------------------------------------------+
   | **Description:**     | Known Answer Test that verifies the correctness of AEAD decryption        |
   +----------------------+---------------------------------------------------------------------------+
   | **Preconditions:**   | None                                                                      |
   +----------------------+---------------------------------------------------------------------------+
   | **Input Values:**    | -  Block Cipher: The underlying block cipher, e.g., AES-128 or AES-256    |
   |                      |                                                                           |
   |                      | -  Key: The encryption/decryption key used for the block cipher (varying  |
   |                      |    length depending on the block cipher)                                  |
   |                      |                                                                           |
   |                      | -  Nonce: The nonce used to initialize the AEAD mode (varying length)     |
   |                      |                                                                           |
   |                      | -  Out: Ciphertext (varying length depending on the block cipher)         |
   |                      |                                                                           |
   |                      | -  AD: Additional data to be authenticated (varying length, optional)     |
   +----------------------+---------------------------------------------------------------------------+
   | **Expected Output:** | -  In: The original test message (plaintext, varying length)              |
   +----------------------+---------------------------------------------------------------------------+
   | **Steps:**           | #. Create a AEAD_Decryption object                                        |
   |                      |                                                                           |
   |                      | #. Check that the AEAD output length matches the length of *Out*          |
   |                      |                                                                           |
   |                      | #. Check that the AEAD mode accepts nonces of the default nonce length    |
   |                      |                                                                           |
   |                      | #. Check that trying to decrypt a random value before setting a key       |
   |                      |    throws an exception                                                    |
   |                      |                                                                           |
   |                      | #. If the AEAD mode requires the key to be set prior to setting           |
   |                      |    associated data, check that setting *AD* on the AEAD_Decryption object |
   |                      |    throws an exception                                                    |
   |                      |                                                                           |
   |                      | #. Set the key *Key* on the AEAD_Encryption object                        |
   |                      |                                                                           |
   |                      | #. Check that trying to decrypt a random value before setting a nonce     |
   |                      |    throws an exception                                                    |
   |                      |                                                                           |
   |                      | #. Set a modified version of nonce *Nonce* on the AEAD_Decryption object  |
   |                      |                                                                           |
   |                      | #. Set a modified version of associated data *AD* on the AEAD_Decryption  |
   |                      |    object                                                                 |
   |                      |                                                                           |
   |                      | #. Check that trying to decrypt a random value before setting a nonce     |
   |                      |    throws an exception                                                    |
   |                      |                                                                           |
   |                      | #. Set a modified version of nonce *Nonce* on the AEAD_Decryption object  |
   |                      |                                                                           |
   |                      | #. Pass a random ciphertext value into the AEAD_Decryption object         |
   |                      |                                                                           |
   |                      | #. Reset the AEAD_Decryption object                                       |
   |                      |                                                                           |
   |                      | #. Set the nonce *Nonce* on the AEAD\_Decryption object                   |
   |                      |                                                                           |
   |                      | #. Set the associated data *AD* on the AEAD_Decryption object             |
   |                      |                                                                           |
   |                      |    #. In case it throws an exception (for some modes that don't allow     |
   |                      |       setting AD after the nonce), reset the AEAD_Decryption object, and  |
   |                      |       set *AD* and *Nonce*                                                |
   |                      |                                                                           |
   |                      | #. Calculate the plaintext of input value *Out* and compare the result    |
   |                      |    with the expected output value *In*                                    |
   |                      |                                                                           |
   |                      | #. If *Out* is longer than the block size of the AEAD mode, calculate the |
   |                      |    plaintext of input value *Out* by decrypting *Out* in block size       |
   |                      |    blocks and comparing the result with the expected output value *In*    |
   |                      |                                                                           |
   |                      | #. If *Out* is longer than the block size of the AEAD mode, calculate the |
   |                      |    plaintext of input value *Out* by decrypting *Out* in multiples of     |
   |                      |    block size blocks and comparing the result with the expected output    |
   |                      |    value *In*                                                             |
   |                      |                                                                           |
   |                      | #. Clear the AEAD_Decryption object                                       |
   |                      |                                                                           |
   |                      | #. Check that trying to decrypt a random value after clearing throws an   |
   |                      |    exception                                                              |
   |                      |                                                                           |
   |                      | #. If the AEAD requires the key to be set prior to setting associated     |
   |                      |    data, check that setting *AD* on the AEAD_Decryption object throws an  |
   |                      |    exception                                                              |
   +----------------------+---------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +----------------------+---------------------------------------------------------------------------+
   | **Test Case No.:**   | AEAD-3                                                                    |
   +----------------------+---------------------------------------------------------------------------+
   | **Type:**            | Negative Test                                                             |
   +----------------------+---------------------------------------------------------------------------+
   | **Description:**     | Make sure AEAD decryption correctly rejects manipulated ciphertexts and   |
   |                      | manipulated nonces                                                        |
   +----------------------+---------------------------------------------------------------------------+
   | **Preconditions:**   | None                                                                      |
   +----------------------+---------------------------------------------------------------------------+
   | **Input Values:**    | -  Block Cipher: The underlying block cipher, e.g., AES-128 or AES-256    |
   |                      |                                                                           |
   |                      | -  Key: The encryption/decryption key used for the block cipher (varying  |
   |                      |    length depending on the block cipher)                                  |
   |                      |                                                                           |
   |                      | -  Nonce: The nonce used to initialize the AEAD mode (varying length)     |
   |                      |                                                                           |
   |                      | -  Out: Ciphertext (varying length depending on the block cipher)         |
   |                      |                                                                           |
   |                      | -  AD: Additional data to be authenticated (varying length, optional)     |
   +----------------------+---------------------------------------------------------------------------+
   | **Expected Output:** | Decryption shall output an error (throw an exception)                     |
   +----------------------+---------------------------------------------------------------------------+
   | **Steps:**           | #. Create a AEAD_Decryption object                                        |
   |                      |                                                                           |
   |                      | #. Set the key *Key* on the AEAD_Decryption object                        |
   |                      |                                                                           |
   |                      | #. Set the associated data *AD* on the AEAD_Decryption object             |
   |                      |                                                                           |
   |                      | #. Set the nonce *Nonce* on the AEAD\_Decryption object                   |
   |                      |                                                                           |
   |                      | #. Create a modified version of *Out*, by changing the length of Out or   |
   |                      |    by flipping random bits in *Out*                                       |
   |                      |                                                                           |
   |                      | #. Calculate the plaintext of the modified *Out*, which should throw an   |
   |                      |    exception                                                              |
   |                      |                                                                           |
   |                      | If *Nonce* is of length n > 0:                                            |
   |                      |                                                                           |
   |                      | 7. Create a modified version of *Nonce* by flipping random bits in        |
   |                      |    *Nonce*                                                                |
   |                      |                                                                           |
   |                      | 8. Set the modified nonce on the AEAD_Decryption object                   |
   |                      |                                                                           |
   |                      | 9. Calculate the plaintext of the original ciphertext *Out*, which should |
   |                      |    throw an exception                                                     |
   |                      |                                                                           |
   |                      | End If                                                                    |
   |                      |                                                                           |
   |                      | 10. Create a modified version of *AD*, by changing the length of *AD* or  |
   |                      |     by flipping random bits in *AD*                                       |
   |                      |                                                                           |
   |                      | 11. Set the modified associated data on the *AEAD*\_Decryption object     |
   |                      |                                                                           |
   |                      | 12. Set the nonce *Nonce* on the AEAD\_ Decryption object                 |
   |                      |                                                                           |
   |                      | 13. Calculate the plaintext of the original ciphertext *Out*, which       |
   |                      |     should throw an exception                                             |
   +----------------------+---------------------------------------------------------------------------+

GCM
---

GCM is tested with the following constraints:

-  Number of test cases: 43
-  Sources: NIST CAVP, generated using OpenSSL, Project Wycheproof

-  Block Cipher: AES-128 and AES-256

-  Key: 128 bits, 192 bits, 256 bits

   -  Extreme values: 128 bits all zero, 192 bits all zero, 256 bits all
      zero

-  Nonce: 64 bits, 96 bits, 128 bits and 480 bits

   -  Extreme values: 128 bits, 480 bits [1]_

-  Out: 64 bits, 128 bits, 608 bits, 640 bits

-  AD: 64 bits, 128 bits, 160 bits, 192 bits, no AD

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/aead/gcm.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +----------------------+---------------------------------------------------------------------------+
   | **Test Case No.:**   | AEAD-GCM-1                                                                |
   +----------------------+---------------------------------------------------------------------------+
   | **Type:**            | Positive Test                                                             |
   +----------------------+---------------------------------------------------------------------------+
   | **Description:**     | Known Answer Test that verifies the correctness of GCM encryption         |
   +----------------------+---------------------------------------------------------------------------+
   | **Preconditions:**   | None                                                                      |
   +----------------------+---------------------------------------------------------------------------+
   | **Input Values:**    | Block Cipher = AES-128                                                    |
   |                      |                                                                           |
   |                      | Key = 0x00000000000000000000000000000000 (128 bits)                       |
   |                      |                                                                           |
   |                      | Nonce = 0x000000000000000000000000 (96 bits)                              |
   |                      |                                                                           |
   |                      | In = Message of length zero                                               |
   |                      |                                                                           |
   |                      | AD = None                                                                 |
   +----------------------+---------------------------------------------------------------------------+
   | **Expected Output:** | Out = 0x58E2FCCEFA7E3061367F1D57A4E7455A (128 bits)                       |
   +----------------------+---------------------------------------------------------------------------+
   | **Steps:**           | See generic description in test case *AEAD-1*                             |
   +----------------------+---------------------------------------------------------------------------+
   | **Notes:**           | Corresponds to NIST Test Case 1                                           |
   +----------------------+---------------------------------------------------------------------------+

.. [1]
   These GCM nonces are not 96 bits and so are hashed with GHASH to
   produce the counter value. For these inputs the CTR value is very
   near 2^32, which exposed a bug in GCM when the counter overflowed
