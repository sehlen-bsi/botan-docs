.. _rng/main:

Random Number Generators
========================

Random number generators are used for different purposes inside the
library, as explained in the former chapters, and can also be used by
application developers. All functions in Botan that need random numbers
take a reference to a random number generator instance as a parameter.

Random number generators in Botan include deterministic generators, such as
``HMAC_DRBG`` and ``AutoSeeded_RNG``, system-specific generators such as
System_RNG and hardware random number generators such as ``Processor_RNG``.

All random number generators in Botan implement the
``RandomNumberGenerator`` interface. This interface provides the following
important member functions that typically take ``std::span`` from C++20:

-  ``randomize(output)``: Extracts ``output.size()`` random bytes from the
   random number generator and writes them into ``output``.
-  ``add_entropy(input)``: Incorporates ``input.size()`` bytes of entropy
   from the input buffer ``input`` into the random number generator's
   entropy pool.
-  ``randomize_with_input(output, input)``:
   Incorporates ``input.size()`` bytes of entropy from the input buffer
   ``input`` into the random number generator's entropy pool and then
   extracts ``output.size()`` random bytes from the random number generator
   and writes them into ``output``.
-  ``randomize_with_ts_input(output)``: First refreshes the random number
   generator's entropy pool with a 64 bit system timestamp and, if a system
   RNG is available, 96bits from the system's RNG. Otherwise, those 96bits
   are filled with a 64 bit processor timestamp and the operating system's
   process ID. It then extracts ``output.size()`` random bytes from the
   random number generator and writes them into ``output``.
-  ``reseed(entropy_sources, poll_bits, poll_timeout)``: Polls the
   ``entropy_sources`` for up to ``poll_bits`` bits of entropy or until the
   ``poll_timeout`` expires, calls ``add_entropy()`` on this random
   generator and returns an estimate of the number of bits collected.
   The default value for ``poll_bits`` is ``BOTAN_RNG_RESEED_POLL_BITS``,
   which defaults to 256. The default value for ``poll_timeout`` is
   ``BOTAN_RNG_RESEED_DEFAULT_TIMEOUT``, which defaults to 50
   milliseconds.
-  ``reseed_from_rng(rng, poll_bits)``: Polls the ``rng`` for ``poll_bits``
   bits of entropy and calls ``add_entropy()`` on this random generator.
   The default value for ``poll_bits`` is ``BOTAN_RNG_RESEED_POLL_BITS``,
   which defaults to 256.

Deterministic Generators
------------------------

There are two classes of random bit generators. Non-deterministic random
bit generators are based on a physical process that is unpredictable. In
contrast, deterministic random bit generators compute bits
deterministically using a specific algorithm. Deterministic generators
**must** be seeded with a seed of sufficiently high entropy. For the
requirements on seed generation, see [TR-02102-1]_ sec. 9.5.

.. _rng/hmac_drbg:

HMAC_DRBG
^^^^^^^^^

HMAC_DRBG is a deterministic random bit generator specified in
[SP800-90A]_. The ``HMAC_DRBG`` class derives from the ``Stateful_RNG`` base
class, which provides such functionality as automatic reseeding after a
defined interval and after a process fork. The HMAC_DRBG is provided in
:srcref:`src/lib/rng/hmac_drbg/hmac_drbg.cpp`, the Stateful_RNG in
:srcref:`src/lib/rng/stateful_rng/stateful_rng.cpp`.

HMAC_DRBG Instantiation
~~~~~~~~~~~~~~~~~~~~~~~

HMAC_DRBG can be instantiated with different types of entropy sources.
Therefore, HMAC_DRBG provides five constructors.

1. No entropy sources, just the keyed hash function: This instance will
   not be able to seed and reseed itself. Seeding must be done by
   explicitly calling the function ``initialize_with()``. If a fork is
   detected during calls to ``randomize()``, the instance will throw an
   exception.
2. ``underlying_rng``: An object implementing the ``RandomNumberGenerator``
   interface used for seeding and reseeding. Automatic reseeding from
   ``underlying_rng`` will take place after reseed interval many requests
   or after a fork was detected.
3. ``entropy_sources``: A collection of objects implementing the
   ``Entropy_Source`` interface used for seeding and reseeding. Automatic
   reseeding from ``entropy_sources`` will take place after reseed
   interval many requests or after a fork was detected.
4. ``underlying_rng``, ``entropy_sources``: An object implementing the
   ``RandomNumberGenerator`` interface and a collection of objects
   implementing the ``Entropy_Source`` interface both used for seeding and
   reseeding. Automatic reseeding from ``underlying_rng`` and
   ``entropy_sources`` will take place after reseed interval many requests
   or after a fork was detected.
