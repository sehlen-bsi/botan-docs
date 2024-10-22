.. _pubkey/hss_lms:

HSS/LMS
=======

Botan implements the Hierarchical Signature System (HSS) with Leighton-Micali
Hash-Based Signatures (LMS) as defined in [RFC8554]_ under consideration of
the recommendations of [SP800-208]_. It supports the parameter sets defined in
[RFC8554]_ and those in [draft-fluhrer-11]_.

Algorithm Internals
-------------------

The Hierarchical Signature System (HSS) with Leighton-Micali
Hash-Based Signatures (LMS) consists of multiple components.
Like most hash-based signature schemes,
it uses a One-Time Signature (OTS) at its base, named Leighton-Micali OTS
(LM-OTS). The public keys of multiple LM-OTS instances compose the leaves
of a Merkle tree, called the Leighton-Micali Signature (LMS) tree. The root node of the LMS
tree defines its public key. [RFC8554]_
also provides HSS, a hypertree composition of multiple LMS trees, where the leaves
of LMS trees sign the public keys of subsequent LMS trees.
Table :ref:`HSS/LMS logical components <pubkey/hss_lms/comp_table>` shows an
overview of these components and their Botan implementation.

.. _pubkey/hss_lms/comp_table:

.. table::  HSS/LMS logical components and file locations.

   +---------------------------------------+----------------------------------------------+---------------------------+-----------------------+
   |  Component                            | File                                         | Purpose                   | Section in [RFC8554]_ |
   +=======================================+==============================================+===========================+=======================+
   | :ref:`LM-OTS <pubkey/hss_lms/lm_ots>` | :srcref:`[src/lib/pubkey/hss_lms]/lm_ots.h`  | LM-OTS                    | 4.                    |
   +---------------------------------------+----------------------------------------------+---------------------------+-----------------------+
   | :ref:`LMS <pubkey/hss_lms/lms>`       | :srcref:`[src/lib/pubkey/hss_lms]/lms.h`     | LMS                       | 5.                    |
   +---------------------------------------+----------------------------------------------+---------------------------+-----------------------+
   | :ref:`HSS <pubkey/hss_lms/hss>`       | :srcref:`[src/lib/pubkey/hss_lms]/hss.h`     | HSS with LMS              | 6.                    |
   +---------------------------------------+----------------------------------------------+---------------------------+-----------------------+
   | HSS/LMS                               | :srcref:`[src/lib/pubkey/hss_lms]/hss_lms.h` | Botan's HSS/LMS interface |                       |
   +---------------------------------------+----------------------------------------------+---------------------------+-----------------------+

.. _pubkey/hss_lms/lm_ots:

LM-OTS
^^^^^^

LM-OTS is configured with several parameters displayed in Table :ref:`Supported LM-OTS parameter sets <pubkey/hss_lms/lm-ots-params>`.
``Hash`` specifies the hash function used.
Botan's implementation only allows one hash function for all
LMS trees and their LM-OTS algorithm (recommended in [RFC8554]_ and [SP800-208]_).
Another parameter, the width  ``w`` of the Winternitz coefficient, defines the
time-signature-size-tradeoff of the LM-OTS instance.
Those two parameters implicitly define the hash function output size ``n``,
the number of Winternitz chains ``p``, and the constant ``ls`` used for the
checksum computation (see [RFC8554]_ Section 4.1.). Botan allows all combinations
of hash function and ``w`` defined in [RFC8554]_ and [draft-fluhrer-11]_ and
listed here in Table :ref:`Supported LM-OTS parameter sets <pubkey/hss_lms/lm-ots-params>`.

.. _pubkey/hss_lms/lm-ots-params:

.. table::  Supported LM-OTS parameter sets

   +---------------------+--------------+-----+-----+-----+-----+--------+
   | Parameter Set Name  | Hash         | n   | w   | p   | ls  | id     |
   +=====================+==============+=====+=====+=====+=====+========+
   | LMOTS_SHA256_N32_W1 | SHA-256      | 32  | 1   | 265 | 7   | 0x0001 |
   +---------------------+--------------+-----+-----+-----+-----+--------+
   | LMOTS_SHA256_N32_W2 | SHA-256      | 32  | 2   | 133 | 6   | 0x0002 |
   +---------------------+--------------+-----+-----+-----+-----+--------+
   | LMOTS_SHA256_N32_W4 | SHA-256      | 32  | 4   | 67  | 4   | 0x0003 |
   +---------------------+--------------+-----+-----+-----+-----+--------+
   | LMOTS_SHA256_N32_W8 | SHA-256      | 32  | 8   | 34  | 0   | 0x0004 |
   +---------------------+--------------+-----+-----+-----+-----+--------+
   | LMOTS_SHA256_N24_W1 | SHA-256/192  | 24  | 1   | 200 | 8   | 0x0005 |
   +---------------------+--------------+-----+-----+-----+-----+--------+
   | LMOTS_SHA256_N24_W2 | SHA-256/192  | 24  | 2   | 101 | 6   | 0x0006 |
   +---------------------+--------------+-----+-----+-----+-----+--------+
   | LMOTS_SHA256_N24_W4 | SHA-256/192  | 24  | 4   | 51  | 4   | 0x0007 |
   +---------------------+--------------+-----+-----+-----+-----+--------+
   | LMOTS_SHA256_N24_W8 | SHA-256/192  | 24  | 8   | 26  | 0   | 0x0008 |
   +---------------------+--------------+-----+-----+-----+-----+--------+
   | LMOTS_SHAKE_N32_W1  | SHAKE256/256 | 32  | 1   | 265 | 7   | 0x0009 |
   +---------------------+--------------+-----+-----+-----+-----+--------+
   | LMOTS_SHAKE_N32_W2  | SHAKE256/256 | 32  | 2   | 133 | 6   | 0x000a |
   +---------------------+--------------+-----+-----+-----+-----+--------+
   | LMOTS_SHAKE_N32_W4  | SHAKE256/256 | 32  | 4   | 67  | 4   | 0x000b |
   +---------------------+--------------+-----+-----+-----+-----+--------+
   | LMOTS_SHAKE_N32_W8  | SHAKE256/256 | 32  | 8   | 34  | 0   | 0x000c |
   +---------------------+--------------+-----+-----+-----+-----+--------+
   | LMOTS_SHAKE_N24_W1  | SHAKE256/192 | 24  | 1   | 200 | 8   | 0x000d |
   +---------------------+--------------+-----+-----+-----+-----+--------+
   | LMOTS_SHAKE_N24_W2  | SHAKE256/192 | 24  | 2   | 101 | 6   | 0x000e |
   +---------------------+--------------+-----+-----+-----+-----+--------+
   | LMOTS_SHAKE_N24_W4  | SHAKE256/192 | 24  | 4   | 51  | 4   | 0x000f |
   +---------------------+--------------+-----+-----+-----+-----+--------+
   | LMOTS_SHAKE_N24_W8  | SHAKE256/192 | 24  | 8   | 26  | 0   | 0x0010 |
   +---------------------+--------------+-----+-----+-----+-----+--------+

In addition to these parameters, an LM-OTS
instance is defined by the identifier ``I`` of the LMS tree
and the index of its leaf ``q``, where the LM-OTS instance is located; this is
represented by the class ``OTS_Instance``.
For each LM-OTS instance, we can create a keypair with a secret key (class
``LMOTS_Private_Key``) and a public key (class ``LMOTS_Public_Key``). As recommended
by [SP800-208]_, Botan uses the pseudorandom key generation method of [RFC8554]_ Appendix A to
derive the secret key's Winternitz chain inputs (``x[]`` of [RFC8554]_). The inputs for this
method are the LM-OTS instance parameters and a
secret seed ``SEED`` associated with an LMS tree:

.. math::
   \mathtt{x[i]\ =\ Hash(I\ ||\ u32str(q)\ ||\ u16str(i)\ ||\ u8str(0xff)\ ||\ SEED)}

The public key is created by computing all Winternitz hash chains
beginning with their secret chain inputs ``x[]`` (see [RFC8554]_ Algorithm 1).
Besides the instance parameters, it contains the final hash value denoted as
``K`` in [RFC8554]_ Algorithm 1.

For creating an LM-OTS signature of a message, Botan offers the method
``LMOTS_Private_Key::sign``. For that, it implements Algorithm 1 of [RFC8554]_.
One important remark is the creation of the randomizer ``C``. To create this
randomizer, Botan adapts the same approach as the Cisco reference implementation
(see [RFC8554]_ Appendix E) by computing ``C`` with the following pseudorandom
key generation method:

.. math::
   \mathtt{C = Hash(I\ ||\ u32str(q)\ ||\ u16str(0xfffd)\ ||\ u8str(0xff)\ ||\ SEED)}

Note that the input for this hash computation will never collide with one of
the computations of the secret chain inputs since the chain index ``i`` will
never exceed ``0x0108``; in particular, it will not match ``0xfffd``.

A deterministic approach for computing ``C`` is essential since Botan does not store
the signatures created by upper HSS tree layers in the HSS private key. Instead,
it recomputes the intermediate LMS signatures for each new HSS signature. If ``C``
were not deterministic, we would create two different signatures with the same
(upper tree's) leaf. That would compromise the scheme's security.

For verification of an LMS signature, Botan's LM-OTS logic provides the function
``lmots_compute_pubkey_from_sig``, which computes a public key candidate for
a signature-message pair; it implements [RFC8554]_ Algorithm 4b.

.. _pubkey/hss_lms/lms:

LMS
^^^

An LMS tree is a Merkle tree, which is generated from the public keys of multiple
LM-OTS instances. The parameters for LMS instances are provided in
:ref:`Supported LMS parameter sets <pubkey/hss_lms/lms-params>`.
As with LM-OTS, the parameter ``Hash`` is the hash algorithm used.
This one is used to compute the parent node using two adjacent child nodes. As
described in :ref:`Section LM-OTS <pubkey/hss_lms/lm_ots>`, the hash functions
of LMS and LM-OTS must match. Another
parameter is the height ``h`` of the LMS tree. The remaining parameter ``m``,
the associated byte size, is deduced by the used hash function. Botan allows the
LMS parameter sets from [RFC8554]_ and [draft-fluhrer-11]_, collected in Table
:ref:`Supported LMS parameter sets <pubkey/hss_lms/lms-params>`.

.. _pubkey/hss_lms/lms-params:

.. table::  Supported LMS parameter sets

   +--------------------+--------------+-----+-----+--------+
   | Parameter Set Name | Hash         | m   | h   | id     |
   +====================+==============+=====+=====+========+
   | LMS_SHA256_M32_H5  | SHA-256      | 32  | 5   | 0x0005 |
   +--------------------+--------------+-----+-----+--------+
   | LMS_SHA256_M32_H10 | SHA-256      | 32  | 10  | 0x0006 |
   +--------------------+--------------+-----+-----+--------+
   | LMS_SHA256_M32_H15 | SHA-256      | 32  | 15  | 0x0007 |
   +--------------------+--------------+-----+-----+--------+
   | LMS_SHA256_M32_H20 | SHA-256      | 32  | 20  | 0x0008 |
   +--------------------+--------------+-----+-----+--------+
   | LMS_SHA256_M32_H25 | SHA-256      | 32  | 25  | 0x0009 |
   +--------------------+--------------+-----+-----+--------+
   | LMS_SHA256_M24_H5  | SHA-256/192  | 24  | 5   | 0x000a |
   +--------------------+--------------+-----+-----+--------+
   | LMS_SHA256_M24_H10 | SHA-256/192  | 24  | 10  | 0x000b |
   +--------------------+--------------+-----+-----+--------+
   | LMS_SHA256_M24_H15 | SHA-256/192  | 24  | 15  | 0x000c |
   +--------------------+--------------+-----+-----+--------+
   | LMS_SHA256_M24_H20 | SHA-256/192  | 24  | 20  | 0x000d |
   +--------------------+--------------+-----+-----+--------+
   | LMS_SHA256_M24_H25 | SHA-256/192  | 24  | 25  | 0x000e |
   +--------------------+--------------+-----+-----+--------+
   | LMS_SHAKE_M32_H5   | SHAKE256/256 | 32  | 5   | 0x000f |
   +--------------------+--------------+-----+-----+--------+
   | LMS_SHAKE_M32_H10  | SHAKE256/256 | 32  | 10  | 0x0010 |
   +--------------------+--------------+-----+-----+--------+
   | LMS_SHAKE_M32_H15  | SHAKE256/256 | 32  | 15  | 0x0011 |
   +--------------------+--------------+-----+-----+--------+
   | LMS_SHAKE_M32_H20  | SHAKE256/256 | 32  | 20  | 0x0012 |
   +--------------------+--------------+-----+-----+--------+
   | LMS_SHAKE_M32_H25  | SHAKE256/256 | 32  | 25  | 0x0013 |
   +--------------------+--------------+-----+-----+--------+
   | LMS_SHAKE_M24_H5   | SHAKE256/192 | 24  | 5   | 0x0014 |
   +--------------------+--------------+-----+-----+--------+
   | LMS_SHAKE_M24_H10  | SHAKE256/192 | 24  | 10  | 0x0015 |
   +--------------------+--------------+-----+-----+--------+
   | LMS_SHAKE_M24_H15  | SHAKE256/192 | 24  | 15  | 0x0016 |
   +--------------------+--------------+-----+-----+--------+
   | LMS_SHAKE_M24_H20  | SHAKE256/192 | 24  | 20  | 0x0017 |
   +--------------------+--------------+-----+-----+--------+
   | LMS_SHAKE_M24_H25  | SHAKE256/192 | 24  | 25  | 0x0018 |
   +--------------------+--------------+-----+-----+--------+

In addition to its LMS parameters, an LMS instance (class ``LMS_Instance``) is
defined by its identifier ``I`` and the LM-OTS parameters used for all
contained LM-OTS instances.
We can create a keypair with a secret key (class ``LMS_Private_Key``) and a
public key (class ``LMS_Public_Key``) for each LMS instance. The secret
key contains the value ``SEED`` used for LM-OTS secret key derivation, while the
public key contains the root node of the LMS tree. The public key is derived from the
secret key in the constructor of ``LMS_Public_Key``.

For creating an LMS signature, Botan offers the method
``LMS_Private_Key::sign_and_pk_gen``, which signs the message and computes the
public key associated with the LMS instance according to Section 5.3. and 5.4.
of [RFC8554]_. For verification of a signature-message pair, Botan provides
``LMS_PublicKey::verify_signature``, implementing  Algorithm 5 of [RFC8554]_.
The internal logic to create and reconstruct Merkle trees is implemented in the
cross-algorithm helper module ``tree_hash``
(:srcref:`[src/lib]/utils/tree_hash/tree_hash.h`). The leaves are created using the
constructs introduced in :ref:`Section LM-OTS <pubkey/hss_lms/lm_ots>`.

.. _pubkey/hss_lms/hss:

HSS
^^^

An HSS hypertree consists of multiple LMS trees, where leaf nodes of higher LMS
trees sign the public keys of lower LMS instances. The following
parameters define the HSS hypertree. The parameter ``L`` configures the height
of the HSS hypertree, i.e., the number of LMS tree levels in the hypertree.
As specified in [RFC8554]_, Botan permits values :math:`1,2,\dots,8` for ``L``.
An LMS and LM-OTS parameter set pair is defined for each level. Botan allows all
parameter combinations as long as the hash function is always the
same at all levels (recommended in [SP800-208]_).

As defined in [RFC8554]_, the public key of an HSS instance is composed of
``L`` and the public key of the hypertree's root LMS tree. The
HSS secret key format is not defined in [RFC8554]_. Botan defines its own
secret key format under a private OID. The following describes its byte
composition in the same syntax as [RFC8554]_:

.. math::
   \mathtt{SK\_Bytes =\ } &\mathtt{u32str(L)\ ||\ u64str(idx)\ || }

      &\mathtt{u32str(LMSAlgorithmId_{root\_layer})\ ||\ u32str(LMOTSAlgorithmId_{root\_layer})\ || }

      &\mathtt{\dots\ || }

      &\mathtt{u32str(LMSAlgorithmId_{bottom\_layer})\ ||\ u32str(LMOTSAlgorithmId_{bottom\_layer})\ || }

      &\mathtt{SEED_{root\_tree} ||\ I_{root\_tree} }


``idx`` is the index of the next signature created using this
secret key, defining the LMS leaves to use. This entry updates
after every signature creation. Next, the LMS and LMOTS algorithm IDs are given
for each level as defined in Tables :ref:`Supported LM-OTS parameter sets
<pubkey/hss_lms/lm-ots-params>` and :ref:`Supported LMS parameter sets
<pubkey/hss_lms/lms-params>`. Finally, ``SEED`` and ``I`` of the root LMS tree
are given. The classes ``HSS_LMS_PublicKeyInternal`` and
``HSS_LMS_PrivateKeyInternal`` realize the public and secret keys, respectively.

Botan's HSS implementation derives LMS seeds and identifiers
using the same method Cisco's reference implementation applies. This approach
is called ``SECRET_METHOD 2`` in the Cisco implementation's configuration.
``SEED`` and ``I`` of child LMS trees are derived from the values of their
parents and their position in the hypertree. This operation is similar to the
pseudorandom key generation method of [RFC8554]_ Appendix A.
The derivation functions are the following:

.. math::
   \mathtt{SEED_{child}}\ &\mathtt{= Hash(I_{parent}\ ||\ u32str(q_{parent})\
   ||\ u16str(0xfffe)\ ||\ u8str(0xff)\ ||\ SEED_{parent})}

   \mathtt{I_{child}}\    &\mathtt{= Hash(I_{parent}\ ||\ u32str(q_{parent})\
   ||\ u16str(0xffff)\ ||\ u8str(0xff)\ ||\ SEED_{parent})}

:math:`\mathtt{I_{parent}}` and :math:`\mathtt{SEED_{parent}}` are the
identifier and seed of the parent LMS tree, while :math:`\mathtt{I_{child}}`
and :math:`\mathtt{SEED_{child}}` are derived for the new child.
:math:`\mathtt{q_{parent}}` is the parent's LMS leaf index used to sign the
child LMS tree's public key. Note that since the third entry separates their
domain, the hash inputs will never collide with
the ones of the LM-OTS computations of ``x[i]`` and ``C``.

The method ``HSS_LMS_Signature_Operation::sign`` is used for signature creation,
implementing Algorithm 8 of [RFC8554]_.
``HSS_LMS_Verification_Operation::is_valid_signature`` provides signature
verification, as in Section 6.3. of [RFC8554]_.

.. _pubkey/hss_lms/key_gen:

Key Generation
--------------

HSS key generation follows Section 6.1. of [RFC8554]_ and is implemented
within the ``HSS_LMS_PrivateKeyInternal`` constructor (see :srcref:`[src/lib/pubkey/hss_lms]/hss.cpp:114|HSS_LMS_PrivateKeyInternal`)
and ``HSS_LMS_PublicKeyInternal::create`` (see :srcref:`[src/lib/pubkey/hss_lms]/hss.cpp:298|HSS_LMS_PublicKeyInternal::create`).

Note that [RFC8554]_ and [SP800-208]_ require that all LMS instances' public/private key
pairs must be created independently from each other. Since Botan applies the seed
derivation logic of the reference implementation, multiple LMS instances are
derived from the same parent seed. Therefore, the specification requirement
is only fulfilled if the derivation method is strong enough to ensure that no
dependency between the derived seeds can be observed without knowledge of the
parent seed. Since it uses the same process as [RFC8554]_ Appendix A,
the derivation method is built as strong as the other building blocks of the
scheme. We therefore consider the requirement fulfilled.

Botan's key generation algorithm works as follows:

.. admonition:: HSS Key Generation

   **Input:**

   -  ``rng``: random number generator
   -  ``L``: The number of levels in the HSS hypertree
   -  ``lms-params[0], ..., lms-params[L-1]`` : LMS parameter sets at all
      ``L`` levels
   -  ``lm-ots-params[0], ..., lm-ots-params[L-1]``: LM-OTS parameter sets at all
      ``L`` levels

   **Output:**

   -  ``SK``, ``PK``: secret and public key

   **Steps:**

   1. Generate new values ``SEED`` and ``I`` using ``rng``.
   2. ``idx = 0`` sets the initial signature index.
   3. | ``SK = {L, idx, lms-params[0], lm-ots-params[0], ..., lms-params[L-1],``
      |       ``lm-ots-params[L-1], SEED, I}``.
   4. Construct the root LMS secret key ``lms-sk[0]`` with parameters
      ``lms-params[0]`` and ``lm-ots-params[0]`` containing ``SEED`` and ``I``
      (see :ref:`LMS <pubkey/hss_lms/lms>`).
   5. Construct the root LMS public key ``lms-pk[0]`` from ``lms-sk[0]``
      (see :ref:`LMS <pubkey/hss_lms/lms>`).
   6. ``PK = {L, lms-pk[0]}``.

   **Notes:**

   - A formatted string provides ``L`` and the LMS and OTS parameters.
   - In contrast to [RFC8554]_ Algorithm 7 Step 2, the keys and signatures of
     lower LMS trees are not computed during key generation but during signature
     creation.
   - Additional checks ensure that the hash functions used for the LMS and LM-OTS
     are the same for all instances. Otherwise, the key generation is aborted.


.. _pubkey/hss_lms/sig_creation:

Signature Creation
------------------

An HSS signature is created using ``HSS_LMS_Signature_Operation::sign``,
which follows Section 6.2. of [RFC8554]_ (see :srcref:`[src/lib/pubkey/hss_lms]/hss.cpp:221|HSS_LMS_PrivateKeyInternal::sign`).
It works as follows:

.. admonition:: HSS Signature Creation

   **Input:**

   -  ``m``: message to be signed
   - | ``SK``: HSS secret key, ``SK = {L, idx, lms-params[0], lm-ots-params[0], ...,``
     |      ``lms-params[L-1], lm-ots-params[L-1], SEED, I}``

   **Output:**

   -  ``sig``:  HSS signature

   **Steps:**

   1. If ``idx`` denotes that ``SK`` is exhausted, the signature creation is
      aborted.
   2. Derive the LMS signing leaf indices ``q[0], ..., q[L-1]`` from ``idx`` and
      the LMS parameters.
   3. Derive the LMS secret keys ``lms-sk[i]`` for HSS levels
      ``i = 1, ..., (L-1)`` using the seed and identifier derivation method
      described in :ref:`HSS <pubkey/hss_lms/hss>`.
   4. ``lms-sig[L-1], lms-pk[L-1] = lms-sk[L-1].sign_and_pk_gen(msg, q[L-1])``
      creates the bottom layer LMS signature and the public key bytes of the
      signing LMS tree.
   5. ``lms-sig[i], lms-pk[i] = lms-sk[i].sign_and_pk_gen(lms-pk[i+1], q[i])``
      creates the higher level public key signatures and public keys for
      ``i = L-2, ..., 0``.
   6. | ``sig = u32str(L-1) || lms-sig[0] || lms-pk[1] || lms-sig[1] || ...``
      |       ``|| lms-pk[L-1] || lms-sig[L-1]``.

   **Notes:**

   - After signature creation, ``idx`` of ``SK`` is increased by one.

.. _pubkey/hss_lms/sig_validation:

Signature Validation
--------------------

Botan's method ``HSS_LMS_Verification_Operation::is_valid_signature`` verifies a
signature-message pair by implementing the method of Section 6.3. of [RFC8554]_
(see :srcref:`[src/lib/pubkey/hss_lms]/hss.cpp:343|HSS_LMS_PublicKeyInternal::verify_signature`).
It does the following:

.. admonition:: HSS Signature Validation

   **Input:**

   -  ``m``: message to be validated
   -  ``sig``: signature to be validated
   -  ``PK``: HSS public key, ``PK = {L, lms-pk[0]}``

   **Output:**

   -  ``true`` if the signature for message ``m`` is valid. ``false`` otherwise.

   **Steps:**

   1. Parse the bytes in ``sig`` and check for correct syntax, including a
      proper length, a valid number of levels, and syntactically valid LMS
      public keys and signatures. Obtains
      ``Nspk, lms-sig[0], lms-pk[1], lms-sig[1], ..., lms-pk[Nspk], lms-sig[Nspk]``
      from the signature.
   2. Verify that ``Nspk == (L-1)``. Return ``false`` otherwise.
   3. Verify that ``lms-pk[i].verify_signature`` returns ``true`` for signature
      ``lms-sig[i]`` of message ``lms-pk[i+1]`` for ``i = 0, ..., Nspk-1``.
      Return ``false`` otherwise.
   4. Return ``true`` iff ``lms-pk[Nspk-1].verify_signature`` returns ``true``
      for signature ``lms-sig[Nspk]`` of message ``m``.

   **Notes:**

   - The first step also parses and syntactically checks the contained LMS and
     LM-OTS signatures.
   - ``LMS_PublicKey::verify_signature`` checks that the parameter and leaf
     index of the LMS signature are valid and match the ones
     in the LMS public key. Afterward, it reconstructs the LMS root node from
     the data in the signature and compares it with the one contained in the LMS
     public key.

