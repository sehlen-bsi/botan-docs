Password-based Key Derivation Functions
=======================================

Password-based Key derivation functions (PBKDFs) are tested using a
known answer test that derives a key from a set of input values. The
test is implemented in :srcref:`src/tests/test_pbkdf.cpp`. The test case is
described in the following.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PBKDF-1                                                                 |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Derives a key from the PBKDF                                            |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Hash Function: The underlying hash function, e.g., SHA-1 or          |
   |                        |                                                                         |
   |                        | -  MAC: The underlying message authentication code, e.g., HMAC-SHA1     |
   |                        |                                                                         |
   |                        | -  Output Length: The desired output length in bytes (varying length)   |
   |                        |                                                                         |
   |                        | -  Iterations: The number of iterations                                 |
   |                        |                                                                         |
   |                        | -  Salt: A salt value (varying length)                                  |
   |                        |                                                                         |
   |                        | -  Passphrase: The passphrase used to derive the key (varying length)   |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | -  Out: The derived key (length depending the desired output length)    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the PBKDF object                                              |
   |                        |                                                                         |
   |                        | #. Input *Output Length*, *Iterations*, *Salt* and *Passphrase* into    |
   |                        |    the PBKDF and compare the result with the expected output value      |
   |                        |    *Out*                                                                |
   +------------------------+-------------------------------------------------------------------------+

PBKDF2
------

PBKDF2 from PKCS#5 is tested with the following constraints:

-  Number of test cases: 13
-  MAC: HMAC-SHA1, HMAC-SHA256, HMAC-SHA384, HMAC-SHA512
-  Salt: 64 bits, 160 bits, 240 bits

-  Output Length: 80 bits - 512 bits

-  Iterations: 1 - 10000

-  Passphrase: 3 - 20 characters

   -  Extreme values: Empty passphrase

-  Out: 80 bits - 512 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/pbkdf/pbkdf2.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | PBKDF-PBKDF2-1                                                          |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Derives a key from the PBKDF2                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | MAC = HMAC-SHA1                                                         |
   |                        |                                                                         |
   |                        | Output Length = 256 bits                                                |
   |                        |                                                                         |
   |                        | Iterations = 10000                                                      |
   |                        |                                                                         |
   |                        | Salt = 0x0001020304050607 (64 bits)                                     |
   |                        |                                                                         |
   |                        | Passphrase = Empty passphrase                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Out =                                                                   |
   |                        | 0x59B2B1143B4CB1059EC58D9722FB1C72471E0D85C6F7543BA5228526375B0127 (256 |
   |                        | bits)                                                                   |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the PBKDF2 object                                             |
   |                        |                                                                         |
   |                        | #. Input *Output Length*, *Iterations*, *Salt* and *Passphrase* into    |
   |                        |    the PBKDF2 and compare the result with the expected output value     |
   |                        |    *Out*                                                                |
   +------------------------+-------------------------------------------------------------------------+
