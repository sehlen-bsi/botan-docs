Hash Functions
==============

Hash Function Tests
-------------------

Hash functions are tested using a (1) combined unit and known answer
test that hashes a message as a whole and (2) a known answer test that
hashes a message in separate chunks. All the tests are implemented in
:srcref:`src/tests/test_hash.cpp`. The test cases are described in the
following.

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | HASH-1                                                                   |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Combined unit and known answer test that checks that reset works         |
   |                       | correctly and hashes a test message as a whole                           |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | -  In: The test message to be hashed (varying length)                    |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | -  Out: Message digest (varying length depending on the hash function)   |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create a HashFunction object                                          |
   |                       |                                                                          |
   |                       | #. Test the hash function's name                                         |
   |                       |                                                                          |
   |                       | #. Repeat five times in a loop:                                          |
   |                       |                                                                          |
   |                       |    #. Feed the input value *In* into the hash function                   |
   |                       |                                                                          |
   |                       |    #. Calculate the message digest and compare with the expected output  |
   |                       |       value *Out*                                                        |
   |                       |                                                                          |
   |                       | #. Feed the string value *“some discarded input”* into the hash function |
   |                       |                                                                          |
   |                       | #. Reset the hash function                                               |
   |                       |                                                                          |
   |                       | #. Feed an input value of length zero into the hash function             |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the hash function                      |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed one byte from *In* into the hash function                        |
   |                       |                                                                          |
   |                       | #. Copy HashFunction object and its state                                |
   |                       |                                                                          |
   |                       | #. Feed rest of *In* into both the original and the copied hash          |
   |                       |    functions                                                             |
   |                       |                                                                          |
   |                       | #. Verify that both hash functions return same result                    |
   +-----------------------+--------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | HASH-2                                                                   |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Known Answer Test that hashes a message in two chunks                    |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | *In* must be of length n > 1 byte                                        |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | -  In: The test message to be hashed (varying length)                    |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | -  Out: Message digest (varying length depending on the hash function)   |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Feed the first byte of the input value *In* into the hash function    |
   |                       |                                                                          |
   |                       | #. Feed the bytes 2..n of the input value *In* into the hash function    |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   +-----------------------+--------------------------------------------------------------------------+

Additionally, some hash functions are tested using NIST’s Monte Carlo
Test.

-  Number of test cases: 7
-  Hash Functions: SHA-1, SHA-224, SHA-256, SHA-384, SHA-512-224,
   SHA-512-256, SHA-512
-  Source: NIST CAVS 11.1

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | HASH-3                                                                   |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | NIST Monte Carlo Test                                                    |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | -  Seed: A random seed (varying length)                                  |
   |                       |                                                                          |
   |                       | -  Count: Number of iterations                                           |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | -  Out: Message digest (varying length depending on the hash function)   |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Add the seed *Seed* three times into a new vector of buffers *In*     |
   |                       |                                                                          |
   |                       | #. From j = *0* to *Count* do                                            |
   |                       |                                                                          |
   |                       |    #. From i = *3* to *1002* do                                          |
   |                       |                                                                          |
   |                       |       #. Feed *In[0]* into the hash function                             |
   |                       |                                                                          |
   |                       |       #. Feed *In[1]* into the hash function                             |
   |                       |                                                                          |
   |                       |       #. Feed *In[2]* into the hash function                             |
   |                       |                                                                          |
   |                       |       #. Feed *In[0]* into the hash function and calculate the message   |
   |                       |          digest                                                          |
   |                       |                                                                          |
   |                       |       #. Swap the first and second buffer in *In*                        |
   |                       |                                                                          |
   |                       |       #. Swap the second and third buffer in *In*                        |
   |                       |                                                                          |
   |                       |    #. If j < *Count* do                                                  |
   |                       |                                                                          |
   |                       |       #. *In[0]* = *In[2]*                                               |
   |                       |                                                                          |
   |                       |       #. *In[1]* = *In[2]*                                               |
   |                       |                                                                          |
   |                       | #. Check that *In[2]* equals *Output*                                    |
   +-----------------------+--------------------------------------------------------------------------+

Some hash functions are also tested with very long inputs.

