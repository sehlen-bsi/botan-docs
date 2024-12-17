""""""
ML KEM
""""""

Analysed variants:

- ML-KEM-512
- ML-KEM-768
- ML-KEM-1024

For the analysis of ML KEM, a utility was written that calls the functions to be analyzed in a similar way to the Botan CLI.
The following call is used to perform the key encapsulation method:

.. code-block:: cpp

    auto sk = Botan::Kyber_PrivateKey(rng, mode);
    ...
    auto pk = Botan::Kyber_PublicKey(sk_bits, mode)

    ...

    Botan::AutoSeeded_RNG rng;
    auto encryptor = Botan::PK_KEM_Encryptor(pk, "HKDF(SHA-256)", "");
    encryptor.encrypt(ctxt, sym_key, rng, shared_secret_length);

    ...

    Botan::AutoSeeded_RNG rng;
    auto decryptor = Botan::PK_KEM_Decryptor(sk, rng, "HKDF(SHA-256)", "");
    sym_key = decryptor.decrypt(ctxt.data(), ctxt.size(), shared_secret_length);


The Botan library is configured using the following console prompt:

.. code-block::

    ./configure.py --prefix=~/workspace/bsi/DATA/cryptolib/botan/build --cc=gcc \
    --cc-bin=g++-12 --cc-abi=-fno-plt --disable-modules sm4 --disable-sse2      \
    --disable-ssse3 --disable-sse4.1 --disable-sse4.2 --disable-avx2            \
    --disable-bmi2 --disable-rdrand --disable-rdseed --disable-aes-ni           \
    --disable-sha-ni --disable-altivec --disable-neon --disable-armv8crypto     \
    --disable-powercrypto --without-os-feature=threads --with-debug-info

The binary is compiled with the `gcc` compiler with the following version:

.. code-block::

    $ g++-12 --version
    g++-12 (Debian 12.2.0-14) 12.2.0

The host operating system is `Debian GNU/Linux 12 (bookworm)`.


**Summary**

No critical leak was identified.
All leaks found by DATA are unproblematic.
The reasoning for each identified leak is explained below.

**Leak: Polynomial matrix.**

A data leak was found in the ``sample_matrix()`` function (:srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_algos.cpp:380|sample_matrix`) which generates the Kyber polynomial matrix.
The polynomial matrix is generated using the public key.
This is therefore merely a leak of the public key, which is not considered problematic.
No leaks were found during decryption with the private key.
