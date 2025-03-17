.. _pubkey/slh_dsa:

SLH-DSA
=======

Botan's implementation of the Stateless Hash-Based Digital Signature Standard
(SLH-DSA) is found in
:srcref:`src/lib/pubkey/sphincsplus/` and follows [FIPS-205]_.

BSI's [TR-02102-1]_ recommends using SLH-DSA in "hedged" mode with the parameter
sets that fulfill NIST's category 3 and 5 ("192" or "256", with botn SHA2 or
SHAKE and either fast or small). Hash-based signatures are considered secure for
long-term secure authentication and are not required to be used in a hybrid form
with a classical signature method.

Algorithm Internals
-------------------

SLH-DSA is composed of Forest Of Random Subsets (FORS) few-time signatures
and Winternitz One-Time Signatures (WOTS\ :sup:`+`), which are used within
hypertree signatures (a variant of XMSS\ :sup:`MT`). In short, messages
are signed via FORS. The FORS public key is signed via XMSS with WOTS\ :sup:`+`
as part of the hypertree. The root of the top-level tree in the hypertree
structure then essentially represents the SLH-DSA root.
Table :ref:`SLH-DSA logical components <signatures/slh_dsa/table>`
provides an overview of these components and their Botan implementations. The
:ref:`SLH-DSA <signatures/slh_dsa/slh_dsa>` component, by making use of
the other components, provides the overall signature generation and verification
operations.

.. _signatures/slh_dsa/table:

.. table::  SLH-DSA logical components and file locations.
   :widths: 15 25 45 15

   +------------------------------------------------------------+---------------------------------------------------------------------------+--------------------------------------------+------------------------------+
   |  Component                                                 | File                                                                      | Purpose                                    | Section in [FIPS-205]_       |
   +============================================================+===========================================================================+============================================+==============================+
   | :ref:`Types <signatures/slh_dsa/types>`                    | :srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sp_types.h`      | Strong types                               |                              |
   +------------------------------------------------------------+---------------------------------------------------------------------------+--------------------------------------------+------------------------------+
   | :ref:`Addresses <signatures/slh_dsa/address>`              | :srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sp_address.h`    | Address representation and manipulation    | 4.2, 4.3                     |
   +------------------------------------------------------------+---------------------------------------------------------------------------+--------------------------------------------+------------------------------+
   | :ref:`Parameters <signatures/slh_dsa/parameters>`          | :srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sp_parameters.h` | Parameter set instantiations               | 11                           |
   +------------------------------------------------------------+---------------------------------------------------------------------------+--------------------------------------------+------------------------------+
   | :ref:`Hashes <signatures/slh_dsa/hashes>`                  | :srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sp_hash.h`       | All hash functions                         | 11.1, 11.2                   |
   +------------------------------------------------------------+---------------------------------------------------------------------------+--------------------------------------------+------------------------------+
   | :ref:`Treehash <signatures/slh_dsa/treehash>`              | :srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sp_treehash.h`   | Merkle tree hashing for FORS and XMSS      | 6.1, 8.2                     |
   +------------------------------------------------------------+---------------------------------------------------------------------------+--------------------------------------------+------------------------------+
   | :ref:`FORS <signatures/slh_dsa/fors>`                      | :srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sp_fors.h`       | FORS signature                             | 8                            |
   +------------------------------------------------------------+---------------------------------------------------------------------------+--------------------------------------------+------------------------------+
   | :ref:`WOTS+ <signatures/slh_dsa/wotsplus>`                 | :srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sp_wots.h`       | WOTS\ :sup:`+` signature                   | 5                            |
   +------------------------------------------------------------+---------------------------------------------------------------------------+--------------------------------------------+------------------------------+
   | :ref:`XMSS <signatures/slh_dsa/xmss>`                      | :srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sp_xmss.h`       | XMSS signature                             | 6                            |
   +------------------------------------------------------------+---------------------------------------------------------------------------+--------------------------------------------+------------------------------+
   | :ref:`Hypertree <signatures/slh_dsa/hypertree>`            | :srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sp_hypertree.h`  | Hypertree signature                        | 7                            |
   +------------------------------------------------------------+---------------------------------------------------------------------------+--------------------------------------------+------------------------------+
   | :ref:`SLH-DSA Internal <signatures/slh_dsa/internal>`      | :srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sphincsplus.h`   | SLH-DSA internal functions                 | 9                            |
   +------------------------------------------------------------+---------------------------------------------------------------------------+--------------------------------------------+------------------------------+
   | :ref:`SLH-DSA <signatures/slh_dsa/slh_dsa>`                | :srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sphincsplus.h`   | SLH-DSA signature                          | 10                           |
   +------------------------------------------------------------+---------------------------------------------------------------------------+--------------------------------------------+------------------------------+

.. _signatures/slh_dsa/types:

Types
^^^^^

In Botan's SLH-DSA implementation, the concept of strong types is
used. A strong type can be used to create unique C++ types for data that is
semantically different, but operates on the same internal data structures.
SLH-DSA mainly operates on byte vectors in various contexts (e.g.,
XMSS tree nodes, WOTS\ :sup:`+` chain node, public/secret seeds, etc.), as well
as combined contexts like a WOTS\ :sup:`+` signature composed of multiple
WOTS\ :sup:`+` nodes. In SLH-DSA, every context is represented by a
separate strong type. The usage of strong types creates a much clearer and more
self-documenting interface, which also guarantees that no data is misused in the
wrong context. More details on all defined strong types and their interpretation
are documented in the respective header file.

.. _signatures/slh_dsa/address:

Addresses
^^^^^^^^^

Section 4.2 of [FIPS-205]_ defines a 32-byte address as an additional
domain separating input to SLH-DSA's hash and pseudorandom functions.
Botan wraps this address specification
into a class ``Sphincs_Address``. Methods for getting, copying, and setting
specified fields of an address are provided as well as constants. All constants,
fields, and representations are set as specified in Section 4.2 of [FIPS-205]_.

.. _signatures/slh_dsa/parameters:

Parameters
^^^^^^^^^^

The class ``Sphincs_Parameters`` represents all parameters of SLH-DSA.
It checks whether provided parameters are valid and can be created from a given
``Sphincs_Parameter_Set``, representing each set of Table :ref:`Supported
SLH-DSA parameter sets <pubkey_key_generation/slh_dsa/params_table>`.
Parameters that can be computed directly from the parameter set are calculated
in the constructor and stored as members instead of being calculated on demand.

.. _signatures/slh_dsa/hashes:

Hashes
^^^^^^

Botan implements the SHA2 and SHAKE versions of SLH-DSA as different
modules. All hash functions used within SLH-DSA are represented by the
class ``Sphincs_Hash_Functions``, which can be instantiated from given
parameters and the public seed ``pub_seed``. The public seed is given at
creation because all calls to the ``T`` and ``PRF`` functions use the public
seed as input. All underlying hash function members are instantiated in the
constructor according to Sections 11.1 and 11.2 of [FIPS-205]_. The specific
child classes for the SHA2 and SHAKE modules are given in
:srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sphincsplus_sha2_base/sp_hash_sha2.h` and
:srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sphincsplus_shake_base/sp_hash_shake.h`.

respectively.

The specification defines three tweaked hash functions that share similarities.
:math:`\mathbf{T_\ell}` is a tweaked hash function with a message input length
of :math:`\ell n` bytes. :math:`\mathbf{F}` and :math:`\mathbf{H}` are simply
defined as :math:`\mathbf{T_1}` and :math:`\mathbf{T_2}`. For clarity and
convenience, Botan omits the additional definitions by only implementing and
calling the method ``T``, which allows for arbitrary input lengths.

.. _signatures/slh_dsa/treehash:

Merkle Tree Computation
^^^^^^^^^^^^^^^^^^^^^^^

Botan generalizes the Merkle tree creation Algorithms 9
(:math:`\mathtt{xmss\_node}`) and 15 (:math:`\mathtt{fors\_node}`) of
[FIPS-205]_ using a single function
``treehash``. This
approach minimizes duplicate code while being in accordance with the
specification. However, in contrast to the algorithms specified in [FIPS-205]_
Botan uses an iterative approach instead of a recursive one.
The only difference between the Merkle tree root node computation
of FORS and XMSS is the creation of leaf nodes. Therefore, ``treehash``
takes a callback function for the leaf creation logic as an additional argument.
This callback function also handles the hash function addresses according to its
purpose. The used callback functions are ``xmss_gen_leaf`` (for XMSS; see
:ref:`SLH-DSA XMSS <signatures/slh_dsa/xmss>`) and ``fors_gen_leaf``
(for FORS; see :ref:`SLH-DSA FORS <signatures/slh_dsa/fors>`).

Another generalization of the specification that is also adapted from the
reference implementation is the integration of authentication path computations
into the ``treehash`` function. To achieve this, the function also takes the
index of the leaf for which to compute the authentication path. When building up
the Merkle tree, the function adds currently computed nodes to the
authentication path if they are contained in it. Alternatively, if only the root
node is requested (i.e. when computing :math:`\mathbf{PK}.\mathsf{root}`), the
leaf index can be set to an empty value, in which case no authentication path is
computed.

Furthermore, the same generalization ideas are applied to the root computation
from a signature, i.e., Algorithms 11 (:math:`\mathtt{xmss\_pkFromSig}`) and 17
(:math:`\mathtt{fors\_pkFromSig}`) of [FIPS-205]_. Botan's function
``compute_root`` computes the root of a Merkle tree using a leaf and its
authentication path. For both XMSS and FORS, the logic is the same, with the
only condition being that correctly preconfigured hash function addresses must
be passed to the function.

.. _signatures/slh_dsa/fors:

FORS
^^^^

As recommended in [FIPS-205]_, Section 3.2, the FORS few-time signature scheme
is not part of the public API. Botan only implements the FORS methods relevant
to SLH-DSA. This is :math:`\mathtt{fors\_sign}` of [FIPS-205]_
(Algorithm 16) and :math:`\mathtt{fors\_pkFromSig}` of [FIPS-205]_
(Algorithm 17). More concretely,
both methods are combined into Botan's ``fors_sign_and_pkgen``, which computes
both the signature and the FORS public key. The authentication path computation
therein and :math:`\mathtt{fors\_node}` of [FIPS-205]_ (Algorithm 15) are
implemented in the generalized ``treehash`` (see
:ref:`Merkle Tree Computation <signatures/slh_dsa/treehash>`), whereby
:math:`\mathtt{fors\_skGen}` of [FIPS-205]_ (Algorithm 14) is implemented
within the callback function ``fors_gen_leaf`` supplied to ``treehash``.
Similarly, the computation of the root and authentication path in the
implementation of :math:`\mathtt{fors\_pkFromSig}` utilizes the generalized
``compute_root`` method (see :ref:`Merkle Tree Computation
<signatures/slh_dsa/treehash>`), resulting in the method
``fors_public_key_from_signature``.

.. _signatures/slh_dsa/wotsplus:

WOTS\ :sup:`+`
^^^^^^^^^^^^^^

The implementation of WOTS\ :sup:`+` in the context of SLH-DSA is
based on [FIPS-205]_ with some adaptions of the SLH-DSA reference
implementations. In the same manner as FORS, it utilizes a generalization that
fuses the WOTS\ :sup:`+` public key and signature creation, i.e., the algorithms
:math:`\mathtt{wots\_pkGen}` (Algorithm 6) and
:math:`\mathtt{wots\_sign}` (Algorithm 7) of [FIPS-205]_, into
one method. When building up an XMSS tree, all leaf nodes must be computed,
which are the hashed WOTS\ :sup:`+` public keys. Only one leaf is used to sign
the underlying root. The WOTS\ :sup:`+` signature consists of values that are
computed in every public key creation; these values are elements of the
WOTS\ :sup:`+` hash chains. This observation leads to Botan's
``wots_sign_and_pkgen`` method that combines both logics, i.e., the entire
WOTS\ :sup:`+` chains are computed for the public key while the WOTS\ :sup:`+`
signature values are extracted at the same time if the current leaf is the
signing one.

.. _signatures/slh_dsa/XMSS:

XMSS
^^^^

**Remark:** Botan's implementation of the XMSS logic of SLH-DSA is
specifically tailored to SLH-DSA and separate from Botan's standalone
XMSS implementation (see :ref:`XMSS Key Generation <pubkey_key_generation/xmss>`
and :ref:`XMSS Signatures <signatures/xmss>`). This is due to the differences in
their tweaked hash applications, including a different hash function addressing.
Also, it is in accordance with the implementation considerations given by
[FIPS-205]_, Section 3.2.

To create a single XMSS signature, the building blocks of the preceding sections
are composed into the function ``xmss_sign_and_pkgen``. The generic ``treehash``
function (see :ref:`Merkle Tree Computation <signatures/slh_dsa/treehash>`)
is the
core logic of XMSS. For generating leaves, it uses the provided callback
function ``xmss_gen_leaf``, which calls ``wots_sign_and_pkgen`` (see :ref:`WOTS+
<signatures/slh_dsa/wotsplus>`) since XMSS leaves are hashed WOTS\ :sup:`+`
public keys. This callback function contains all necessary parameters including
the index of the leaf to sign, the message to sign (already divided into
:math:`lg_w` sized chunks), and the required hash function addresses.

While ``xmss_gen_leaf`` creates and stores the neccessary WOTS\ :sup:`+`
signature, ``treehash`` adds the authentication path to the XMSS signature when
building up the XMSS Merkle tree. Therefore, ``xmss_sign_and_pkgen`` creates its
XMSS root node and signature for a given leaf index and message and covers both
Algorithm 10 (:math:`\mathtt{xmss\_sign}`) and Algorithm 11
(:math:`\mathtt{xmss\_pkFromSig}`) of [FIPS-205]_.

For public key creation, i.e., the creation of :math:`\mathbf{PK}.\mathsf{root}`,
the function ``xmss_gen_root`` is used. It uses ``xmss_sign_and_pkgen`` with an
empty leaf index to only create the root node (see :ref:`Merkle Tree Computation
<signatures/slh_dsa/treehash>` invoked by ``xmss_sign_and_pkgen``).
Algorithm 11 (:math:`\mathtt{xmss\_pkFromSig}`), i.e., the reconstruction of an
XMSS root node using an XMSS signature, is achieved by calling the function
``compute_root`` (see :ref:`Merkle Tree Computation <signatures/slh_dsa/treehash>`).

.. _signatures/slh_dsa/hypertree:

Hypertree
^^^^^^^^^

The XMSS hypertree signature creation according to Algorithm 12 of [FIPS-205]_
(:math:`\mathtt{ht\_sign}`) is implemented by the method ``ht_sign``. Beginning
at the hypertree's leaves, the hypertree is built up using subsecutive calls of
``xmss_sign_and_pkgen`` (see :ref:`XMSS <signatures/slh_dsa/XMSS>`)
with each call signing the root of the previous XMSS tree or the hypertree
signature's message for the first call. As described in :ref:`XMSS
<signatures/slh_dsa/XMSS>`, this also creates the XMSS root node used in the
next iteration. The leaf indices selected to sign the hypertree signature's
message or roots are computed according to the specification.

The hypertree verification, Algorithm 13  of [FIPS-205]_
(:math:`\mathtt{ht\_verify}`), is performed in ``ht_verify``. By calling
``compute_root``, it reconstructs the roots from bottom to top using the
concatenated XMSS signatures. For verification, the final root, which is the
root of the hypertree, is compared with :math:`\mathbf{PK}.\mathsf{root}`.

.. _signatures/slh_dsa/internal:

SLH-DSA Internal Functions
^^^^^^^^^^^^^^^^^^^^^^^^^^

The functions :math:`\mathtt{slh\_sign\_internal}` (Algorithm 19) and
:math:`\mathtt{slh\_verify\_internal}` (Algorithm 20) are named in Botan as
specified by [FIPS-205]_.  As defined by the specification, these algorithms
utilize the hashes, FORS, and hypertree interfaces to create and verify SLH-DSA
signatures. The function :math:`\mathtt{slh\_keygen\_internal}` (Algorithm 18)
is implemented by the SLH-DSA private key's constructor, which also implements
the logic specified in :math:`\mathtt{slh\_keygen}`.

.. _signatures/slh_dsa/slh_dsa:

SLH-DSA
^^^^^^^

All the above components are combined to constitute Botan's SLH-DSA
component used for creating or verifying SLH-DSA signatures.

.. _pubkey_key_generation/slh_dsa:

Key Generation
--------------

Botan supports the parameter sets provided in Table 2 of [FIPS-205]_ for the
SHA2 and SHAKE instantiations of hash functions.
An overview is provided in Table
:ref:`Supported SLH-DSA parameter sets <pubkey_key_generation/slh_dsa/params_table>`.

.. _pubkey_key_generation/slh_dsa/params_table:

.. table::  Supported SLH-DSA parameter sets (see Table 2 of [FIPS-205]_). <hash> can either be ``SHA2`` or ``SHAKE``.

   +-------------------------+-----------+-----------+-----------+------------+-----------+-----------+--------------+-----------+
   | Parameter Set           | :math:`n` | :math:`h` | :math:`d` | :math:`h'` | :math:`a` | :math:`k` | :math:`lg_w` | :math:`m` |
   +=========================+===========+===========+===========+============+===========+===========+==============+===========+
   | ``SLH-DSA-<hash>-128s`` | 16        | 63        | 7         | 9          | 12        | 14        | 4            | 30        |
   +-------------------------+-----------+-----------+-----------+------------+-----------+-----------+--------------+-----------+
   | ``SLH-DSA-<hash>-128f`` | 16        | 66        | 22        | 3          | 6         | 33        | 4            | 34        |
   +-------------------------+-----------+-----------+-----------+------------+-----------+-----------+--------------+-----------+
   | ``SLH-DSA-<hash>-192s`` | 24        | 63        | 7         | 9          | 14        | 17        | 4            | 39        |
   +-------------------------+-----------+-----------+-----------+------------+-----------+-----------+--------------+-----------+
   | ``SLH-DSA-<hash>-192f`` | 24        | 66        | 22        | 3          | 8         | 33        | 4            | 42        |
   +-------------------------+-----------+-----------+-----------+------------+-----------+-----------+--------------+-----------+
   | ``SLH-DSA-<hash>-256s`` | 32        | 64        | 8         | 8          | 14        | 22        | 4            | 47        |
   +-------------------------+-----------+-----------+-----------+------------+-----------+-----------+--------------+-----------+
   | ``SLH-DSA-<hash>-256f`` | 32        | 68        | 17        | 4          | 9         | 35        | 4            | 49        |
   +-------------------------+-----------+-----------+-----------+------------+-----------+-----------+--------------+-----------+

