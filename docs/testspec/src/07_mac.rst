Message Authentication Codes
============================

Message authentication codes (MACs) are tested using a (1) combined unit
and known answer test that calculates the MAC tag on a message as a
whole and (2) a known answer test that calculates the MAC tag on a
message in separate chunks. All the tests are implemented in
:srcref:`src/tests/test_mac.cpp`. The test cases are described in the
following.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | MAC-1                                                                   |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Combined unit and known answer test that checks that reset works        |
   |                        | correctly and calculates the MAC tag on a test message as a whole. It   |
   |                        | also ensures that the same MAC object can be reused for multiple        |
   |                        | calculations.                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Block Cipher: The underlying block cipher, e.g., AES-128 or AES-256  |
   |                        |    or                                                                   |
   |                        |                                                                         |
   |                        | -  Hash Function: The underlying hash function, e.g., SHA-1             |
   |                        |                                                                         |
   |                        | -  Key: The encryption/decryption key used for the block cipher         |
   |                        |    (varying length depending on the block cipher)                       |
   |                        |                                                                         |
   |                        | -  In: The test message (varying length)                                |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | -  Out: The MAC tag (varying length depending on the block cipher)      |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the MAC object                                                |
   |                        |                                                                         |
   |                        | #. Test the name of the MAC                                             |
   |                        |                                                                         |
   |                        | #. Test MAC computation fails if key is not set                         |
   |                        |                                                                         |
   |                        | #. Repeat twice:                                                        |
   |                        |                                                                         |
   |                        |    #. Set the key *Key*                                                 |
   |                        |                                                                         |
   |                        |    #. Input *In* into the MAC, calculate the tag and compare it with    |
   |                        |       the expected output value *Out*                                   |
   |                        |                                                                         |
   |                        | #. For MACs that do not require a fresh key for every message\ *        |
   |                        |    (cf.* *fresh_key_required_per_message())*                            |
   |                        |                                                                         |
   |                        |    #. Repeat three times                                                |
   |                        |                                                                         |
   |                        |       #. **Do not** set the key *Key*                                   |
   |                        |                                                                         |
   |                        |       #. Input *In* into the MAC, calculate the tag and compare it with |
   |                        |          the expected output value *Out*                                |
   |                        |                                                                         |
   |                        | #. Set the key *Key*                                                    |
   |                        |                                                                         |
   |                        | #. Input the string “some discarded input” into the MAC                 |
   |                        |                                                                         |
   |                        | #. Reset the MAC                                                        |
   |                        |                                                                         |
   |                        | #. Set the key *Key*                                                    |
   |                        |                                                                         |
   |                        | #. Input *In* into the MAC                                              |
   |                        |                                                                         |
   |                        | #. Clone the MAC object and check that the cloned object points to a    |
   |                        |    different memory location                                            |
   |                        |                                                                         |
   |                        | #. Check that the cloned and the original MAC object return the same    |
   |                        |    MAC name                                                             |
   |                        |                                                                         |
   |                        | #. Set the key *Key* on the cloned object                               |
   |                        |                                                                         |
   |                        | #. Input 32 random bytes as the message into the cloned object          |
   |                        |                                                                         |
   |                        | #. Verify the tag on the original MAC object with the expected output   |
   |                        |    value *Out*                                                          |
   |                        |                                                                         |
   |                        | #. Reset the MAC                                                        |
   |                        |                                                                         |
   |                        | #. Test MAC computation after reset fails if key is not set             |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | MAC-2                                                                   |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Calculates the MAC tag on a test message in chunks                      |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | *In* is of length n > 1 byte                                            |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Block Cipher: The underlying block cipher, e.g., AES-128 or AES-256  |
   |                        |    or                                                                   |
   |                        |                                                                         |
   |                        | -  Hash Function: The underlying hash function, e.g., SHA-1             |
   |                        |                                                                         |
   |                        | -  Key: The encryption/decryption key used for the block cipher         |
   |                        |    (varying length depending on the block cipher)                       |
   |                        |                                                                         |
   |                        | -  In: The test message (varying length)                                |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | -  Out: The MAC tag (varying length depending on the block cipher)      |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the MAC object                                                |
   |                        |                                                                         |
   |                        | #. Set the key *Key*                                                    |
   |                        |                                                                         |
   |                        | #. Feed the first byte of the input value *In* into the MAC             |
   |                        |                                                                         |
   |                        | #. Feed the bytes 2..n-1 of the input value *In* into the MAC           |
   |                        |                                                                         |
   |                        | #. Feed the last byte of the input value *In* into the MAC              |
   |                        |                                                                         |
   |                        | #. Calculate the tag and compare with the expected output value *Out*   |
   |                        |                                                                         |
   |                        | #. Set the key *Key*                                                    |
   |                        |                                                                         |
   |                        | #. Feed the first byte of the input value *In* into the MAC             |
   |                        |                                                                         |
   |                        | #. Feed the bytes 2..n-1 of the input value *In* into the MAC           |
   |                        |                                                                         |
   |                        | #. Feed the last byte of the input value *In* into the MAC              |
   |                        |                                                                         |
   |                        | #. Input *In* into the MAC and verify the tag with the expected output  |
   |                        |    value *Out*                                                          |
   +------------------------+-------------------------------------------------------------------------+

CMAC
----

CMAC is tested with the following constraints:

-  Number of test cases: 36

-  Block Cipher: AES-128, AES-192, AES-256
-  Key: 128 bits, 192 bits and 256 bits

-  In: varying length

   -  Range: 8 bits - 960 bits
   -  Extreme values: empty message, 960 bits

