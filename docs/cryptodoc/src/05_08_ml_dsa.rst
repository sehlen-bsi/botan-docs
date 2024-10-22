.. _pubkey/ml_dsa:

ML-DSA
======

Botan implements the Module-Lattice-based Digital Signature Algorithm (ML-DSA)
in :srcref:`src/lib/pubkey/dilithium`. The implementation is based on
[FIPS-204]_. The list of supported algorithm parametres is listed in the table
:ref:`pubkey/ml_dsa/params`.

.. _pubkey/ml_dsa/params:

.. table:: Supported ML-DSA Parameter Sets (see Table 1 of [FIPS-204]_)

   +------------+-----------+-----------+---------------+-----------+--------------+-----------------+------------------+------------------+---------------+--------------+---------------+----------------+
   | Mode       | :math:`q` | :math:`n` | :math:`\zeta` | :math:`d` | :math:`\tau` | :math:`\lambda` | :math:`\gamma_1` | :math:`\gamma_2` | :math:`(k,l)` | :math:`\eta` | :math:`\beta` | :math:`\omega` |
   +============+===========+===========+===============+===========+==============+=================+==================+==================+===============+==============+===============+================+
   | ML-DSA-4x4 | 8380417   | 256       | 1753          | 13        | 39           | 128             | 2\ :sup:`17`     | :math:`(q-1)/88` | (4,4)         | 2            | 78            | 80             |
   +------------+-----------+-----------+---------------+-----------+--------------+-----------------+------------------+------------------+---------------+--------------+---------------+----------------+
   | ML-DSA-6x5 | 8380417   | 256       | 1753          | 13        | 49           | 192             | 2\ :sup:`19`     | :math:`(q-1)/32` | (6,5)         | 4            | 196           | 55             |
   +------------+-----------+-----------+---------------+-----------+--------------+-----------------+------------------+------------------+---------------+--------------+---------------+----------------+
   | ML-DSA-8x7 | 8380417   | 256       | 1753          | 13        | 60           | 256             | 2\ :sup:`19`     | :math:`(q-1)/32` | (8,7)         | 2            | 120           | 75             |
   +------------+-----------+-----------+---------------+-----------+--------------+-----------------+------------------+------------------+---------------+--------------+---------------+----------------+

The parameter sets claim a NIST security level of 2, 3, and 5 respectively.

.. _pubkey/ml_dsa/internals:

Algorithm Internals
-------------------

[FIPS-204]_ describes three primary operations: key generation, signing, and
verification.

Internally, those operations are further split into two functional layers:
the public-facing ML-DSA (Section 5), and ML-DSA-internal (Section 6). ML-DSA
and ML-DSA-internal decouple the actual high-level logic from the generation of
randomness. The functions in ML-DSA-internal receive pre-determined random bytes
as needed and are, therefore, fully deterministic.

ML-DSA is a Schnorr-like signature where the typically interactive protocol is
made non-interactive by pseudorandomly deriving the verifier's challenge from
the commitment and the message to be signed.

.. _pubkey/ml_dsa/components:

