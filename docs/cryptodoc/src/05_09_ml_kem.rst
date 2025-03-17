.. _pubkey/kyber:

ML-KEM
======

Botan implements the Module-Lattice-Based Key-Encapsulation Mechanism Standard
(ML-KEM) in :srcref:`src/lib/pubkey/kyber/`. The implementation is based on
[FIPS-203]_. The list of supported algorithms and their parameters is depicted
in Table
:ref:`Supported ML-KEM parameter sets <pubkey_key_generation/kyber/table_params>`.

.. _pubkey_key_generation/kyber/table_params:

.. table::  Supported ML-KEM parameter sets (see Table 2 of [FIPS-203]_)

   +-------------------+-----------+-----------+-----------+----------------+----------------+-------------+-------------+
   |  Mode             | :math:`n` | :math:`q` | :math:`k` | :math:`\eta_1` | :math:`\eta_2` | :math:`d_u` | :math:`d_v` |
   +===================+===========+===========+===========+================+================+=============+=============+
   | ML-KEM-512        | 256       | 3329      | 2         | 3              | 2              | 10          | 4           |
   +-------------------+-----------+-----------+-----------+----------------+----------------+-------------+-------------+
   | ML-KEM-768        | 256       | 3329      | 3         | 2              | 2              | 10          | 4           |
   +-------------------+-----------+-----------+-----------+----------------+----------------+-------------+-------------+
   | ML-KEM-1024       | 256       | 3329      | 4         | 2              | 2              | 11          | 5           |
   +-------------------+-----------+-----------+-----------+----------------+----------------+-------------+-------------+

BSI's [TR-02102-1]_ recommends using either ML-KEM-768 or ML-KEM-1024 to meet
its desired security levels. Additionally, it recommends using all modes of
ML-KEM in a hybrid form in a suitable combination with a classical key agreement
mechanism such as RSA or ECDH.

.. _pubkey/kyber/internals:

Algorithm Internals
-------------------

Being a key encapsulation mechanism, [FIPS-203]_ defines three primary
operations: key generation, encapsulation, and decapsulation.

Internally, those operations are further split into three functional layers:
ML-KEM (Section 7), ML-KEM-internal (Section 6), and K-PKE (Section 5). ML-KEM
and ML-KEM-internal decouple the actual high-level logic from the generation of
randomness. ML-KEM-internal receives pre-determined random bytes and is,
therefore, fully deterministic. ML-KEM-internal applies a modified
Fujisaki-Okamoto transform to define an IND-CCA2 secure KEM based on the
internal IND-CPA secure key exchange algorithm K-PKE.

Table :ref:`ML-KEM components and file locations <pubkey/kyber/component_table>`
shows an overview of all ML-KEM components and their file locations.

.. _pubkey/kyber/component_table:

