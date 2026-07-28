.. _pubkey/xmssmt:

XMSS^MT
=======

Botan implements the multi-tree version of the eXtended Merkle
Signature Scheme (XMSS^MT) using Winternitz One Time Signatures+ (WOTS+) in
Section :srcref:`src/lib/pubkey/xmssmt/`.

XMSS^MT, specified in RFC8391 [XMSS]_,  is realized by arranging individual XMSS trees in multiple layers to achieve efficient scaling of the key and signature generation time to a larger number of signatures.
The reduced computational effort is achieved at the expense of larger signatures due to multiple intermediate (reduced) XMSS signatures.

Despite being implemented in its own module, XMSS^MT heavily utilizes already-implemented functionality in the XMSS module.
Therefore, the description in this section omits the details of the low-level building blocks and focuses on the XMSS^MT keys and signatures.
The details for the common XMSS functionality can be found in :ref:`pubkey/xmss`.


.. _pubkey_key_generation/xmssmt:

Key Generation
--------------

The implementation is based on RFC8391 [XMSS]_ and implements
the additional parameter sets and the adaptations to the key generation defined in
NIST's [SP800-208]_.
The list of supported algorithms and their parameters is depicted in
Table :ref:`Supported XMSS^MT Signature algorithms <pubkey_key_generation/xmssmt/table>`.

.. _pubkey_key_generation/xmssmt/table:

This table lists the supported XMSS^MT signature algorithms along with their parameters.
For details, see Section 5.4 in [XMSS]_ and [SP800-208]_.