-  Number of test cases: 18
-  Hash Functions: SHA-1, SHA-224, SHA-256, SHA-384, SHA-512,
   SHA-3(224), SHA-3(256), SHA-3(384), SHA-3(512)
-  Source: https://www.di-mgt.com.au/sha_testvectors.html

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | HASH-4                                                                   |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Test very long inputs                                                    |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | -  In: The test message to be hashed (varying length)                    |
   |                       |                                                                          |
   |                       | -  TotalLength: The number of times *In* should be processed by the hash |
   |                       |    function                                                              |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | -  Out: Message digest (varying length depending on the hash function)   |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Feed *In* *TotalLength* times into the hash function                  |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and check that the digest matches *Out*  |
   +-----------------------+--------------------------------------------------------------------------+

MD-5
~~~~

MD-5 is tested with the following constraints:

-  Number of test cases: 76

-  In: varying length

   -  Range: 1 byte - 67 bytes
   -  Extreme values: empty message, 1029 bytes

-  Out: 128 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/hash/md5.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | HASH-MD5-1                                                               |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Combined unit and known answer test that checks that reset works         |
   |                       | correctly and hashes a test message as a whole                           |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | In = Input value of length zero                                          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | Out = 0xD41D8CD98F00B204E9800998ECF8427E                                 |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create an MD5 object                                                  |
   |                       |                                                                          |
   |                       | #. Test MD5's name                                                       |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the MD5                                |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed the string value *“some discarded input”* into the MD5           |
   |                       |                                                                          |
   |                       | #. Reset the MD5                                                         |
   |                       |                                                                          |
   |                       | #. Feed an input value of length zero into the MD5                       |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the MD5                                |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed one byte from *In* into the hash function                        |
   |                       |                                                                          |
   |                       | #. Copy HashFunction object and its state                                |
   |                       |                                                                          |
   |                       | #. Feed rest of *In* into both the original and the copied hash          |
   |                       |    functions.                                                            |
   |                       |                                                                          |
   |                       | #. Verify that both hash functions return same result                    |
   +-----------------------+--------------------------------------------------------------------------+

SHA-1
~~~~~

SHA-1 is tested with the following constraints:

-  Number of test cases: 76

-  In: varying length

   -  Range: 8 bits - 536 bits
   -  Extreme values: empty message, 8232 bits

-  Out: 160 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/hash/sha1.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | HASH-SHA1-1                                                              |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Combined unit and known answer test that checks that reset works         |
   |                       | correctly and hashes a test message as a whole                           |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | In = Input value of length zero                                          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | Out = 0xDA39A3EE5E6B4B0D3255BFEF95601890AFD80709 (160 bits)              |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create a SHA1 object                                                  |
   |                       |                                                                          |
   |                       | #. Test SHA1's name                                                      |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHA1                               |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed the string value *“some discarded input”* into the SHA1          |
   |                       |                                                                          |
   |                       | #. Reset the SHA1                                                        |
   |                       |                                                                          |
   |                       | #. Feed an input value of length zero into the SHA1                      |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHA1                               |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed one byte from *In* into the hash function                        |
   |                       |                                                                          |
   |                       | #. Copy HashFunction object and its state.                               |
   |                       |                                                                          |
   |                       | #. Feed rest of *In* into both the original and the copied hash          |
   |                       |    functions.                                                            |
   |                       |                                                                          |
   |                       | #. Verify that both hash functions return same result                    |
   +-----------------------+--------------------------------------------------------------------------+

SHA-224
~~~~~~~

SHA-224 is tested with the following constraints:

-  Number of test cases: 2

-  In: varying length

   -  Range: 0 bits, 8 bits
   -  Extreme values: empty message, 8 bits message