SLH-DSA key generation follows Sections 9.1 and 10.1 of [FIPS-205]_ and is
implemented in :srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sphincsplus.cpp:311|SphincsPlus_PrivateKey`
within the ``SphincsPlus_PrivateKey`` constructor. It works as follows:

.. admonition:: SLH-DSA Key Generation

   **Input:**

   -  ``rng``: random number generator
   -  ``params``: SLH-DSA parameters

   **Output:**

   -  ``SK``, ``PK``: private and public key

   **Steps:**

   1. Generate new values ``sk_seed``, ``sk_prf``, and ``pub_seed`` using ``rng``.
   2. ``root = xmss_gen_root(sk_seed)``
      (see :ref:`XMSS <signatures/slh_dsa/XMSS>`).
   3. | ``SK = {sk_seed, sk_prf, pub_seed, root}``
      | ``PK = {pub_seed, root}``

   **Notes:**

   - Step 1 corresponds to Algorithm 21, and Steps 2-3 correspond to Algorithm 18 of [FIPS-205]_. All are performed in :srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sphincsplus.cpp:311|SphincsPlus_PrivateKey`.
   - The creation of a public key is conducted using the
     ``public_key`` method of the private key.
   - The addresses are set according to Algorithm 18 of [FIPS-205]_.

