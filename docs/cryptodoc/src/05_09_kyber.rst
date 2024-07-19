.. _pubkey/kyber:

Kyber
=====


Botan implements the CRYSTALS-Kyber KEM in
:srcref:`src/lib/pubkey/kyber/`. The implementation is based on the NIST round 3 specification [Kyber-R3]_.
The list of supported algorithms and their parameters is depicted in
Table :ref:`Supported Kyber parameter sets <pubkey_key_generation/kyber/table_params>`.

**Structure**

The IND-CCA2-secure KEM Kyber (Kyber.CCAKEM, Section 1.3, [Kyber-R3]_) is obtained from an IND-CPA-secure public-key encryption scheme (Kyber.CPAPKE, Section 1.2, [Kyber-R3]_) via a modified Fujisaki–Okamoto transform.
The table below provides pointers to the implementation of Kyber's high-level algorithms in Botan.

.. table::  High-level algorithms of Kyber in Botan

   +---------------------------------------------------------+----------------------------------------------------------------------------------+
   | Algorithm                                               | Implementation in Botan                                                          |
   +=========================================================+==================================================================================+
   | :ref:`Key Generation <pubkey_key_generation/kyber>`     | :srcref:`[src/lib/pubkey/kyber]/kyber_common/kyber.cpp:205|Kyber_PrivateKey`     |
   +---------------------------------------------------------+----------------------------------------------------------------------------------+
   | :ref:`CPAPKE Encryption <pubkey/kyber/cpapke_enc>`      | :srcref:`[src/lib/pubkey/kyber]/kyber_common/kyber_keys.cpp:29|indcpa_encrypt`   |
   +---------------------------------------------------------+----------------------------------------------------------------------------------+
   | :ref:`CPAPKE Decryption <pubkey/kyber/cpapke_dec>`      | :srcref:`[src/lib/pubkey/kyber]/kyber_common/kyber_keys.cpp:57|indcpa_decrypt`   |
   +---------------------------------------------------------+----------------------------------------------------------------------------------+
   | :ref:`CCAKEM Encapsulation <pubkey/kyber/ccakem_enc>`   | :srcref:`[src/lib/pubkey/kyber]/kyber_round3/kyber_encaps.cpp:23|encapsulate`    |
   +---------------------------------------------------------+----------------------------------------------------------------------------------+
   | :ref:`CCAKEM Decapsulation <pubkey/kyber/ccakem_dec>`   | :srcref:`[src/lib/pubkey/kyber]/kyber_round3/kyber_encaps.cpp:39|decapsulate`    |
   +---------------------------------------------------------+----------------------------------------------------------------------------------+

**Keys**

The class ``Kyber_PublicKeyInternal`` (see :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_keys.h:21|Kyber_PublicKeyInternal`) supplies the values ``m_rho`` (the public seed) and ``m_t`` (:math:`\mathbf{\hat{t}}` of L.2, Alg. 5 [Kyber-R3]_).
In the following, we denote the public key as ``pk = (pk_t, seed)``.

The class ``Kyber_PrivateKeyInternal`` (see :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_keys.h:50|Kyber_PrivateKeyInternal`) supplies the secret polynomial vector ``m_s`` (:math:`\mathbf{\hat{s}}`, L.3, Alg. 6, [Kyber-R3]_) and the implicit rejection value ``m_z``.
We, therefore, denote the secret key as ``sk = (sk_s, z)``.

**Ciphertexts**

The ``Ciphertext`` class is given a ``PolynomialVector b``, a ``Polynomial v``, and a ``KyberMode mode``. A ciphertext instance is represented via the members ``b`` and ``v`` (corresponding to :math:`\textbf{u}` and :math:`v` of [Kyber-R3]_, respectively).

