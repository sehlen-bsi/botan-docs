Key Derivation Functions
========================

Key derivation functions (KDFs) are tested using a known answer test
that derives a key from a set of input values. The test is implemented
in :srcref:`src/tests/test_kdf.cpp`. The test case is described in the
following.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KDF-1                                                                   |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Derives a key from the KDF                                              |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Hash Function: The underlying hash function, e.g., SHA-1 or          |
   |                        |                                                                         |
   |                        | -  MAC: The underlying message authentication code, e.g., HMAC-SHA1     |
   |                        |                                                                         |
   |                        | -  Salt: A salt value (varying length, optional)                        |
   |                        |                                                                         |
   |                        | -  Secret: The secret input used to derive the key (varying length)     |
   |                        |                                                                         |
   |                        | -  Label: A label value (varying length, optional)                      |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | -  Out: The derived key (length depending the desired output length)    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the KDF object                                                |
   |                        |                                                                         |
   |                        | #. *InputSalt* *(optional)*, *Secret*, and *Label* *(optional)* into    |
   |                        |    the KDF and compare the result with the expected output value *Out*  |
   |                        |                                                                         |
   |                        | #. Clone the KDF object and check that it points to a different memory  |
   |                        |    location                                                             |
   +------------------------+-------------------------------------------------------------------------+

KDF1 (ISO 18033-2)
------------------

KDF1 from ISO 18033-2 is tested with the following constraints:

-  Number of test cases: 2
-  Source: ISO 18033-2

-  Hash Function: SHA-1, SHA-256

-  Output Length: 160 bits, 856 bits
-  Secret: 160 bits, 856 bits
-  Out: 160 bits, 856 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/kdf/kdf1_iso18033.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KDF-KDF1-1                                                              |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Derives a key from the KDF                                              |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Hash Function = SHA-256                                                 |
   |                        |                                                                         |
   |                        | Secret = 0xD6E168C5F256A2DCFF7EF12FACD390F393C7A88D (160 bits)          |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Out = 0x0742BA966813AF75536BB6149CC44FC256FD6406 (160 bits)             |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the KDF1_18033 object                                         |
   |                        |                                                                         |
   |                        | #. Input *Secret* into KDF1_18033 and compare the result with the       |
   |                        |    expected output value *Out*                                          |
   +------------------------+-------------------------------------------------------------------------+

NIST SP 800-108 (Counter Mode)
------------------------------

The NIST SP 800-108 KDF in Counter Mode is tested with the following
constraints:

-  Number of test cases: 240
-  Source: Generated with BouncyCastle

-  MAC: HMAC-SHA1, HMAC-SHA256, HMAC-SHA384, HMAC-SHA512, CMAC-AES128,
   CMAC-AES192, CMAC-AES256

-  Output Length: 16 bits - 160 bits
-  Salt: 80 bits - 800 bits
-  Secret: 128 bits - 512 bits
-  Out: 16 bits - 160 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/kdf/sp800_108_ctr.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KDF-NISTSP800-108-CTR-1                                                 |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Derives a key from the NIST SP 800-108 KDF in Counter Mode              |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | MAC = HMAC-SHA1                                                         |
   |                        |                                                                         |
   |                        | Salt = 0x876F7274958C9F920019 (80 bits)                                 |
   |                        |                                                                         |
   |                        | Secret = 0x4C5FFEE342D0F1D9204CE138ED131558CF364BBC (160 bits)          |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Out = 0x5B3A (16 bits)                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the SP800_108_Counter object                                  |
   |                        |                                                                         |
   |                        | #. Input *Salt* and *Secret* into SP800_108_Counter and compare the     |
   |                        |    result with the expected output value *Out*                          |
   +------------------------+-------------------------------------------------------------------------+

NIST SP 800-108 (Feedback Mode)
-------------------------------

The NIST SP 800-108 KDF in Feedback Mode is tested with the following
constraints:

-  Number of test cases: 240
-  Source: Generated with BouncyCastle
-  MAC: HMAC-SHA1, HMAC-SHA256, HMAC-SHA384, HMAC-SHA512, CMAC-AES128,
   CMAC-AES192, CMAC-AES256

-  Output Length: 16 bits - 160 bits
-  Salt: 144 bits - 1104 bits
-  Secret: 128 bits - 512 bits
-  Out: 16 bits - 160 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/kdf/sp800_108_fb.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KDF-NISTSP800-108-FB-1                                                  |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Derives a key from the NIST SP 800-108 KDF in Feedback Mode             |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | MAC = HMAC-SHA1                                                         |
   |                        |                                                                         |
   |                        | Salt = 0x0976FDEC7817D94D60C4E0C9091D82E38BCFC58D7FFF0829A13D1B4455B8   |
   |                        | (240 bits)                                                              |
   |                        |                                                                         |
   |                        | Secret = 0xE6EA4E4F7178A81230A01DA05705B9C8B902121B (160 bits)          |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Out = 0x1092 (16 bits)                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the SP800_108_Feedback object                                 |
   |                        |                                                                         |
   |                        | #. Input *Salt* and *Secret* into SP800_108_Feedback and compare the    |
   |                        |    result with the expected output value *Out*                          |
   +------------------------+-------------------------------------------------------------------------+

NIST SP 800-108 (Pipeline Mode)
-------------------------------

The NIST SP 800-108 KDF in Pipeline Mode is tested with the following
constraints:

-  Number of test cases: 240
-  Source: Generated with BouncyCastle
-  MAC: HMAC-SHA1, HMAC-SHA256, HMAC-SHA384, HMAC-SHA512, CMAC-AES128,
   CMAC-AES192, CMAC-AES256

-  Output Length: 16 bits - 160 bits
-  Salt: 80 bits - 800 bits
-  Secret: 128 bits - 512 bits
-  Out: 16 bits - 160 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/kdf/sp800_108_pipe.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KDF-NISTSP800-108-PI-1                                                  |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Derives a key from the NIST SP 800-108 KDF in Pipeline Mode             |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | MAC = HMAC-SHA1                                                         |
   |                        |                                                                         |
   |                        | Salt = 0xB65A30885B0849C7099B (80 bits)                                 |
   |                        |                                                                         |
   |                        | Secret = 0x63CB90F9CD34B95007277AE6FC17FB45A9248725 (160 bits)          |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Out = 0x4B0D (16 bits)                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the SP800_108_Pipeline object                                 |
   |                        |                                                                         |
   |                        | #. Input *Salt* and *Secret* into SP800_108_Pipeline and compare the    |
   |                        |    result with the expected output value *Out*                          |
   +------------------------+-------------------------------------------------------------------------+

SP 800-56C
----------

The NIST SP 800-56C KDF is tested with the following constraints:

-  Number of test cases: 40
-  Source: Generated with PyCryptodome
-  MAC: HMAC-SHA1, HMAC-SHA256, HMAC-SHA384, HMAC-SHA512

-  Output Length: 16 bits – 400 bits
-  Salt: 80 bits – 800 bits
-  Secret: 160 bits – 512 bits
-  Label: 96 bits
-  Out: 16 bits – 400 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/kdf/sp800_56c.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KDF-NISTSP800-56C-1                                                     |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Derives a key from the NIST SP 800-56C KDF                              |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | MAC = HMAC-SHA1                                                         |
   |                        |                                                                         |
   |                        | Salt = 0x97ca00eac481e8b3556a (80 bits)                                 |
   |                        |                                                                         |
   |                        | Label = 0xae8cf2e46773a68098ea53b3 (96 bits)                            |
   |                        |                                                                         |
   |                        | Secret = 0x52f4676023946c7307b5e8148d97f312623a6e88 (160 bits)          |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Out = 0x1bcd (16 bits)                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the SP800_56C object                                          |
   |                        |                                                                         |
   |                        | #. Input *Salt*, *Secret* and *Label* into SP800_56C and compare the    |
   |                        |    result with the expected output value *Out*                          |
   +------------------------+-------------------------------------------------------------------------+

TLS 1.0/1.1 PRF
---------------

The PRF used in TLS 1.0/1.1 is tested with the following constraints:

-  Number of test cases: 30

-  MAC: HMAC-MD5, HMAC-SHA1

-  Output Length: 8 bits - 256 bits
-  Salt: 120 bits - 248 bits
-  Secret: 152 bits, 160 bits
-  Out: 8 bits - 256 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/kdf/tls_prf.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KDF-TLS1-PRF-1                                                          |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Derives a key from the PRF used in TLS 1.0/1.1                          |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | MAC = HMAC-MD5, HMAC-SHA1                                               |
   |                        |                                                                         |
   |                        | Salt = 0xA6D455CB1B2929E43D63CCE55CE89D66F252549729C19C1511 (208 bits)  |
   |                        |                                                                         |
   |                        | Secret = 0x6C81AF87ABD86BE83C37CE981F6BFE11BD53A8 (152 bits)            |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Out = 0xA8 (8 bits)                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the TLS_PRF object                                            |
   |                        |                                                                         |
   |                        | #. Input *Salt* and *Secret* into the TLS_PRF and compare the result    |
   |                        |    with the expected output value *Out*                                 |
   +------------------------+-------------------------------------------------------------------------+

TLS 1.2 PRF
-----------

The PRF used in TLS 1.2 is tested with the following constraints:

-  Number of test cases: 4
-  Source:
   https://www.ietf.org/mail-archive/web/tls/current/msg03416.html

-  Hash Function: SHA-224, SHA-256, SHA-384, SHA-512

-  Output Length: 704 bits - 1568 bits
-  Salt: 128 bits
-  Secret: 128 bits
-  Label: 80 bits
-  Out: 704 bits - 1568 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/kdf/tls_prf.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KDF-TLS12-PRF-1                                                         |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Derives a key from the PRF used in TLS 1.2                              |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | MAC = SHA-224                                                           |
   |                        |                                                                         |
   |                        | Salt = 0xf5a3fe6d34e2e28560fdcaf6823f9091 (128 bits)                    |
   |                        |                                                                         |
   |                        | Secret = 0xe18828740352b530d69b34c6597dea2e (128 bits)                  |
   |                        |                                                                         |
   |                        | Label = 0x74657374206c6162656c (80 bits)                                |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    Out = 0x224d8af3c0453393a9779789d21cf7da5ee62ae6b617873d489428efc8dd |
   |                        |    58d1566e7029e2ca3a5ecd355dc64d4d927e2fbd78c4233e8604b14749a77a92a70f |
   |                        |    ddf614bc0df623d798604e4ca5512794d802a258e82f86cf (704 bits)          |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the TLS_12_PRF object                                         |
   |                        |                                                                         |
   |                        | #. Input *Salt,* *Label* and *Secret* into the TLS_12_PRF and compare   |
   |                        |    the result with the expected output value *Out*                      |
   +------------------------+-------------------------------------------------------------------------+