SPHINCS\ :sup:`+`
^^^^^^^^^^^^^^^^^

Botan supports the SPHINCS\ :sup:`+` Round 3.1 NIST submission [SPX-R3]_. The
SPHINCS\ :sup:`+` instances are activated using the ``sphincsplus_sha2`` and
``sphincsplus_shake`` modules, enabling their selection for key creation.
As with the SLH-DSA instances, they are provided to the constructors of the
SLH-DSA keys.
These instances are maintained solely for backwards compatibility. It is strongly
recommended to use the SLH-DSA instances instead.

Signature Creation
------------------

**Remark:** Signature creation with non-empty contexts is currently not
supported in Botan. Support for the pre-hash variant (HashSLH-DSA) of SLH-DSA is also not yet
available.

An SLH-DSA signature is created in the following manner, following
Algorithm 22 of [FIPS-205]_ (see :srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sphincsplus.cpp:361|sign`):

.. admonition:: SLH-DSA Signature Creation

   **Input:**

   -  ``rng``: random number generator
   -  ``m``: message to be signed
   -  ``SK = {sk_seed, sk_prf, pub_seed, root}``: SLH-DSA secret key

   **Output:**

   -  ``sig``:  SLH-DSA signature

   **Steps:**

   1. Generate new value ``addrnd`` using ``rng``. For the deterministic variant, set ``addrnd`` to ``NULL``.
   2. ``internal_msg = 0x00 || 0x00 || m`` (contexts are currently not supported).
   3. Create signature ``sig`` using ``slh_sign_internal``

      1. ``opt_rand = SK.pub_seed`` if ``addrnd == NULL``. Otherwise, set ``opt_rand`` to ``addrnd``.
      2. ``msg_random_s = PRF_msg(m, SK.prf, opt_rand)`` and set ``sig = msg_random_s``.
      3. ``(mhash, tree_idx, leaf_idx) = H_msg(msg_random_s, SK.root, m)``.
      4. Set tree address of ``fors_addr`` to ``tree_idx``, its type to ``ForsTree``, and its keypair address to ``leaf_idx``.
      5. ``(fors_sig, fors_root) = fors_sign_and_pkgen(mhash, SK.sk_seed, fors_addr)`` and append ``fors_sig`` to ``sig``.
      6. ``ht_sig = ht_sign(fors_root, SK.sk_seed, tree_idx, leaf_idx)`` and append ``ht_sig`` to ``sig``.


   **Notes:**

   - Steps 1-3 correspond to Algorithm 22 of [FIPS-205]_ and are performed in :srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sphincsplus.cpp:361|sign`.
   - Steps 4-9 correspond to Algorithm 19 of [FIPS-205]_ and are performed in :srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sphincsplus.cpp:381|slh_sign_internal`.
   - Steps 3.3, 3.5, 3.6: ``SK.pub_seed`` is omitted as an input because the hash functions are already instantiated with a corresponding member variable.
   - ``SK`` is passed to ``slh_sign_internal`` via member variables.

Signature Verification
----------------------

**Remark:** Signature verification with non-empty contexts is currently not
supported in Botan. Support for the pre-hash variant of SLH-DSA is also not yet
available.

An SLH-DSA signature is verified in the following manner, following
Algorithm 24 of [FIPS-205]_ (see :srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sphincsplus.cpp:206|is_valid_signature`):

