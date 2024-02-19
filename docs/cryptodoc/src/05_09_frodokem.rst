.. _pubkey/frodokem:

FrodoKEM
=================

Botan's FrodoKEM implementation is found in
:srcref:`src/lib/pubkey/frodokem/` and follows [FrodoKEM-ISO]_.
The parameter sets shown in the tables below are supported.

.. _pubkey/frodokem/parameter_table:

.. table::  Supported FrodoKEM parameter sets (see Tables A.1 and A.2 of [FrodoKEM-ISO]_). ``<PRG>`` can either be ``AES`` or ``SHAKE``, depending on whether AES-128 or SHAKE-128 is used for expanding the seed for the matrix :math:`A`.

   +----------------------+------------------------+------------------------+-------------------------+
   | ``FrodoKEMMode``     | ``FrodoKEM-640-<PRG>`` | ``FrodoKEM-976-<PRG>`` | ``FrodoKEM-1344-<PRG>`` |
   +======================+========================+========================+=========================+
   | :math:`D`            | 15                     | 16                     | 16                      |
   +----------------------+------------------------+------------------------+-------------------------+
   | :math:`q`            | 32768                  | 65536                  | 65536                   |
   +----------------------+------------------------+------------------------+-------------------------+
   | :math:`n`            | 640                    | 976                    | 1344                    |
   +----------------------+------------------------+------------------------+-------------------------+
   | :math:`\overline{n}` | 8                      | 8                      | 8                       |
   +----------------------+------------------------+------------------------+-------------------------+
   | :math:`B`            | 2                      | 3                      | 4                       |
   +----------------------+------------------------+------------------------+-------------------------+
   | :math:`len_A`        | 128                    | 128                    | 128                     |
   +----------------------+------------------------+------------------------+-------------------------+
   | :math:`len_{sec}`    | 128                    | 192                    | 256                     |
   +----------------------+------------------------+------------------------+-------------------------+
   | :math:`\text{SHAKE}` | SHAKE-128              | SHAKE-256              | SHAKE-256               |
   +----------------------+------------------------+------------------------+-------------------------+
   | :math:`len_{SE}`     | 256                    | 384                    | 512                     |
   +----------------------+------------------------+------------------------+-------------------------+
   | :math:`len_{salt}`   | 256                    | 384                    | 512                     |
   +----------------------+------------------------+------------------------+-------------------------+

.. table::  Supported eFrodoKEM parameter sets (see Tables A.1 and A.2 of [FrodoKEM-ISO]_). Note that these are ephemeral modes of the algorithm and the public key may not be used more than once. ``<PRG>`` can either be ``AES`` or ``SHAKE``, depending on whether AES-128 or SHAKE-128 is used for expanding the seed for the matrix :math:`A`.

   +----------------------+-------------------------+-------------------------+--------------------------+
   | ``FrodoKEMMode``     | ``eFrodoKEM-640-<PRG>`` | ``eFrodoKEM-976-<PRG>`` | ``eFrodoKEM-1344-<PRG>`` |
   +======================+=========================+=========================+==========================+
   | :math:`D`            | 15                      | 16                      | 16                       |
   +----------------------+-------------------------+-------------------------+--------------------------+
   | :math:`q`            | 32768                   | 65536                   | 65536                    |
   +----------------------+-------------------------+-------------------------+--------------------------+
   | :math:`n`            | 640                     | 976                     | 1344                     |
   +----------------------+-------------------------+-------------------------+--------------------------+
   | :math:`\overline{n}` | 8                       | 8                       | 8                        |
   +----------------------+-------------------------+-------------------------+--------------------------+
   | :math:`B`            | 2                       | 3                       | 4                        |
   +----------------------+-------------------------+-------------------------+--------------------------+
   | :math:`len_A`        | 128                     | 128                     | 128                      |
   +----------------------+-------------------------+-------------------------+--------------------------+
   | :math:`len_{sec}`    | 128                     | 192                     | 256                      |
   +----------------------+-------------------------+-------------------------+--------------------------+
   | :math:`\text{SHAKE}` | SHAKE-128               | SHAKE-256               | SHAKE-256                |
   +----------------------+-------------------------+-------------------------+--------------------------+
   | :math:`len_{SE}`     | 128                     | 192                     | 256                      |
   +----------------------+-------------------------+-------------------------+--------------------------+
   | :math:`len_{salt}`   | 0                       | 0                       | 0                        |
   +----------------------+-------------------------+-------------------------+--------------------------+


