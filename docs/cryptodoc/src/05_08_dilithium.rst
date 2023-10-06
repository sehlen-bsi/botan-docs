.. _pubkey/dilithium:

Dilithium
=========

.. _pubkey_key_generation/dilithium:

Key Generation
--------------

Botan's implementation of the CRYSTALS-Dilithium signature algorithm is based on the NIST round 3 specification [Dilithium-R3]_ and
can be found in :srcref:`src/lib/pubkey/dilithium`.
The parameter sets shown in Table :ref:`Supported Dilithium signature algorithms <pubkey_key_generation/dilithium/parameter_table>` are supported.

.. _pubkey_key_generation/dilithium/parameter_table:

.. table::  Supported Dilithium signature algorithms and their parameters (see Table 2 of [Dilithium-R3]_)

   +---------------------+------------------+------------------+------------------+
   | ``DilithiumMode``   | ``Dilithium4x4`` | ``Dilithium6x5`` | ``Dilithium8x7`` |
   +=====================+==================+==================+==================+
   | NIST Security Level |     2            |     3            |     5            |
   +---------------------+------------------+------------------+------------------+
   |         :math:`q`   |  8380417         |  8380417         |  8380417         |
   +---------------------+------------------+------------------+------------------+
   |         :math:`d`   |     13           |     13           |     13           |
   +---------------------+------------------+------------------+------------------+
   |      :math:`\tau`   |     39           |     49           |     60           |
   +---------------------+------------------+------------------+------------------+
   | challenge entropy   |    192           |    225           |    257           |
   +---------------------+------------------+------------------+------------------+
   | :math:`\gamma_1`    |  :math:`2^{17}`  |  :math:`2^{19}`  |  :math:`2^{19}`  |
   +---------------------+------------------+------------------+------------------+
   | :math:`\gamma_2`    |(q - 1)/88        |(q - 1)/32        |(q - 1)/32        |
   +---------------------+------------------+------------------+------------------+
   | :math:`(k, \ell)`   |   (4, 4)         |   (6, 5)         |   (8, 7)         |
   +---------------------+------------------+------------------+------------------+
   |     :math:`\eta`    |     2            |     4            |     2            |
   +---------------------+------------------+------------------+------------------+
   |    :math:`\beta`    |     78           |    196           |    120           |
   +---------------------+------------------+------------------+------------------+
   |    :math:`\omega`   |     80           |     55           |     75           |
   +---------------------+------------------+------------------+------------------+
   |     Repetitions     |    4.25          |    5.1           |    3.85          |
   +---------------------+------------------+------------------+------------------+

The Dilithium implementation is composed of several components.
An overview of the components is provided in Table :ref:`Dilithium components and file locations <pubkey_key_generation/dilithium/component_table>`.

.. _pubkey_key_generation/dilithium/component_table:

.. table::  Dilithium components and file locations.

   +-----------------------------------------------------------------------------------+----------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | Component                                                                         | File                                                                                   | Purpose                                                                                                                                                                                |
   +===================================================================================+========================================================================================+========================================================================================================================================================================================+
   | :ref:`Modes <pubkey_key_generation/dilithium/modes>`                              | :srcref:`[src/lib/pubkey/dilithium]/dilithium_common/dilithium.h`                      | Provide parameters and primitives                                                                                                                                                      |
   +-----------------------------------------------------------------------------------+----------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | :ref:`Constants and Symmetric Primitives <pubkey_key_generation/dilithium/modes>` | :srcref:`[src/lib/pubkey/dilithium]/dilithium_common/dilithium_symmetric_primitives.h` | Constants and primitives interface                                                                                                                                                     |
   +-----------------------------------------------------------------------------------+----------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | :ref:`Modern Variant <pubkey_key_generation/dilithium/modes>`                     | :srcref:`[src/lib/pubkey/dilithium]/dilithium`                                         | "Modern" instantiations of primitives                                                                                                                                                  |
   +-----------------------------------------------------------------------------------+----------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | :ref:`AES Variant <pubkey_key_generation/dilithium/modes>`                        | :srcref:`[src/lib/pubkey/dilithium]/dilithium_aes`                                     | "AES" instantiations of primitives                                                                                                                                                     |
   +-----------------------------------------------------------------------------------+----------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | :ref:`Polynomial Operations <pubkey_key_generation/dilithium/polynomials>`        | :srcref:`[src/lib/pubkey/dilithium]/dilithium_common/dilithium_polynomials.h`          | Polynomials and operations on them                                                                                                                                                     |
   +-----------------------------------------------------------------------------------+----------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | Dilithium                                                                         | :srcref:`[src/lib/pubkey/dilithium]/dilithium_common/dilithium.h`                      | Dilithium :ref:`Keys <pubkey_key_generation/dilithium/keys>`, :ref:`Signature Creation <pubkey_signature/dilithium/sig>`, :ref:`Signature Validation <pubkey_signature/dilithium/val>` |
   +-----------------------------------------------------------------------------------+----------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