-  Out: 224 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/hash/sha2_32.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | HASH-SHA224-1                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Combined unit and known answer test that checks that reset works         |
   |                       | correctly and hashes a test message as a whole                           |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | In = Input value of length zero                                          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | Out = 0xD14A028C2A3A2BC9476102BB288234C415A2B01F828EA62AC5B3E42F (224    |
   |                       | bits)                                                                    |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create a SHA224 object                                                |
   |                       |                                                                          |
   |                       | #. Test SHA224's name                                                    |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHA224                             |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed the string value *“some discarded input”* into the SHA224        |
   |                       |                                                                          |
   |                       | #. Reset the SHA224                                                      |
   |                       |                                                                          |
   |                       | #. Feed an input value of length zero into the SHA224                    |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHA224                             |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed one byte from *In* into the hash function                        |
   |                       |                                                                          |
   |                       | #. Copy HashFunction object and its state.                               |
   |                       |                                                                          |
   |                       | #. Feed rest of *In* into both the original and the copied hash          |
   |                       |    functions.                                                            |
   |                       |                                                                          |
   |                       | #. Verify that both hash functions return same result                    |
   +-----------------------+--------------------------------------------------------------------------+

SHA-256
~~~~~~~

SHA-256 is tested with the following constraints:

-  Number of test cases: 262

-  In: varying length

   -  Range: 8 byte - 256 bits
   -  Extreme values: empty message, 640 bits, only one bit set

-  Out: 256 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/hash/sha2_32.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | HASH-SHA256-1                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Combined unit and known answer test that checks that reset works         |
   |                       | correctly and hashes a test message as a whole                           |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | In = Input value of length zero                                          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | .. code-block:: none                                                     |
   |                       |                                                                          |
   |                       |    Out = 0xE3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B |
   |                       |    855 (256 bits)                                                        |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create a SHA256 object                                                |
   |                       |                                                                          |
   |                       | #. Test SHA256's name                                                    |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHA256                             |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed the string value *“some discarded input”* into the SHA256        |
   |                       |                                                                          |
   |                       | #. Reset the SHA256                                                      |
   |                       |                                                                          |
   |                       | #. Feed an input value of length zero into the SHA256                    |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHA256                             |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed one byte from *In* into the hash function                        |
   |                       |                                                                          |
   |                       | #. Copy HashFunction object and its state.                               |
   |                       |                                                                          |
   |                       | #. Feed rest of *In* into both the original and the copied hash          |
   |                       |    functions.                                                            |
   |                       |                                                                          |
   |                       | #. Verify that both hash functions return same result                    |
   +-----------------------+--------------------------------------------------------------------------+

SHA-384
~~~~~~~

SHA-384 is tested with the following constraints:

-  Number of test cases: 7

-  In: varying length

   -  Range: 8 bits - 640 bits
   -  Extreme values: empty message, 896 bits

-  Out: 384 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/hash/sha2_64.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | HASH-SHA384-1                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Combined unit and known answer test that checks that reset works         |
   |                       | correctly and hashes a test message as a whole                           |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | In = Input value of length zero                                          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | .. code-block:: none                                                     |
   |                       |                                                                          |
   |                       |    Out = 0x38B060A751AC96384CD9327EB1B1E36A21FDB71114BE07434C0CC7BF63F6E |
   |                       |    1DA274EDEBFE76F65FBD51AD2F14898B95B                                   |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create a SHA384 object                                                |
   |                       |                                                                          |
   |                       | #. Test SHA384's name                                                    |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHA384                             |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed the string value *“some discarded input”* into the SHA384        |
   |                       |                                                                          |
   |                       | #. Reset the SHA384                                                      |
   |                       |                                                                          |
   |                       | #. Feed an input value of length zero into the SHA384                    |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHA384                             |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed one byte from *In* into the hash function                        |
   |                       |                                                                          |
   |                       | #. Copy HashFunction object and its state.                               |
   |                       |                                                                          |
   |                       | #. Feed rest of *In* into both the original and the copied hash          |
   |                       |    functions.                                                            |
   |                       |                                                                          |
   |                       | #. Verify that both hash functions return same result                    |
   +-----------------------+--------------------------------------------------------------------------+

SHA-512
~~~~~~~

SHA-512 is tested with the following constraints:

-  Number of test cases: 7

-  In: varying length

   -  Range: 8 bits - 640 bits
   -  Extreme values: empty message, 896 bits