5. No entropy sources, just the hash function name: This instance will
   not be able to seed and reseed itself. Seeding must be done by
   explicitly calling the function ``initialize_with()``. If a fork is
   detected during calls to ``randomize()``, the instance will throw an
   exception.

The first constructor is implemented as follows.

.. admonition:: ``HMAC_DRBG()``

   **Input:**

   1. ``prf``: An approved keyed hash function, e.g., HMAC(SHA-512).

   **Output:**

   1. An HMAC_DRBG instance

   **Steps:**

   1. Set ``max_number_of_bytes_per_request`` = 64*1024
   2. Set Stateful_RNG.\ ``reseed_counter`` = 0
   3. Set Stateful_RNG.\ ``last_pid`` = 0
   4. Set ``V`` = 0x01 01..01 -- Comment: prf.\ ``outlen`` bits
   5. Set ``Key`` = 0x00 00..00 -- Comment: prf.\ ``outlen`` bits

The second constructor is implemented as follows:

.. admonition:: ``HMAC_DRBG()``

   **Input:**

   1. ``prf``: An approved keyed hash function, e.g., HMAC(SHA-512).
   2. ``underlying_rng``: A random number generator used for seeding and
      reseeding.
   3. ``reseed_interval``: The reseed interval.
   4. ``max_number_of_bytes_per_request``: The maximum number of bytes per
      request.

   **Output:** An HMAC_DRBG instance

   **Steps:**

   1. If (``reseed_interval`` = 0) or (``reseed_interval`` > 2^24), then Return
      "Invalid Argument"
   2. If (``max_number_of_bytes_per_request`` = 0) or
      (``max_number_of_bytes_per_request`` >= 64*1024), then Return "Invalid
      Argument"
   3. Set Stateful_RNG.\ ``underlying_rng`` = ``underlying_rng``
   4. Set Stateful_RNG.\ ``reseed_counter`` = 0
   5. Set Stateful_RNG.\ ``last_pid`` = 0
   6. Set ``V`` = 0x01 01..01 -- Comment: prf.\ ``outlen`` bits
   7. Set ``Key`` = 0x00 00..00 -- Comment: prf.\ ``outlen`` bits

The third constructor is implemented as follows:

.. admonition:: ``HMAC_DRBG()``

   **Input:**

   1. ``prf``: An approved keyed hash function, e.g., HMAC(SHA-512).
   2. ``entropy_sources``: A collection of entropy sources used the source
      for seeding and reseeding.
   3. ``reseed_interval``: The reseed interval.
   4. ``max_number_of_bytes_per_request``: The maximum number of bytes per
      request.

   **Output:** An HMAC_DRBG instance

   **Steps:**

   1. If (``reseed_interval`` = 0) or (``reseed_interval`` > 2^24), then Return
      "Invalid Argument"
   2. If (``max_number_of_bytes_per_request`` = 0) or
      (``max_number_of_bytes_per_request`` >= 64*1024), then Return "Invalid
      Argument"
   3. Set Stateful_RNG.\ ``entropy_sources`` = ``entropy_sources``
   4. Set Stateful_RNG.\ ``reseed_counter`` = 0
   5. Set Stateful_RNG.\ ``last_pid`` = 0
   6. Set ``V`` = 0x01 01..01 -- Comment: prf.\ ``outlen`` bits
   7. Set ``Key`` = 0x00 00..00 -- Comment: prf.\ ``outlen`` bits

The fourth constructor is implemented as follows:

.. admonition:: ``HMAC_DRBG()``

   **Input:**

   1. ``prf``: An approved keyed hash function, e.g., HMAC(SHA-512).
   2. ``underlying_rng``: A random number generator used for seeding and
      reseeding.
   3. ``entropy_sources``: A collection of entropy sources used the source
      for seeding and reseeding.
   4. ``reseed_interval``: The reseed interval.
   5. ``max_number_of_bytes_per_request``: The maximum number of bytes per
      request.

   **Output:** An HMAC_DRBG instance

   **Steps:**

   1. If (``reseed_interval`` = 0) or (``reseed_interval`` > 2^24), then Return
      "Invalid Argument"
   2. If (``max_number_of_bytes_per_request`` = 0) or
      (``max_number_of_bytes_per_request`` >= 64*1024), then Return "Invalid
      Argument"
   3. Set Stateful_RNG.\ ``underlying_rng`` = ``underlying_rng``
   4. Set Stateful_RNG.\ ``entropy_sources`` = ``entropy_sources``
   5. Set Stateful_RNG.\ ``reseed_counter`` = 0
   6. Set Stateful_RNG.\ ``last_pid`` = 0
   7. Set ``V`` = 0x01 01..01 -- Comment: prf.\ ``outlen`` bits
   8. Set ``Key`` = 0x00 00..00 -- Comment: prf.\ ``outlen`` bits

