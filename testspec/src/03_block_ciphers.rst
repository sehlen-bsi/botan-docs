Block Ciphers
=============

Block ciphers are tested using (1) unit tests and known answer tests that (2) encrypt a message and (3) decrypt a message. All the tests are implemented in ``src/tests/test_block.cpp``. The test cases are described in the following.

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | BLOCK-1                                                                  |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Unit Test that checks certain properties of the BlockCipher              |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | -  Name: The block cipher name                                           |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | |                                                                        |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create a block cipher object                                          |
   |                       |                                                                          |
   |                       | #. Test the block cipher name                                            |
   |                       |                                                                          |
   |                       | #. Test that block cipher parallelism equals or is greater than one      |
   |                       |                                                                          |
   |                       | #. Test that block size equals or is greater than eight                  |
   |                       |                                                                          |
   |                       | #. Test that block cipher parallel bytes equals *block size*parallel     |
   |                       |    bytes*                                                                |
   |                       |                                                                          |
   |                       | #. Test that block cipher encryption throws an exception if key is not   |
   |                       |    set                                                                   |
   |                       |                                                                          |
   |                       | #. Test that block cipher decryption throws an exception if key is not   |
   |                       |    set                                                                   |
   +-----------------------+--------------------------------------------------------------------------+


.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | BLOCK-2                                                                  |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Known Answer Test that verifies the correctness of block cipher          |
   |                       | encryption                                                               |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | -  Key: The encryption key used for the block cipher (varying length     |
   |                       |    depending on the block cipher)                                        |
   |                       |                                                                          |
   |                       | -  In: The test message to be encrypted (varying length)                 |
   |                       |                                                                          |
   |                       | -  Iterations: The number of encrypt operations to conduct on the input  |
   |                       |    value *In*                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | -  Out: Ciphertext (varying length depending on the block cipher)        |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create a block cipher object                                          |
   |                       |                                                                          |
   |                       | #. Set a randomly generated key of length *minimum key length* bits      |
   |                       |                                                                          |
   |                       | #. Generate a random plaintext of length *key length* bits and encrypt   |
   |                       |    it                                                                    |
   |                       |                                                                          |
   |                       | #. Reset the block cipher object                                         |
   |                       |                                                                          |
   |                       | #. Set the key *Key* on the block cipher object                          |
   |                       |                                                                          |
   |                       | #. Clone the block cipher object                                         |
   |                       |                                                                          |
   |                       | #. Check that cloned object points to a different memory location        |
   |                       |                                                                          |
   |                       | #. Check that cloned object has the same block cipher name               |
   |                       |                                                                          |
   |                       | #. Set a random key on the cloned object                                 |
   |                       |                                                                          |
   |                       | #. Encrypt *Iterations* times the input value *In* and compare the       |
   |                       |    result with the expected value *Out*                                  |
   |                       |                                                                          |
   |                       | #. Decrypt *Iterations* times the result from the previous step and      |
   |                       |    compare with the input value *In*                                     |
   |                       |                                                                          |
   |                       | #. Perform steps 10-11 with input value In, but prepend a zero byte to   |
   |                       |    simulate a misaligned input buffer                                    |
   +-----------------------+--------------------------------------------------------------------------+


.. table::
   :class: longtable
   :widths: 20 80


   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | BLOCK-3                                                                  |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Known Answer Test that verifies the correctness of block cipher          |
   |                       | decryption                                                               |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | -  Key: The decryption key used for the block cipher (varying length     |
   |                       |    depending on the block cipher)                                        |
   |                       |                                                                          |
   |                       | -  Out: Ciphertext (varying length depending on the block cipher)        |
   |                       |                                                                          |
   |                       | -  Iterations: The number of decrypt operations to conduct on the input  |
   |                       |    value Out                                                             |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | -  In: The original test message (plaintext, varying length)             |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create a block cipher object                                          |
   |                       |                                                                          |
   |                       | #. Set the key *Key* on the block cipher object                          |
   |                       |                                                                          |
   |                       | #. Encrypt *Iterations* times the value *In*                             |
   |                       |                                                                          |
   |                       | #. Decrypt *Iterations* times the result from the previous step and      |
   |                       |    compare with the input value *Out*                                    |
   +-----------------------+--------------------------------------------------------------------------+

AES
---

The AES tests are executed with the AES software implementation and on
systems with SSSE3 support additionally with SSSE3 and on systems with
support for hardware acceleration additionally with AES-NI.

AES-128 is tested with the following constraints:

-  Number of test cases: 1350
-  Source: NIST CAVP AESAVS

-  Key: 128 bits

   -  Extreme values: 128 bits all zero, only one bit set

-  In: 128 bits, 1024 bits

   -  Extreme values: 128 bits all zero, only one bit set, 1024 bits

-  Out: 128 bits, 1024 bits

AES-192 is tested with the following constraints:

-  Key: 192 bits

   -  Extreme values: 192 bits all zero, only one bit set

-  In: 128 bits, 896 bits

   -  Extreme values: 192 bits all zero, only one bit set, 896 bits

-  Out: 128 bits, 896 bits

AES-256 is tested with the following constraints:

-  Key: 256 bits

   -  Extreme values: 256 bits all zero, only one bit set

-  In: 128 bits, 640 bits

   -  Extreme values: 256 bits all zero, only one bit set, 640 bits

-  Out: 128 bits, 640 bits

Note: The BlockCipher interface allows processing multiples of the
cipher's block size (via encrypt_n()/decrypt_n()). In this case,
processing happens blockwise and the result is concatenated.

The following table shows an example test case with one test vector. All
test vectors are listed in *src/tests/data/block/aes.vec*.

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | BLOCK-AES-2                                                              |
   +=======================+==========================================================================+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Known Answer Test that verifies the correctness of AES encryption        |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | Key = 0x000102030405060708090A0B0C0D0E0F (128 bits)                      |
   |                       |                                                                          |
   |                       | In = 0x00112233445566778899AABBCCDDEEFF (128 bits)                       |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | Out = 0x69C4E0D86A7B0430D8CDB78070B4C55A (128 bits)                      |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create an AES object                                                  |
   |                       |                                                                          |
   |                       | #. Set a randomly generated key of length *minimum key length* bits      |
   |                       |                                                                          |
   |                       | #. Generate a random plaintext of length *key length* bits and encrypt   |
   |                       |    it                                                                    |
   |                       |                                                                          |
   |                       | #. Reset the AES object                                                  |
   |                       |                                                                          |
   |                       | #. Set the key *Key* on the AES object                                   |
   |                       |                                                                          |
   |                       | #. Encrypt the input value *In* and compare the result with the expected |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Decrypt the result from the previous step and compare with the input  |
   |                       |    value *In*                                                            |
   +-----------------------+--------------------------------------------------------------------------+