Furthermore, the ``Ciphertext`` class (see :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_structures.h:554|Ciphertext`) provides ciphertext compression and encoding.
The implementation of the algorithms :math:`\mathsf{Compress}_q(x,d)` and :math:`\mathsf{Decompress}_q(x,d)` of [Kyber-R3]_ are optimized for all occurring values of :math:`d`.
The compression with :math:`d=d_u` and :math:`d=d_v` [#kyber_du_dv]_ is implemented in two respective ``Ciphertext::compress`` methods, i.e., one for polynomial vectors and one for polynomials. The same holds for decompression via ``Ciphertext::decompress_polynomial_vector`` and ``Ciphertext::decompress_polynomial``.
The public member functions ``Ciphertext::from_bytes`` and ``Ciphertext::to_bytes`` use this to realize **L. 1/L. 2 of Alg. 6** [Kyber-R3]_ and **L. 21/L. 22 of Alg. 5** [Kyber-R3]_, respectively.
The compression and decompression with :math:`d=1` are performed simultaneously with :math:`\mathsf{Encode}_1` and :math:`\mathsf{Decode}_1` within the methods ``Polynomial::to_message`` and ``Polynomial::from_message``, respectively (used in **L. 4, Alg. 6** and **L. 20, Alg. 5** [Kyber-R3]_).

Compression in Kyber requires division by the Kyber constant ``q``. However,
this division may introduce timing side-channels on some platforms.
Botan uses the ``ct_int_div_kyber_q`` (see :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_structures.h:45|ct_int_div_kyber_q`) function to address this issue, which performs
constant-time division by ``q``. This function leverages
a technique described in [HD]_, where the fraction ``n/q`` is extended by a
specific constant ``m`` to become ``(m*n)/(m*q)``. Here, ``m`` is chosen so that
``(m*q)`` is reasonably close to a power of two ``2^p``. For integer division, it holds that
``n/q = (m*n)/(2^p)`` for all ``n`` is smaller than a boundary ``2^W``.
The boundary constant ``W`` is chosen to encompass all possible numerators
encountered in Kyber's compression functions. The constants ``m = 161271`` and ``p = 29`` are
selected using the algorithm outlined in Chapter 10.9 of [HD]_. Hence, instead of a potentially
variable-time division, the compiled runtime code will always perform a
multiplication (by ``m``) followed by a right-shift (by ``p`` bits), both of which are
constant-time operations.