.. table::  ML-KEM components and file locations
   :widths: 15, 40, 32, 13

   +-----------------------------------------------------------+----------------------------------------------------------------------------+--------------------------------------------------------------------+------------------------+
   | Component                                                 | Location                                                                   | Purpose                                                            | Section in [FIPS-203]_ |
   +===========================================================+============================================================================+====================================================================+========================+
   | :ref:`Types <pubkey/kyber/types>`                         | :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_types.h`                | Strong types                                                       | \-                     |
   +-----------------------------------------------------------+----------------------------------------------------------------------------+--------------------------------------------------------------------+------------------------+
   | :ref:`Constants <pubkey/kyber/constants>`                 | :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_constants.h`            | Parameter set instantiations                                       | 8                      |
   +-----------------------------------------------------------+----------------------------------------------------------------------------+--------------------------------------------------------------------+------------------------+
   | :ref:`Compression Helpers <pubkey/kyber/compr_helpers>`   | :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_helpers.h`              | Specific bit operations, compression and decompression             | 4.2.1                  |
   +-----------------------------------------------------------+----------------------------------------------------------------------------+--------------------------------------------------------------------+------------------------+
   | :ref:`Polynomials <pubkey/kyber/polynomials>`             | :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_polynomial.h`           | Polynomials and polynomial vectors, matrices, and operations       | 4.3                    |
   +-----------------------------------------------------------+----------------------------------------------------------------------------+--------------------------------------------------------------------+------------------------+
   | :ref:`Supporting Algorithms <pubkey/kyber/sup_algos>`     | :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_algos.h`                | Byte encoding, sampling, polynomial encoding, keypair expansion    | 4.2.1, 4.2.2, 5.1, 6.1 |
   +-----------------------------------------------------------+----------------------------------------------------------------------------+--------------------------------------------------------------------+------------------------+
   | :ref:`Symmetric Primitives <pubkey/kyber/sym_primitives>` | :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_symmetric_primitives.h` | ML-KEM specific abstraction for PRFs, XOFs, and hash functions     | 4.1                    |
   +-----------------------------------------------------------+----------------------------------------------------------------------------+--------------------------------------------------------------------+------------------------+
   | :ref:`Internal Keys and K-PKE <pubkey/kyber/kpke_keys>`   | :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_keys.h`                 | Internal key class with K-PKE encryption and decryption            | 5.2, 5.3               |
   +-----------------------------------------------------------+----------------------------------------------------------------------------+--------------------------------------------------------------------+------------------------+
   | :ref:`ML-KEM Implementation <pubkey/kyber/ml_kem_impl>`   | :srcref:`[src/lib/pubkey/kyber/ml_kem]/ml_kem_impl.h`                      | ML-KEM (internal) encapsulation and decapsulation                  | 6.2, 6.3, 7.2, 7.3     |
   +-----------------------------------------------------------+----------------------------------------------------------------------------+--------------------------------------------------------------------+------------------------+
   | :ref:`ML-KEM <pubkey/kyber/ml_kem_api>`                   | :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber.h`                      | ML-KEM API and ML-KEM key generation                               | 7.1                    |
   +-----------------------------------------------------------+----------------------------------------------------------------------------+--------------------------------------------------------------------+------------------------+


.. _pubkey/kyber/types:

Types
^^^^^

ML-KEM employs strong types and type aliases to represent the various value
types involved in the algorithm. This approach binds the semantic meaning of
values to their types, resulting in a more robust interface and self-documenting
code. Type aliases are defined for ML-KEM polynomials, polynomial vectors, and
polynomial matrices, as well as their NTT representations. All bitstrings,
including various hash values, random seeds, and others, are encapsulated as
strong types. Additionally, the ML-KEM keypair and keypair seed data are
organized within C++ structures.


.. _pubkey/kyber/constants:

Constants
^^^^^^^^^

Botan's ``KyberConstants`` class contains all parameters and constants
outlined in Section 8 of [FIPS-203]_ (see
:ref:`Supported ML-KEM parameter sets <pubkey_key_generation/kyber/table_params>`).
Additionally, the class contains parameters implicitly
derived from these constants, such as key and ciphertext sizes, along with
various intermediate value sizes utilized within the algorithm.


.. _pubkey/kyber/compr_helpers:

Compression Helpers
^^^^^^^^^^^^^^^^^^^

Botan's helper component implements Formulas 4.7 and 4.8 from [FIPS-203]_
for the compression and decompression of modular ring elements. These operations
involve divisions. While divisions by powers of two can be efficiently executed
in constant time using the right-shift operator, division by the modulus
requires careful handling to avoid timing side-channel leaks, as some compilers
may produce non-constant-time instructions.

To mitigate this risk, Botan employs an alternative division algorithm commonly
used by many compilers for optimization. Based on a technique described in
Section 10-9 of
[HD]_, this algorithm replaces division with multiplication followed
by a right-shift operation. [HD]_ provides a method for selecting constants for
multiplication and shifting to ensure consistent results across all inputs
within a specified range. These constants are integrated into Botan's
implementation of the compression function and are thoroughly documented.


.. _pubkey/kyber/polynomials:

Polynomials
^^^^^^^^^^^