.. _pubkey_key_generation/dilithium/modes:

**Modes, Constants and Symmetric Primitives**

Similar to CRYSTALS-Kyber, the different ways to instantiate Dilithium are realized as different modes (class ``DilithiumMode``; see Table :ref:`Supported Dilithium signature algorithms <pubkey_key_generation/dilithium/parameter_table>`).
A ``DilithiumMode`` provides the constants of the respective parameter set as ``DilithiumModeConstants``.
Also like Kyber, Dilithium additionally supports different instantiations of symmetric primitives via the class ``Dilithium_Symmetric_Primitives`` (see usage of SHAKE-128 vs. AES in Section 5.3 of [Dilithium-R3]_).
These are also provided by the mode and result in the "modern" and "AES" versions.
An "AES" version is identified via the ``_aes`` suffix in the mode string.

.. _pubkey_key_generation/dilithium/polynomials:

**Polynomial Operations**

``A*b`` of a polynomial matrix ``A`` and a polynomial vector ``b`` in the NTT domain is given via ``PolynomialVector::generate_polyvec_matrix_pointwise_montgomery`` and ``a*b`` of two polynomial vectors ``a`` and ``b`` is given via ``PolynomialVector::polyvec_pointwise_poly_montgomery``.
Matrices and vectors are transformed to the NTT representation prior to the operation.
To perform the multiplication ``2^d*a`` with the scalar ``2^d`` and the vector ``a``, the method ``PolynomialVector::polyvec_shiftl`` is used.

In addition to core polynomial operations, Dilithium relies on several supporting algorithms, see Section 2.3, Section 2.4, and the alterations of Section 5 of [Dilithium-R3]_.
Concretely, :math:`\mathsf{SampleInBall}` of [Dilithium-R3]_ is provided via ``Polynomial::poly_challenge``, :math:`\mathsf{ExpandA}` via ``PolynomialMatrix::generate_matrix``, :math:`\mathsf{ExpandS}` via ``PolynomialVector::fill_polyvec_uniform_eta`` (called to fill vectors of different lengths), and :math:`\mathsf{ExpandMask}` via ``PolynomialVector::polyvecl_uniform_gamma1``.
The function :math:`\mathsf{H}` is instantiated directly.

Furthermore, the algorithm :math:`\mathsf{Power2Round}_q` of [Dilithium-R3]_ corresponds to the functions ``Polynomial::power2round`` and ``Polynomial::fill_polys_power2round``.
:math:`\mathsf{MakeHint}_q` and :math:`\mathsf{UseHint}_q` of [Dilithium-R3]_ are realized by ``Polynomial::make_hint``\/\ ``Polynomial::generate_hint_polynomial`` and ``Polynomial::use_hint``, respectively.
:math:`\mathsf{Decompose}_q` is given via ``Polynomial::decompose`` and ``Polynomial::poly_decompose``.
During the signature operations, the decomposition functions are used directly instead of using the :math:`\mathsf{HighBits}_q` \/ :math:`\mathsf{LowBits}_q` paradigm.
Versions with element-wise applications on polynomial vectors are given as well.

Finally, Botan supplies packing operations (Section 5.2, [Dilithium-R3]) and the function ``PolynomialVector::polyvec_chknorm``, which realizes a check if the :math:`\lVert \cdot \rVert_\infty` norm of a given polynomial vector surpasses a provided bound.

.. _pubkey_key_generation/dilithium/keys:

**Keys**

