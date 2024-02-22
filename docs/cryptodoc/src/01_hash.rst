Hash Functions
==============

The BSI documents [TR-02102-1]_ [TR-02102-2]_ recommend usage of SHA-2 and SHA-3
algorithms in cryptographic software.
In addition, SHA-1 is required in Botan for TLS,
as the ``x509`` Botan module still requires SHA-1.
Note that SHA-1 is not recommended to be used any longer.

SHA-1 and SHA-2 hash functions rely on the Merkle-Damgard construction.
The general functionality of this construction is implemented in class
``MerkleDamgard_Hash`` (located in :srcref:`src/lib/hash/mdx_hash/mdx_hash.h`).
This class handles splitting data into appropriate blocks and invocation
of hash compression methods.

SHA-1
-----

Botan provides four SHA-1 implementations: software, SSE2 (Streaming
SIMD Extensions 2), x86 (Intel SHA Extensions) and ARMv8 (ARMv8
Cryptography Extensions). The description of SHA-1 is provided in
[NIST-SHS]_.

The software implementation is located
in :srcref:`src/lib/hash/sha1/sha1.cpp`. It uses the Botan structure
``secure_vector`` to implement data handling and compressions.

The SSE2 implementation is in :srcref:`src/lib/hash/sha1/sha1_sse2/sha1_sse2.cpp`.
It is based on the code by Dean Gaudet [#sha1_dean]_.

The ARMv8 implementation is in
:srcref:`src/lib/hash/sha1/sha1_armv8/sha1_armv8.cpp`. The x86 implementation is
in :srcref:`src/lib/hash/sha1/sha1_x86/sha1_x86.cpp`. Both are based on the
code by Jeffrey Walton [#sha_intrinsics]_.

.. [#sha1_dean]
   http://arctic.org/~dean/crypto/sha1.html

.. [#sha_intrinsics]
   https://github.com/noloader/SHA-Intrinsics

SHA-2
-----

Botan provides four SHA-2 implementations: software, BMI2 (Bit
Manipulation Instruction Set 2), x86 (Intel SHA Extensions) and ARMv8
(ARMv8 Cryptography Extensions). The description of SHA-2 is provided in
[NIST-SHS]_.

The software implementations are located in
:srcref:`src/lib/hash/sha2_64/sha2_64.cpp` and in
:srcref:`src/lib/hash/sha2_32/sha2_32.cpp`. ``sha2_32.cpp`` implements the SHA-224
and SHA-256 hash functions. ``sha2_64.cpp`` implements SHA-384 and
SHA-512.

The BMI2 implementations are located in
:srcref:`src/lib/hash/sha2_64/sha2_64_bmi2/sha2_64_bmi2.cpp` and in
:srcref:`src/lib/hash/sha2_32/sha2_32_bmi2/sha2_32_bmi2.cpp`.
``sha2_32_bmi2.cpp`` implements the SHA-224 and SHA-256 hash functions.
``sha2_64_bmi2.cpp`` implements SHA-384 and SHA-512.

The ARMv8 implementation is in
:srcref:`src/lib/hash/sha2_32/sha2_32_armv8/sha2_32_armv8.cpp`. The x86
implementation is in :srcref:`src/lib/hash/sha2_32/sha2_32_x86/sha2_32_x86.cpp`.
Both are based on the code by Jeffrey Walton [#sha_intrinsics]_.

SHA-3
-----

SHA-3 does not rely on a Merkle-Damgard construction, as it uses a sponge
construction to perform data compression. Botan provides two implementations of
the Keccak sponge construction: software and BMI2 (Bit Manipulation Instruction
Set 2).

The software implementation is located in
:srcref:`src/lib/permutations/keccak_perm/keccak_perm.cpp`. The BMI2
implementation is located in
:srcref:`src/lib/permutations/keccak_perm/keccak_perm_bmi2/keccak_perm_bmi2.cpp`.

Based on the generic Keccak construction Botan implements SHA-3 as defined in
[FIPS-202]_ and thus supports output lengths of 224, 256, 384 and 512 bits. The
SHA-3 parameterization is implemented in :srcref:`src/lib/hash/sha3/sha3.cpp`.

SHAKE
-----

Botan implements the two Keccak-based XOFs SHAKE128 and SHAKE256 in
:srcref:`src/lib/hash/shake/shake.cpp` as defined in [FIPS-202]_. It
utilizes the Keccak sponge construction methods also used in the SHA-3
implementation using a padding that is specific to SHAKE. In contrast to SHA-3
it allows arbitrary output lengths which are provided to the constructor
of the class.

As of version 3.2.0, Botan additionally provides SHAKE using a first-class XOF
API that resides in :srcref:`src/lib/xof/shake_xof/shake_xof.cpp`.

BLAKE2b
-------

Botan implements the hash function BLAKE2b as defined in [RFC7693]_.
The implementation is located in :srcref:`src/lib/hash/blake2/blake2b.cpp`.

As defined in [RFC7693]_ Botan's BLAKE2b implementation allows for an arbitrary
number of up to 64 output bytes with the respective security implications.
Also, it contains an interface to initialize the hash function with a secret
key. As described in [RFC7693]_, the key can have an arbitrary size of up to 64
bytes. It is padded and set as the first input block of the hash function.

BLAKE2s
-------

Botan implements the hash function BLAKE2s as defined in [RFC7693]_.
The implementation is located in :srcref:`src/lib/hash/blake2s/blake2s.cpp`.

As defined in [RFC7693]_ Botan's BLAKE2s implementation allows for an arbitrary
number of up to 32 output bytes with the respective security implications.
In contrast to BLAKE2b, it does not contain an interface to initialize the hash
function with a secret key.