.. table:: ML-DSA Components and File Locations

   +-------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------+--------------------+
   | Component                                                                                                                                             | Purpose                                                        | [FIPS-204]_        |
   +=======================================================================================================================================================+================================================================+====================+
   | :ref:`Types <pubkey/ml_dsa/types>` (:srcref:`src <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_types.h>`)                                    | Strong Types                                                   | n/a                |
   +-------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------+--------------------+
   | :ref:`Constants <pubkey/ml_dsa/constants>` (:srcref:`src <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_constants.h>`)                        | Parameter set instantiation                                    | 4                  |
   +-------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------+--------------------+
   | :ref:`Polynomials <pubkey/ml_dsa/polynomials>` (:srcref:`src <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_polynomial.h>`)                   | Polynomials, Structures on Polynomials and Operations          | 7.5, 7.6           |
   +-------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------+--------------------+
   | :ref:`Algorithms <pubkey/ml_dsa/algorithms>` (:srcref:`src <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.h>`)                          | Encoding, Sampling, Key Expansion, Hint Generation, Rounding   | 7.1, 7.2, 7.3, 7.4 |
   +-------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------+--------------------+
   | :ref:`Symmetric Primitives <pubkey/ml_dsa/primitives>` (:srcref:`src <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_symmetric_primitives.h>`) | ML-DSA abstractions for PRFs, XOFs, Hashes, and KDFs           | 3.7                |
   +-------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------+--------------------+
   | :ref:`Internal Keys <pubkey/ml_dsa/keys>` (:srcref:`src <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_keys.h>`)                              | Internal key representation and serialization                  | n/a                |
   +-------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------+--------------------+
   | :ref:`ML-DSA Implementation <pubkey/ml_dsa/ml_dsa_impl>` (:srcref:`src <[src/lib/pubkey/dilithium/ml_dsa]/ml_dsa_impl.h>`)                            | Functional disambiguation to (also provided) Dilithium         | 3.7, 6.2, 6.3, 7.2 |
   +-------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------+--------------------+
   | :ref:`ML-DSA <pubkey/ml_dsa/ml_dsa_api>` (:srcref:`src <[src/lib/pubkey/dilithium/dilithium_common]/dilithium.h>`)                                    | Public ML-DSA API                                              | 5                  |
   +-------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------+--------------------+

.. _pubkey/ml_dsa/types:

Strong Types
^^^^^^^^^^^^

ML-DSA uses strong types and type aliases to represent the various value
types involved in the algorithm. This approach binds the semantic meaning of
values to their types, resulting in a more robust interface and self-documenting
code. Type aliases are defined for ML-DSA polynomials, polynomial vectors, and
polynomial matrices, as well as their NTT representations. All bitstrings,
including various hash values, random seeds, and others, are encapsulated as
strong types.

.. _pubkey/ml_dsa/constants:

Paramter Instantiations
^^^^^^^^^^^^^^^^^^^^^^^

Botan's ``DilithiumConstants`` class contains all parameters and constants
outlined in Section 4 of [FIPS-204]_ (see :ref:`pubkey/ml_dsa/params`).
Additionally, the class contains parameters implicitly derived from these
constants, such as key and ciphertext sizes, along with various intermediate
value sizes required within internal algorithms.

Also, this class contains the theoretical XOF-bounds outlined in Appendix C of
[FIPS-204]_ used as a guard rail for the various rejection sampling operations
within the ML-DSA implementation.

.. _pubkey/ml_dsa/polynomials:

Polynomial Operations
^^^^^^^^^^^^^^^^^^^^^

ML-DSA relies extensively on polynomials within the polynomial ring :math:`R_q`,
utilizing vectors and matrices of polynomials, both inside and outside the NTT
domain. Botan uses :ref:`strong types <pubkey/ml_dsa/types>` to distinguish
polynomials and polynomial vectors as ``DilithiumPoly`` and
``DilithiumPolyVec``, as well as their NTT counterparts ``DilithiumPolyNTT`` and
``DilithiumPolyVecNTT``. Matrices only appear in the NTT domain and are
represented by the class ``DilithiumPolyMatNTT``.

ML-KEM, as defined in [FIPS-202]_, also employs polynomials, leading to shared
polynomial logic between the two algorithms. This shared logic is located in
:srcref:`[src/lib/pubkey]/pqcrystals/pqcrystals.h`, encompassing common
operations on vectors and matrices, as well as algorithm-independent operations
like polynomial addition and subtraction. The ML-DSA specific logic implemented
in :srcref:`[src/lib/pubkey/dilithium/dilithium_common]/dilithium_polynomial.h`
supplements this construction by including the NTT (Algorithm 41 of [FIPS-204]_)
and inverse NTT (Algorithm 42 of [FIPS-204]_) operations, along with NTT
polynomial multiplication (Algorithms 45 [FIPS-204]_).

