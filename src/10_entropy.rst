Entropy Sources
===============

An accompanying programming interface to the RandomNumberGenerator
interface is the Entropy_Source interface. Objects of this class can be
used to feed entropy in the pool of a ``RandomNumberGenerator`` object.
There are several entropy sources available in Botan. All of these
implement the abstract ``Entropy_Source`` interface. The interface
consists only of a few methods:

-  ``std::unique_ptr<Entropy_Source> create(type)``: Returns a new entropy
   source of a particular type, or NULL if it's not available.

-  ``name()``: Returns the name of the entropy source.

-  ``poll(rng)``: Performs an entropy gathering poll and adds this entropy
   to the random number generator ``rng``. Returns a conservative estimate
   in bits of the actual entropy added to the ``rng`` during this poll.

Available Sources
-----------------

The following entropy sources are currently defined:

-  ``System_RNG_EntropySource``: Uses the System_RNG random number
   generator (see :ref:`rng/system_generators`). Botan expects this entropy
   source to provide 256bits of randomness for each poll.

-  ``Processor_RNG_EntropySource``:
   If available use the ``Processor_RNG`` (see :ref:`rng/processor_generators`).
   It polls 8192 bytes of entropy from the
   on-chip hardware random number generator. As according to Intel [#intel_drng]_
   there is an upper bound of 511 samples of 128-bit size per seed, this
   guarantees on Intel processors a reseed of the internal ``RdRand`` state. Botan does not
   trust ``Processor_RNG`` so ``Processor_RNG_EntropySource::poll()`` always returns 0.

-  ``Intel_Rdseed``: This entropy source is available on CPU's supporting
   the ``RdSeed`` instruction. It polls entropy from the on-chip hardware
   random number generator. Internally it polls RdSeed 256 times,
   whereas each poll generates 32 bit of entropy. Each poll is retried
   on failure at most 512 times because RdSeed is not guaranteed to
   generate a random number within a specific number of retries. If each
   try was successful 1024 bytes are gathered. Botan does not trust
   ``RdSeed`` so ``Intel_Rdseed::poll()`` always returns 0.

-  ``Win32_EntropySource``: This entropy source is available on Windows,
   Cygwin and MinGW. It gathers entropy from the following Win32 API
   functions. These inputs are not counted.

   -  ``GetTickCount()``
   -  ``GetMessagePos()``
   -  ``GetMessageTime()``
   -  ``GetInputState()``
   -  ``GetCurrentProcessId()``
   -  ``GetCurrentThreadId()``
   -  ``GetSystemInfo()``
   -  ``GlobalMemoryStatusEx()``
   -  ``GetCursorPos()``
   -  ``GetCaretPos()``

-  ``Getentropy``: This entropy source is available on OpenBSD and macOS
   by default. It can be enabled for Linux and Android. It gathers 256
   bytes of entropy using the ``getentropy(2)`` system call first
   introduced in OpenBSD 5.6. Note that the maximum buffer size of the
   buffer provided ``getentropy(2)`` is limited to 256 bytes. This call is
   guaranteed to never block or fail.

.. [#intel_drng]

   https://software.intel.com/en-us/articles/intel-digital-random-number-generator-drng-software-implementation-guide

The Entropy_Sources class
-------------------------

This class manages the available sources. The static method

``Entropy_Sources& Entropy_Sources::global_sources()``

returns a reference to the default sources which are defined in build.h
as follows:

.. code-block:: C++

   #define BOTAN_ENTROPY_DEFAULT_SOURCES \
   { "rdseed", "hwrng", "getentropy", "system_rng", "system_stats" }

These sources are used by the ``AutoSeeded_RNG`` if no system RNG is
available.

RNGs can use an underlying RNG, entropy sources or both for reseeding.
If they use the entropy sources they call the ``poll()`` method of the
available and configured sources:

.. code-block:: C++

   size_t Entropy_Sources::poll (RandomNumberGenerator& rng, size_t
   poll_bits, std::chrono::milliseconds timeout)

All sources that are configured in the ``Entropy_Sources`` object are
polled until ``poll_bits`` entropy bits are collected or the timeout is
reached. So, the order in which the Entropy Sources were added to the
``Entropy_Sources`` is important here. The collected bits are returned
after the poll is finished.