The implementation consists of several components; these are shown in the table below.

.. _pubkey/frodokem/component_table:

.. table::  FrodoKEM components and file locations.

   +----------------------------------------------------------------+-----------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | Component                                                      | File                                                                  | Purpose                                                                                                                                                                                |
   +================================================================+=======================================================================+========================================================================================================================================================================================+
   | :ref:`Types <pubkey/frodokem/types>`                           | :srcref:`[src/lib/pubkey/frodokem]/frodokem_common/frodo_types.h`     | Strong types                                                                                                                                                                           |
   +----------------------------------------------------------------+-----------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | :ref:`Modes <pubkey/frodokem/modes>`                           | :srcref:`[src/lib/pubkey/frodokem]/frodokem_common/frodo_mode.h`      | Parameter set representation                                                                                                                                                           |
   +----------------------------------------------------------------+-----------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | :ref:`Constants <pubkey/frodokem/modes>`                       | :srcref:`[src/lib/pubkey/frodokem]/frodokem_common/frodo_constants.h` | Parameter set instantiations                                                                                                                                                           |
   +----------------------------------------------------------------+-----------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | :ref:`Matrix Operations <pubkey/frodokem/matrix_operations>`   | :srcref:`[src/lib/pubkey/frodokem]/frodokem_common/frodo_matrix.h`    | Matrices and operations on them                                                                                                                                                        |
   +----------------------------------------------------------------+-----------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   | FrodoKEM                                                       | :srcref:`[src/lib/pubkey/frodokem]/frodokem_common/frodokem.h`        | FrodoKEM :ref:`Key Generation <pubkey/frodokem/key_generation>`, :ref:`Encapsulation <pubkey/frodokem/encapsulation>`, :ref:`Decapsulation <pubkey/frodokem/decapsulation>`            |
   +----------------------------------------------------------------+-----------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Algorithm Internals
-------------------

..  _pubkey/frodokem/types:

Types
^^^^^

For similar reasons as for :ref:`SPHINCS+ strong types <signatures/sphincsplus/types>`,
Botan's FrodoKEM implementation relies on the use of strong types.
As most data is just defined as byte sequences, the usage of strong types ensures that
the correct data is used at each step of the computation.
More concretely, strong types are used for the different kinds of seeds, random samples, matrix
representations, and plaintexts as well as for the values
:math:`salt`, :math:`k`, and :math:`pkh` as found in [FrodoKEM-ISO]_.

..  _pubkey/frodokem/modes:

Modes and Constants
^^^^^^^^^^^^^^^^^^^

The implementation realizes all parameter sets shown in Table
:ref:`Supported FrodoKEM parameters <pubkey/frodokem/parameter_table>`.
Parameter sets are represented as instances of the enum-like class ``FrodoKEMMode``.
When a mode has been selected, the parameters as well as the function :math:`\text{SHAKE}` of [FrodoKEM-ISO]_ are instantiated
via the ``FrodoKEMConstants`` class. Furthermore, this class contains
the distribution table entries required for sampling from the error distribution (see Table A.4 of [FrodoKEM-ISO]_).

..  _pubkey/frodokem/matrix_operations:

Matrix Operations
^^^^^^^^^^^^^^^^^

FrodoKEM heavily relies on matrix operations which are implemented in Botan
within the ``FrodoMatrix`` class. Specifically, factory methods to create or store matrices
according to the :math:`Encode` (Section 7.2 of [FrodoKEM-ISO]_),
:math:`Decode` (Section 7.2), :math:`Pack` (Section 7.3), :math:`Unpack` (Section 7.3),
and :math:`SampleMatrix` (Section 7.4 and 7.5) functions are provided, thereby realizing
the respective functions in accordance with the specification.

The implementation does not explicitly provide the :math:`Gen` function (Section 7.6
of [FrodoKEM-ISO]_) to create the large public matrix :math:`A` from :math:`seed_A`.
Instead, to avoid having the entire matrix :math:`A` in memory for just one use per operation,
the desired elements of :math:`A` are derived from :math:`seed_A` on demand when matrix
multiplication is performed. This is done via callable generator functions which generate
the required rows of :math:`A` and correspond to
Section 7.6.1 or 7.6.2 of [FrodoKEM-ISO]_, depending on whether AES-128 or SHAKE-128 is used.

