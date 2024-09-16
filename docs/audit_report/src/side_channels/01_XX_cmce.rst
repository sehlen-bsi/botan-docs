""""
Classic McEliece
""""

Analysed variants:

- 348864
- 348864f

For the analysis of Classic McEliece (CMCE), a utility program has been written that calls the functions to be analyzed in a similar way to the Botan CLI.
The following call is used to obtain the encapsulation and decapsulation outputs:

.. code-block:: cpp

    const Botan::Classic_McEliece_PrivateKey priv_key(rng, params);

    [...]

    auto encryptor = Botan::PK_KEM_Encryptor(priv_key, "Raw", "base");
    encryptor.encrypt(cipher_text, sym_key, rng, shared_secret_length);

    [...]

    auto decryptor = Botan::PK_KEM_Decryptor(priv_key, rng, "Raw");
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

In the first evaluation runs DATA identified leakage points within the routines used for key pair generation, encryption and decryption.
Based on these results, the PRNG instantiated in the utility program was modified to isolate the cause of the observed leakage points.
The modifications comprised seeding the PRNG with a constant and a key-unique seed.
The constant seed resulted in no differences within the execution.
In contrast, the key-unique seed resulted in a clear distinction of the execution traces between the used key material.

The leakage occurs at the same lines of code for all three routines (key pair generation, encryption, decryption) within the CMCE Botan implementation.
In the following we describe the cause of the leakage and the criticality in relation to the decryption routine.
Please note that this also applies to the key pair generation and encryption routine but is omitted here as the information would be redundant.

The leakage was observed in the `decode()` routine which is part of the `Classic_McEliece_Decryptor`.
The function definition is in the file `cmce_decaps.cpp` in file 84 to 119.
It is listed below:

.. code-block::

    std::pair<CT::Mask<uint8_t>, secure_bitvector> Classic_McEliece_Decryptor::decode(
       const Classic_McEliece_PrivateKeyInternal& sk, bitvector big_c) {
       BOTAN_ASSERT(big_c.size() == sk.params().m() * sk.params().t(), "Correct ciphertext input size");
       big_c.resize(sk.params().n());

       auto syndrome = compute_goppa_syndrome(
          sk.params(), sk.g(), sk.field_ordering(), big_c.as_locked());
       auto locator = berlekamp_massey(sk.params(), syndrome);

       std::vector<Classic_McEliece_GF> images;
       auto alphas = sk.field_ordering().alphas(sk.params().n());
       std::transform(
          alphas.begin(), alphas.end(), std::back_inserter(images), [&](const auto& alpha) { return locator(alpha); });

       // Obtain e and check whether wt(e) = t
       secure_bitvector e;
       size_t hamming_weight_e = 0;
       auto decode_success = CT::Mask<uint8_t>::set();  // Avoid bool to avoid compiler optimizations
       for(const auto& image : images) {
          auto is_zero_mask = CT::Mask<uint16_t>::is_zero(image.elem());
          e.push_back(is_zero_mask.as_bool());
          hamming_weight_e += is_zero_mask.if_set_return(1);
       }
       decode_success &= CT::Mask<uint8_t>(CT::Mask<size_t>::is_equal(hamming_weight_e, sk.params().t()));

       // Check the error vector
       auto syndrome_from_e = compute_goppa_syndrome(sk.params(), sk.g(), sk.field_ordering(), e);
       auto syndromes_are_eq = GF_Mask::set();
       for(size_t i = 0; i < syndrome.size(); ++i) {
          syndromes_are_eq &= GF_Mask::is_equal(syndrome.at(i), syndrome_from_e.at(i));
       }

       decode_success &= syndromes_are_eq.elem_mask();

       return {decode_success, std::move(e)};
    }

Within the `decode()` function the leakage was observed at code lines 102 to 106.
This is the part where the error vector `e` is obtained.
The identified leakage was due to an execution flow difference.
This execution flow difference stems from the code in the `bitvector.h` file at line 223.
It contains the following constant expression: A bit is set if the given bool is true.
The relevant line is listed below:

.. code-block::

         private:
            constexpr bitref& assign(bool bit) noexcept { return (bit) ? set() : unset(); }

When compiled, this line results in a conditional jump instruction in assembly code.
Depending on the boolean input value a different code branch is executed.
This expression is executed when assigning values to the elements of `e` at line 104:

.. code-block::

      e.push_back(is_zero_mask.as_bool());

The `push_back()` routine is contained in the file `bitvector.h` at lines 381 to 385 and is implemented as follows:

.. code-block::

      void push_back(bool bit) {
         const auto i = size();
         resize(i + 1);
         ref(i) = bit;
      }

The `=` operator at line 384 is implemented for the `bitvector` class at line 208 as:

.. code-block::

            constexpr bitref& operator=(bool bit) noexcept { return assign(bit); }

This results in a call of the `assign()` routine listed above.

The identified leakage would allow an adversary to potentially recover the error vector from the code execution, which is security critical.

**Countermeasure implementation and evaluation**

In the following, we propose a countermeasure, implement it and evaluate its effectiveness.
The underlying issue of the leakage is due to the branch of the `?` operator used in the `assign()` routine.
This must be avoided, e.g., by performing the set and unset operations regardless of the input value.
As only one of the two operations is needed at a time, the other operation has to be ineffective.
Below is a proposal for such a countermeasure:

.. code-block::

         private:
            constexpr bitref& assign(bool bit) noexcept {
                const block_type assign_mask = 0 - static_cast<block_type>(bit);
                this->m_block \|=  (this->m_mask &  assign_mask);
                this->m_block &= ~(this->m_mask & ~assign_mask);
                return \*this;
            }

The input bool `bit` is casted as an `uint8_t` datatype and is used to generate a mask.
This mask is used to implement the behavior that only one operation is effective at a time.
When compiled, this results in the following instructions - without any conditional branch based on the input:

.. code-block::

  [ ... ]
                                           const block_type assign_mask = 0 - static_cast<block_type>(bit);
  41d397: 41 f7 dc                   neg %r12d
  [ ... ]
                                           this->m_block \|= (this->m_mask & assign_mask);
  41d3ab: 44 89 e1                   mov %r12d,%ecx
  41d3ae: 21 c1                      and %eax,%ecx
                                           this->m_block &= ~(this->m_mask & ~assign_mask);
  41d3b0: f7 d0                      not %eax
                                           this->m_block \|= (this->m_mask & assign_mask);
  41d3b2: 0a 0a                      or (%rdx),%cl
                                           this->m_block &= ~(this->m_mask & ~assign_mask);
  41d3b4: 44 09 e0                   or %r12d,%eax
  41d3b7: 21 c8                      and %ecx,%eax
  [ ... ]