The fifth constructor is implemented as follows.

.. admonition:: ``HMAC_DRBG()``

   **Input:**

   1. ``hash``: A hash function name, e.g., SHA-512.

   **Output:**

   1. An HMAC_DRBG instance

   **Steps:**

   1. Set ``max_number_of_bytes_per_request`` = 64*1024
   2. Set Stateful_RNG.\ ``reseed_counter`` = 0
   3. Set Stateful_RNG.\ ``last_pid`` = 0
   4. Set ``V`` = 0x01 01..01 -- Comment: prf.\ ``outlen`` bits
   5. Set ``Key`` = 0x00 00..00 -- Comment: prf.\ ``outlen`` bits

**Remark:** [SP800-90A]_ allows a ``reseed_interval`` of up to
2\ :sup:`48`. For implementation reasons Botan limits this to
2\ :sup:`24`.

**Remark:** Due to the polymorphic API design of Botan, the constructors of
``HMAC_DRBG`` take an abstract ``Botan::MessageAuthenticationCode``. This might
represent any MAC and is not limitted to HMAC. Neither is there a runtime check
that ensures ``HMAC_DRBG`` is instantiated with an HMAC, only. Users are required
to ensure to use this class exclusively with HMAC.

Function security_level():
~~~~~~~~~~~~~~~~~~~~~~~~~~

``security_level()`` is a pure virtual function that must be implemented
by classes derived from Stateful_RNG. It returns the security level of
the DRBG. For HMAC_DRBG, the security level of the DRBG depends on the
security level of the hash function used in the PRF, given in
[SP800-57-P1]_ Table 3. For SHA-1, a maximum of 128 bits is supported,
for SHA-224 and SHA-512/224 a maximum of 192 bits is supported and for
SHA-256, SHA-512/256, SHA-384, SHA-512 and SHA3-512 a maximum security
level of 256 bits is supported.

Function reset_reseed_counter():
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Stateful_RNG's ``reset_reseed_counter()`` is used to reset the reseed
counter from derived classes.

.. admonition:: ``reset_reseed_counter()``

   **Input:** None

   **Output:** None

   **Steps:**

   1. Set ``reseed_counter = 1``

Function initialize_with():
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Stateful_RNG's ``initialize_with()`` can be used to manually seed an
HMAC_DRBG, e.g., if it has no entropy sources given during construction.
``initialize_with()`` adds the given entropy to HMAC_DRBG's entropy pool
and resets the reseed counter if at ``security_level()`` entropy bytes
were passed.

.. admonition:: ``initialize_with()``

   **Input:**

   -  ``input``: The string of bits obtained from the entropy source.

   **Output:** None

   **Steps:**

   1. Call ``add_entropy(input)``
   2. If (``8*input.size() >= security_level()``) then do call
      ``reset_reseed_counter()``

HMAC_DRBG Reseeding
~~~~~~~~~~~~~~~~~~~

HMAC_DRBG can be reseeded using the ``add_entropy()`` function, which
internally calls the function ``update()`` to update the entropy pool and
resets the reseed counter if ``security_level()`` entropy bytes were passed.

.. admonition:: HMAC_DRBG Reseeding

   **Input:**

   1. ``input``: The string of bits obtained from the entropy source.

   **Output:** None

   **Steps:**

   1. Call ``update(input)``
   2. If (``8*input.size() >= security_level()``) then do call
      ``reset_reseed_counter()``

Function update():
~~~~~~~~~~~~~~~~~~

The ``update()`` function resets the internal state values ``V`` and MAC
``Key`` with new values according to [SP800-90A]_ section 10.1.2.2.

.. admonition:: ``update()``

   **Input:**

   1. ``input``: The string of bits obtained from the entropy source.

   **Output:** None

   **Steps:**

   1. ``K`` = **HMAC**\ (``K``, ``V`` \|\| 0x00 \|\| ``input``)
   2. ``V`` = **HMAC**\ (``K``, ``V``)
   3. If (``input.size()`` > 0) then:

      1. ``K`` = **HMAC**\ (``K``, ``V`` \|\| 0x01 \|\| ``input``)
      2. ``V`` = **HMAC**\ (``K``, ``V``)

HMAC_DRBG Randomize
~~~~~~~~~~~~~~~~~~~