-  Out: 512 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/hash/sha2_64.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | HASH-SHA512-1                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Combined unit and known answer test that checks that reset works         |
   |                       | correctly and hashes a test message as a whole                           |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | In = Input value of length zero                                          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | .. code-block:: none                                                     |
   |                       |                                                                          |
   |                       |    Out = 0xCF83E1357EEFB8BDF1542850D66D8007D620E4050B5715DC83F4A921D36CE |
   |                       |    9CE47D0D13C5D85F2B0FF8318D2877EEC2F63B931BD47417A81A538327AF927DA3E   |
   |                       |    (512 bits)                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create a SHA512 object                                                |
   |                       |                                                                          |
   |                       | #. Test SHA512's name                                                    |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHA512                             |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed the string value *“some discarded input”* into the SHA512        |
   |                       |                                                                          |
   |                       | #. Reset the SHA512                                                      |
   |                       |                                                                          |
   |                       | #. Feed an input value of length zero into theSHA512                     |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHA512                             |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed one byte from *In* into the hash function                        |
   |                       |                                                                          |
   |                       | #. Copy HashFunction object and its state.                               |
   |                       |                                                                          |
   |                       | #. Feed rest of *In* into both the original and the copied hash          |
   |                       |    functions.                                                            |
   |                       |                                                                          |
   |                       | #. Verify that both hash functions return same result                    |
   +-----------------------+--------------------------------------------------------------------------+

SHA-512/256
~~~~~~~~~~~

SHA-512/256 is tested with the following constraints:

-  Number of test cases: 1

-  In: empty message
-  Out: 256 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/hash/sha2_64.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | HASH-SHA512-256-1                                                        |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Combined unit and known answer test that checks that reset works         |
   |                       | correctly and hashes a test message as a whole                           |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | In = Input value of length zero                                          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | .. code-block:: none                                                     |
   |                       |                                                                          |
   |                       |    Out = 0xC672B8D1EF56ED28AB87C3622C5114069BDD3AD7B8F9737498D0C01ECEF09 |
   |                       |    67A                                                                   |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create a SHA512_256 object                                            |
   |                       |                                                                          |
   |                       | #. Test SHA512_256's name                                                |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHA512_256                         |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed the string value *“some discarded input”* into the SHA512_256    |
   |                       |                                                                          |
   |                       | #. Reset the SHA512_256                                                  |
   |                       |                                                                          |
   |                       | #. Feed an input value of length zero into the SHA512_256                |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHA512_256                         |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed one byte from *In* into the hash function                        |
   |                       |                                                                          |
   |                       | #. Copy HashFunction object and its state.                               |
   |                       |                                                                          |
   |                       | #. Feed rest of *In* into both the original and the copied hash          |
   |                       |    functions.                                                            |
   |                       |                                                                          |
   |                       | #. Verify that both hash functions return same result                    |
   +-----------------------+--------------------------------------------------------------------------+

SHA-3/224
~~~~~~~~~

SHA-3/224 is tested with the following constraints:

-  In: varying length

   -  Range: 8 bits - 14644 bytes
   -  Extreme values: empty message, 14644 bytes

-  Out: 224 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/hash/sha3.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | HASH-SHA3-224-1                                                          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Combined unit and known answer test that checks that reset works         |
   |                       | correctly and hashes a test message as a whole                           |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | In = Input value of length zero                                          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | Out = 0x6b4e03423667dbb73b6e15454f0eb1abd4597f9a1b078e3f5b5a6bc7         |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create a SHA3_224 objectTest SHA3_224's nameFeed the input value *In* |
   |                       |    into the SHA3_224Calculate the message digest and compare with the    |
   |                       |    expected output value *Out*\ Feed the string value *“some discarded   |
   |                       |    input”* into the SHA3_224Reset the SHA3_224Feed an input value of     |
   |                       |    length zero into the SHA3_224Feed the input value *In* into the       |
   |                       |    SHA3_224Calculate the message digest and compare with the expected    |
   |                       |    output value *Out*                                                    |
   |                       |                                                                          |
   |                       | #. Feed one byte from *In* into the hash function                        |
   |                       |                                                                          |
   |                       | #. Copy HashFunction object and its state.                               |
   |                       |                                                                          |
   |                       | #. Feed rest of *In* into both the original and the copied hash          |
   |                       |    functions.                                                            |
   |                       |                                                                          |
   |                       | #. Verify that both hash functions return same result                    |
   +-----------------------+--------------------------------------------------------------------------+

