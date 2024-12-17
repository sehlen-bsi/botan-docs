""""""
ML-DSA
""""""

Analysed variants:

- ML-DSA-44
- ML-DSA-65
- ML-DSA-87

For the analysis of ML-DSA, a utility was written that calls the functions to be analyzed in a similar way to the Botan CLI.
The following call is used to create the signature:

.. code-block:: cpp

    auto sk = Botan::Dilithium_PrivateKey(rng, mode);

    Botan::PK_Signer sig(sk, rng, "Deterministic");
    signature = sig.sign_message(message, rng);


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


**Leak: Hints**

In the analysis with DATA, leaks were detected in the functions `make_hint()` (:srcref:`[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp:843|make_hint`),
and `hint_pack()` (:srcref:`[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp:232|hint_pack`).
The leakage observation is due to a combination of the measurement method of DATA and the rejection method of ML-DSA.
The rejection method leads to a changed pointer base address which is detected by DATA.
Hence, the leaks of the hints are not considered problematic.

**Leak: SampleInBall**

Leaks were identified in the function `sample_in_ball()` during the generation of *c_tilde* (:srcref:`[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp:532|sample_in_ball`).
The function corresponds in the pseudocode to the function `SampleInBall()` in line 18.
*c_tilde* is added to the signature, is therefore publicly known and allows the `SampleInBall()` function to be executed during verification.
For this reason, the leaks found during the generation of *c_tilde* can be classified as unproblematic.


**Leak: Infinity norm within bound**

Leaks were identified for the function `infinity_norm_within_bound()` (:srcref:`src/lib/pubkey/dilithium/dilithium_common/dilithium_algos.cpp:936|infinity_norm_within_bound`).
The function `infinity_norm_within_bound()` iterates over each polynomial and checks whether the infinity norm of the given polynomial is strictly smaller than the specified limit value.
DATA has detected a control flow leak for the following condition:

.. code-block:: cpp

  if(!Dilithium_Algos::infinity_norm_within_bound(r0, to_underlying(mode.gamma2()) - mode.beta())) {
    continue;
  }


This condition can be found in line 21 of the pseudo code and is part of the `sign()` function in Botan (:srcref:`src/lib/pubkey/dilithium/dilithium_common/dilithium_algos.cpp:936|infinity_norm_within_bound`).
If the condition is met, the generated signature is discarded and the process starts again.
The leaks found can make it possible for attackers to gain knowledge of which of the polynomials will cause the signature to be discarded.
According to the state-of-the-art, this knowledge does not enable an attack on the private key or the message to be signed.

To check the infinity norm, the absolute value of each term is compared with the bound value in the implementation.
The reference implementation of CRYSTALS-Dilithium [DILITHIUM_REFERENCE_IMPLEMENTATION]_ states that the element that fulfills this condition and thus leads to the rejection of a signature can leak, but not the sign of the element:

.. code-block:: c

  /* It is ok to leak which coefficient violates the bound since
     the probability for each coefficient is independent of secret
     data but we must not leak the sign of the centralized representative. */
  for(i = 0; i < N; ++i) {
    /* Absolute value */
    t = a->coeffs[i] >> 31;
    t = a->coeffs[i] - (t & 2*a->coeffs[i]);

The current implementation in the function `infinity_norm_within_bound()` in Botan fulfills this requirement.
The sign is not leaked, as the following code snippet shows.

.. code-block:: cpp

  bool infinity_norm_within_bound(const DilithiumPolyVec& vec, size_t bound) {
    BOTAN_DEBUG_ASSERT(bound <= (DilithiumConstants::Q - 1) / 8);

    // It is ok to leak which coefficient violates the bound as the probability
    // for each coefficient is independent of secret data but we must not leak
    // the sign of the centralized representative.
    for(const auto& p : vec) {
      for(auto c : p) {
        const auto abs_c = c - is_negative_mask(c).if_set_return(2 * c);
        if(CT::driveby_unpoison(abs_c >= bound)) {
          return false;
        }
      }
    }

    return true;
  }

For these reasons, the leaks can be categorized as unproblematic.