ML-KEM relies extensively on polynomials within the polynomial ring :math:`R_q`,
utilizing vectors and matrices of polynomials, both inside and outside the NTT
domain. Botan uses :ref:`strong types <pubkey/kyber/types>` to distinguish
polynomials and polynomial vectors as ``KyberPoly`` and ``KyberPolyVec``, as
well as their NTT counterparts ``KyberPolyNTT`` and ``KyberPolyVecNTT``.
Matrices only appear in the NTT domain and are represented by the class
``KyberPolyMatrix``.

ML-DSA, as defined in [FIPS-204]_, also employs polynomials, leading to shared
polynomial logic between the two algorithms. This shared logic is located in
:srcref:`[src/lib/pubkey]/pqcrystals/pqcrystals.h`, encompassing common
operations on vectors and matrices, as well as algorithm-independent operations
like polynomial addition and subtraction. The ML-KEM specific logic implemented
in :srcref:`[src/lib/pubkey/kyber]/kyber_common/kyber_polynomial.h` supplements
this construction by including the NTT (Algorithm 9 of [FIPS-203]_) and inverse
NTT (Algorithm 10 of [FIPS-203]_) operations, along with NTT polynomial
multiplication (Algorithms 11 and 12 of [FIPS-203]_).

Due to this type-based construction, the C++ compiler can detect domain-specific
implementation issues statically. For instance, the polynomial
multiplication operation is only defined for the ``PolyVecNTT`` type. Misuse
would result in a compile-time error.

Botan utilizes either Montgomery or Barrett reduction for modular reduction,
depending on the expected result range of certain operations. Reductions are
explicitly applied in the implementation as needed.


.. _pubkey/kyber/sup_algos:

Supporting Algorithms
^^^^^^^^^^^^^^^^^^^^^

The ``KyberAlgos`` namespace includes a variety of specialized functions
designed to support the primary algorithm. Table
:ref:`ML-KEM Algorithms Overview <pubkey/kyber/algos>` offers a comprehensive
summary of these functions and their specific purposes.

.. _pubkey/kyber/algos:

.. table::  ML-KEM Algorithms Overview
   :widths: 28, 28, 21, 13

   +------------------------------+---------------------------------------------------------------------------------------------+----------------------------------------------------------------------+---------------------------+
   | Botan Function               | Code Reference                                                                              | Purpose                                                              | Algorithms of [FIPS-203]_ |
   +==============================+=============================================================================================+======================================================================+===========================+
   | ``encode_polynomial_vector`` | :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_algos.cpp:184|encode_polynomial_vector`  | Byte encoding of polynomial vectors                                  | 5                         |
   +------------------------------+---------------------------------------------------------------------------------------------+----------------------------------------------------------------------+---------------------------+
   | ``decode_polynomial_vector`` | :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_algos.cpp:192|decode_polynomial_vector`  | Byte decoding of polynomial vectors                                  | 6                         |
   +------------------------------+---------------------------------------------------------------------------------------------+----------------------------------------------------------------------+---------------------------+
   | ``polynomial_from_message``  | :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_algos.cpp:204|polynomial_from_message`   | Byte decoding of the K-PKE message :math:`m`                         | 6                         |
   +------------------------------+---------------------------------------------------------------------------------------------+----------------------------------------------------------------------+---------------------------+
   | ``polynomial_to_message``    | :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_algos.cpp:212|polynomial_to_message`     | Byte encoding of the K-PKE message :math:`m`                         | 5                         |
   +------------------------------+---------------------------------------------------------------------------------------------+----------------------------------------------------------------------+---------------------------+
   | ``expand_keypair``           | :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_algos.cpp:321|expand_keypair`            | Create public and secret keys from the seeds :math:`d` and :math:`z` | 13, 16                    |
   +------------------------------+---------------------------------------------------------------------------------------------+----------------------------------------------------------------------+---------------------------+
   | ``compress_ciphertext``      | :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_algos.cpp:352|compress_ciphertext`       | Compress, byte encode, and concatenate polynomial vector             | 5, Formula 4.7            |
   |                              |                                                                                             | :math:`\mathbf{u}` and polynomial :math:`\mathbf{v}`                 |                           |
   +------------------------------+---------------------------------------------------------------------------------------------+----------------------------------------------------------------------+---------------------------+
   | ``decompress_ciphertext``    | :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_algos.cpp:362|decompress_ciphertext`     | Split, byte decode, and decompress bytes to polynomial vector        | 6, Formula 4.8            |
   |                              |                                                                                             | :math:`\mathbf{u'}` and polynomial :math:`\mathbf{v'}`               |                           |
   +------------------------------+---------------------------------------------------------------------------------------------+----------------------------------------------------------------------+---------------------------+
   | ``sample_matrix``            | :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_algos.cpp:380|sample_matrix`             | Samples a matrix from a secret seed                                  | 7, 13                     |
   +------------------------------+---------------------------------------------------------------------------------------------+----------------------------------------------------------------------+---------------------------+