SHA-3/256
~~~~~~~~~

SHA-3/256 is tested with the following constraints:

-  In: varying length

   -  Range: 8 bits - 13836 bytes
   -  Extreme values: empty message, 13836 bytes

-  Out: 256 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/hash/sha3.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | HASH-SHA3-256-1                                                          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Combined unit and known answer test that checks that reset works         |
   |                       | correctly and hashes a test message as a whole                           |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | In = Input value of length zero                                          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | .. code-block:: none                                                     |
   |                       |                                                                          |
   |                       |    Out = 0xa7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f84 |
   |                       |    34a                                                                   |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create a SHA3_256 object                                              |
   |                       |                                                                          |
   |                       | #. Test SHA3_256's name                                                  |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHA3_256                           |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed the string value *“some discarded input”* into the SHA3_256      |
   |                       |                                                                          |
   |                       | #. Reset the SHA3_256                                                    |
   |                       |                                                                          |
   |                       | #. Feed an input value of length zero into the SHA3_256                  |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHA3_256                           |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed one byte from *In* into the hash function                        |
   |                       |                                                                          |
   |                       | #. Copy HashFunction object and its state.                               |
   |                       |                                                                          |
   |                       | #. Feed rest of *In* into both the original and the copied hash          |
   |                       |    functions.                                                            |
   |                       |                                                                          |
   |                       | #. Verify that both hash functions return same result                    |
   +-----------------------+--------------------------------------------------------------------------+

SHA-3/384
~~~~~~~~~

SHA-3/384 is tested with the following constraints:

-  In: varying length

   -  Range: 8 bits - 10604 bytes
   -  Extreme values: empty message, 10604 bytes

-  Out: 384 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/hash/sha3.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | HASH-SHA3-384-1                                                          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Combined unit and known answer test that checks that reset works         |
   |                       | correctly and hashes a test message as a whole                           |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | In = Input value of length zero                                          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | .. code-block:: none                                                     |
   |                       |                                                                          |
   |                       |    Out = 0x0c63a75b845e4f7d01107d852e4c2485c51a50aaaa94fc61995e71bbee983 |
   |                       |    a2ac3713831264adb47fb6bd1e058d5f004                                   |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create a SHA3_384 object                                              |
   |                       |                                                                          |
   |                       | #. Test SHA3_384's name                                                  |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHA3_384                           |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed the string value *“some discarded input”* into the SHA3_384      |
   |                       |                                                                          |
   |                       | #. Reset the SHA3_384                                                    |
   |                       |                                                                          |
   |                       | #. Feed an input value of length zero into the SHA3_384                  |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHA3_384                           |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed one byte from *In* into the hash function                        |
   |                       |                                                                          |
   |                       | #. Copy HashFunction object and its state.                               |
   |                       |                                                                          |
   |                       | #. Feed rest of *In* into both the original and the copied hash          |
   |                       |    functions.                                                            |
   |                       |                                                                          |
   |                       | #. Verify that both hash functions return same result                    |
   +-----------------------+--------------------------------------------------------------------------+

.. _section-1:

SHA-3/512
~~~~~~~~~

SHA-3/512 is tested with the following constraints:

-  In: varying length

   -  Range: 8 bits - 7372 bytes
   -  Extreme values: empty message, 7372 bytes

-  Out: 512 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/hash/sha3.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | HASH-SHA3-512-1                                                          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Combined unit and known answer test that checks that reset works         |
   |                       | correctly and hashes a test message as a whole                           |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | In = Input value of length zero                                          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | .. code-block:: none                                                     |
   |                       |                                                                          |
   |                       |    Out = 0xa69f73cca23a9ac5c8b567dc185a756e97c982164fe25859e0d1dcc1475c8 |
   |                       |    0a615b2123af1f5f94c11e3e9402c3ac558f500199d95b6d3e301758586281dcd26   |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create a SHA3_512 object                                              |
   |                       |                                                                          |
   |                       | #. Test SHA3_512's name                                                  |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHA3_512                           |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed the string value *“some discarded input”* into the SHA3_512      |
   |                       |                                                                          |
   |                       | #. Reset the SHA3_512                                                    |
   |                       |                                                                          |
   |                       | #. Feed an input value of length zero into the SHA3_512                  |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHA3_512                           |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed one byte from *In* into the hash function                        |
   |                       |                                                                          |
   |                       | #. Copy HashFunction object and its state.                               |
   |                       |                                                                          |
   |                       | #. Feed rest of *In* into both the original and the copied hash          |
   |                       |    functions.                                                            |
   |                       |                                                                          |
   |                       | #. Verify that both hash functions return same result                    |
   +-----------------------+--------------------------------------------------------------------------+