.. [#kyber_du_dv]
   The values of :math:`d_u` and :math:`d_v` are not given as ``KyberConstants`` but are rather computed in place based on the value of `k`.


Algorithm Internals
-------------------

All possible modes are represented by the class ``KyberMode`` found in :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber.h:30|KyberMode`.
The ``_90s`` suffix denotes different symmetric functions for Kyber's \"90s mode\", which uses SHA2 and AES instead of SHA3 and SHAKE as symmetric primitives.
The abstract adapter class ``Kyber_Symmetric_Primitives`` is the interface for Kyber's five symmetric primitives, which are instantiated either as a ``Kyber_Modern_Symmetric_Primitives`` object (in :srcref:`[src/lib/pubkey/kyber]/kyber_round3/kyber/kyber_modern.h:23|Kyber_Modern_Symmetric_Primitives`) for modern Kyber
or as a ``Kyber_90s_Symmetric_Primitives`` one (in :srcref:`[src/lib/pubkey/kyber]/kyber_round3/kyber_90s/kyber_90s.h:23|Kyber_90s_Symmetric_Primitives`) for the 90s variant (see Table :ref:`Kyber's symmetric primitives <pubkey_key_generation/kyber/table_sym_primitives>`).
For each mode, the ``KyberConstants`` class contains the corresponding set of parameters and symmetric functions (``Kyber_Symmetric_Primitives``).

.. _pubkey_key_generation/kyber/table_params:

.. table::  Supported Kyber parameter sets (see Section 1.4 in [Kyber-R3]_)

   +-------------------+-----+---+------+------+------+-----+-----+
   |  Mode             | N   | k | Q    | eta1 | eta2 | d_u | d_v |
   +===================+=====+===+======+======+======+=====+=====+
   | Kyber512          | 256 | 2 | 3329 | 3    | 2    | 10  | 4   |
   +-------------------+-----+---+------+------+------+-----+-----+
   | Kyber768          | 256 | 3 | 3329 | 2    | 2    | 10  | 4   |
   +-------------------+-----+---+------+------+------+-----+-----+
   | Kyber1024         | 256 | 4 | 3329 | 2    | 2    | 11  | 5   |
   +-------------------+-----+---+------+------+------+-----+-----+

.. _pubkey_key_generation/kyber/table_sym_primitives:

.. table:: Kyber's symmetric primitives (see Section 1.4 in [Kyber-R3]_)

   +-------------------+--------------+----------+-----------+--------------+------------+
   |  Variant          | XOF          | H        | G         | PRF          | KDF        |
   +===================+==============+==========+===========+==============+============+
   | Kyber             | SHAKE-128    | SHA3-256 | SHA3-512  | SHAKE-256    | SHAKE-256  |
   +-------------------+--------------+----------+-----------+--------------+------------+
   | Kyber 90s         | AES-256-CTR  | SHA-256  | SHA512    | AES-256-CTR  | SHA-256    |
   +-------------------+--------------+----------+-----------+--------------+------------+

.. warning::

   The 90s-variants of Kyber that use AES and SHA-2 are deprecated and will be removed in a future release.
   NIST decided not to standardize those variants in their final ML-KEM standard.

Kyber itself is implemented in :srcref:`[src/lib/pubkey/kyber]/kyber_common/kyber.cpp`.
Basic representations and operations on polynomials, polynomial vectors, and polynomial matrices are given via the ``Polynomial``, ``PolynomialVector``, and ``PolynomialMatrix`` classes (see :srcref:`[src/lib/pubkey/kyber/kyber_common]/kyber_structures.h`), respectively.
``Polynomial`` and ``PolynomialVector`` support member functions ``.ntt()`` and ``.invntt()`` for the number-theoretic transform (NTT; see more details in Section 1.1 of [Kyber-R3]_) and fast multiplication in the NTT domain.
Multiplication of two polynomial vectors in NTT domain ``a*b`` is given via the function ``PolynomialVector::pointwise_acc_montgomery`` using Montgomery reduction.
Note that the inverse NTT is called ``.invntt_tomont()`` in Botan's implementation as it directly multiplies by the Montgomery factor; however, for simplicity, we write ``.invntt()`` in this documentation.

Additionally, ``PolynomialMatrix`` has a member function ``generate(seed, transposed, mode)``, which generates a (possibly transposed) ``k``:math:`\times`\ ``k`` matrix ``a`` from the ``seed`` given a ``mode``.
The matrix is already generated in the NTT domain via rejection sampling with ``XOF`` (using the function ``Polynomial::sample_rej_uniform(XOF)`` that corresponds to **Algorithm 1** of [Kyber-R3]_).

**Algorithm 2** of [Kyber-R3]_ is implemented via the member function ``Polynomial::getnoise_cbd2`` for the case ``eta1=2`` (and a respective version for ``eta1=3``). It deterministically samples noise from a centered binomial distribution.

Encoding/decoding of polynomials (**Algorithm 3** of [Kyber-R3]_) is realized via the ``Polynomial::to_bytes()``/ ``Polynomial::from_bytes()`` functions.

.. _pubkey_key_generation/kyber:

Key Generation
--------------

Based on these functions the key generation process follows **Algorithms 4 and 7** of [Kyber-R3]_ and works as follows:

.. admonition:: Kyber_PrivateKey::Kyber_PrivateKey()

   **Input:**

   -  ``rng``: random number generator
   -  ``m``: Kyber mode providing (``N``, ``k``, ``Q``, ``XOF``, ``H``, ``G``, ``PRF``, ``KDF``), see Table :ref:`Supported Kyber parameter sets <pubkey_key_generation/kyber/table_params>` and Table :ref:`Kyber's symmetric primitives <pubkey_key_generation/kyber/table_sym_primitives>`

   **Output:**

   -  ``sk``: secret key
   -  ``pk``: public key

   **Steps:**

   1. Generate the random seed ``d`` and the implicit rejection value ``z`` at random using ``rng``
   2. ``(rho || sigma) = G(d)`` (L. 1-2, Alg. 4 [Kyber-R3]_)
   3. ``a = PolynomialMatrix::generate(rho, false, m)`` (``false`` means "not transposed") (L. 4-8, Alg. 4 [Kyber-R3]_)
   4. ``s = PolynomialVector::getnoise_eta1(sigma, 0, m)`` (performs ``k`` invocations of ``Polynomial::getnoise_eta1``, one for each component of ``s``; L. 9-12, Alg. 4 [Kyber-R3]_)
   5. ``e = PolynomialVector::getnoise_eta1(sigma, k, m)`` (performs ``k`` invocations of ``Polynomial::getnoise_eta1``, one for each component of ``e``; L. 13-16, Alg. 4 [Kyber-R3]_)
   6. ``s.ntt()`` and ``e.ntt()`` (L. 17-18, Alg. 4 [Kyber-R3]_)
   7. ``pk = (a*s + e, rho)`` and ``sk = (s, z)`` (L. 19-22, Alg. 4 [Kyber-R3]_ and L.1, 3, Alg. 7 [Kyber-R3]_)

   **Notes:**

   - The member function ``Polynomial::getnoise_eta1(seed, nonce, mode)`` uses ``PRF`` on the seed with incremented nonce values to call ``Polynomial::getnoise_cbd2`` or ``Polynomial::getnoise_cbd3`` depending on ``eta1``.
   - Serialization to bytes of the keys (:math:`\mathsf{Encode}` in L.20, 21, Alg. 4 [Kyber-R3]_) is performed via the constructor of the internal classes for public and secret keys (``Kyber_PublicKeyInternal`` and ``Kyber_PrivateKeyInternal``) by calling ``Polynomial::to_bytes()``.


Key Encapsulation
-----------------

.. _pubkey/kyber/cpapke_enc:

Kyber.CPAPKE
^^^^^^^^^^^^

Encryption works as follows, realizing **Algorithm 5** of [Kyber-R3]_:

.. admonition:: Kyber_KEM_Cryptor::indcpa_enc()

   **Input:**

   - ``pk = (pk_t, seed)``: public key
   - ``m``: message
   - ``coins``: randomness (input :math:`r` in Alg. 5 [Kyber-R3]_)

   **Output:**

   - ``c``: ciphertext bytes

   **Steps:**

   1. ``at = PolynomialMatrix::generate(seed, true, mode)`` (``true`` means "transposed") (L. 3-8, Alg. 5 [Kyber-R3]_)
   2. ``sp = PolynomialVector::getnoise_eta1(coins, 0, mode)`` (performs ``k`` invocations of ``Polynomial::getnoise_eta1``, one for each component of ``sp``; L. 9-12, Alg. 5 [Kyber-R3]_)
   3. ``ep = PolynomialVector::getnoise_eta2(coins, k, mode)`` (performs ``k`` invocations of ``Polynomial::getnoise_eta2``, one for each component of ``ep``; L. 13-16, Alg. 5 [Kyber-R3]_)
   4. ``epp = Polynomial::getnoise_eta2(coins, 2*k, mode)`` (L. 17, Alg. 5 [Kyber-R3]_)
   5. ``sp.ntt()`` (L. 18, Alg. 5 [Kyber-R3]_)
   6. ``bp = (at * sp).invntt() + ep`` (L. 19, Alg. 5 [Kyber-R3]_)
   7. ``v = (pk_t * sp).invntt() + epp + Polynomial::from_message(m)`` (L. 20, Alg. 5 [Kyber-R3]_)
   8. ``c = Ciphertext(bp, v, mode).to_bytes()`` (L. 21-23, Alg. 5 [Kyber-R3]_)

   **Notes:**

   - The member function ``Polynomial::getnoise_eta1(seed, nonce, mode)`` uses ``PRF`` on the seed with incremented nonce values to call ``Polynomial::getnoise_cbd2`` or ``Polynomial::getnoise_cbd3`` depending on ``eta1``.
   - The member function ``Polynomial::getnoise_eta2(seed, nonce, mode)`` uses ``PRF`` on the seed with incremented nonce values to call ``Polynomial::getnoise_cbd2`` (as for all parameter sets ``eta2 = 2``).

.. _pubkey/kyber/ccakem_enc:

Kyber.CCAKEM
^^^^^^^^^^^^

Encapsulation works as follows, realizing **Algorithm 8** of [Kyber-R3]_:

.. admonition:: Kyber_KEM_Encryptor::raw_kem_encrypt()

   **Input:**

   - ``pk = (pk_t, seed)``: public key
   - ``out_encapsulated_key``: ciphertext of shared key (to be overwritten)
   - ``out_shared_key``: plaintext shared key (to be overwritten)
   - ``rng``: random number generator

   **Output:**

   -  Overwritten ``out_encapsulated_key``, ``out_shared_key``

   **Steps:**

   1. Generate ``m`` at random using ``rng``
   1. ``shared_secret = H(m)`` (L. 1-2, Alg. 8 [Kyber-R3]_)
   2. ``(shared_secret || coins) = G(shared_secret || H(pk))`` where ``coins`` is the second half of the output of ``G`` (L. 3, Alg. 8 [Kyber-R3]_)
   3. ``out_encapsulated_key = Kyber_KEM_Cryptor::indcpa_enc(pk, shared_secret, coins)`` (L. 4, Alg. 8 [Kyber-R3]_)
   4. ``out_shared_key = KDF(shared_secret || H(out_encapsulated_key))`` (L. 5, Alg. 8 [Kyber-R3]_)

   **Notes:**

   - ``H(pk)`` is precomputed in ``Kyber_PublicKeyInternal`` and accessible via ``H_public_key_bits_raw()``.
   - The input/output structure corresponds to Botan's ``KEM_Encryption`` interface.


Key Decapsulation
-----------------

.. _pubkey/kyber/cpapke_dec:

Kyber.CPAPKE
^^^^^^^^^^^^

IND-CPA decryption works as follows, realizing **Algorithm 6** of [Kyber-R3]_:

.. |step_3_formular| replace:: :math:`\mathbf{\hat{s}}^T \circ \mathsf{NTT}(\mathbf{u})`
.. |step_4_formular| replace:: :math:`\mathsf{NTT}^{-1}(\mathbf{\hat{s}}^T \circ \mathsf{NTT}(\mathbf{u}))`
.. |step_5_formular| replace:: :math:`v - \mathsf{NTT}^{-1}(\mathbf{\hat{s}}^T \circ \mathsf{NTT}(\mathbf{u}))`
.. admonition:: Kyber_KEM_Decryptor::indcpa_dec()

   **Input:**

   -  ``sk = (sk_s, z)``: secret key
   -  ``c``: ciphertext bytes

   **Output:**

   -  ``m``: message bytes (decapsulated key)

   **Steps:**

   1. Create a ``Ciphertext`` object ``ct`` by decoding and decompressing the ciphertext bytes. (L. 1-2, Alg. 6 [Kyber-R3]_)
   2. ``ct.b.ntt()``
   3. ``mp = sk_s * ct.b``  (|step_3_formular| of L. 4, Alg. 6 [Kyber-R3]_)
   4. ``mp.invntt()`` (|step_4_formular| of L. 4, Alg. 6 [Kyber-R3]_)
   5. ``mp -= ct.v`` (|step_5_formular| of L. 4, Alg. 6 [Kyber-R3]_)
   6. ``m = mp.to_message()`` (L. 4, Alg. 6 [Kyber-R3]_)

   **Notes:**

   - The coefficients of ``mp`` are additively inverse to the specification. For the subsequent compression, however, only the distances of the coefficients to zero are relevant, which are the same in both cases.

.. _pubkey/kyber/ccakem_dec:

Kyber.CCAKEM
^^^^^^^^^^^^

Decapsulation works as follows, realizing **Algorithm 9** of [Kyber-R3]_:

.. admonition:: Kyber_KEM_Decryptor::raw_kem_decrypt()

   **Input:**

   -  ``pk = (pk_t, seed)``: public key (typically part of the secret key)
   -  ``sk = (sk_s, z)``: secret key
   -  ``encap_key``: encapsulated key bytes

   **Output:**

   -  ``shared_key``: shared key

   **Steps:**

   1. ``m = indcpa_dec(sk, encap_key)`` to extract the shared secret using the CPA-secure decryption algorithm. (L. 4, Alg. 9 [Kyber-R3]_)
   2. ``(shared_secret || coins) = G(m || sk_h)`` (L. 5, Alg. 9 [Kyber-R3]_)
   3. ``cmp = indcpa_enc(pk, m, coins)`` (L. 6, Alg. 9 [Kyber-R3]_)
   4. The value ``cmp`` is compared with the value ``encap_key``. This comparison is performed using the constant time comparison function ``constant_time_compare``. Using the constant time function ``conditional_copy_mem``, ``shared_secret`` is set to either ``shared_secret`` if the ciphertext was valid or ``z`` if not. (L. 7, Alg. 9 [Kyber-R3]_)
   5. ``shared_key = KDF(shared_secret || H(c))`` (L. 8, 10, Alg. 9 [Kyber-R3]_)

   **Notes:**

   - Algorithm 9 [Kyber-R3]_ only takes the secret key bytes as input. These can be transformed to a ``Kyber_PrivateKey`` object using the respective constructor which performs the parsing of the secret key like in L. 1-3 of Alg. 9 [Kyber-R3]_.
   - Regarding side-channel attacks, Botan's operations after step 2 are crucial. Therefore, ``pointwise_acc_montgomery``, ``invntt``, ``to_message``, and the subtraction and reduction are constant-time implementations.

**Remark:** [Kyber-R3]_ notes that implementations of the 90s variant may be vulnerable to timing attacks if the AES implementation is not constant time. However, like all of Botan's AES implementations, the one used for Kyber's 90s versions is.

**Remark:** Modular operations are performed with Barrett and Montgomery reductions.