Moreover, the implementation does not perform the transpose operation on the matrix
:math:`S^T` to obtain :math:`S` as in the pseudocode of Section 8 of [FrodoKEM-ISO]_
when computing :math:`B = AS + E` and :math:`B'S` during key generation and decapsulation, respectively. Instead, it performs
the matrix operations directly on input :math:`S^T` to obtain the desired result
without an expensive transpose operation.

Consequently, each unique combination of matrix operations used by FrodoKEM
:ref:`Key Generation <pubkey/frodokem/key_generation>`,
:ref:`Encapsulation <pubkey/frodokem/encapsulation>` and
:ref:`Decapsulation <pubkey/frodokem/decapsulation>` is implemented as a
``FrodoMatrix`` factory method. Hence, the operations :math:`AS + E`, :math:`S'A + E'`,
:math:`S'B + E''` and :math:`B'S` each have a corresponding method. Additionally, generic
addition and subtraction methods are provided.
The methods for :math:`AS + E` and :math:`S'A + E'` make use of manual loop unrolling
to speed up performance according to [BORSvV21]_.

Since the implementations of the underlying matrix operations
do not perform the neccessary reduction :math:`\text{mod}\, q`, a ``FrodoMatrix``
possesses a ``reduce`` method, reducing all elements modulo :math:`q` and thereby
producing matrices with entries in :math:`\mathbb{Z}_q` as required by [FrodoKEM-ISO]_.

Finally, the ``FrodoMatrix`` class contains the method ``constant_time_compare``
which uses Botan's constant time comparison to check for equality of the object
matrix to another input matrix in constant time. This is used during
decapsulation, specifically in Step 14 of :ref:`Key Decapsulation
<pubkey/frodokem/decapsulation>`, to ensure that the re-encryption yields the
same ciphertext as the presented encapsulation.

..  _pubkey/frodokem/key_generation:

Key Generation
--------------

FrodoKEM key generation follows Section 8.1 of [FrodoKEM-ISO]_ and is
implemented within ``FrodoKEM_PrivateKey`` constructor (see: :srcref:`[src/lib/pubkey/frodokem/frodokem_common]/frodokem.cpp:303|FrodoKEM_PrivateKey`).
It works as follows:

.. admonition:: FrodoKEM Key Generation

   **Input:**

   -  ``rng``: random number generator

   **Output:**

   -  ``SK``, ``PK``: private and public key

   **Steps:**

   1. Generate new values ``s``, ``seed_se``, and ``z`` using ``rng``
   2. ``seed_a = SHAKE(z, len_a)``
   3. ``r = SHAKE(0x5F || seed_se, 32*n*n_bar)``
   4. ``s_trans = sample_matrix(r[:n*n_bar - 1])``
   5. ``e = sample_matrix(r[n*n_bar:])``
   6. ``b = a*s + e``
   7. | ``PK = {seed_a, pack(b)}``
      | ``pkh = SHAKE(PK, len_sec)``
      | ``SK = {s, seed_a, pack(b), s_trans, pkh}``

   **Notes:**

   - Computation of ``b = a*s + e`` is done by a specialised function that performs on-demand
     expansion of ``seed_a`` into the desired row of the matrix :math:`A` of [FrodoKEM-ISO]_
     and assumes getting the transpose ``s_trans`` of ``s`` as input to avoid transposition.
   - The operation ``pack(b)`` is performed when accessing the serialized or raw key bits of
     a key.
   - The computation of ``pkh`` is performed in the constructor of ``FrodoKEM_PublicKeyInternal``,
     an internal class used to represent ``PK``.
   - The creation of a ``FrodoKEM_PublicKey`` is conducted using the
     ``public_key`` method of the private key.

..  _pubkey/frodokem/encapsulation:

Key Encapsulation
-----------------

The FrodoKEM encapsulation procedure of Botan (see :srcref:`[src/lib/pubkey/frodokem/frodokem_common]/frodokem.cpp:89|raw_kem_encrypt`) follows Section 8.2 of [FrodoKEM-ISO]_ and
works as follows:

.. admonition:: FrodoKEM Encapsulation

   **Input:**

   - ``PK = {seed_a, packed_b}``: public key
   - ``rng``: random number generator

   **Output:**

   - ``encapsulated_key``: ciphertext of shared key
   - ``shared_key``: plaintext shared key

   **Steps:**

   1. Generate new values ``u`` and ``salt`` using ``rng``
   2.  ``seed_se || k = SHAKE(pkh || u || salt, len_se + len_sec)``
   3. ``r = SHAKE(0x96 || seed_se, 16*(2*n_bar*n + n_bar*n_bar))``
   4. ``s_p = sample_matrix(r[:n*n_bar - 1])``
   5. ``e_p = sample_matrix(r[n*n_bar:2*n*n_bar - 1])``
   6. ``b_p = s_p*a + e_p``
   7. ``c_1 = pack(b_p)``
   8. ``e_pp = sample_matrix(r[2*n*n_bar:])``
   9.  ``v = s_p*b + e_pp``
   10. ``c = v + encode(u)``
   11. ``c_2 = pack(c)``
   12. ``encapsulated_key = c_1 || c_2 || salt``
   13. ``shared_key = SHAKE(encapsulated_key || k, len_sec)``

   **Notes:**

   - The computation of ``pkh`` is already performed in the constructor of ``FrodoKEM_PublicKeyInternal``,
     an internal class used to represent ``PK``.
   - ``b = unpack(packed_b)`` is already performed in the constructor of ``FrodoKEM_PublicKey``.
   - The computation of ``s_p*a + e_p`` is done by a specialised function that performs on-demand
     expansion of ``seed_a`` into the desired row of the matrix :math:`A` of [FrodoKEM-ISO]_.
   - The computation of ``s_p*b + e_pp`` is done by a specialised function realising this sequence
     of operations.

..  _pubkey/frodokem/decapsulation:

Key Decapsulation
-----------------

The FrodoKEM decapsulation procedure of Botan (see :srcref:`[src/lib/pubkey/frodokem/frodokem_common]/frodokem.cpp:156|raw_kem_decrypt`) follows Section 8.3 of [FrodoKEM-ISO]_ and
works as follows:

.. admonition:: FrodoKEM Decapsulation

   **Input:**

   -  ``SK = {s, seed_a, packed_b, s_trans, pkh}``: secret key
   -  ``encap_key = c_1 || c_2 || salt``: encapsulated key bytes

   **Output:**

   -  ``shared_key``: shared key

   **Steps:**

   1. ``b_p = unpack(c_1, n_bar, n)``
   2. ``c = unpack(c_2, n_bar, n_bar)``
   3. ``m = c - b_p*s``
   4. ``seed_u_p = decode(m)``
   5.  ``seed_se_p || k_p = SHAKE(pkh || seed_u_p || salt, len_se + len_sec)``
   6. ``r = SHAKE(0x96 || seed_se_p, 16*(2*n_bar*n + n_bar*n_bar))``
   7. ``s_p = sample_matrix(r[:n*n_bar - 1])``
   8. ``e_p = sample_matrix(r[n*n_bar:2*n*n_bar - 1])``
   9.  ``b_pp = s_p*a + e_p``
   10. ``e_pp = sample_matrix(r[2*n*n_bar:])``
   11. ``v = s_p*b + e_pp``
   12. ``c_p = v + encode(seed_u_p)``
   13. ``b_pp.reduce()`` and ``c_p.reduce()``
   14. If ``b_p = b_pp`` and ``c = c_p`` set ``k_bar = k_p``, otherwise set ``k_bar = s``
   15. ``shared_key = SHAKE(encap_key || k_bar, len_sec)``

   **Notes:**

   - The computation of ``b_p*s`` is done by a specialised function working on the input ``s_trans``.
   - The computations of ``s_p*a + e_p`` and ``s_p*b + e_pp`` are done by specialised functions,
     as noted in :ref:`FrodoKEM Encapsulation <pubkey/frodokem/encapsulation>`.
   - ``b = unpack(packed_b)`` is already performed in the constructor of ``FrodoKEM_PrivateKey``.
   - ``b_pp`` and ``c_p`` require manual reduction in Step 13 because ``b_p`` and ``c`` are
     already reduced due to the packing operations. This is the only time where a
     reduction needs to be implemented.
   - Comparisons and assignments of Step 14 are performed in constant time (CT) using Botan's CT
     utilities (CT comparisons of ``b_p = b_pp`` and ``c = c_p`` via
     ``FrodoMatrix.constant_time_compare``, a CT logical AND of the result,
     and a CT conditional select to set ``k_bar``).