-  Out: varying length

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/mac/cmac.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | MAC-CMAC-1                                                              |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Combined unit and known answer test that checks that reset works        |
   |                        | correctly and calculates the CMAC tag on a test message as a whole      |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Block Cipher = AES-128                                                  |
   |                        |                                                                         |
   |                        | Key = 0x2B7E151628AED2A6ABF7158809CF4F3C (128 bits)                     |
   |                        |                                                                         |
   |                        | In = Input value of length zero                                         |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Out = 0xBB1D6929E95937287FA37D129B756746 (128 bits)                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the CMAC object                                               |
   |                        |                                                                         |
   |                        | #. Test the name of the CMAC                                            |
   |                        |                                                                         |
   |                        | #. Set the key *Key*                                                    |
   |                        |                                                                         |
   |                        | #. Input *In* into the CMAC, calculate the tag and compare it with the  |
   |                        |    expected output value *Out*                                          |
   |                        |                                                                         |
   |                        | #. Set the key *Key*                                                    |
   |                        |                                                                         |
   |                        | #. Input the string “some discarded input” into the CMAC                |
   |                        |                                                                         |
   |                        | #. Reset the CMAC                                                       |
   |                        |                                                                         |
   |                        | #. Set the key *Key*                                                    |
   |                        |                                                                         |
   |                        | #. Input *In* into the CMAC and verify the tag with the expected output |
   |                        |    value *Out*                                                          |
   +------------------------+-------------------------------------------------------------------------+

HMAC
----

HMAC is tested with the following constraints:

-  Number of test cases: 15

-  Hash Function: MD5, SHA-1, SHA-256
-  Key: 128 bits, 160 bits, 256 bits

-  In: varying length

   -  Range: 24 bits – 896 bits
   -  Extreme values: 896 bits

-  Out: varying length

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/mac/hmac.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | MAC-HMAC-1                                                              |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Combined unit and known answer test that checks that reset works        |
   |                        | correctly and calculates the HMAC tag on a test message as a whole      |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Hash Function = MD5                                                     |
   |                        |                                                                         |
   |                        | Key = 0x0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B (128 bits)                     |
   |                        |                                                                         |
   |                        | In = 0x4869205468657265 (64 bits)                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Out = 0x9294727A3638BB1C13F48EF8158BFC9D (128 bits)                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the HMAC object                                               |
   |                        |                                                                         |
   |                        | #. Test the name of the HMAC                                            |
   |                        |                                                                         |
   |                        | #. Set the key *Key*                                                    |
   |                        |                                                                         |
   |                        | #. Input *In* into the HMAC, calculate the tag and compare it with the  |
   |                        |    expected output value *Out*                                          |
   |                        |                                                                         |
   |                        | #. Set the key *Key*                                                    |
   |                        |                                                                         |
   |                        | #. Input the string “some discarded input” into the HMAC                |
   |                        |                                                                         |
   |                        | #. Reset the HMAC                                                       |
   |                        |                                                                         |
   |                        | #. Set the key *Key*                                                    |
   |                        |                                                                         |
   |                        | #. Input *In* into the HMAC and verify the tag with the expected output |
   |                        |    value *Out*                                                          |
   +------------------------+-------------------------------------------------------------------------+

GMAC
----

GMAC is tested with the following constraints:

-  Number of test cases: 15
-  Source: Generated with BouncyCastle

-  Cipher: AES-128, AES-192, AES-256
-  Key: 128 bits, 192 bits, 256 bits

-  In: varying length

   -  Range: 0 bits – 400 bits

-  IV: different 96 bit values, one 32 bit value

-  Out: varying length

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/mac/gmac.vec`.

The test vectors were generated with Bouncy Castle Crypto 1.54.

.. table::
   :class: longtable
   :widths: 20 80

   +----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**   | MAC-GMAC-1                                                               |
   +======================+==========================================================================+
   | **Type:**            | Positive Test                                                            |
   +----------------------+--------------------------------------------------------------------------+
   | **Description:**     | Combined unit and known answer test that checks that reset works         |
   |                      | correctly and calculates the GMAC tag on a test message                  |
   +----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**   | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Input Values:**    | Cipher = AES-128                                                         |
   |                      |                                                                          |
   |                      | IV = 0xFFFFFFFFFFFFFFFFFFFFFFFF (96 bits)                                |
   |                      |                                                                          |
   |                      | Key = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF (128 bits)                      |
   |                      |                                                                          |
   |                      | In = 0x00000000000000000000000000000000 (128 bits)                       |
   +----------------------+--------------------------------------------------------------------------+
   | **Expected Output:** | Out = 0xB19E0699327D423B057C95D258AC3129 (128 bits)                      |
   +----------------------+--------------------------------------------------------------------------+
   | **Steps:**           | #. Create the GMAC object                                                |
   |                      |                                                                          |
   |                      | #. Test the name of the GMAC                                             |
   |                      |                                                                          |
   |                      | #. Set the key *Key*                                                     |
   |                      |                                                                          |
   |                      | #. Set the initialization vector *IV*                                    |
   |                      |                                                                          |
   |                      | #. Input *In* into the GMAC, calculate the tag and compare it with the   |
   |                      |    expected output value *Out*                                           |
   |                      |                                                                          |
   |                      | #. Reset the GMAC                                                        |
   |                      |                                                                          |
   |                      | #. Set the key *Key*                                                     |
   |                      |                                                                          |
   |                      | #. Set the initialization vector *IV*                                    |
   |                      |                                                                          |
   |                      | #. Split the input string *IN* into three arrays and invoke three update |
   |                      |    functions on the GMAC with these arrays. Calculate the tag and        |
   |                      |    compare it with the expected output value *Out*                       |
   +----------------------+--------------------------------------------------------------------------+
