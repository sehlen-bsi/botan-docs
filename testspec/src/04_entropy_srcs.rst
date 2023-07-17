Entropy Sources
===============

Entropy sources are tested using a system test that polls the entropy
source for entropy and checks that entropy was added to given random
number generator's entropy pool. Additionally, the entropy returned by
the entropy sources is compressed using different compression algorithms
and the compressed byte size is compared to the number of entropy bytes
returned by the entropy source. All entropy sources in the build-time
configuration variable BOTAN_ENTROPY_DEFAULT_SOURCES are tested. In the
default configuration these are "rdseed", "rdrand", "darwin_secrandom",
"dev_random", "win32_cryptoapi", "proc_walk" and "system_stats". Note
that some entropy sources are not available on all platforms and
therefore tests are skipped on unsupported platforms.

All the tests are implemented in *src/tests/test\_entropy.cpp*.

Entropy sources are tested with the following constraints:

-  Number of test cases: 1
-  Source: -

.. table::
   :class: longtable
   :widths: 20 80

   +-----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**    | ENTROPY-1                                                                |
   +-----------------------+--------------------------------------------------------------------------+
   | **Type:**             | Positive Test                                                            |
   +-----------------------+--------------------------------------------------------------------------+
   | **Description:**      | Tests whether each enabled entropy source outputs entropy bytes          |
   +-----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**    | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Input Values:**     | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Expected Output:**  | None                                                                     |
   +-----------------------+--------------------------------------------------------------------------+
   | **Steps:**            | #. Create an Entropy_Sources object from all entropy sources in          |
   |                       |    BOTAN_ENTROPY_DEFAULT_SOURCES using Entropy_Sources::global_sources() |
   |                       |                                                                          |
   |                       | #. Get all sources supported by this platform and for each entropy       |
   |                       |    source do:                                                            |
   |                       |                                                                          |
   |                       |    a. Poll the entropy source using a SeedCapturing_RNG test object and  |
   |                       |       check that the number of entropy bytes added to the                |
   |                       |       SeedCapturing_RNG pool is greater or equal to the entropy estimate |
   |                       |       returned by the entropy source                                     |
   |                       |                                                                          |
   |                       |    b. If the entropy source added entropy to the pool in the previous    |
   |                       |       step, check that it added at least one byte and check that it      |
   |                       |       added entropy exactly once                                         |
   +-----------------------+--------------------------------------------------------------------------+
