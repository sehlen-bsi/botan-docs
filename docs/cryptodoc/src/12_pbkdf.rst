Password Based Key Derivation Functions
=======================================

Argon2 (RFC 9106)
-----------------

Argon2 is a memory-hard function for password hashing.
The implementation in Botan can be found in :srcref:`src/lib/pbkdf/argon2/argon2.cpp`
and follows the standard [RFC9106]_.

The maximum parallelism in Botan is more restricted than specified in [RFC9106]_.
Botan allows a maximum of 128 threads.

The maximum memory size in Botan is more restricted than specified in [RFC9106]_.
Botan allows a maximum of :math:`2^{23}` KiB.

The default parameter choice and tuning of parameters does not follow [RFC9106]_.
Instead a less secure default is used for the default values.
Used parameters should be selected by an expert for the specific use case
instead of relying on Botan's default values.
