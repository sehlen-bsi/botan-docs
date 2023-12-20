""""""""
FrodoKEM
""""""""

Analysed variants:

- FrodoKEM 640 SHAKE
- FrodoKEM 976 SHAKE
- FrodoKEM 1344 SHAKE
- FrodoKEM 640 AES
- FrodoKEM 976 AES
- FrodoKEM 1344 AES
- eFrodoKEM 640 SHAKE
- eFrodoKEM 976 SHAKE
- eFrodoKEM 1344 SHAKE
- eFrodoKEM 640 AES
- eFrodoKEM 976 AES
- eFrodoKEM 1344 AES

For the analysis of FrodoKEM, a utility has been written that calls the functions to be analysed in a similar way to the Botan CLI.
The following call is used to create the signature:

.. code-block:: cpp

    const Botan::FrodoKEM_PrivateKey priv_key(rng, mode);

    [...]

    auto encryptor = Botan::PK_KEM_Encryptor(pub_key, "KDF2(SHA-256)", "");
    encryptor.encrypt(cipher_text, sym_key, rng, shared_secret_length);

    [...]

    auto decryptor = Botan::PK_KEM_Decryptor(priv_key, rng, "KDF2(SHA-256)", "");
    sym_key = decryptor.decrypt(cipher_text.data(), cipher_text.size(), shared_secret_length);

The Botan library is configured using the following console prompt:

.. code-block::

        ./configure.py --prefix=./build --cc=gcc
    --cc-bin=/home/wagner/workspace/tools/homebrew/Cellar/gcc@11/11.4.0/bin/g++-11      \
    --cc-abi=-fno-plt                                                                   \
    --disable-modules locking_allocator --disable-sse2 --disable-ssse3                  \
    --disable-sse4.1 --disable-sse4.2 --disable-avx2 --disable-bmi2 --disable-rdrand    \
    --disable-rdseed --disable-aes-ni --disable-sha-ni --disable-altivec                \
    --disable-neon --disable-armv8crypto --disable-powercrypto                          \
    --without-os-feature=threads --build-targets=static,cli

The binary is compiled with the `gcc` compiler with the following version:

.. code-block::

    $ g++-11 --version
    g++-11 (Homebrew GCC 11.4.0) 11.4.0

The host operating system is `Ubuntu 20.04.6 LTS`.

**Analysis with DATA**

No differences were found by DATA for any of the variants analysed.
Therefore, only phase one of DATA was performed and no further analysis with DATA was necessary.

**Attacking the FO transformation**

In 2020, Guo et al. published a key recovery timing attack against any cryptographic primitive using the Fujisaki-Okamoto (FO) transformation [FRODOKEM_SCA]_.
During the FO transformation, the decoded ciphertext is re-encoded and compared against the received ciphertext.
The key recovery timing attack targets the comparison operation.
If it is not performed in constant time, an attacker can use it as a decryption error oracle.
In the case of the reference implementation of FrodoKEM, the comparison was performed with an unprotected memcmp routine [FRODOKEM_REF_IMPL_FIX_SCA]_.
Therefore it was vulnerable to this attack.
In Botan this is implemented in constant time [FRODOKEM_BOTAN_FIX_SCA]_.

**Constant time sampling of the matrix A**

To reduce the memory footprint, the matrix A is generated on the fly using a seed and a PRNG.
In the previously analysed LWE KEM algorithm Kyber, the sampling of the matrix showed differences within the execution.
This is not the case with FrodoKEM.
The reason for this is the choice of modulus value.
For Kyber the modulus must be a prime number.
For FrodoKEM the modulus has to be a power of two.
In the case of a prime modulus, a rejection-based approach must be used for the matrix A to maintain a uniform distribution.
In the other case of a modulus of a power of two, a modulo operation can be applied to the values returned by the PRNG.
The nature of the power of two modulus maintains a uniform distribution throughout the modulo operation.
Therefore no differences are detected within the FrodoKEM execution during this operation.

**Constant time sampling of the error distribution**

A Gaussian-derived distribution is required for the error distribution.
This is achieved by using inversion sampling with different pre-computed tables.
Since table lookups would lead to execution differences, constant time alternatives are required.
The small table size allows the implementation of a constant time alternative which has a negligible performance overhead.
The FrodoKEM implementation reference and the FrodoKEM implementation in Botan contain such constant time table lookup alternative implementations.