.. admonition:: SLH-DSA Signature Verification

   **Input:**

   -  ``m``: message to be verified
   -  ``sig``: signature to be verified
   -  ``PK``: SLH-DSA public key, ``PK = {pub_seed, root}``

   **Output:**

   -  ``true``, if the signature for message ``m`` is valid. ``false`` otherwise

   **Steps:**

   1. ``internal_msg = 0x00 || 0x00 || m`` (contexts are currently not supported)
   2. The signature is valid iff ``slh_verify_internal(internal_msg, sig, PK) == true``

      1. Return ``false`` if the length of ``sig`` is invalid.
      2. Take the first ``n`` bytes of ``sig`` as value ``msg_random_s``.
      3. ``(mhash, tree_idx, leaf_idx) = H_msg(msg_random_s, PK.root, m)``.
      4. Set tree address of ``fors_addr`` to tree_idx, its type to ``ForsTree``, and its keypair address to ``leaf_idx``.
      5. Take the FORS signature bytes of ``sig`` as value ``fors_sig_s``.
      6. ``fors_root = fors_public_key_from_signature(mhash, fors_sig_s, fors_addr)``.
      7. Take the hypertree signature bytes of ``sig`` as value ``ht_sig_s``.
      8. The signature is valid iff ``ht_verify(fors_root, ht_sig_s, PK.root, tree_idx, leaf_idx) == true``.

   **Notes:**

   - Steps 1-2 correspond to Algorithm 24 of [FIPS-205]_ and are performed in :srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sphincsplus.cpp:206|is_valid_signature`.
   - Steps 3-10 correspond to Algorithm 20 of [FIPS-205]_ and are performed in :srcref:`[src/lib/pubkey/sphincsplus/sphincsplus_common]/sphincsplus.cpp:215|slh_verify_internal`.
   - Steps 2.3, 2.6, 2.8: ``PK.pub_seed`` is omitted as an input because the hash functions are already instantiated with a corresponding member variable.
   - ``PK`` is passed to ``slh_verify_internal`` via member variables.
   - The lengths of the FORS and the hypertree signatures are precomputed in the ``Sphincs_Parameters`` object.