Additionally, the ``PolynomialSampler`` class offers robust functionality for
sequentially sampling polynomials and polynomial vectors from a given seed
(Algorithm 8 of [FIPS-203]_).
This capability is essential for the processes of key generation and
encapsulation in ML-KEM. Table
:ref:`Polynomial Sampling Methods <pubkey/kyber/poly_sample>` lists the
supported methods. The sampling counter :math:`N` is managed by the sampler
object and is incremented with each method call accordingly.

.. _pubkey/kyber/poly_sample:

.. table::  Polynomial Sampling Methods
   :widths: 40, 26, 34

   +------------------------------------------+---------------------------------------------------------------------------------------------------+---------------------------------------------------------------------+
   | Polynomial sampler method                | Code Reference                                                                                    | Purpose                                                             |
   +==========================================+===================================================================================================+=====================================================================+
   | ``sample_polynomial_vector_cbd_eta1``    | :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_algos.h:70|sample_polynomial_vector_cbd_eta1`  | Polynomial vector sampling in :math:`\mathcal{D}_{\eta_1}(R_q)`     |
   +------------------------------------------+---------------------------------------------------------------------------------------------------+---------------------------------------------------------------------+
   | ``sample_polynomial_cbd_eta2``           | :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_algos.h:78|sample_polynomial_cbd_eta2`         | Polynomial sampling in :math:`\mathcal{D}_{\eta_2}(R_q)`            |
   +------------------------------------------+---------------------------------------------------------------------------------------------------+---------------------------------------------------------------------+
   | ``sample_polynomial_vector_cbd_eta2``    | :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_algos.h:86|sample_polynomial_vector_cbd_eta2`  | Polynomial vector sampling in :math:`\mathcal{D}_{\eta_2}(R_q)`     |
   +------------------------------------------+---------------------------------------------------------------------------------------------------+---------------------------------------------------------------------+


.. _pubkey/kyber/sym_primitives:

Symmetric Primitives
^^^^^^^^^^^^^^^^^^^^

In Botan, the symmetric primitives of ML-KEM are represented by the
``KyberSymmetricPrimitives`` class
(:srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_symmetric_primitives.h:30|Kyber_Symmetric_Primitives`).
This class provides an interface for the primitives, which are defined as
``PRF``, ``H``, ``J``, ``G``, and ``XOF`` in Section 4.1 of
[FIPS-203]_.


.. _pubkey/kyber/kpke_keys:

K-PKE Keys
^^^^^^^^^^

The ``KyberPublicKeyInternal`` and ``KyberPrivateKeyInternal`` classes represent
the public and private keys of ML-KEM, respectively. These classes also provide
methods for K-PKE encryption and decryption, as described in Algorithms 14 and
15 of [FIPS-203]_.


.. _pubkey/kyber/ml_kem_impl:

ML-KEM Implementation
^^^^^^^^^^^^^^^^^^^^^

The ``ML_KEM_Encryptor`` and ``ML_KEM_Decryptor`` classes implement the methods
for high-level and internal ML-KEM encryption and decryption, corresponding to
Algorithms 17, 18, 20, and 21 of [FIPS-203]_.


.. _pubkey/kyber/ml_kem_api:

ML-KEM
^^^^^^

The ``Kyber_PublicKey`` and ``Kyber_PrivateKey`` classes serve as Botan's
public API for public and private ML-KEM keys, respectively. The ``KyberMode``
class is used to select the desired parameter set.


.. _pubkey/kyber/kyber:

Kyber
^^^^^

For compatibility reasons, Botan continues to support the Kyber Round 3.1 NIST
implementation [Kyber-R3]_, which was implemented and released before the completion
of the final standard. The Kyber and Kyber 90s instances can be activated by
enabling the ``kyber`` or ``kyber_90s`` module, respectively.

Note that the Kyber 90s is already marked as deprecated, and both Kyber and
Kyber 90s may be removed as early as the next major release of the library. It
is not advisable to use any other variant than the ones specified in
[FIPS-203]_.


.. _pubkey/kyber/key_gen:

Key Generation
--------------

The high-level ML-KEM key generation (Algorithm 19) is implemented in
:srcref:`[src/lib/pubkey/kyber]/kyber_common/kyber.cpp:232|Kyber_PrivateKey::Kyber_PrivateKey`
within the ``Kyber_PrivateKey`` constructor. It delegates to the
internal and K-PKE key generation algorithms (Algorithms 16 and 13 of
[FIPS-203]_) implemented in
:srcref:`[src/lib/pubkey/kyber]/kyber_common/kyber_algos.cpp:321|expand_keypair`.
In combination, Botan does the following:

.. admonition:: Kyber_PrivateKey::Kyber_PrivateKey

   **Input:**

   -  ``rng``: random number generator
   -  ``mode``: ML-KEM mode (containing matrix dimension ``k``)

   **Output:**

   -  ``sk``: secret key
   -  ``pk``: public key

   **Steps:**

   1. Generate the random seed ``seed.d`` and the implicit rejection value ``seed.z`` at random using ``rng``
   2. ``(rho, sigma) = G(seed.d || k)``
   3. Sample matrix ``A`` from ``rho`` using ``sample_matrix``
   4. Initialize a ``PolynomialSampler`` ``ps`` with ``sigma``
   5. ``s = ntt(ps.sample_polynomial_vector_cbd_eta1())``
   6. ``e = ntt(ps.sample_polynomial_vector_cbd_eta1())``
   7. Compute ``t = A * s + e``
   8. ``pk = (t, rho)`` and ``sk = (seed.d, seed.z)``

   **Notes:**

   - Step 1 corresponds to Algorithm 19 of [FIPS-203]_ and is performed in
     :srcref:`[src/lib/pubkey/kyber]/kyber_common/kyber.cpp:232|Kyber_PrivateKey::Kyber_PrivateKey`.
   - Steps 2-7 correspond to Algorithms 16 and 13 of [FIPS-203]_ and are
     performed in :srcref:`[src/lib/pubkey/kyber]/kyber_common/kyber_algos.cpp:321|expand_keypair`.
   - Botan follows the consensus [#seed_keys]_ that only the seeds are
     stored in the private key. The required values for
     decapsulation are recomputed on demand. Loading or storing the partially
     expanded key format specified in [FIPS-203]_ is explicitly not supported.

.. [#seed_keys] See `<https://mailarchive.ietf.org/arch/msg/spasm/KPg3lbPeNms2H5PNDBt0iJByuE0/>`_

.. _pubkey/kyber/encaps:

Key Encapsulation
-----------------

The algorithms for high-level ML-KEM encapsulation and internal encapsulation
(Algorithms 20 and 17 of [FIPS-203]_) are implemented in
:srcref:`[src/lib/pubkey/kyber]/ml_kem/ml_kem_impl.cpp:25|ML_KEM_Encryptor::encapsulate`.
They use the K-PKE encapsulation algorithm (Algorithm 14 of [FIPS-203]_)
implemented in
:srcref:`[src/lib/pubkey/kyber]/kyber_common/kyber_keys.cpp:55|Kyber_PublicKeyInternal::indcpa_encrypt`.
In combination, Botan does the following:

.. admonition:: ML_KEM_Encryptor::encapsulate

   **Input:**

   -  ``rng``: random number generator
   -  ``pk = (t, rho)``: public key

   **Output:**

   -  ``K``: shared secret key
   -  ``c``: ciphertext

   **Steps:**

   1. Generate a random message ``m`` using ``rng``
   2. ``(K, r) = G(m || H(pk))``
   3. K-PKE encrypt ``m`` using ``r`` to obtain ciphertext ``c``

      1. Sample transposed matrix ``At`` from ``rho`` using ``sample_matrix``
      2. Initialize a ``PolynomialSampler`` ``ps`` with ``r``
      3. ``y = ntt(ps.sample_polynomial_vector_cbd_eta1())``
      4. ``e1 = ps.sample_polynomial_vector_cbd_eta2()``
      5. ``e2 = ps.sample_polynomial_cbd_eta2()``
      6. ``u = inverse_ntt(At * y) + e1``
      7. ``mu = polynomial_from_message(m)`` for byte decoding and decompression
      8. ``v = inverse_ntt(t * y) + e2 + mu``
      9. Encode, compress and concatenate ``u`` and ``v`` to obtain the
         ciphertext ``c`` using ``compress_ciphertext``


   **Notes:**

   - Steps 1-3 correspond to Algorithms 20 and 17 of [FIPS-203]_ and are
     performed in :srcref:`[src/lib/pubkey/kyber]/ml_kem/ml_kem_impl.cpp:25|ML_KEM_Encryptor::encapsulate`.
   - Steps 3.1-3.9 correspond to Algorithms 14 of [FIPS-203]_ and are performed
     in :srcref:`[src/lib/pubkey/kyber]/kyber_common/kyber_keys.cpp:55|indcpa_encrypt`.
   - The transposed matrix ``At`` is precomputed and stored in the public key
     object. This way, consecutive encapsulations for the same public key do not
     have to re-generate ``At`` from ``rho``.


.. _pubkey/kyber/decaps:

Key Decapsulation
-----------------

The algorithms for high-level ML-KEM decapsulation and internal decapsulation
(Algorithms 21 and 18 of [FIPS-203]_) are implemented in
:srcref:`[src/lib/pubkey/kyber]/ml_kem/ml_kem_impl.cpp:48|ML_KEM_Decryptor::decapsulate`.
They use the K-PKE encapsulation and decapsulation algorithms (Algorithm 14
and 15 of [FIPS-203]_) implemented in
:srcref:`[src/lib/pubkey/kyber]/kyber_common/kyber_keys.cpp:55|Kyber_PublicKeyInternal::indcpa_encrypt`
and
:srcref:`[src/lib/pubkey/kyber]/kyber_common/kyber_keys.cpp:84|Kyber_PrivateKeyInternal::indcpa_decrypt`.
In combination, Botan does the following:

.. admonition:: ML_KEM_Decryptor::decapsulate

   **Input:**

   -  ``c``: ciphertext
   -  ``sk = (seed.d, seed.z)``: secret key
   -  ``pk``: public key

   **Output:**

   -  ``K_prime``: shared secret key

   **Steps:**

   1. Recompute the secret key value ``s`` from ``seed.d``
   2. K-PKE decrypt ``c`` to obtain message ``m_prime``

      1. Retrieve ``u, v`` using ``decompress_ciphertext`` on ``c``
      2. Compute ``w = v - inverse_ntt(s * ntt(u))``
      3. ``m = polynomial_to_message(w)`` for compression and byte encoding

   3. ``(K_prime, r_prime) = G(m_prime || H(pk))``
   4. ``K_bar = J(seed.z || c)``
   5. K-PKE encrypt ``m`` using ``r_prime`` to obtain ciphertext ``c_prime``
   6. if ``c != c_prime`` set ``K_prime = K_bar``

   **Notes:**

   - Steps 1-6 correspond to Algorithm 18 of [FIPS-203]_ and are
     performed in :srcref:`[src/lib/pubkey/kyber]/ml_kem/ml_kem_impl.cpp:48|ML_KEM_Decryptor::decapsulate`.
   - Steps 2.1-2.3 correspond to Algorithm 15 of [FIPS-203]_ and are performed
     in :srcref:`[src/lib/pubkey/kyber]/kyber_common/kyber_keys.cpp:84|Kyber_PrivateKeyInternal::indcpa_decrypt`.
   - Step 6 uses a constant time check and memory assignment function.