SHAKE
~~~~~

SHAKE being a XOF it is tested for a number of output lengths with the following constraints:

-  In: varying length

   -  Range: 0 bits - 3041 bytes

-  Out: 128 bits, 256 bits, 1120 bits, 2000 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/hash/shake.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | HASH-SHAKE-128-128                                                       |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Combined unit and known answer test that checks that reset works         |
   |                       | correctly and hashes a test message as a whole                           |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | In = 0xd4d67b00ca51397791b81205d5582c0a (128 bits)                       |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | .. code-block:: none                                                     |
   |                       |                                                                          |
   |                       |    Out = 0xd0acfb2a14928caf8c168ae514925e4e (128 bits)                   |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create a SHAKE-128(128) object                                        |
   |                       |                                                                          |
   |                       | #. Test SHAKE-128(128)'s name                                            |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHAKE-128(128)                     |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed the string value *“some discarded input”* into the               |
   |                       |    SHAKE-128(128)                                                        |
   |                       |                                                                          |
   |                       | #. Reset the SHAKE-128(128)                                              |
   |                       |                                                                          |
   |                       | #. Feed an input value of length zero into the SHAKE-128(128)            |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the SHAKE-128(128)                     |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed one byte from *In* into the hash function                        |
   |                       |                                                                          |
   |                       | #. Copy HashFunction object and its state.                               |
   |                       |                                                                          |
   |                       | #. Feed rest of *In* into both the original and the copied hash          |
   |                       |    functions.                                                            |
   |                       |                                                                          |
   |                       | #. Verify that both hash functions return same result                    |
   +-----------------------+--------------------------------------------------------------------------+

Blake2b
~~~~~~~

Blake2b having a configurable output length it is being tested with the following constraints:

-  In: varying length

   -  Range: 0 bytes - 255 bytes

-  Out: 224 bits, 256 bits, 384 bits, 512 bits

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/hash/blake2b.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | HASH-BLAKE2B-384                                                         |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Combined unit and known answer test that checks that reset works         |
   |                       | correctly and hashes a test message as a whole                           |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | In = 0xd8dc8fdefbdce9d44e4cbafe78447bae3b5436102a (168 bits)             |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | .. code-block:: none                                                     |
   |                       |                                                                          |
   |                       |    Out = 0x6b27923e5a298cfc27c65daaedb95ad14eb60921f32ec921d75304cdcb70a |
   |                       |          2f03c4b679b648b95bb3de654f99cc18a40 (384 bits)                  |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create a Blake2b(384) object                                          |
   |                       |                                                                          |
   |                       | #. Test Blake2b(384)'s name                                              |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the Blake2b(384)                       |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed the string value *“some discarded input”* into the               |
   |                       |    Blake2b(384)                                                          |
   |                       |                                                                          |
   |                       | #. Reset the Blake2b(384)                                                |
   |                       |                                                                          |
   |                       | #. Feed an input value of length zero into the Blake2b(384)              |
   |                       |                                                                          |
   |                       | #. Feed the input value *In* into the Blake2b(384)                       |
   |                       |                                                                          |
   |                       | #. Calculate the message digest and compare with the expected output     |
   |                       |    value *Out*                                                           |
   |                       |                                                                          |
   |                       | #. Feed one byte from *In* into the hash function                        |
   |                       |                                                                          |
   |                       | #. Copy HashFunction object and its state.                               |
   |                       |                                                                          |
   |                       | #. Feed rest of *In* into both the original and the copied hash          |
   |                       |    functions.                                                            |
   |                       |                                                                          |
   |                       | #. Verify that both hash functions return same result                    |
   +-----------------------+--------------------------------------------------------------------------+