In Botan, Dilithium's keys are represented as ``Dilithium_PublicKey`` for public keys ``pk`` and as ``Dilithium_PrivateKey`` for secret keys ``sk``.
Public keys contain the matrix seed ``rho`` and the public value ``t1``.
Also, when creating a ``pk`` object the value  ``tr = CRH(rho || t1)`` is precomputed from the public key values ``rho`` and ``t1``, which is used by the verification algorithm.
We therefore write ``pk = (rho, t1)`` during key generation and ``pk = (rho, t1, tr)`` during verification.
The ``sk`` object contains the values ``rho`` and ``tr`` of the ``pk``.
It also contains the seed ``key``, the vectors ``s1`` and ``s2``, and the value ``t0``. We write ``sk = (rho, tr, key, s1, s2, t0)``.

The keys use a helper function ``calculate_t0_and_t1`` to compute :math:`(\mathbf{t_1},\mathbf{t_0})` based on the public key seed ``rho`` and private vectors ``s1, s2``, i.e., realizing L. 3, L.5, and L. 6, Fig. 4, [Dilithium-R3]_.
Furthermore, encoding and decoding of keys and signatures are provided via the key classes.

The Dilithium key generation process follows :math:`\mathsf{Gen}` of Figure 4 of [Dilithium-R3]_ and works as follows (see :srcref:`[src/lib/pubkey/dilithium/dilithium_common]/dilithium.cpp:573|Dilithium_PrivateKey`):

.. admonition:: Dilithium_PrivateKey::Dilithium_PrivateKey()

   **Input:**

   -  ``rng``: random number generator
   -  ``m``: Dilithium mode providing parameters and symmetric functions

   **Output:**

   -  ``sk``: secret key
   -  ``pk``: public key

   **Steps:**

   1. Generate random seed ``seedbuf`` using ``rng`` (L. 1, Fig. 4, [Dilithium-R3]_)
   2. ``(rho || rhoprime || key) = H(seedbuf)`` (L. 2, Fig. 4, [Dilithium-R3]_)
   3. ``matrix = PolynomialMatrix::generate_matrix(rho, m)`` (L. 3, Fig. 4, [Dilithium-R3]_)
   4. Use ``PolynomialVector::fill_polyvec_uniform_eta`` to fill ``s1`` and ``s2`` (L. 4, Fig. 4, [Dilithium-R3]_)
   5. ``(t0, t1) = calculate_t0_and_t1(m, rho, s1, s2)`` (L. 5-6, Fig. 4, [Dilithium-R3]_)
   6. ``pk = (rho, t1)`` (:math:`pk` in L. 8, Fig. 4, [Dilithium-R3]_)
   7. ``tr = H(rho || t1)`` (L. 7, Fig. 4, [Dilithium-R3]_)
   8. ``sk = (rho, tr, key, s1, s2, t0)`` (:math:`sk` in L. 8, Fig. 4, [Dilithium-R3]_)

   **Notes:**

   - ``matrix`` is already generated in NTT representation.
   - The calculation of ``calculate_t0_and_t1`` includes the computation of ``matrix*s1`` in the NTT domain.


.. _pubkey_signature/dilithium/sig:

Signature Creation
------------------

CRYSTALS-Dilithium signing follows the :math:`\mathsf{Sign}` algorithm of Figure 4 of [Dilithium-R3]_. It uses some functions already documented in :ref:`Dilithium Key Generation <pubkey_key_generation/dilithium>`.
It is implemented in the ``Dilithium_Signature_Operation`` (see :srcref:`[src/lib/pubkey/dilithium/dilithium_common]/dilithium.cpp:263|sign`) class and receives the secret key via the constructor.
Message bytes are given to the object via consecutive calls of ``Dilithium_Signature_Operation::update``.

The signature generation process works as follows:

.. admonition:: ``Dilithium_Signature_Operation::sign()``

   **Input:**

   -  ``sk = (rho, tr, key, s1, s2, t0)``: secret key
   -  ``matrix``: public key matrix :math:`\mathbf{A}` (corresponds to L. 9, Fig. 4, [Dilithium-R3]_)
   -  ``mu``: hash of ``tr`` and the message ``msg`` (corresponds to L. 10, Fig. 4, [Dilithium-R3]_)
   -  ``rng``: random number generator
   -  ``m``: Dilithium mode providing parameters (``gamma1``, ``gamma2``, ``beta``, ``omega``) and symmetric functions
   -  ``randomized``: whether randomized signing should be used

   **Output:**

   -  ``sig``: signature

   **Steps:**

   1. If ``randomized``, generate ``rhoprime`` using ``rng``, otherwise set ``rhoprime = H(key || mu)`` (L. 12, Fig. 4, [Dilithium-R3]_)
   2. For incremental ``nonce``: (L. 13, Fig. 4, [Dilithium-R3]_)

      1. ``y = polyvecl_uniform_gamma1(rhoprime, nonce, m)`` (L. 14, Fig. 4, [Dilithium-R3]_)
      2. ``w1 = A*y`` (L. 15, Fig. 4, [Dilithium-R3]_)
      3. ``(w1, w0) = w1.polyvec_decompose()`` (L. 16, Fig. 4, [Dilithium-R3]_)
      4. ``sm = H(mu || w1)`` (L. 17, Fig. 4, [Dilithium-R3]_)
      5. ``cp = Polynomial::poly_challenge(sm, m)`` (L. 18, Fig. 4, [Dilithium-R3]_)
      6. ``z = y + c*s1`` (L. 19, Fig. 4, [Dilithium-R3]_)
      7. If ``z.polyvec_chknorm(gamma1 - beta)``, continue with next iteration (Check on :math:`\mathbf{z}`, L. 21, Fig. 4, [Dilithium-R3]_)
      8. ``w0 = w0 - c*s2`` (L. 20, Fig. 4, [Dilithium-R3]_)
      9. If ``w0.polyvec_chknorm(gamma2 - beta)``, continue with next iteration (Check on :math:`\mathbf{r_0}`, L. 21, Fig. 4, [Dilithium-R3]_)
      10. ``h = c*t0``
      11. If ``h.polyvec_chknorm(gamma2)``, continue with next iteration (First check on :math:`c\mathbf{t0}`, L. 24, Fig. 4, [Dilithium-R3]_)
      12. ``w0 = w0 + h``
      13. ``(h, n) = PolynomialVector::generate_hint_polyvec(w0, w1, m)`` (``h`` is the hint vector, ``n`` the amount of 1's in ``h``; L. 23, Fig. 4, [Dilithium-R3]_, see `Hint Generation`_)
      14. If ``n > omega``, continue with the next iteration (Last check, L. 24, Fig. 4, [Dilithium-R3]_)
      15. ``sig = (z, h, c)`` (L. 26, Fig. 4, [Dilithium-R3]_)
      16. Break loop

   **Notes:**

   - ``matrix`` is already generated in NTT representation in the constructor via ``matrix = PolynomialMatrix::generate_matrix(rho, m)``.
   - ``mu = H(tr || msg)`` is already computed beforehand (in the constructor and using the ``update(msg)`` function).
   - NTTs are performed as indicated by the comments in Fig. 4, [Dilithium-R3]_.
   - ``nonce`` here is incremented by 1 but multiplied by ``l`` within the called function ``polyvecl_uniform_gamma1``.
   - ``w0`` corresponds to :math:`\mathbf{r_0}` in Fig. 4, [Dilithium-R3]_ and is computed directly via the decomposition of ``A*y`` and subtraction with ``c*s2``.
   - Botan's hint generation differs slightly from [Dilithium-R3]_. This is discussed in `Hint Generation`_.


.. _pubkey_signature/dilithium/val:

Signature Validation
--------------------

The signature validation follows the :math:`\mathsf{Verify}` algorithm of Figure 4 of [Dilithium-R3]_. It is
implemented in the ``Dilithium_Verification_Operation`` class (see :srcref:`[src/lib/pubkey/dilithium/dilithium_common]/dilithium.cpp:440|is_valid_signature`), which receives the public key via the constructor.
Message bytes are given to the object via consecutive calls of ``Dilithium_Verification_Operation::update``.

.. admonition:: Dilithium_Verification_Operation::is_valid_signature()

   **Input:**

   -  ``pk = (rho, t_1, tr)``: public key
   -  ``matrix``: public key matrix :math:`\mathbf{A}` (corresponds to L. 27, Fig. 4, [Dilithium-R3]_)
   -  ``mu``:  hash of ``tr`` and the message ``msg`` (corresponds to L. 28, Fig. 4, [Dilithium-R3]_)
   -  ``sig = (z, h, c)``: the signature
   -  ``m``: Dilithium mode providing parameters (``gamma1``, ``gamma2``, ``beta``, ``omega``) and symmetric functions

   **Output:**

   -  ``true``, if the signature for message ``msg`` is valid. ``false`` otherwise.

   **Steps:**

   1. Check that the signature has the appropriate length and extract its parameters. Return ``false`` if
      the signature length is invalid, ``z`` is no valid signature vector (i.e., ``z.polyvec_chknorm(gamma1 - beta)``), or
      ``h`` is no valid hint vector (i.e., ``amount of 1's in h > omega``) (first and third check of L. 31, Fig. 4, [Dilithium-R3]_)
   2. ``cp = Polynomial::poly_challenge(c)`` (L. 29, Fig. 4, [Dilithium-R3]_)
   3. ``w1 = A*z - c*t*2^d`` (Second input of L. 30, Fig. 4, [Dilithium-R3]_)
   4. ``w1 = PolynomialVector::polyvec_use_hint(h, w1, m)`` (L. 30, Fig. 4, [Dilithium-R3]_)
   5. Signature is valid if ``c == H(mu || w1)`` (L. 31, Fig. 4, [Dilithium-R3]_)

   **Notes:**

   - ``matrix`` is already generated in NTT representation in the constructor via ``matrix = PolynomialMatrix::generate_matrix(rho, m)``.
   - NTTs are performed as indicated by the comments in Fig. 4, [Dilithium-R3]_.
   - mu = ``H(tr || msg)`` is already computed beforehand (in the constructor and using the ``update(msg)`` function).


.. _pubkey_signature/dilithium/hint:

Hint Generation
---------------

Dilithium uses a simple technique to reduce the size of the public key.
Given the public matrix :math:`\mathbf{A}` and :math:`\mathbf{t} = \mathbf{As_1} + \mathbf{s_2}`, the public key only contains the "high-order" bits :math:`\mathbf{t_1}` of :math:`\mathbf{t}`.
However, Dilithium's verification algorithm requires computation of the high bits of the sum :math:`\mathbf{Az}-c\mathbf{t}` (see Section 1.1 of [Dilithium-R3]_).
This computation cannot be conducted solely with :math:`\mathbf{t_1}` because carries from the subtraction with the product of :math:`c` and the missing "lower-order" bits :math:`\mathbf{t_0}` may influence the high bits of the result.
In order to still use only :math:`\mathbf{t_1}` in the public key, Dilithium computes a "hint" as part of the signature that indicates the carries.
The corresponding simple algorithm is :math:`\mathsf{MakeHint}_q` specified in Figure 3 of [Dilithium-R3]_.

More concretely, the goal of the hint is as follows: given :math:`\mathbf{A}\mathbf{z} - c\mathbf{t_1}\cdot 2^d = \mathbf{w}-c\mathbf{s_2}+c\mathbf{t_0}` and the hint, one can recover :math:`\mathbf{w_1}`.
The hint generation of [Dilithium-R3]_ uses inputs :math:`(\mathbf{w}-c\mathbf{s_2}+c\mathbf{t_0},-c\mathbf{t_0})`.
However, like the reference implementation of [Dilithium-R3]_, Botan's hint computation operates on inputs ``(w0 - c*s2 + c*t0, w1)`` and slightly differs to Figure 3 of [Dilithium-R3]_.
Despite this, Botan's hint computation is equivalent to the hint generation of the specification.

To show the equivalence, we expand the definition of the :math:`[[\ ]]`-operator to vectors, i.e., :math:`[[ \mathbf{u} = \mathbf{v} ]]` returns a vector :math:`\mathbf{b} \in \mathbb{F}_2^{n \cdot k}` comparing all polynomial coefficients of both vectors element-wise.
Then, [Dilithium-R3]_ computes the hint vector as follows:

.. math:: \mathbf{h} = \mathbf{1} - [[ \mathsf{HighBits}_q(\mathbf{w} - c \mathbf{s_2} + c\mathbf{t_0}, 2\gamma_2) = \mathsf{HighBits}_q(\mathbf{w} - c \mathbf{s_2}, 2\gamma_2)  ]]

According to Section 3.3, Equation (3) of [Dilithium-R3]_, :math:`\mathsf{HighBits}_q(\mathbf{w} - c \mathbf{s_2}, 2\gamma_2)=\mathbf{w_1}`. Also, we can
write :math:`\mathbf{w} = \mathbf{w_1} 2\gamma_2 + \mathbf{w_0}`. We get:

.. math:: \mathbf{h} = \mathbf{1} - [[ \mathsf{HighBits}_q(\mathbf{w_1} 2\gamma_2 + \mathbf{w_0} - c \mathbf{s_2} + c\mathbf{t_0}, 2\gamma_2) = \mathbf{w_1} ]]

Since :math:`\|\mathbf{w_0} - c \mathbf{s_2}\|_{\infty} < \gamma_2 - \beta` (second check of L. 21, Fig. 4, [Dilithium-R3]_) and :math:`\|c\mathbf{t_0}\|_{\infty} \leq \gamma_2` (first check of L. 24, Fig. 4, [Dilithium-R3]_), we know that:

.. math:: \|\mathbf{w_0} - c \mathbf{s_2} + c\mathbf{t_0}\|_{\infty} < 2 \gamma_2 - \beta

In the following, we will look at the 1-bit hint :math:`h` creation of single polynomial coefficients :math:`x \in \mathbb{Z}_q` of vector elements of :math:`(\mathbf{w_0} - c \mathbf{s_2} + c\mathbf{t_0})` and coefficients :math:`w_1 \in \mathbb{Z}_q` of vector elements of :math:`\mathbf{w_1}`.
Two cases are distinguished.

**Case 1.** :math:`w_1 \neq 0`:

:math:`w_1 2 \gamma_2 \in [2 \gamma_2, 4 \gamma_2, ..., (q-1) - 2 \gamma_2]` and therefore:

.. math:: \beta < w_1 2 \gamma_2 + x < (q-1) - \beta

According to the constructions of :math:`\mathsf{HighBits}_q` and :math:`\mathsf{Decompose}_q`, we get via L. 23, Figure 3 of [Dilithium-R3]_:

.. math::
    & \mathsf{HighBits}_q(w_1 2 \gamma_2 + x, 2 \gamma_2)

   =& \frac{(w_1 2 \gamma_2 + x) - (w_1 2 \gamma_2 + x\ \textrm{mod}^{\pm}\ 2 \gamma_2)}{2 \gamma_2}

   =& \frac{w_1 2 \gamma_2 + x - (x\ \textrm{mod}^{\pm}\ 2 \gamma_2)}{2 \gamma_2}

which equals :math:`w_1` if and only if

.. math:: (x\ \textrm{mod}^{\pm}\ 2 \gamma_2) = x

Therefore, :math:`\mathsf{HighBits}_q(w_1 2 \gamma_2 + x, 2\gamma_2) = w_1` (and equivalently :math:`h=0`) if and only if:

.. math:: -\gamma_2 < x \leq \gamma_2

**Case 2.** :math:`w_1 = 0`:

The equation gets:

.. math:: \mathsf{HighBits}_q(x, 2 \gamma_2) = 0

According to the construction, this equation is true for all values of:

.. math:: -\gamma_2 < x \leq \gamma_2

but also for :math:`x = -\gamma_2`. Hence, the hint becomes :math:`0` if and only if

.. math:: -\gamma_2 \leq x \leq \gamma_2

To demonstrate this, we need to show that
:math:`\mathsf{HighBits}_q(-\gamma_2, 2 \gamma_2) = 0`. In particular, we show that :math:`\mathsf{Decompose}_q(-\gamma_2, 2 \gamma_2)` returns :math:`(0, -\gamma_2)`

It first computes:

.. math::
   r = - \gamma_2\ \textrm{mod}^{+}\ q = q - \gamma_2

Then, given that :math:`\gamma_2` divides :math:`q - 1`:

.. math::

   r_0 =& q - \gamma_2\ \textrm{mod}^{\pm}\ 2 \gamma_2 = (q-1)+1 - \gamma_2\ \textrm{mod}^{\pm}\ 2 \gamma_2 = -\gamma_2 + 1

   r - r_0 =& (q - \gamma_2) - (-\gamma_2 + 1) = q - 1

Hence, the special case occurs (L.21-22, Figure 3 of [Dilithium-R3]_) and we get :math:`r_1 = 0` and :math:`r_0 = -\gamma_2`.

Taking into account these cases where the hint becomes :math:`0`, Botan only checks the :math:`\gamma_2` bounds of coefficients :math:`x` of the input vector :math:`(\mathbf{w_0} - c \mathbf{s_2} + c\mathbf{t_0})`.
To distinguish both cases with slightly different boundaries, :math:`\mathbf{w_1}` must be given as well.

