.. _valgrind/sca:

Side Channel Analysis Using Valgrind
=====================================

Overview
--------

Originally, Valgrind was designed to be a memory error detector. As such it is a
dynamic analysis tool and analyzes program behavior during execution. However,
it can also be used to detect side-channel vulnerabilities in cryptographic
implementations. This approach was first used in `"ctgrind"
<https://github.com/agl/ctgrind>`_, but the basic idea works with a vanilla
Valgrind as well.

The implementer adds annotations to mark specific memory regions as explicitly
secret or explicitly public. Valgrind then tracks runtime data dependencies of
these regions and warns whenever a control flow decision or indexed memory
access depends on the annotated secret data or any data that was derived from it.

This is a powerful technique to detect side-channel vulnerabilities, but it
requires careful code annotation and a good understanding of the cryptographic
algorithm.

Using Valgrind to Detect Side-Channels
--------------------------------------

Secret data regions are marked using ``VALGRIND_MAKE_MEM_UNDEFINED()``, telling
Valgrind that the data in this region is "undefined". For Valgrind this is
equivalent to allocated memory that was never explicitly initialized. Note that
it is legal to read from such regions and even to perform operations on the
data, as long as no assumption on the result of these operations is made. Hence,
Valgrind will only emit a warning if such a result is used to create side
effects that might lead to program bugs. Coincidentally, this is exactly what
causes certain side-channel vulnerabilities based on secret-dependent execution
patterns.

Explicitly note that the "undefined" state of memory regions is propagated by
Valgrind as the program performs operations on such values. This means that any
derived value, such as some operation's result, that is *dependent* on
"undefined" data will also be *marked* as "undefined".

Here is a basic example:

.. code-block:: c

   uint8_t secret_byte = 42;
   uint8_t public_byte = 23;

   VALGRIND_MAKE_MEM_UNDEFINED(&secret_byte, sizeof(secret_byte));

   uint8_t x = secret_byte ^ public_byte;

   if (x % 2 == 1) {
      // do something 'odd'
   }

Valgrind would emit a single warning for the conditional statement because the
value of ``x`` depends on the "undefined" data ``secret_byte``. No warning would
be generated for the calculation of ``x``.

In practice, such secret-dependent control flow or memory access is detected on
the level of machine code and then mapped back to the relevant C/C++ code.
Hence, even if the conditional jump was introduced by a compiler optimization,
Valgrind would still detect it.

To explicitly mark data as public, one may use ``VALGRIND_MAKE_MEM_DEFINED()``.

Botan wraps these Valgrind annotations into convenient helper functions, see
:srcref:`[src/lib/utils]/ct_utils.h`. Also, it provides a basic self-test suite
to verify that the helper functions and the Valgrind setup work as expected, see
:srcref:`[src/ct_selftest]/ct_selftest.cpp`. Those self-tests serve as a good
starting point to understand the guarantees and limitations of this approach.

Limitations
-----------

 * **Requires manual annotation of the implementation**

      The implementer must manually annotate the code to mark secret data
      regions. Additionally, public data that was derived from secret values
      must also be marked as "public" explicitly. For instance, asymmetric
      encryption schemes usually derive the public key from the secret key.

      This is a tedious and error-prone process, especially for complex
      implementations.

 * **Results are not easily generalizable**

      Valgrind detects secret-dependent execution patterns in a specific binary
      that was generated with certain compiler flags and for a concrete hardware
      platform. This does not guarantee that the implementation is free of such
      side-channels in any other configuration of compiler, flags, and target.

 * **Limited scope of detection**

      Valgrind can detect side-channels that are based on secret-dependent
      control flow or memory access patterns. Timing side-channels that are
      based on cache access patterns or other micro-architectural features, such
      as operand-dependent execution times of certain machine instructions, are
      not detected.

 * **Performance overhead**

      Valgrind is a dynamic analysis tool and hence incurs a significant
      performance overhead. This slows down development and testing cycles and
      creates an obstacle for an extensive set of configurations in continuous
      integration.