Parallel Hash Function Tests
----------------------------

.. table::
   :class: longtable
   :widths: 20 80

   +----------------------------------+---------------------------------------------------------------+
   | **Test Case No.:**               | H-PHASH-1                                                     |
   +----------------------------------+---------------------------------------------------------------+
   | **Type:**                        | Positive Test                                                 |
   +----------------------------------+---------------------------------------------------------------+
   | **Description:**                 | Unit test for cloning of a Parallel hash object               |
   +----------------------------------+---------------------------------------------------------------+
   | **Preconditions:**               | None                                                          |
   +----------------------------------+---------------------------------------------------------------+
   | **Input Values:**                | In = Input value of length zero                               |
   +----------------------------------+---------------------------------------------------------------+
   | **Expected Output:**             | .. code-block:: none                                          |
   |                                  |                                                               |
   |                                  |    Out = 0xD41D8CD98F00B204E9800998ECF8427EDA39A3EE5E6B4B0D32 |
   |                                  |    55BFEF95601890AFD80709 (288 bits)                          |
   +----------------------------------+---------------------------------------------------------------+
   | **Steps:**                       | #. Create a Parallel hash object with MD5 and SHA-160         |
   |                                  |                                                               |
   |                                  | #. Feed an input value of length zero into the hash function  |
   |                                  |                                                               |
   |                                  | #. Calculate the message digest and compare with the expected |
   |                                  |    output value *Out*                                         |
   |                                  |                                                               |
   |                                  | #. Clone the parallel hash function object                    |
   |                                  |                                                               |
   |                                  | #. Reset the cloned parallel hash function object             |
   |                                  |                                                               |
   |                                  | #. Feed an input value of length zero into the hash function  |
   |                                  |                                                               |
   |                                  | #. Calculate the message digest and compare with the expected |
   |                                  |    output value *Out*                                         |
   +----------------------------------+---------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +----------------------------------+---------------------------------------------------------------+
   | **Test Case No.:**               | H-PHASH-2                                                     |
   +----------------------------------+---------------------------------------------------------------+
   | **Type:**                        | Positive Test                                                 |
   +----------------------------------+---------------------------------------------------------------+
   | **Description:**                 | Unit test for construction of a Parallel hash object          |
   +----------------------------------+---------------------------------------------------------------+
   | **Preconditions:**               | None                                                          |
   +----------------------------------+---------------------------------------------------------------+
   | **Input Values:**                | In = Input value of length zero                               |
   +----------------------------------+---------------------------------------------------------------+
   | **Expected Output:**             | .. code-block:: none                                          |
   |                                  |                                                               |
   |                                  |    Out = 0xE3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA4 |
   |                                  |    95991B7852B855CF83E1357EEFB8BDF1542850D66D8007D620E4050B57 |
   |                                  |    15DC83F4A921D36CE9CE47D0D13C5D85F2B0FF8318D2877EEC2F63B931 |
   |                                  |    BD47417A81A538327AF927DA3E (1536 bits)                     |
   +----------------------------------+---------------------------------------------------------------+
   | **Steps:**                       | #. Create a SHA-256 object                                    |
   |                                  |                                                               |
   |                                  | #. Create a SHA-512 object                                    |
   |                                  |                                                               |
   |                                  | #. Create a Parallel hash object with the SHA-256 and SHA-512 |
   |                                  |    objects                                                    |
   |                                  |                                                               |
   |                                  | #. Feed an input value of length zero into the hash function  |
   |                                  |                                                               |
   |                                  | #. Calculate the message digest and compare with the expected |
   |                                  |    output value *Out*                                         |
   |                                  |                                                               |
   |                                  | #. Clone the parallel hash function object                    |
   |                                  |                                                               |
   |                                  | #. Reset the cloned parallel hash function object             |
   |                                  |                                                               |
   |                                  | #. Feed an input value of length zero into the hash function  |
   |                                  |                                                               |
   |                                  | #. Calculate the message digest and compare with the expected |
   |                                  |    output value *Out*                                         |
   +----------------------------------+---------------------------------------------------------------+