All random number generators in Botan are implemented based on the
virtual internal method `fill_bytes_with_input()` that takes the buffers
``output`` and ``input``. Either of those can be empty. Typically, this
will first incorporate the bits in ``input`` into the RNG's internal state
and then fill the ``output`` buffer with random bytes. All public methods
are implemented as facades of this internal method.

For all subclasses of ``Stateful_RNG`` (i.e. ``HMAC_DRBG``), the
``fill_bytes_with_input()`` is implemented based on the virtual internal
methods ``update()`` and ``generate_output()``.
``generate_output()`` extracts the requested number of random bytes
from the internal state ``V`` using the PRF given during construction
and will update ``V`` as defined in [SP800-90A]_ using ``update()``. Note
that ``update()`` by itself can also be used to update ``V`` without
generating output bytes.
See :srcref:`src/lib/rng/hmac_drbg/hmac_drbg.cpp` for further details.

Random bytes can be requested from HMAC_DRBG using the public methods
``randomize()``, ``randomize_with_input()`` and ``randomize_with_ts_input()``
functions. See above for further implementation details of those methods.

In contrast to [SP800-90A]_ section 10.1.2.5, Botan's implementation of
``HMAC_DRBG`` will not output an error if a reseed is required, but instead
perform an automatic reseed from the entropy source given during construction.
Additionally, it will also not output an error if ``requested_number_of_bytes >
max_number_of_bytes_per_request``, but instead treat such calls as if multiple
subsequent calls to the random number generator were made.

The automatic reseeding will also attempts to detect a fork of the process
on Unix systems by comparing the process ID between calls. If the
process ID changed, it will automatically perform a reseed. Seeding and
reseeding is done in the Stateful_RNG's ``reseed_check()`` member
function.