Due to this type-based construction, the C++ compiler can detect specific
implementation issues statically. For instance, the polynomial
multiplication operation is only defined for the ``PolyVecNTT`` type. Misuse
would result in a compile-time error.

Botan utilizes Montgomery as well as Barrett reduction and conditional addition
of :math:`q`, for modular reduction and handling of negative values, depending
on the expected result range of certain operations. Those operations are
explicitly applied in the implementation as needed.

.. _pubkey/ml_dsa/algorithms:

Internal Algorithms
^^^^^^^^^^^^^^^^^^^

The ``Dilithium_Algos`` namespace includes a variety of internal functions to
support the primary algorithm. Table :ref:`pubkey/ml_dsa/algos` offers a summary
of those functions that are exposed to the rest of the implementation. The
:srcref:`[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp`
contains additional functions that are used within this module only, such as the
encoding functionality from [FIPS-204]_ Section 7.1.

.. _pubkey/ml_dsa/algos:

.. table:: ML-DSA Algorithms Overview

   +---------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+-------------+
   | Function                                                                                                                              | Description                                                                                | [FIPS-204]_ |
   +=======================================================================================================================================+============================================================================================+=============+
   | :srcref:`encode_public_key <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp:327|encode_public_key>`                   | Byte encoding of a public key                                                              | 7.2 A. 22   |
   +---------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+-------------+
   | :srcref:`decode_public_key <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp:345|decode_public_key>`                   | Decoding a public key from bytes                                                           | 7.2 A. 23   |
   +---------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+-------------+
   | :srcref:`encode_keypair <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp:368|encode_keypair>` [#dilithium_comp]_      | Byte encoding of a private key                                                             | 7.2 A. 24   |
   +---------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+-------------+
   | :srcref:`decode_keypair <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp:409|decode_keypair>` [#dilithium_comp]_      | Decoding a private key from bytes                                                          | 7.2 A. 25   |
   +---------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+-------------+
   | :srcref:`encode_signature <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp:474|encode_signature>`                     | Byte encoding of a signature                                                               | 7.2 A. 26   |
   +---------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+-------------+
   | :srcref:`decode_signature <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp:493|decode_signature>`                     | Decoding a signature from bytes                                                            | 7.2 A. 27   |
   +---------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+-------------+
   | :srcref:`encode_commitment <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp:518|encode_commitment>`                   | Byte encoding of a commitment                                                              | 7.2 A. 28   |
   +---------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+-------------+
   | :srcref:`sample_in_ball <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp:532|sample_in_ball>`                         | Sample a challenge from the commitment hash                                                | 7.3 A. 29   |
   +---------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+-------------+
   | :srcref:`expand_keypair <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp:665|expand_keypair>`                         | Expand a private key from a seed :math:`\xi`                                               | 6.1 A. 6    |
   +---------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+-------------+
   | :srcref:`expand_A <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp:695|expand_A>`                                     | Expand matrix :math:`A` from a seed :math:`\rho`                                           | 7.3 A. 32   |
   +---------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+-------------+
   | :srcref:`expand_s <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp:708|expand_s>`                                     | Expand vectors :math:`s1` and :math:`s2` from a seed :math:`\rho`                          | 7.3 A. 33   |
   +---------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+-------------+
   | :srcref:`expand_mask <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp:728|expand_mask>`                               | Samples a vector :math:`y` from a seed :math:`\rho'` and a nonce :math:`\kappa`            | 7.3 A. 34   |
   +---------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+-------------+
   | :srcref:`decompose <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp:819|decompose>`                                   | Decompose coefficients in a vector :math:`w` into high and low bits                        | 7.4 A. 36   |
   +---------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+-------------+
   | :srcref:`make_hint <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp:843|make_hint>`                                   | Allows the signer to compress the signature                                                | 7.4 A. 39   |
   +---------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+-------------+
   | :srcref:`use_hint <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp:918|use_hint>`                                     | Lets the verifier decompress the signature                                                 | 7.4 A. 40   |
   +---------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+-------------+
   | :srcref:`infinity_norm_within_bound <[src/lib/pubkey/dilithium/dilithium_common]/dilithium_algos.cpp:936|infinity_norm_within_bound>` | Given vector :math:`v` and :math:`bound`, validates that :math:`\|v\|_{\infty} \geq bound` | n/a         |
   +---------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+-------------+

.. [#dilithium_comp] The private key encoding and decoding functions are used
   for the legacy support of Dilithium (round 3) only. Botan's ML-DSA
   implementation exclusively store its private keys as the secret seed
   :math:`\xi`.

.. _pubkey/ml_dsa/primitives:

Symmetric Primitives
^^^^^^^^^^^^^^^^^^^^

This module provides an interface to the symmetric primitives required to
implement ML-DSA: namely XOFs, hash functions and KDFs.

To allow sharing significant portions of the ML-DSA implementation with the
pre-standard Dilithium and Dilithium-AES algorithms that Botan currently keeps
supporting, these primitives are accessible via the polymorphic base classes
:srcref:`Dilithium_Symmetric_Primitives_Base
<src/lib/pubkey/dilithium/dilithium_common/dilithium_symmetric_primitives.h:101|Dilithium_Symmetric_Primitives_Base>`,
:srcref:`DilithiumXOF
<src/lib/pubkey/dilithium/dilithium_common/dilithium_symmetric_primitives.h:89|DilithiumXOF>`,
and :srcref:`DilithiumMessageHash
<src/lib/pubkey/dilithium/dilithium_common/dilithium_symmetric_primitives.h:31|DilithiumMessageHash>`.

The concrete implementations relevant for ML-DSA may
be found in :srcref:`[src/lib/pubkey/dilithium]/ml_dsa/ml_dsa_impl.h` and
:srcref:`[src/lib/pubkey/dilithium/dilithium_common/dilithium_shake]/dilithium_shake_xof.h`.

.. _pubkey/ml_dsa/keys:

Internal Key Representation
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :srcref:`Dilithium_PublicKeyInternal
<src/lib/pubkey/dilithium/dilithium_common/dilithium_keys.h:33|Dilithium_PublicKeyInternal>`
and :srcref:`Dilithium_PrivateKeyInternal
<src/lib/pubkey/dilithium/dilithium_common/dilithium_keys.h:68|Dilithium_PrivateKeyInternal>`
classes are the internal representation of the ML-DSA key pair in expandedd form.

Additionally, the :srcref:`Dilithium_Keypair_Codec
<src/lib/pubkey/dilithium/dilithium_common/dilithium_keys.h:23|Dilithium_Keypair_Codec>`
serves as a customization point for the key encoding and decoding functions that
differ between ML-DSA (:math:`\xi` only) and Dilithium (round 3) (partially
expanded key format as specified in [FIPS-204]_). By *always* expanding the
private key from the secret seed :math:`\xi`, sanity checks during decoding of
the key pair can be omitted.

.. _pubkey/ml_dsa/ml_dsa_impl:

ML-DSA Specifics
^^^^^^^^^^^^^^^^

This module provides concrete ML-DSA specific implementations for the
customization points outlined in :ref:`pubkey/ml_dsa/primitives` and
:ref:`pubkey/ml_dsa/keys`. Namely:

  * :srcref:`ML_DSA_Expanding_Keypair_Codec <src/lib/pubkey/dilithium/ml_dsa/ml_dsa_impl.h:21|ML_DSA_Expanding_Keypair_Codec>`
    Implements encoding and decoding of ML-DSA private keys by serializing the
    private seed :math:`\xi` and/or expanding the deserialized seed into the
    private key representation outlined in :ref:`pubkey/ml_dsa/keys`.
  * :srcref:`ML_DSA_MessageHash <src/lib/pubkey/dilithium/ml_dsa/ml_dsa_impl.h:28|ML_DSA_MessageHash>`
    Implements the transformation of the user-provided message :math:`M` into
    the message representation :math:`\mu`. This includes the incorporation of
    the domain separations outlined in [FIPS-204]_ Sectoin 5.2 Algorithm 2.
  * :srcref:`ML_DSA_Symmetric_Primitives
    <src/lib/pubkey/dilithium/ml_dsa/ml_dsa_impl.h:54|ML_DSA_Symmetric_Primitives>`
    Implements the ML-DSA specific symmetric primitives based on the specified
    SHAKE-based XOFs, the optional hedged randomization of :math:`H(K \| rnd \| \mu)`,
    and the domain separator for expanding :math:`\rho`, :math:`\rho'`, and
    :math:`K` from the private seed :math:`\xi`.

.. _pubkey/ml_dsa/ml_dsa_api:

Public API
^^^^^^^^^^

The :srcref:`Dilithium_PublicKey
<src/lib/pubkey/dilithium/dilithium_common/dilithium.h:67|Dilithium_PublicKey>`
and :srcref:`Dilithium_PrivateKey
<src/lib/pubkey/dilithium/dilithium_common/dilithium.h:115|Dilithium_PrivateKey>`
classes serve as Botan's public API for public and private ML-DSA keys,
respectively. The :srcref:`DilithiumMode
<src/lib/pubkey/dilithium/dilithium_common/dilithium.h:21|DilithiumMode>` class
is used to select the desired parameter set.

New applications that do not rely on the pre-standard Dilithium round 3
implementations are strongly advised to use the type aliases for ML-DSA defined
in :srcref:`[src/lib/pubkey/dilithium/ml_dsa]/ml_dsa.h`.


.. _pubkey/ml_dsa/kyber_compat:

Dilithium Compatibility
-----------------------

The final ML-DSA standard is not compatible with the round 3 submission of
Dilithium. Botan did provide support for Dilithium and Dilithium-AES as
specified in [Dilithium-R3]_ since April 2023. This support is still available
and can be activated by enabling the ``dilithium`` or ``dilithium_aes`` modules.

Note that Dilithium-AES is already deprecated, and both Dilithium and
Dilithium-AES may be removed as early as the next major release of the library.
It is not advisable to use any other variant than the ones specified in
[FIPS-204]_.

.. _pubkey/ml_dsa/keygen:

Key Generation
--------------

Generating a fresh ML-DSA key pair as specified in [FIPS-204]_ Section 5.1
Algorithm 1, is available in the constructor of :srcref:`Dilithium_PrivateKey
<src/lib/pubkey/dilithium/dilithium_common/dilithium.cpp:403|Dilithium_PrivateKey>`.
This mostly delegates the actual key generation to the internal function
:srcref:`expand_keypair
<src/lib/pubkey/dilithium/dilithium_common/dilithium_algos.cpp:665|expand_keypair>`
that follows [FIPS-204]_ Section 6.1 Algorithm 6.

.. admonition:: Dilithium_PrivateKey::Dilithium_PrivateKey / Dilithium_Algos::expand_keypair

   **Input:**

   - ``rng``: random number generator
   - ``mode``: ML-DSA parameter set descriptor

   **Output:**

   - ``sk``: private signing key
   - ``pk``: public verification key

   **Steps:**

   1. Generate a random 32-byte seed :math:`\xi` using ``rng``
   2. :math:`(\rho, \rho', K) = H(\xi)` (32, 64, and 32 bytes respectively)
   3. Sample matrix :math:`\hat{A}` from :math:`\rho` using ``expand_A``
   4. Sample vectors :math:`s_1` and :math:`s_2` from :math:`\rho'` using ``expand_s``
   5. Calculate :math:`(t_1, t_0)` from :math:`\hat{A}`, :math:`s_1`, and :math:`s_2` using ``compute_t1_and_t0`` (see :srcref:`here <src/lib/pubkey/dilithium/dilithium_common/dilithium_algos.cpp:310|compute_t1_and_t0>`)

      1. :math:`t = NTT^{-1}(\hat{A} \cdot NTT(s_1)) + s_2`
      2. :math:`(t_1, t_0) = power2round(t)` (see :srcref:`here <src/lib/pubkey/dilithium/dilithium_common/dilithium_algos.cpp:746|power2round>`)

   6. :math:`pk = (\rho, t_1)` and :math:`sk = (\xi, K, s_1, s_2, t_0)`

   **Notes:**

   - Step 1 corresponds to [FIPS-204]_ Algorithm 1
   - Steps 2-5 correspond to [FIPS-204]_ Algorithm 6
   - Step 6 returns the key pair in Botan's internal representation. The
     encoding and hashing of the encoded public key are done later and on
     demand.


.. _pubkey/ml_dsa/signing:

Signing
-------

Signature generation as specified in [FIPS-204]_ Algorithms 2 and 7 are
implemented in :srcref:`Dilithium_Signature_Operation::sign
<src/lib/pubkey/dilithium/dilithium_common/dilithium.cpp:153|sign>` with the
preparation of the message representative :math:`\mu` being done in
:srcref:`DilithiumMessageHash
<src/lib/pubkey/dilithium/dilithium_common/dilithium_symmetric_primitives.h:31|DilithiumMessageHash>`.

.. admonition:: Dilithium_Signature_Operation::sign

   **Input:**

   - ``sk``: private signing key, with :math:`\hat{A}` and :math:`\hat{s_1}`, :math:`\hat{s_2}`, and :math:`\hat{t_0}` in NTT domain
   - ``M``: message to be signed

   **Output:**

   - ``signature``: the valid signature

   **Steps:**

   1. Calculate the message representative :math:`\mu = H(sk.tr \| 0x00 \| 0x00 \| M)` (see :srcref:`here <src/lib/pubkey/dilithium/ml_dsa/ml_dsa_impl.h:36|start>`)
   2. :math:`\rho' = H(sk.K \| rnd \| \mu)` (see :srcref:`here <src/lib/pubkey/dilithium/ml_dsa/ml_dsa_impl.h:68|H_maybe_randomized>`)
   3. Run the rejection sampling loop (incrementing the nonce :math:`\kappa` by :math:`l` in each iteration)

      1. Expand :math:`y` from :math:`\rho'` and :math:`\kappa` using ``expand_mask``
      2. :math:`\hat{w} = \hat{A} \cdot NTT(y)`
      3. :math:`w = NTT^{-1}(\hat{w})`
      4. :math:`(w_1, w_0) = decompose(w)`
      5. :math:`\tilde{c} = H(\mu \| w_1)` (:math:`w_1` is encoded using ``encode_commitment``)
      6. :math:`\hat{c} = NTT(sample\_in\_ball(\tilde{c}))`
      7. :math:`cs_1 = NTT^{-1}(\hat{c} \cdot sk.\hat{s_1})`
      8. :math:`z = y + cs_1`
      9. *Retry* iff :math:`\|z\|_{\infty} \geq \gamma_1 - \beta` (see ``infinity_norm_within_bound``)
      10. :math:`cs_2 = NTT^{-1}(\hat{c} \cdot sk.\hat{s_2})`
      11. :math:`r_0 = w_0 - cs_2`
      12. *Retry* iff :math:`\|r_0\|_{\infty} \geq \gamma_2 - \beta` (see ``infinity_norm_within_bound``))
      13. :math:`ct_0 = NTT^{-1}(\hat{c} \cdot sk.\hat{t_0})`
      14. *Retry* iff :math:`\|c\|_{\infty} \geq \gamma_2` (see ``infinity_norm_within_bound``)
      15. :math:`h = make\_hint(r_0 + ct_0, w_1)`
      16. *Retry* if the Hamming weight of :math:`h > \omega`

   4. :math:`\sigma = (\tilde{c}, z, h)` encoded using ``encode_signature``

   **Notes:**

   - This algorithm description assumes that the private signing key is expanded
     into the internal representation already. Additionally, the expansion of
     :math:`\hat{A}`, as well as the NTT for :math:`s_1`, :math:`s_2`, and
     :math:`t_0` are done :srcref:`prior to the actual signing operation
     <src/lib/pubkey/dilithium/dilithium_common/dilithium.cpp:131|Dilithium_Signature_Operation>`
     to armortize the complexity of these operations across multiple consecutive
     signature generations.
   - Step 1: Botan 3.6.0 does not yet support the application-defined context
     string as specified in [FIPS-204]_ Algorithm 2. See `GitHub #4376
     <https://github.com/randombit/botan/issues/4376>`_.
   - Step 3.12: We calculate :math:`r_0 = w_0 - cs_2`, this is equivalent to
     :math:`r_0 = LowBits(w - cs_2)` as specified in [FIPS-204]_ Algorithm 7.
   - Step 3.15: We generate the hint from :math:`w_0 - cs_2 + ct_0` this is equivalent
     to the specification's :math:`w - cs_2 + ct_0`.

.. _pubkey/ml_dsa/verification:

Signature Verification
----------------------

Signature verification as specified in [FIPS-204]_ Algorithms 3 and 8 are
implemented in :srcref:`Dilithium_Verification_Operation::is_valid_signature
<src/lib/pubkey/dilithium/dilithium_common/dilithium.cpp:269|is_valid_signature>`
with the preparation of the message representative :math:`\mu` being done in
:srcref:`DilithiumMessageHash
<src/lib/pubkey/dilithium/dilithium_common/dilithium_symmetric_primitives.h:31|DilithiumMessageHash>`.

.. admonition:: Dilithium_Verification_Operation::is_valid_signature

   **Input:**

   - ``pk``: public verification key, with :math:`\hat{A}` and :math:`\hat{t_1'} = NTT(t_1 \cdot 2^{d})` in NTT domain
   - ``M``: message to be verified
   - ``signature``: the signature to be verified

   **Output:**

   - ``ok``: boolean value whether or not the signature is valid

   **Steps:**

   1. Calculate the message representative :math:`\mu = H(H(pk) \| 0x00 \| 0x00 \| M)` (see :srcref:`here <src/lib/pubkey/dilithium/ml_dsa/ml_dsa_impl.h:36|start>`)
   2. Decode the signature into :math:`(\tilde{c}, z, h)` using ``decode_signature``
   3. *Abort with "not valid"* if the Hamming weight of :math:`h > \omega`
   4. *Abort with "not valid"* if :math:`\|z\|_{\infty} \geq \gamma_1 - \beta` (see ``infinity_norm_within_bound``)
   5. :math:`\hat{c} = NTT(sample\_in\_ball(\tilde{c}))`
   6. :math:`w'_{approx} = \hat{A} \cdot NTT(z) - \hat{c} \cdot \hat{t_1'}`
   7. :math:`w_1' = use\_hint(w'_{approx}, h)`
   8. :math:`\tilde{c'} = H(\mu, w_1')` (:math:`w_1'` is encoded using ``encode_commitment``)
   9. Iff :math:`\tilde{c} = \tilde{c'}` *return "valid"*, else *"not valid"*

   **Notes:**

   - This algorithm description assumes that the public verification key is
     deserialized into the internal representation already. Additionally, the
     expansion of :math:`\hat{A}`, as well as the prepartion of
     :math:`\hat{t_1'} = NTT(t_1 \cdot 2^{d})` are done :srcref:`prior to the actual
     verification operation
     <src/lib/pubkey/dilithium/dilithium_common/dilithium.cpp:251|Dilithium_Verification_Operation>`
     to armortize the complexity of these operations across multiple consecutive
     signature verification.
