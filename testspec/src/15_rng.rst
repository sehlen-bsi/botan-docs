Random Number Generators
========================

Random number generators (RNGs) are tested using positive tests which
compare the resulting output of the seeded random number generator with
the data from test vectors (*hmac_drbg*). In addition to these tests, a
unit test for HMAC-DRBG defines positive and negative tests which
validates the correctness of the HMAC-DRBG random number generator
(*hmac_drbg_unit*).

All unit tests for various RNGs are implemented in
:srcref:`src/tests/test_rngs.cpp`.

All Known-Answer tests are implemented in :srcref:`src/tests/test_rng_kat.cpp`.

HMAC-DRBG
---------

HMAC-DRBG RNG is tested with the following constraints:

-  Number of test cases: 3360
-  Source: NIST CAVP (NIST CAVS file 14.3)

-  EntropyInput: initial entropy input
-  EntropyInputReseed: entropy input used to reseed the RNG
-  AdditionalInput1: optional randomization input
-  AdditionalInput2: optional randomization input
-  Out: RNG output (80-256 bytes)

The tests are executed for HMAC-DRBG with SHA-1, SHA-224, SHA-256,
SHA-384, SHA-512, and SHA-512-256.

The following table shows an example test case with one test vector.
Tests are implemented in :srcref:`src/tests/test_rng_kat.cpp`. All test vectors
are listed in :srcref:`src/tests/data/rng/hmac_drbg.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | RNG-HMAC-DRBG-1                                                          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | A known answer test that checks the correct RNG output                   |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | .. code-block:: none                                                     |
   |                       |                                                                          |
   |                       |    EntropyInput = 0x29C62AFA3C52208A3FDECB43FA613F156C9EB59AC3C2D48B     |
   |                       |    EntropyInputReseed = 0xBD87BE99D184165412314140D4027141433DDAF259D14B |
   |                       |    CF897630CCAA27338C                                                    |
   |                       |    AdditionalInput1 = 0x141146D404F284C2D02B6A10156E3382                 |
   |                       |    AdditionalInput2 = 0xEDC343DBFFE71AB4114AC3639D445B65                 |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | .. code-block:: none                                                     |
   |                       |                                                                          |
   |                       |     Out =  0x8C730F0526694D5A9A45DBAB057A1975357D65AFD3EFF303320BD14061  |
   |                       |     F9AD38759102B6C60116F6DB7A6E8E7AB94C05500B4D1E357DF8E957AC8937B05FB  |
   |                       |     3D080A0F90674D44DE1BD6F94D295C4519D                                  |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create an HMAC_DRBG object                                            |
   |                       |                                                                          |
   |                       | #. Seed the RNG with *EntropyInput*                                      |
   |                       |                                                                          |
   |                       | #. Reseed the RNG with *EntropyInputReseed*                              |
   |                       |                                                                          |
   |                       | #. Add additional randomization input *AdditionalInput1* and             |
   |                       |    *AdditionalInput2*                                                    |
   |                       |                                                                          |
   |                       | #. Compare the result with the output value *Out*                        |
   +-----------------------+--------------------------------------------------------------------------+

Unit Test for HMAC-DRBG
~~~~~~~~~~~~~~~~~~~~~~~

The unit tests for HMAC-DRBG (**hmac_drbg_unit**) are implemented in
:srcref:`src/tests/test_rngs.cpp`. They extend the **hmac_drbg** test suite with
negative tests. The following additional properties of HMAC-DRBG are
tested:

-  test_reseed_kat.
-  test_reseed: Tests the reseed interval.
-  test_max_number_of_bytes_per_request:
-  test_broken_entropy_input: Tests whether the RNG throws exceptions if
   it is provided with insufficient entropy.
-  test_check_nonce: Tests whether the nonce provided to the RNG has at
   least one half of the security bit strength. Otherwise, the RNG has
   to throw an exception (for HMAC-SHA-256, the nonce has to be at least
   16 bytes long).
-  test_prediction_resistance: Tests with a reseed interval set to 1.
-  test_fork_safety: Tests whether a forked process has a different RNG
   output than its parent process.
-  test_randomize_with_ts_input: Tests the function
   *randomize_with_ts_input*.
-  test_security_level: Tests that HMAC_DRBG derives the security level
   from the hash function output length correctly
-  test_reseed_interval_limits: Tests that HMAC_DRBG only accepts reseed
   intervals *0 < x <= 2*\ :sup:`24`

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | RNG-HMAC-DRBG-2                                                          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Unit Test                                                                |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | test_max_number_of_bytes_per_request: test requests for random bytes     |
   |                       | trigger reseeding and split of long requests into smaller ones           |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | -  RI : Reseed interval                                                  |
   |                       |                                                                          |
   |                       | -  MNBPR : max number of bytes per request                               |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Check that instantiation of HMAC_DRBG using the *MNBPR* = 0 throws an |
   |                       |    exception                                                             |
   |                       |                                                                          |
   |                       | #. Check that instantiation of HMAC_DRBG using the *MNBPR* > 64 kiB      |
   |                       |    throws an exeception                                                  |
   |                       |                                                                          |
   |                       | #. Instantiate HMAC_DRBG using the *MNBPR* = 64 and *RI* = 1             |
   |                       |                                                                          |
   |                       | #. Check that requesting more bytes than *MNBPR* results in split of     |
   |                       |    initial request into multiple, at most *MNBPR* bytes long, requests.  |
   +-----------------------+--------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | RNG-HMAC-DRBG-3                                                          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Unit Test                                                                |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | test_security_level: test that HMAC_DRBG returns security level that     |
   |                       | corresponds to the underlying hash function it was instantiated with     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | -  Approved hash functions: SHA-160, SHA-224, SHA-256, SHA-512/256,      |
   |                       |    SHA-384, SHA-512                                                      |
   |                       |                                                                          |
   |                       | -  Security levels: 128, 192, 256, 256, 256, 256                         |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Instantiate MAC object using one of the approved hash functions       |
   |                       |                                                                          |
   |                       | #. Instantiate HMAC_DRBG object by passing it the MAC object             |
   |                       |                                                                          |
   |                       | #. Test that the security level of the HMAC_DRBG object returns          |
   |                       |    corresponding security level                                          |
   +-----------------------+--------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | RNG-HMAC-DRBG-4                                                          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Unit Test                                                                |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | test_reseed_kat: test that HMAC_DRBG reseeds on second RNG request by    |
   |                       | calling randomize() on the underlying RNG                                |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | .. code-block:: none                                                     |
   |                       |                                                                          |
   |                       |    SeedData = 0x00112233445566778899AABBCCDDEEFF                         |
   |                       |    OutFirstRequest = 48D3B45AAB65EF92CCFCB9427EF20C90297065ECC1B8A525B   |
   |                       |    FE4DC6FF36D0E38                                                       |
   |                       |    OutSecondRequest = 2F8FCA696832C984781123FD64F4B20C7379A25C87AB29A2   |
   |                       |    1C9BF468B0081CE2                                                      |
   |                       |    ReseedInterval = 2                                                    |
   |                       |                                                                          |
   |                       | -  SourceRNG: an RNG to be an entropy source for HMAC_DRBG               |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Instantiate HMAC_DRBG object by passing it the *SourceRNG* and        |
   |                       |    *ReseedInterval* equal to 2                                           |
   |                       |                                                                          |
   |                       | #. Test that instantiated HMAC_DRBG object is not seeded                 |
   |                       |                                                                          |
   |                       | #. Initialize HMAC_DRBG with *SeedData*                                  |
   |                       |                                                                          |
   |                       | #. Do first request for 32 bytes of random data from HMAC_DRBG           |
   |                       |                                                                          |
   |                       | #. Test that output is equal to *OutFirstRequest*                        |
   |                       |                                                                          |
   |                       | #. *Do second request* *for* *32 bytes of random data* *from*            |
   |                       |    *HMAC_DRBG*                                                           |
   |                       |                                                                          |
   |                       | #. *Test that auto reseeding takes place and randomize() is called on    |
   |                       |    the underlying* *RNG*                                                 |
   +-----------------------+--------------------------------------------------------------------------+

AutoSeeded_RNG
--------------

The AutoSeeded_RNG random number generator is tested using a unit test
for initialization, seeding and reseeding.

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | RNG-AUTO-RNG-1                                                           |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | A unit test that makes sure initialization, seeding and reseeding work   |
   |                       | correctly                                                                |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create an AutoSeeded_RNG object with an empty set of entropy sources  |
   |                       |    and check that it throws a PRNG_Unseeded exception                    |
   |                       |                                                                          |
   |                       | #. Create an AutoSeeded_RNG object with a Null_RNG as the entropy source |
   |                       |    and check that it throws a PRNG_Unseeded exception                    |
   |                       |                                                                          |
   |                       | #. Create an AutoSeeded_RNG object with a an empty set of entropy        |
   |                       |    sources and a Null_RNG as the entropy source and check that it throws |
   |                       |    a PRNG_Unseeded exception                                             |
   |                       |                                                                          |
   |                       | #. Create an AutoSeeded_RNG object with the default constructor          |
   |                       |                                                                          |
   |                       | #. Check that the name is HMAC_DRBG plus the HMAC specified in           |
   |                       |    BOTAN_AUTO_RNG_HMAC                                                   |
   |                       |                                                                          |
   |                       | #. Check that the AutoSeeded_RNG is seeded                               |
   |                       |                                                                          |
   |                       | #. Extract 16 random bytes from the AutoSeeded_RNG                       |
   |                       |                                                                          |
   |                       | #. Reset the AutoSeeded_RNG                                              |
   |                       |                                                                          |
   |                       | #. Check that the AutoSeeded_RNG is not seeded                           |
   |                       |                                                                          |
   |                       | #. Extract 16 random bytes from the AutoSeeded_RNG, forcing an automatic |
   |                       |    reseed                                                                |
   |                       |                                                                          |
   |                       | #. Check that the AutoSeeded_RNG is seeded                               |
   |                       |                                                                          |
   |                       | #. Check that the AutoSeeded_RNG is seeded                               |
   |                       |                                                                          |
   |                       | #. Extract 16 random bytes from the AutoSeeded_RNG                       |
   |                       |                                                                          |
   |                       | #. Reset the AutoSeeded_RNG                                              |
   |                       |                                                                          |
   |                       | #. Check that the AutoSeeded_RNG is not seeded                           |
   |                       |                                                                          |
   |                       | #. Attempt to reseed the AutoSeeded_RNG with 256 bits from an empty set  |
   |                       |    of entropy sources and check that the returned entropy estimation is  |
   |                       |    zero                                                                  |
   |                       |                                                                          |
   |                       | #. Check that the AutoSeeded_RNG is not seeded                           |
   |                       |                                                                          |
   |                       | #. Extract 16 random bytes from the AutoSeeded_RNG, forcing an automatic |
   |                       |    reseed                                                                |
   |                       |                                                                          |
   |                       | #. Check that the AutoSeeded_RNG is seeded                               |
   +-----------------------+--------------------------------------------------------------------------+

System_RNG
----------

The system RNG is tested for basic consistency and functionality.

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | RNG-SYS-RNG-1                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | A unit test that makes sure initialization and basic functionality work  |
   |                       | correctly                                                                |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | (partially) 64bit system (size_t > 4 bytes)                              |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create a System_RNG object using its default constructor              |
   |                       |                                                                          |
   |                       | #. Check that the System_RNG reports a reasonable “name”                 |
   |                       |                                                                          |
   |                       | #. | Make sure that the System_RNG is seeded                             |
   |                       |    | (invariant: system RNG is always seeded, as it is not under Botan’s |
   |                       |      control)                                                            |
   |                       |                                                                          |
   |                       | #. Clear the System_RNG (which is a NO-OP) and check that the RNG is     |
   |                       |    still seeded (see invariant above)                                    |
   |                       |                                                                          |
   |                       | #. Reseed the System_RNG                                                 |
   |                       |                                                                          |
   |                       | #. | Fetch several random data buffers from the RNG:                     |
   |                       |    | Consecutively weighing from 1 byte to 128 bytes                     |
   |                       |                                                                          |
   |                       | #. | On 64-bit systems (size_t > 4 bytes):                               |
   |                       |    | *Regression Test*                                                   |
   |                       |                                                                          |
   |                       |    #. Prepare an output buffer (4 GiB + 1024 bytes) with a well-known    |
   |                       |       bit pattern for the highest 1024 bytes of the buffer               |
   |                       |                                                                          |
   |                       |    #. Pull 4 GiB + 1024 bytes from the RNG into the prepared output      |
   |                       |       buffer                                                             |
   |                       |                                                                          |
   |                       |    #. Confirm that the prepared 1024bytes at the end of the buffer were  |
   |                       |       overwritten as expected                                            |
   +-----------------------+--------------------------------------------------------------------------+