.. admonition:: ``fill_bytes_with_input()``

   **Input:**

   1. ``output``: Output buffer to hold the requested random bytes.
   2. ``input``: A string of bits obtained from an entropy source to be mixed
                 into the entropy pool before extraction.

   **Output:**

   1. ``output``: The pseudorandom bits to be returned to the consuming
      application.

   **Steps:**

   1. Set ``bytes_to_generate = output.size()``
   2. While (``bytes_to_generate`` > 0) do:

      1. Set ``this_req = min(max_number_of_bytes_per_request, bytes_to_generate``
      2. Call Stateful_RNG's ``reseed_check()``
      3. If ``input.size() != 0``, then ``update(input)`` (once per top-level request, see (7))
      4. While (``this_req`` > 0) do:

         1. ``to_copy = min(this_req, V.size())``
         2. ``V = HMAC(Key, V)``
         3. ``output = output || leftmost(V, to_copy)``
         4. ``this_req = this_req - to_copy``

      5. Call ``update(input)``
      6. Set ``bytes_to_generate = bytes_to_generate - this_req``
      7. Clear the input for the next inner loop: ``input = {}``

``randomize_with_ts_input()`` incorporates a 64 bit processor timestamp,
using QueryPerformanceCounter's QuadPart value on Windows and an inline
assembly to query the processor counter on other platforms. If
System_RNG is available, it also incorporates 96 bit from it. Otherwise
it additionally incorporates a system clock timestamp in nanoseconds
precision (64 bit) and the 32 bit process ID (PID)
It is implemented as follows.

.. admonition:: ``randomize_with_ts_input()``

   **Input:**

   1. ``output``: Output buffer to hold the requested random bytes\ *.*

   **Output:** None

   **Steps:**

   1. Add a 64 bit processor timestamp to ``additional_input``
   2. If System_RNG is available, get 96 bit from it by calling its
      ``randomize()`` member function and add it to ``additional_input``
   3. If System_RNG is not available

      1. Add a 64 bit system clock timestamp to ``additional_input``
      2. Add the 32 bit process ID to ``additional_input``

   4. Call ``fill_bytes_with_input(output, additional_input)``

Function ``Stateful_RNG::reseed_check()``:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Stateful_RNG's ``reseed_check()`` initially seeds HMAC_DRBG and reseeds
HMAC_DRBG if a fork occurred in the calling process or if the reseed
interval is exceeded. If a seed or reseed is required, it requests
``security_level()`` bits from the entropy sources. ``reseed_check()`` is
implemented as follows.

.. admonition:: ``Stateful_RNG::reseed_check()``

   **Input:** None

   **Output:** None

   **Steps:**

   1. Set ``cur_pid`` = **Get\_Current\_Process\_ID()**
   2. If (``reseed_counter`` = 0) Or ((``last_pid`` > 0) And (``cur_pid`` !=
      ``last_pid``)) Or ((``reseed_interval`` > 0) And (``reseed_counter`` >=
      ``reseed_interval``)) then do:

      1. Set ``reseed_counter`` = 0
      2. Set ``last_pid`` = ``cur_pid``
      3. If the HMAC_DRBG was constructed with at least an underlying
         RNG as an entropy source, ``security_level()`` bits of entropy
         are requested from the underlying RNG and added to HMAC_DRBG's
         entropy pool by calling Stateful_RNG's ``reseed_from_rng()``,
         which works as follows:

         1. Request ``security_level()`` bits of entropy from the
            underlying RNG by calling its ``randomize()`` member
            function, which returns a buffer and an entropy estimation
         2. Mix the returned entropy bytes into HMAC_DRBG's entropy pool
            by calling its ``add_entropy()`` member function (both steps
            via an indirection to the RandomNumberGenerator's
            ``reseed_from_rng()`` member function)
         3. If the returned entropy estimation is equal to or exceeds
            ``security_level()`` then do call ``reset_reseed_counter()``

      4. If the HMAC_DRBG was constructed with at least a collection of
         entropy sources, ``security_level()`` bits of entropy are
         requested from the underlying RNG and added to HMAC_DRBG's
         entropy pool by calling Stateful_RNG's ``reseed_from_rng()``,
         which works as follows:

         1. Request ``security_level()`` bits of entropy from the entropy
            sources by calling Entropy_Sources' ``poll()`` member
            function, which mixes entropy bytes into HMAC_DRBG's entropy
            pool by calling its ``add_entropy()`` member function and
            returning the number of bits collected; ``poll()`` takes a
            timeout value in milliseconds after which polling of the
            entropy sources is stopped, the value used here is
            ``BOTAN_RNG_RESEED_POLL_BITS``, which defaults to 50
            milliseconds
         2. If the returned number of bits collected is equal to or
            exceeds ``security_level()`` bits then:

            1. Call ``reset_reseed_counter()``
            2. Return the number of bits collected

      5. If (``reseed_counter`` = 0) then do:

         1. If ((``last_pid`` > 0) And (``cur_pid`` != ``last_pid``)) then
            output "Fork detected, but unable to reseed" Else output
            "PRNG not seeded: HMAC_DRBG"

   3. Else do:

      1. If (``reseed_counter`` = 0) then output "RNG not seeded"
      2. ``reseed_counter`` = ``reseed_counter`` + 1

**Conclusion:** HMAC_DRBG conforms to [SP800-90A]_, although it differs
from the standard in two ways: It automatically reseeds if required
instead of outputting an error in this case and it outputs random bytes
even if the requested number of bytes is greater than the
max_number_of_bytes_per_request parameter permits. In both cases though,
the internal state is updated with fresh entropy if required and thus
the security is ensured as if the application was to perform individual
calls to the RNG.

AutoSeeded_RNG
^^^^^^^^^^^^^^

AutoSeeded_RNG is a random number generator that is automatically
seeded. AutoSeeded_RNG internally uses the :ref:`HMAC_DRBG <rng/hmac_drbg>`.
If no entropy source is explicitly given, AutoSeeded_RNG uses the System_RNG
as the entropy source for HMAC_DRBG. If the System_RNG is not available, that
means it is not part of the library build because it was explicitly
disabled manually or because it is not available [#System_RNG_available]_ for this platform,
it uses a default [#System_RNG_default]_ set of entropy sources. As the name implies,
AutoSeeded_RNG is automatically seeded (and reseeded) from these
sources. The AutoSeeded_RNG is provided in
:srcref:`src/lib/rng/auto_rng/auto_rng.cpp`.

.. [#System_RNG_available]
   Note that the System_RNG is available on most platforms, including
   Android, BSD, Cygwin, Darwin, iOS, Linux, MinGW, Windows and Windows
   Phone.

.. [#System_RNG_default]
   "rdseed", "hwrng", "getentropy", "system_rng", "system_stats"

.. _rng/system_generators:

System Generators
-----------------

System_RNG provides access to an operating system provided random
generator.

+------------------------------------+----------------------------------+
| Source of Random Bytes             | Operating System                 |
+====================================+==================================+
| ``RtlGenRandom``                   | Windows                          |
+------------------------------------+----------------------------------+
| ``BcryptGenRandom``                | Universal Windows Platform (UWP) |
+------------------------------------+----------------------------------+
| ``CCRandomGenerateBytes()``        | macOS, iOS                       |
+------------------------------------+----------------------------------+
| ``arc4random()``                   | macOS, iOS, OpenBSD, ...         |
+------------------------------------+----------------------------------+
| ``getrandom()``                    | Linux (if explicitly enabled)    |
+------------------------------------+----------------------------------+
| ``/dev/random`` / ``/dev/urandom`` | Unix-like platforms              |
+------------------------------------+----------------------------------+

At build time,
the library selects the first available random byte generator API
in the same order of preference as they appear in the table above.

In the following,
the Instantiate, Add_Entropy and Generate functions of all six
implementations are specified. The System_RNG is provided in
:srcref:`src/lib/rng/system_rng/system_rng.cpp`.

RtlGenRandom
^^^^^^^^^^^^

.. admonition:: Construction

   **Output:**

   1. ``m_rtlgenrandom``: Handle to the RtlGenRandom function.

   **Steps:**

   1. Dynamically load function symbol ``SystemFunction036`` from
      ``advapi32.dll``.

.. admonition:: Reseeding

   RtlGenRandom does not support reseeding with user-provided data, Reseed
   is a no-operation.

.. admonition:: Randomize

   **Input:**

   1. ``m_rtlgenrandom``: Handle to the RtlGenRandom function.
   2. ``buf``: The buffer receiving the pseudorandom bytes.

   **Output:**

   1. ``buf``: The pseudorandom bits to be returned to the consuming
      application.

   **Steps:**

   1. ``limit`` = maximum **RtlGenRandom** can return in one call
   2. ``bytesLeft = buf.size()``
   3. If (``bytesLeft > 0``):

      1. ``blockSize = min(bytesLeft, limit)``
      2. success = **RtlGenRandom**\ (``buf``, ``blockSize``)
      3. If (success != TRUE) then output "RtlGenRandom failed"
      4. ``bytesLeft -= blockSize``
      5. Advance write point into ``buf`` by ``blockSize``
      6. Go to step 3

BCryptGenRandom
^^^^^^^^^^^^^^^

.. admonition:: Construction

   **Input:**

   1. ``provider_type``: A null-terminated string that contains the name of the
      CNG provider to be used (set to MS_PRIMITIVE_PROVIDER).

   **Output:**

   1. ``provider_handle``: Handle to the CNG provider.

   **Steps:**

   1. If (**BCryptOpenAlgorithmProvider**\ (&\ ``provider_handle``,
      BCRYPT_RNG_ALGORITHM, provider_type, 0) != STATUS_SUCCESS) then
      output "System_RNG failed to acquire crypto provider"

.. admonition:: Reseeding

   There is a flag BCRYPT_RNG_USE_ENTROPY_IN_BUFFER to provide entropy
   inputs, but it is ignored in Windows 8 and later, so reseeding is a
   no-operation.

.. admonition:: Randomize

   **Input:**

   1. ``provider_handle``: Handle to the CNG provider.
   2. ``buf``: The buffer receiving the pseudorandom bytes.

   **Output:**

   1. ``buf``: The pseudorandom bits to be returned to the consuming
      application.

   **Steps:**

   1. ``limit`` = maximum **BCryptGenRandom** can return in one call
   2. ``bytesLeft = buf.size()``
   3. If (``bytesLeft > 0``):

      1. ``blockSize = min(bytesLeft, limit)``
      2. ret = **BCryptGenRandom**\ (``provider_handle``, ``buf``, ``blockSize``, ``0``)
      3. If (ret != STATUS_SUCCESS) then output "System_RNG call to
         BCryptGenRandom failed"
      4. ``bytesLeft -= blockSize``
      5. Advance write point into ``buf`` by ``blockSize``
      6. Go to step 3

CCRandomGenerateBytes
^^^^^^^^^^^^^^^^^^^^^

.. admonition:: Construction

   As CCRandomGenerateBytes does not need explicit initialization, Instantiate is a
   no-operation.

.. admonition:: Reseeding

   CCRandomGenerateBytes does not support reseeding with user-provided data, Reseed is
   a no-operation.

.. admonition:: Randomize

   Randomize simply invokes the ``CCRandomGenerateBytes()`` function, which fills
   the given buffer with the given number of bytes.

   **Input:**

   1. ``buf``: The buffer receiving the pseudorandom bytes.

   **Output:**

   1. ``buf``: The pseudorandom bits to be returned to the consuming
      application.

   **Steps:**

   1. ret = **CCRandomGenerateBytes**\ (``buf``, ``buf.size()``)
   2. If (ret != kCCSuccess) then output "System_RNG CCRandomGenerateBytes failed"

arc4random
^^^^^^^^^^

.. admonition:: Construction

   As arc4random does not need explicit initialization, Instantiate is a
   no-operation.

.. admonition:: Reseeding

   arc4random does not support reseeding with user-provided data, Reseed is
   a no-operation.

.. admonition:: Randomize

   Randomize simply invokes the ``arc4random_buf()`` function, which fills
   the given buffer with the given number of bytes of ARC4-derived random
   data.

   **Input:**

   1. ``buf``: The buffer receiving the pseudorandom bytes.

   **Output:**

   1. ``buf``: The pseudorandom bits to be returned to the consuming
      application.

   **Steps:**

   1. If (!buf.empty()) then **arc4random_buf**\ (``buf``, ``buf.size()``)

getrandom
^^^^^^^^^

.. admonition:: Construction

   getrandom does not need explicit initialization, Instantiate is a
   no-operation.

.. admonition:: Reseeding

   getrandom does not support reseeding with user-provided data, Reseed is
   a no-operation.

.. admonition:: Randomize

   Randomize invokes the ``getrandom()`` function in a loop, until the given
   buffer is filled with the given number of bytes.

   **Input:**

   1. ``buf``: The buffer receiving the pseudorandom bytes.

   **Output:**

   1. ``buf``: The pseudorandom bits to be returned to the consuming
      application.

   **Steps:**

   1. ``len = buf.size()``
   2. While (``len`` > 0) do:

      1. ``got`` = **getrandom**\ (``buf``, ``len``, 0)
      2. If (``got`` < 0 ) then do:

         1. If (errno = EINTR) do Continue
         2. Return with output "System_RNG getrandom failed"

      3. ``buf`` = ``buf`` + ``got``
      4. ``len`` = ``len`` - ``got``

/dev/urandom
^^^^^^^^^^^^

.. admonition:: Construction

   Instantiate first attempts to open a file descriptor to the system RNG
   device in read-write mode, so additional entropy can be added using
   Add_Entropy later. In some, especially sandboxed, systems though,
   attempting to open in read-write mode will fail. In this case, the file
   descriptor will be opened in read-only mode as a fallback, allowing to
   get random bytes from the system RNG while turning Add_Entropy into
   a no-operation.

   First open ``/dev/random`` and read one byte. On old Linux kernels
   this blocks the RNG until it has been actually seeded.

   **Input:**

   None.

   **Output:**

   1. ``fd``: File descriptor to the RNG device.

   **Steps:**

   1. ``fd`` = **open**\ (``/dev/random``, O_RDWD \| O_NOCTTY)
   2. If (``fd`` < 0) then output "System_RNG failed to open RNG device"
   3. Read one byte from ``fd`` and close ``fd``.
      If reading failed then output "System_RNG failed to read blocking RNG device".
   4. ``fd`` = **open**\ (``/dev/urandom``, O_RDWD \| O_NOCTTY)
   5. If (``fd`` < 0) then do fd = **open**\ (``/dev/urandom``, O_RDONLY
      \| O_NOCTTY)
   6. If (``fd`` < 0) then output "System_RNG failed to open RNG device"

.. admonition:: Reseeding

   **Input:**

   1. ``fd``: File descriptor to the RNG device.
   2. ``input``: Additional input received from the consuming application.

   **Steps:**

   1. ``len = input.size()``
   2. If (``fd`` was opened as read-only) do Return
   3. While (``len`` > 0) do:

      1. ``got`` = **write**\ (``fd``, ``additional_entropy``, ``len``)
      2. If (``got`` < 0) then do:

         1. If (errno = EINTR) do Continue
         2. If (errno = EPERM Or errno = EBADF) do Return
         3. Return with output "System_RNG write failed error"

      3. input += got
      4. ``len`` = ``len`` - ``got``

.. admonition:: Randomize

   **Input:**

   1. ``fd``: File descriptor to the RNG device.
   2. ``buf``: The buffer receiving the pseudorandom bytes.

   **Output:**

   1. ``buf``: The pseudorandom bits to be returned to the consuming
      application.

   **Steps:**

   1. ``len = buf.size()``
   2. While (len > 0) do:

      1. ``got`` = **read**\ (``fd``, ``buf``, len ``s``)
      2. If (``got`` < 0) then do:

         1. If (errno = EINTR) do Continue
         2. Return with output "System_RNG read failed error"

      3. If (``got`` = 0) then return with output "System_RNG EOF on device"
      4. ``buf += got``
      5. ``len = len - got``

Hardware Generators
-------------------

PKCS11_RNG
^^^^^^^^^^

PKCS11_RNG is a random generator that uses the PKCS#11 interface to
retrieve random bytes from a hardware security module (HSM) supporting
the PKCS#11 standard, e.g., a smartcard. The PKCS11_RNG is provided in
:srcref:`src/lib/prov/pkcs11/p11_randomgenerator.cpp`.

.. admonition:: Construction

   **Input:**

   1. ``session``: A PKCS#11 session object with the HSM.

   **Steps:**

   1. Store a reference to the session as ``m_session = session``

.. admonition:: Reseeding

   **Input:**

   1. ``in``: Additional input received from the consuming application.

   **Steps:**

   1. **C_SeedRandom**\ (``m_session.get().module()``, ``in``, ``in.size()``)

.. admonition:: Randomize

   **Input:**

   1. ``output``: The buffer receiving the pseudorandom bytes.

   **Output:**

   1. ``output``: The pseudorandom bits to be returned to the consuming
      application.

   **Steps:**

   1. **C\_GenerateRandom**\ (``m_session.get().handle()``, ``output``, ``output.size()``)

.. _rng/processor_generators:

Processor_RNG
^^^^^^^^^^^^^

Processor_RNG is a random generator that directly invokes a CPU specific instruction
to generate random numbers.
On x86, the RDRAND instruction is used.
On POWER, the DARN instruction is used.
As there is no way to add entropy to the rdrand or darn entropy pool,
``add_entropy()`` is a no-operation.
The ``Processor_RNG`` is provided in :srcref:`src/lib/rng/processor_rng/processor_rng.cpp`.

.. admonition:: Construction

   **Steps:**

   1. If (**has_cpuid_bit**\ (CPUID_RDRAND_BIT) != true AND **has_cpuid_bit**\ (CPUID_DARN_BIT) != true)
      then output "Current CPU does not support RNG instruction"

.. admonition:: Reseeding

   Not implemented.

.. admonition:: Randomize

   **Input:**

   1. ``out``: The buffer receiving the pseudorandom bytes.

   **Output:**

   1. ``out``: The pseudorandom bits to be returned to the consuming
      application.

   **Steps:**

   1. ``out_len = out.size()``
   2. While (``out_len`` >= 4) do:

      1. ``r`` = **read\_hwrng**\ ()
      2. **store_le**\ (``r``, ``buffer``)
      3. ``out`` = ``out`` + 4
      4. ``out_len`` = ``out_len`` - 4

   3. If (``out_len`` > 0) then do:

      1. ``r`` = **read\_hwrng**\ ()
      2. For (i = 0..\ ``out_len``-1) do:

         1. ``buffer``\ [i] = **get_byte**\ (``i``, ``r``)

**Remark:** On 64-bit systems, 8 is used instead of 4 in step 1, 1.3 and 1.4.

Helper Functions
~~~~~~~~~~~~~~~~

.. admonition:: ``read_hwrng()``

   Get 32 (64 on 64-bit system) random bits from CPU using
   the rdrand or darn instruction

   **Output:** 32/64 bit unsigned integer

   **Steps:**

   ``HWRNG_RETRIES``: 10 for RDRAND, 512 for DARN

   1. For (0..\ ``HWRNG_RETRIES``) do:

      1. ``success`` = false;
      2. ``output`` = read_hwrng(&\ ``success``)
      3. If (``success``) then do return ``output``

   2. Output "Processor RNG instruction failed"


.. admonition:: ``read_hwrng(bool& success)``

   Make a single try to get random bits from CPU using the rdrand or darn instruction.

   **Output:**

   - ``output``: 32/64 bit unsigned integer
   - ``success``: A boolean indicating whether instruction succeeded or not.

   **Steps (RDRAND):**

   1. ``output`` = 0
   2. ``success`` = false
   3. cf = \_rdrand32_step(&\ ``output``)
   4. If (1 == cf) then do ``success`` = true
   5. If ( ``success``) then do return ``output``, ``success``
   6. return 0, ``success``

   **Steps (DARN):**

   1. ``output`` = 0
   2. ``output2`` = 0
   3. ``success`` = false
   4. ``asm volatile("darn %0, 1" : "=r" (output))``
   5. ``asm volatile("darn %0, 1" : "=r" (output2))``
   6. If (``(~output) != 0``  and ``(~output2) != 0``)

      1. ``output`` = ``output`` XOR ``output2``
      2. ``success`` = true

   7. If ( ``success``) then do return ``output``, ``success``
   8. return 0, ``success``

**Remark (RDRAND):** On GNU GCC (for 32- and 64-bit systems), instead an inline
assembly for ``rdrand %eax`` is used in step 3.

**Remark (RDRAND):** On 64-bit systems, instead ``_rdrand64_step`` is used in
step 3.

**Remark (DARN):** As the DARN instruction indicates an error by returning
``0xFF..FF`` it is slightly biased. Botan tries to mitigate the bias by invoking
DARN twice and XORing the two results iff both succeed. In case one or both
invocations fail (i.e. return ``0xFF..FF``), the action is retried 512 times. If
the failure persists it is escalated to the user as an exception.