.. list-table:: Supported XMSS^MT Signature algorithms and their parameters
   :header-rows: 1
   :widths: 30 8 8 8 6 6 12

   * - XMSS^MT algorithm
     - n
     - w
     - len
     - h
     - d
     - defined in
   * - XMSSMT-SHA2_20/2_256
     - 32
     - 16
     - 67
     - 20
     - 2
     - [XMSS]_

   * - XMSSMT-SHA2_20/4_256
     - 32
     -  16
     - 67
     - 20
     - 4
     - [XMSS]_
   * - XMSSMT-SHA2_40/2_256
     - 32
     - 16
     - 67
     - 40
     - 2
     - [XMSS]_
   * - XMSSMT-SHA2_40/4_256
     - 32
     - 16
     - 67
     - 40
     - 4
     - [XMSS]_
   * - XMSSMT-SHA2_40/8_256
     - 32
     - 16
     - 67
     - 40
     - 8
     - [XMSS]_
   * - XMSSMT-SHA2_60/3_256
     - 32
     - 16
     - 67
     - 60
     - 3
     - [XMSS]_
   * - XMSSMT-SHA2_60/6_256
     - 32
     - 16
     - 67
     - 60
     - 6
     - [XMSS]_
   * - XMSSMT-SHA2_60/12_256
     - 32
     - 16
     - 67
     - 60
     - 12
     - [XMSS]_
   * - XMSSMT-SHA2_20/2_512 [#x]_
     - 64
     - 16
     - 131
     - 20
     - 2
     - [XMSS]_
   * - XMSSMT-SHA2_20/4_512 [#x]_
     - 64
     - 16
     - 131
     - 20
     - 4
     - [XMSS]_
   * - XMSSMT-SHA2_40/2_512 [#x]_
     - 64
     - 16
     - 131
     - 40
     - 2
     - [XMSS]_
   * - XMSSMT-SHA2_40/4_512 [#x]_
     - 64
     - 16
     - 131
     - 40
     - 4
     - [XMSS]_
   * - XMSSMT-SHA2_40/8_512 [#x]_
     - 64
     - 16
     - 131
     - 40
     - 8
     - [XMSS]_
   * - XMSSMT-SHA2_60/3_512 [#x]_
     - 64
     - 16
     - 131
     - 60
     - 3
     - [XMSS]_
   * - XMSSMT-SHA2_60/6_512 [#x]_
     - 64
     - 16
     - 131
     - 60
     - 6
     - [XMSS]_
   * - XMSSMT-SHA2_60/12_512 [#x]_
     - 64
     - 16
     - 131
     - 60
     - 12
     - [XMSS]_
   * - XMSSMT-SHAKE_20/2_256 [#x]_
     - 32
     - 16
     - 67
     - 20
     - 2
     - [XMSS]_
   * - XMSSMT-SHAKE_20/4_256 [#x]_
     - 32
     - 16
     - 67
     - 20
     - 4
     - [XMSS]_
   * - XMSSMT-SHAKE_40/2_256 [#x]_
     - 32
     - 16
     - 67
     - 40
     - 2
     - [XMSS]_
   * - XMSSMT-SHAKE_40/4_256 [#x]_
     - 32
     - 16
     - 67
     - 40
     - 4
     - [XMSS]_
   * - XMSSMT-SHAKE_40/8_256 [#x]_
     - 32
     - 16
     - 67
     - 40
     - 8
     - [XMSS]_
   * - XMSSMT-SHAKE_60/3_256 [#x]_
     - 32
     - 16
     - 67
     - 60
     - 3
     - [XMSS]_
   * - XMSSMT-SHAKE_60/6_256 [#x]_
     - 32
     - 16
     - 67
     - 60
     - 6
     - [XMSS]_
   * - XMSSMT-SHAKE_60/12_256 [#x]_
     - 32
     - 16
     - 67
     - 60
     - 12
     - [XMSS]_
   * - XMSSMT-SHAKE_20/2_512 [#x]_
     - 64
     - 16
     - 131
     - 20
     - 2
     - [XMSS]_
   * - XMSSMT-SHAKE_20/4_512 [#x]_
     - 64
     - 16
     - 131
     - 20
     - 4
     - [XMSS]_
   * - XMSSMT-SHAKE_40/2_512 [#x]_
     - 64
     - 16
     - 131
     - 40
     - 2
     - [XMSS]_
   * - XMSSMT-SHAKE_40/4_512 [#x]_
     - 64
     - 16
     - 131
     - 40
     - 4
     - [XMSS]_
   * - XMSSMT-SHAKE_40/8_512 [#x]_
     - 64
     - 16
     - 131
     - 40
     - 8
     - [XMSS]_
   * - XMSSMT-SHAKE_60/3_512 [#x]_
     - 64
     - 16
     - 131
     - 60
     - 3
     - [XMSS]_
   * - XMSSMT-SHAKE_60/6_512 [#x]_
     - 64
     - 16
     - 131
     - 60
     - 6
     - [XMSS]_
   * - XMSSMT-SHAKE_60/12_512 [#x]_
     - 64
     - 16
     - 131
     - 60
     - 12
     - [XMSS]_
   * - XMSSMT-SHA2_20/2_192
     - 24
     - 16
     - 51
     - 20
     - 2
     - [SP800-208]_
   * - XMSSMT-SHA2_20/4_192
     - 24
     - 16
     - 51
     - 20
     - 4
     - [SP800-208]_
   * - XMSSMT-SHA2_40/2_192
     - 24
     - 16
     - 51
     - 40
     - 2
     - [SP800-208]_
   * - XMSSMT-SHA2_40/4_192
     - 24
     - 16
     - 51
     - 40
     - 4
     - [SP800-208]_
   * - XMSSMT-SHA2_40/8_192
     - 24
     - 16
     - 51
     - 40
     - 8
     - [SP800-208]_
   * - XMSSMT-SHA2_60/3_192
     - 24
     - 16
     - 51
     - 60
     - 3
     - [SP800-208]_
   * - XMSSMT-SHA2_60/6_192
     - 24
     - 16
     - 51
     - 60
     - 6
     - [SP800-208]_
   * - XMSSMT-SHA2_60/12_192
     - 24
     - 16
     - 51
     - 60
     - 12
     - [SP800-208]_
   * - XMSSMT-SHAKE256_20/2_256
     - 32
     - 16
     - 67
     - 20
     - 2
     - [SP800-208]_
   * - XMSSMT-SHAKE256_20/4_256
     - 32
     - 16
     - 67
     - 20
     - 4
     - [SP800-208]_
   * - XMSSMT-SHAKE256_40/2_256
     - 32
     - 16
     - 67
     - 40
     - 2
     - [SP800-208]_
   * - XMSSMT-SHAKE256_40/4_256
     - 32
     - 16
     - 67
     - 40
     - 4
     - [SP800-208]_
   * - XMSSMT-SHAKE256_40/8_256
     - 32
     - 16
     - 67
     - 40
     - 8
     - [SP800-208]_
   * - XMSSMT-SHAKE256_60/3_256
     - 32
     - 16
     - 67
     - 60
     - 3
     - [SP800-208]_
   * - XMSSMT-SHAKE256_60/6_256
     - 32
     - 16
     - 67
     - 60
     - 6
     - [SP800-208]_
   * - XMSSMT-SHAKE256_60/12_256
     - 32
     - 16
     - 67
     - 60
     - 12
     - [SP800-208]_
   * - XMSSMT-SHAKE256_20/2_192
     - 24
     - 16
     - 51
     - 20
     - 2
     - [SP800-208]_
   * - XMSSMT-SHAKE256_20/4_192
     - 24
     - 16
     - 51
     - 20
     - 4
     - [SP800-208]_
   * - XMSSMT-SHAKE256_40/2_192
     - 24
     - 16
     - 51
     - 40
     - 2
     - [SP800-208]_
   * - XMSSMT-SHAKE256_40/4_192
     - 24
     - 16
     - 51
     - 40
     - 4
     - [SP800-208]_
   * - XMSSMT-SHAKE256_40/8_192
     - 24
     - 16
     - 51
     - 40
     - 8
     - [SP800-208]_
   * - XMSSMT-SHAKE256_60/3_192
     - 24
     - 16
     - 51
     - 60
     - 3
     - [SP800-208]_
   * - XMSSMT-SHAKE256_60/6_192
     - 24
     - 16
     - 51
     - 60
     - 6
     - [SP800-208]_
   * - XMSSMT-SHAKE256_60/12_192
     - 24
     - 16
     - 51
     - 60
     - 12
     - [SP800-208]_

.. [#x] These parameter sets are explicitly not approved by NIST's [SP800-208]_.



The XMSS^MT key generation functionality is implemented in :srcref:`[src/lib/pubkey/xmssmt]/xmssmt_privatekey.cpp`.
The algorithm for key generation is quite similar to the key generation algorithm of XMSS.
It works as follows:
First, the ``public_seed``, ``private_seed`` and ``SK_PRF`` values are generated by an RNG.
Then, to obtain the root node of the hypertree, the `treeHash` algorithm is computed for the top-layer XMSS tree.
See :ref:`pubkey_key_generation/xmss` for details on WOTS+ that equally apply here.
Major differences to the XMSS single-tree case are that only the top-layer root node is computed and that the addressing scheme includes the XMSS^MT layer and tree addresses.

.. _signatures/xmssmt:

Signature Creation
------------------

The XMSS^MT signature generation functionality is implemented in
:srcref:`[src/lib/pubkey/xmssmt]/xmssmt_privatekey.cpp` and
:srcref:`[src/lib/pubkey/xmssmt]/xmssmt_signature_operation.cpp`

The signature format for XMSS^MT signatures is as follows:

- ``index idx_sig``: the signature index
- ``randomness r``: the signature randomness
- ``reduced XMSS signature (bottom layer 0)``
- ``reduced XMSS signature (layer 1)``
- ``..``
- ``reduced XMSS signature (layer d-1)``

where each reduced XMSS signature contains an authentication path and WOTS+ signature.
In contrast to a ``"full"`` XMSS signature, the signature index and randomness are omitted since they are already present at the beginning of the XMSS^MT signature.

The algorithm for signature generation follows methods ``treeSig`` and
``XMSSMT_sign`` from Algorithms 11 and 16 in [XMSS]_. The algorithm works as
follows:

- First, the signature index and randomness r values are determined and the message hash is computed, like in the XMSS case.
- The leaf node is chosen in the same manner as in XMSS, but looking at the whole hypertree instead of just a single XMSS tree.
- Then, for each XMSS tree, starting at the bottom layer, the reduced XMSS signature is computed, until the signature of the top-level XMSS tree has been computed.
  On the bottom layer, the message hash is signed, and on the higher layers, the root node of the tree in the layer below is directly signed.

In essence, the XMSS^MT signature generation operation consists of one XMSS signature generation operation per hypertree layer.
A major difference to the XMSS single-tree case is again, that the addressing scheme includes the XMSS^MT layer and tree addresses.

**Remark:** Due to the complexity of managing the XMSS^MT private key state it is
generally discouraged to use software for performing XMSS^MT private key operations
in production. See also :ref:`pubkey_signature/xmss/stateful_key_index_registry`.


Signature Verification
----------------------

The XMSS^MT signature verification functionality is implemented in
:srcref:`[src/lib/pubkey/xmssmt]/xmssmt_publickey.cpp` and
:srcref:`[src/lib/pubkey/xmssmt]/xmssmt_verification_operation.cpp`.

The algorithm for signature verification follows methods
``XMSS_rootFromSig`` and ``XMSSMT_verify`` from Algorithms 13 and 17 in
[XMSS]_. The algorithm works as follows:

- First, the message hash is computed, like in the XMSS case.
- The leaf node is chosen in the same manner as in XMSS, but looking at the whole hypertree instead of just a single XMSS tree.
- Then, for each XMSS tree, starting at the bottom layer, the reduced XMSS signature is verified, until the root node of the hypertree is reached.
  On the bottom layer, the message that is verified is the message hash, and on the higher layers, the root node of the tree in the layer below is used as message.
  If the computed root node matches the public key's root node, the verification has succeeded.

.. _pubkey_signature/xmssmt/stateful_key_index_registry:

Stateful Key Index Registry
---------------------------

For handling the key states :ref:`pubkey_signature/xmss/stateful_key_index_registry` equally applies to the XMSS^MT case.
For XMSS^MT, the ``algo_name`` is ``"XMSSMT"``, the ``algo_params`` is the OID value, and ``key_material_1`` is the private seed, and ``key_material_2`` is the PRF.