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
   |                      | #. Check that setting the associated data *AD* now throws an exception    |
   |                      |    (setting associated data after the nonce is not allowed)               |
   |                      |                                                                           |
   |                      | #. Check that setting the nonce *Nonce* a second time, without finishing  |
   |                      |    or resetting the message, throws an exception                          |
   |                      |                                                                           |
   |                      | #. Reset the AEAD_Encryption object, set the associated data *AD* and     |
   |                      |    set the nonce *Nonce*                                                  |
   |                      |                                                                           |
   |                      | #. Calculate the ciphertext of input value *In* and compare the result    |
   |                      |    with the expected output value *Out*                                   |
   |                      |                                                                           |
   |                      | #. If *In* is the empty message, skip the following four steps            |
   |                      |                                                                           |
   |                      | #. If *AD* is not empty, set the nonce *Nonce* again and encrypt *In*     |
   |                      |    without setting the associated data anew; compare the result with the  |
   |                      |    expected output value *Out* (the associated data persists between      |
   |                      |    messages)                                                              |
   |                      |                                                                           |
   |                      | #. If *AD* is not empty, reset the AEAD_Encryption object, set the nonce  |
   |                      |    *Nonce* and encrypt *In* again; compare the result with the expected   |
   |                      |    output value *Out* (the associated data persists across a reset)       |
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
   |                      | #. Set the nonce *Nonce*, reset the AEAD_Encryption object and check      |
   |                      |    that finalizing the encryption now throws an exception and leaves the  |
   |                      |    passed data buffer unmodified                                          |
   |                      |                                                                           |
   |                      | #. Check that setting associated data at an index equal to the number of  |
   |                      |    associated data inputs supported by the mode throws an exception       |
   |                      |                                                                           |
   |                      | #. Set the associated data *AD* and the nonce *Nonce* and check that      |
   |                      |    finalizing the encryption with a start offset past the end of the      |
   |                      |    passed data buffer throws an exception                                 |
   |                      |                                                                           |
   |                      | #. Clear the AEAD_Encryption object                                       |
   |                      |                                                                           |
   |                      | #. Check that trying to encrypt a random value after clearing throws an   |
   |                      |    exception                                                              |
   |                      |                                                                           |
   |                      | #. If the AEAD requires the key to be set prior to setting associated     |
   |                      |    data, check that setting *AD* on the AEAD_Encryption object throws an  |
   |                      |    exception                                                              |
   |                      |                                                                           |
   |                      | #. If the AEAD mode does not require the key to be set prior to setting   |
   |                      |    associated data: set the associated data *AD* on the cleared object,   |
   |                      |    set the key *Key*, set the nonce *Nonce* and encrypt *In*; compare     |
   |                      |    the result with the expected output value *Out* (associated data set   |
   |                      |    before the key is retained)                                            |
   |                      |                                                                           |
   |                      | #. If the AEAD mode requires the key to be set prior to setting           |
   |                      |    associated data: on a fresh AEAD_Encryption object set a different     |
   |                      |    key and different associated data and set the nonce *Nonce*; then set  |
   |                      |    the key *Key* and the associated data *AD*, set the nonce *Nonce*      |
   |                      |    again and encrypt *In*; compare the result with the expected output    |
   |                      |    value *Out* (re-keying drops all key-dependent state)                  |
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
   |                      | #. Check that trying to decrypt a random value before setting a key       |
   |                      |    throws an exception                                                    |
   |                      |                                                                           |
   |                      | #. If the AEAD mode requires the key to be set prior to setting           |
   |                      |    associated data, check that setting *AD* on the AEAD_Decryption object |
   |                      |    throws an exception                                                    |
   |                      |                                                                           |
   |                      | #. Set the key *Key* on the AEAD_Decryption object                        |
   |                      |                                                                           |
   |                      | #. Set a modified version of associated data *AD* on the AEAD_Decryption  |
   |                      |    object                                                                 |
   |                      |                                                                           |
   |                      | #. Check that trying to decrypt a random value before setting a nonce     |
   |                      |    throws an exception                                                    |
   |                      |                                                                           |
   |                      | #. Check that trying to finalize the decryption of a random value before  |
   |                      |    setting a nonce throws an exception                                    |
   |                      |                                                                           |
   |                      | #. Set a modified version of nonce *Nonce* on the AEAD_Decryption object  |
   |                      |                                                                           |
   |                      | #. Pass a random ciphertext value into the AEAD_Decryption object         |
   |                      |                                                                           |
   |                      | #. Reset the AEAD_Decryption object                                       |
   |                      |                                                                           |
   |                      | #. Set the nonce *Nonce* on the AEAD\_Decryption object                   |
   |                      |                                                                           |
   |                      | #. Check that setting the associated data *AD* now throws an exception    |
   |                      |    (setting associated data after the nonce is not allowed)               |
   |                      |                                                                           |
   |                      | #. Check that setting the nonce *Nonce* a second time, without finishing  |
   |                      |    or resetting the message, throws an exception                          |
   |                      |                                                                           |
   |                      | #. Reset the AEAD_Decryption object, set the associated data *AD* and     |
   |                      |    set the nonce *Nonce*                                                  |
   |                      |                                                                           |
   |                      | #. Calculate the plaintext of input value *Out* and compare the result    |
   |                      |    with the expected output value *In*                                    |
   |                      |                                                                           |
   |                      | #. If *AD* is not empty, set the nonce *Nonce* again and decrypt *Out*    |
   |                      |    without setting the associated data anew; compare the result with the  |
   |                      |    expected output value *In* (the associated data persists between       |
   |                      |    messages)                                                              |
   |                      |                                                                           |
   |                      | #. If *AD* is not empty, reset the AEAD_Decryption object, set the nonce  |
   |                      |    *Nonce* and decrypt *Out* again; compare the result with the expected  |
   |                      |    output value *In* (the associated data persists across a reset)        |
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
   |                      | #. Reset the AEAD_Decryption object, set the associated data *AD* and     |
   |                      |    the nonce *Nonce*, then reset the object again and check that          |
   |                      |    finalizing the decryption now throws an exception and leaves the       |
   |                      |    passed data buffer unmodified                                          |
   |                      |                                                                           |
   |                      | #. Check that setting associated data at an index equal to the number of  |
   |                      |    associated data inputs supported by the mode throws an exception       |
   |                      |                                                                           |
   |                      | #. Set the associated data *AD* and the nonce *Nonce* and check that      |
   |                      |    finalizing the decryption with a start offset past the end of the      |
   |                      |    passed data buffer throws an exception                                 |
   |                      |                                                                           |
   |                      | #. Clear the AEAD_Decryption object                                       |
   |                      |                                                                           |
   |                      | #. Check that trying to decrypt a random value after clearing throws an   |
   |                      |    exception                                                              |
   |                      |                                                                           |
   |                      | #. If the AEAD requires the key to be set prior to setting associated     |
   |                      |    data, check that setting *AD* on the AEAD_Decryption object throws an  |
   |                      |    exception                                                              |
   |                      |                                                                           |
   |                      | #. If the AEAD mode does not require the key to be set prior to setting   |
   |                      |    associated data: set the associated data *AD* on the cleared object,   |
   |                      |    set the key *Key*, set the nonce *Nonce* and decrypt *Out*; compare    |
   |                      |    the result with the expected output value *In* (associated data set    |
   |                      |    before the key is retained)                                            |
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
   | **Expected Output:** | Decryption shall output an error (throw an exception); the                |
   |                      | unauthenticated plaintext in the output buffer shall be zeroized          |
   |                      | before the exception is thrown                                            |
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
   |                      | #. Check that the plaintext in the output buffer was zeroized before the  |
   |                      |    exception was thrown                                                   |
   |                      |                                                                           |
   |                      | If *Nonce* is of length n > 0:                                            |
   |                      |                                                                           |
   |                      | 8. Create a modified version of *Nonce* by flipping random bits in        |
   |                      |    *Nonce*                                                                |
   |                      |                                                                           |
   |                      | 9. Set the modified nonce on the AEAD_Decryption object                   |
   |                      |                                                                           |
   |                      | 10. Calculate the plaintext of the original ciphertext *Out*, which       |
   |                      |     should throw an exception                                             |
   |                      |                                                                           |
   |                      | 11. Check that the plaintext in the output buffer was zeroized before     |
   |                      |     the exception was thrown                                              |
   |                      |                                                                           |
   |                      | End If                                                                    |
   |                      |                                                                           |
   |                      | 12. Create a modified version of *AD*, by changing the length of *AD* or  |
   |                      |     by flipping random bits in *AD*                                       |
   |                      |                                                                           |
   |                      | 13. Set the modified associated data on the *AEAD*\_Decryption object     |
   |                      |                                                                           |
   |                      | 14. Set the nonce *Nonce* on the AEAD\_ Decryption object                 |
   |                      |                                                                           |
   |                      | 15. Calculate the plaintext of the original ciphertext *Out*, which       |
   |                      |     should throw an exception                                             |
   |                      |                                                                           |
   |                      | 16. Check that the plaintext in the output buffer was zeroized before     |
   |                      |     the exception was thrown                                              |
   +----------------------+---------------------------------------------------------------------------+

GCM
---

GCM is tested with the following constraints:

-  Number of test cases: 55
-  Sources: NIST CAVP, generated using OpenSSL, Project Wycheproof

-  Block Cipher: AES-128, AES-192, AES-256, ARIA-128, ARIA-192,
   ARIA-256, SM4

-  Key: 128 bits, 192 bits, 256 bits

   -  Extreme values: 128 bits all zero, 192 bits all zero, 256 bits all
      zero

-  Nonce: 64 bits, 96 bits, 128 bits and 480 bits

   -  Extreme values: 128 bits, 480 bits [1]_

-  Out: 128 bits - 8320 bits, including known answer tests with long
   messages

-  AD: 64 bits - 256 bits, no AD

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
