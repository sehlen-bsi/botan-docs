Signatures
==========

RSA
---

The RSA signature algorithm is provided in the class
``RSA_Signature_Operation`` in :srcref:`src/lib/pubkey/rsa/rsa.cpp`. The
respective verification algorithm is implemented in the class
``RSA_Verify_Operation``.
The implementation follows [RFC3447]_.

RSA Signature Schemes
^^^^^^^^^^^^^^^^^^^^^

Before a message can be signed it must be processed to achieve the bit
length of the RSA modulus ``N``. Therefore, a padding scheme is applied to
the message ``m``. Botan implements multiple padding schemes. For RSA
signatures the probabilistic RSA-PSS scheme (EMSA4) implemented in
:srcref:`src/lib/pk_pad/emsa_pssr/pssr.cpp` is recommended [TR-02102-1]_. The
RSA-PSS implementation follows the definition in [RFC3447]_. The ISO
9796-2 DS2 and ISO 9796-2 DS3 padding schemes are implemented in
:srcref:`src/lib/pk_pad/iso9796/iso9796.cpp`
Both implementations follow the specification [ISO-9796-2]_.
Alternatively, Botan provides the deterministic PKCS#1 v1.5 RSA
signature scheme (EMSA3), which is obsolete and thus not recommended [#sig_emsa3_disclaimer]_.

.. [#sig_emsa3_disclaimer]
   Despite being obsolete, PKCS#1 v1.5 is required for TLS 1.2, hence this EMSA
   is not disabled in BSI's build policy by default.

Signature Creation
^^^^^^^^^^^^^^^^^^

To sign data, the function ``secure_vector<byte> raw_sign(const byte
msg[], size_t msg_len,RandomNumberGenerator&)`` is called. The bytes to
sign ``m`` and its length is passed to the function. The RSA signature
algorithm operates as follows:

.. admonition:: ``RSA_Signature_Operation::raw_sign()``

   **Input:**

   -  ``m``: raw bytes to sign
   -  RSA_PrivateKey: the first prime ``p``, the second prime ``q``, the exponent ``e``,
      the modulus :math:`N = p*q`,
      :math:`d = e^{-1} \bmod \text{lcm}(p-1, q-1)`,
      :math:`d_1 = d \bmod (p-1)`,
      :math:`d_2 = d \bmod (q-1)`,
      :math:`c = q^{-1} \bmod p`

   **Output:**

   -  ``x``: raw RSA_Signature

   **Steps:**

   1. Verify that :math:`m < N`.
      If the message to sign exceeds the modulus of the RSA private key,
      the algorithm terminates with error.
   2. Blind message m with random blinding nonce ``k``.
   3. Compute
      :math:`{x_{1} = m^{d_{1}}}\bmod p`
      and
      :math:`{x_{2} = m^{d_{2}}}\bmod q`
      . This computations takes place simultaneously (additional thread).
      Here, :math:`d_1` and :math:`d_2` are part of the RSA private key.
   4. Compute
      :math:`{h = {{({x_{1} - x_{2}})} \ast c}}\bmod p`.
      Here, :math:`c` is part of the RSA private key.
   5. Compute signature
      :math:`x = {{h \ast q} + x_{2}}`.
   6. Unblind ``x`` with :math:`k^{- 1}`.
   7. Verify that
      :math:`x^{e}\bmod {N = m}`
      holds. Thus it is assured, that the algorithm returns a valid
      signature. As a consequence, the implementation resists fault
      attacks.

Signature Verification
^^^^^^^^^^^^^^^^^^^^^^

To verify a RSA signature the signature value is passed to the function
``secure_vector<byte> verify_mr(const byte msg[], size_t msg_len)``. This
function proceeds as follows:

.. admonition:: ``RSA_Verify_Operation::verify_mr()``

   **Input:**

   -  ``x``: raw RSA_Signature
   -  RSA_PublicKey: ``N``, ``e``

   **Output:**

   -  ``v``: value to compare signed data to

   **Steps:**

   1. Verify that the signature is smaller than the modulus of the public
      key.
      I.e., if :math:`x \geq N`, then the algorithm throws an invalid argument error.
   2. Compute :math:`v=x^e \bmod n`

DSA
---

The Digital Signature Algorithm (DSA) is implemented in
:srcref:`src/lib/pubkey/dsa/dsa.cpp`.
The implementation follows [FIPS-186-4]_ or [RFC6979]_ if the corresponding module is enabled.

DSA Signature Schemes
^^^^^^^^^^^^^^^^^^^^^

For DSA signatures no padding is required. The only suitable signature
scheme DL/ECSSA (EMSA1) [IEEE-1363-2000]_ uses a cryptographic hash function to compute a
representative message with the length of ``q`` from the DSA public key.
If the computed hash is longer than the specified ``output_bits`` (length of
``q``), the algorithm returns only the ``output_bits`` highest bits of the
computed hash.

Signature Creation
^^^^^^^^^^^^^^^^^^

The message representative created by the EMSA1 encoding algorithm is
passed to ``raw_sign(const byte msg[], size_t
msg_len,RandomNumberGenerator& rng)`` of class
``DSA_Signature_Operation``. Botan computes the DSA signature with the
following algorithm.

.. admonition:: ``DSA_Signature_Operation::raw_sign()``

   **Input:**

   -  ``rng``: random number generator
   -  ``m``: raw bytes to sign (EMSA1 encoded data)
   -  DSA_PrivateKey: ``x``, ``y``, DL_Group

   **Output:**

   -  (``r``, ``s``): DSA signature

   **Steps:**

   1. Perform conditional subtractions :math:`m=m-q`, while :math:`m \geq q`.
   2. Generate parameter ``k`` as a random number :math:`0<k<q` from the passed ``rng`` using
      the algorithm described in Section :ref:`pubkey_param/rng` or as HMAC_DRBG
      output [RFC6979]_. If Botan is compiled with the module ``rfc6979`` the
      HMAC_DRBG is used, otherwise ``k`` is sampled from the passed random
      number generator ``rng``. HMAC_DRBG is deterministic and k thus depends
      on the HMAC_DRBG inputs ``m`` and ``x``.
   3. Compute :math:`r=(g^k \bmod p) \bmod q` and :math:`k^{-1} \bmod q`.
   4. Compute :math:`s=k^{-1}*(x*r+m)\bmod q`. Computation of :math:`x*r+m` is blinded by computing it as
      :math:`(x*r*b+m*b)/b`.
   5. If :math:`s=0 \lor r=0` applies, the algorithm terminates with an error.

**Remark:** If Botan is built with the RFC6979 module, it implements
deterministic DSA signatures, which are not covered by [TR-02102-1]_. In
this case the implemented DSA signature algorithm is not [FIPS-186-4]_
conform. This cryptographic construct does not need a random number
generator during signature computation. However, the RFC6979 module is
prohibited in the BSI module policy.

Signature Verification
^^^^^^^^^^^^^^^^^^^^^^

To verify a DSA signature the function ``verify(const byte msg[], size_t
msg_len, const byte sig[], size_t sig_len)`` in class
``DSA_Verification_Operation`` is implemented. The function receives a
signature, the respective EMSA1 processed message and the lengths of the
parameters. The algorithm operates as follows:

.. admonition:: ``DSA_Verification_Operation::verify()``

   **Input:**

   -  (``r``, ``s``): DSA signature
   -  ``m``: message bytes
   -  DSA_PublicKey: ``y``, DL_Group

   **Output:**

   -  ``true``, if the signature for message ``m`` is valid. ``false`` otherwise

   **Steps:**

   1. Verify that the signature :math:`({r,s})`
      has length :math:`2 \ast \mathit{qbits}`
      and :math:`m < q`
      applies. If that is not the case, the signature is invalid and
      ``false`` is returned.
   2. Assure that
      :math:`0 < r < {q \land 0} < s < q`
      applies. Otherwise the signature is invalid and ``false`` is
      returned.
   3. Compute
      :math:`{w = s^{- 1}}\bmod q`
   4. Compute
      :math:`{v_{i} = g^{{w \ast i}\bmod q}}\bmod p`
      and
      :math:`{v_{r} = y^{{w \ast r}\bmod q}}\bmod p`
      .
   5. Compute
      :math:`{v = {v_{i} \ast v_{r}}}\bmod p`
   6. Return ``true``, if
      :math:`{v \equiv r}\bmod p`
      applies and ``false`` otherwise.

ECDSA
-----

The Digital Signature Algorithm over elliptic curves is implemented in
:srcref:`src/lib/pubkey/ecdsa/ecdsa.cpp`.
The implementation follows [X9.62]_ or [RFC6979]_ if the corresponding module is enabled.

ECDSA Signature Schemes
^^^^^^^^^^^^^^^^^^^^^^^

Similarly to DSA, ECDSA uses the DL/ECSSA (EMSA1) [IEEE-1363-2000]_ signature scheme to
compute a representative of the message to be signed.

Signature Creation
^^^^^^^^^^^^^^^^^^

The signature generation algorithm works as follows:

.. admonition:: ``ECDSA_Signature_Operation::raw_sign()``

   **Input:**

   -  ``rng``: random number generator
   -  ``m``: raw bytes to sign (EMSA1 encoded data)
   -  EC_Privatekey: ``d``, ``Q``, domain (curve parameters (first coefficient
      ``a``, second coefficient ``b``, prime ``p``), base point ``G``, ``ord(G) n``,
      cofactor of the curve ``h``)

   **Output:**

   -  (``r``, ``s``): ECDSA signature

   **Steps:**

   1. Generate parameter ``k`` as a random number :math:`0<k< \lvert E \rvert` using the algorithm
      described in Section :ref:`pubkey_param/rng` or as HMAC_DRBG output
      [RFC6979]_. If Botan is compiled with the module RFC6979 the HMAC_DRBG
      is used, otherwise ``k`` is sampled from the passed random number
      generator ``rng``. HMAC_DRBG is deterministic and k thus depends on the
      HMAC_DRBG inputs ``m``, ``n`` and ``d``.
   2. Sample a :math:`\lceil \frac{lenth(n)}{2} \rceil` bit long random blinding
      ``mask`` from ``rng`` and compute :math:`k'=k+n*mask`.
      Compute the point multiplication :math:`k_p=(x_1,y_1)=k'*G`, where G is the base point of the
      domain. This computation utilizes randomized Jacobian point
      coordinates with a blinding masks that is equal in size to the
      underlying field. Compute :math:`r=x_1 \bmod n` and :math:`s=k^{-1}*(r*d+m)\bmod n`.
      Computation of :math:`r*d+m` is blinded by
      computing it as :math:`(r*d*b+m*b)/b`. If :math:`s=0 \lor r=0` applies,
      the algorithm terminates with an error.

**Remark:** If Botan is built with the RFC6979 module, it implements
deterministic ECDSA signatures, which are not covered by [TR-02102-1]_. In
this case the implemented ECDSA signature algorithm is not [FIPS-186-4]_
conform. However, the RFC6979 module is prohibited in the BSI module
policy.

Signature Verification
^^^^^^^^^^^^^^^^^^^^^^

The signature verification algorithm works as follows:

.. admonition:: ``ECDSA_Verification_Operation::verify()``

   **Input:**

   -  ``m``: message bytes
   -  EC_Publickey: ``Q``, domain (curve parameters (first coefficient ``a``,
      second coefficient ``b``, prime ``p``), base point ``G``, ``ord(G) n``,
      cofactor of the curve ``h``)
   -  (``r``, ``s``): ECDSA signature

   **Output:**

   -  ``true``, if the signature for message ``m`` is valid. ``false`` otherwise.

   **Steps:**

   1. Verify the passed signature has length :math:`2*qbits`. If that is not the case
      ``false`` is returned.
   2. Assure that :math:`0<r<n \land 0<s<n`. Otherwise the signature is invalid.
   3. Compute :math:`w=s^{-1}\bmod n`
   4. Compute :math:`v_1=m*w \bmod n` and :math:`v_2=r*w \bmod n`
   5. Compute the point :math:`v=(x_1, y_1)=v_1*G+v_2*Q` with Shamir's trick [DI08]_.
   6. Return ``true`` if :math:`v \equiv r \bmod n` applies. ``false`` otherwise.

ECKCDSA
-------

The Korean Certificate-based Digital Signature Algorithm over elliptic
curves is implemented in :srcref:`src/lib/pubkey/eckcdsa/eckcdsa.cpp`. The
implementation follows [ISO-14888-3]_.

ECKCDSA Signature Schemes
^^^^^^^^^^^^^^^^^^^^^^^^^

Unlike other DSA variants, ECKCDSA does not use the DL/ECSSA (EMSA1) [IEEE-1363-2000]_
signature scheme to compute a representative of the message to be
signed.
Instead besides the the message itself,
it also includes the public key in the representative.

Signature Creation
^^^^^^^^^^^^^^^^^^

The signature generation algorithm works as follows:

.. admonition:: ``ECKCDSA_Signature_Operation::raw_sign()``

   **Input:**

   -  ``m``: raw bytes to sign (the hash-code ``H`` in  [ISO-14888-3]_,
      which is the truncated hash from the public key and message)
   -  EC_Privatekey with invers: ``d``, ``Q``, domain (curve parameters (first coefficient
      ``a``, second coefficient ``b``, prime ``p``), base point ``G``, ``ord(G) n``,
      cofactor of the curve ``h``)
   -  ``rng``: random number generator

   **Output:**

   -  (r,s): ECKCDSA signature

   **Steps:**

   1. Sample parameter k as a random number
      :math:`0 < k < n`
      from ``rng`` using the algorithm described in Section
      :ref:`pubkey_param/rng`.
   2. Sample a :math:`\lceil \frac{lenth(n)}{2} \rceil` bit long random blinding
      ``mask`` from ``rng`` and compute :math:`k'=k+n*mask`.
   3. Compute point :math:`W=(x_1,y_1)=k'*G`.
   4. Compute the witness
      :math:`{r = h}{(x_{1})}`
      , where :math:`h`
      is the hash function used in the current instance of the signature scheme.
   5. If the output length of the hash function :math:`h` exceeds the size of the group order,
      truncate the *low side* in :math:`r` on a byte level to the size of the group order.
      This means bytes in :math:`r` are discarded starting from the beginning of the byte sequence.
   6. Compute
      :math:`{s = {d \ast {({{k - r}\oplus m})}}}\bmod n`
      . If :math:`s=0` applies, the algorithm terminates with an error.
   7. Return ECKCDSA signature (r,s).

Signature Verification
^^^^^^^^^^^^^^^^^^^^^^

The signature verification algorithm works as follows:

.. admonition:: ``ECKCDSA_Verification_Operation::verify()``

   **Input:**

   -  ``m``: raw bytes to verify (the hash-code ``H`` in  [ISO-14888-3]_,
      which is the truncated hash from the public key and message)
   -  EC_Publickey: ``Q``, domain (curve parameters (first coefficient ``a``,
      second coefficient ``b``, prime ``p``), base point ``G``, ``ord(G) n``,
      cofactor of the curve ``h``)
   -  (``r``, ``s``): ECKCDSA signature

   **Output:**

   -  ``true``, if the signature for message ``m`` is valid. ``false`` otherwise

   **Steps:**

   1. Perform preliminary parameter checks and verifies that :math:`0<s<n` applies.
      Terminates otherwise.
   2. Compute :math:`e=r \oplus m \bmod n`.
   3. Compute point :math:`W=s*q+e*G` with Shamir's trick.
   4. Recompute the witness :math:`r'=h(x_i)`,
      where :math:`h` is the hash function used in the current instance of the signature scheme.
   5. If the output length of the hash function :math:`h` exceeds the size of the group order,
      truncate the *low side* in :math:`r` on a byte level to the size of the group order.
      This means bytes in :math:`r` are discarded starting from the beginning of the byte sequence.
   6. Return ``true`` if the recomputed witness :math:`r'` is equal to
      the witness :math:`r` inside the signature.
      Otherwise return ``false``.

ECGDSA
------

ECGDSA Signature Schemes
^^^^^^^^^^^^^^^^^^^^^^^^

The German Digital Signature Algorithm over elliptic curves is
implemented in :srcref:`src/lib/pubkey/ecgdsa/ecgdsa.cpp`. The implementation
follows [ISO-14888-3]_.

Signature Creation
^^^^^^^^^^^^^^^^^^

The signature generation algorithm works as follows:

.. admonition:: ``ECGDSA_Signature_Operation::raw_sign()``

   **Input:**

   -  ``m``: raw bytes to sign (EMSA1 encoded data)
   -  EC_Privatekey with invers: ``d``, ``Q``, domain (curve parameters (first coefficient
      ``a``, second coefficient ``b``, prime ``p``), base point ``G``, ``ord(G) n``,
      cofactor of the curve ``h``)
   -  ``rng``: random number generator

   **Output:**

   -  (r,s): ECGDSA signature

   **Steps:**

   1. Sample parameter ``k`` as a random number
      :math:`0 < k < n`
      from ``rng`` using the algorithm described in Section
      :ref:`pubkey_param/rng` .
   2. Sample a :math:`\lceil \frac{lenth(n)}{2} \rceil` bit long random blinding
      ``mask`` from ``rng`` and compute :math:`k'=k+n*mask`.
   3. Compute point :math:`W=(x_1,y_1)=k'*G`. This computation utilizes randomized Jacobian point
      coordinates with a blinding masks that is equal in size to the
      underlying field.
   4. Set :math:`{r = x_{1}}\bmod n`
   5. Compute :math:`{s = {d \ast {({{k \ast r} - m})}}}\bmod n`.
   6. If :math:`s = {0 \vee r} = 0`
      applies, the algorithm terminates with an error.
   7. Return ECGDSA signature (r,s).

Signature Verification
^^^^^^^^^^^^^^^^^^^^^^

The signature verification algorithm works as follows:

.. admonition:: ``ECGDSA_Verification_Operation::verify()``

   **Input:**

   -  ``m``: message bytes
   -  EC_Publickey: ``Q``, domain (curve parameters (first coefficient ``a``,
      second coefficient ``b``, prime ``p``), base point ``G``, ``ord(G) n``,
      cofactor of the curve ``h``)
   -  (``r``, ``s``): ECGDSA signature

   **Output:**

   -  ``true``, if the signature for message ``m`` is valid. ``false`` otherwise

   **Steps:**

   1. Perform preliminary parameter checks and verify that
      :math:`0 < r < {n \land 0} < s < n`
      applies.
   2. Compute :math:`r^{- 1}\bmod n`
   3. Compute :math:`{v_{1} = {r^{- 1} \ast m}}\bmod n`
      and :math:`{v_{2} = {r^{- 1} \ast s}}\bmod n`.
   4. Compute point
      :math:`W = {{v_{1} \ast G} + {v_{2} \ast Q}}`
   5. Return ``true`` if :math:`r \equiv x_1 \bmod q` applies. Otherwise it returns ``false``.

XMSS with WOTS+
---------------

WOTS+
^^^^^

.. _pubkey_signature/xmss/wotsp_sign:

Signature Creation
~~~~~~~~~~~~~~~~~~

WOTS+ signing follows Algorithm 5 in [XMSS]_. It is implemented in
:srcref:`src/lib/pubkey/xmss/xmss_wots.cpp`.

The signature generation process works as follows:

.. admonition:: ``XMSS_WOTS_PrivateKey::sign()``

   **Input:**

   -  ``m``: message to be signed
   -  ``oid``: XMSS WOTS+ parameters (``n``, ``w``, ``len``, ``PRF``), which are chosen
      automatically based on the XMSS parameters from Table
      :ref:`Supported XMSS Signature algorithms <pubkey_key_generation/xmss/table>`, see [XMSS]_
   -  ``ADRS``: Address
   -  ``public_seed``: public seed
   -  ``private_seed``: private seed

   **Output:**

   -  ``sig``: signature

   **Steps:**

   1. Convert the message ``m`` into base_w representation.
   2. Compute a checksum over the converted message and convert this
      checksum into base_w representation. Append the checksum to the
      message ``m``.
   3. Generate the resulting signature bytes ``sig`` as follows:

      1. Set ``i=0;``
      2. While (``i < len``) do:

         1. ``ADRS.set_chain_address(i);``
         2. ``chain(sig[i], 0, m[i], public_seed, ADRS);``

**Remark:** :ref:`Remark about XMSS being based on the repeated application of a hash function <pubkey_key_generation/xmss/Remark_02>`
applies here as well.

Signature Validation
~~~~~~~~~~~~~~~~~~~~

WOTS+ signature validation strictly follows Algorithm 6 in [XMSS]_. It is
implemented in :srcref:`src/lib/pubkey/xmss/xmss_wots.cpp`.

The signature validation process works as follows:

.. admonition:: ``XMSS_WOTS_PublicKey()`` constructor

   **Input:**

   -  ``m``: message to be validated
   -  ``oid``: XMSS WOTS+ parameters (``n``, ``w``, ``len``, ``PRF``), which are chosen
      automatically based on the XMSS parameters from Table
      :ref:`Supported XMSS Signature algorithms <pubkey_key_generation/xmss/table>`, see [XMSS]_
   -  ``sig``: Signature
   -  ``ADRS``: Address
   -  ``public_seed``: public seed

   **Output:**

   -  ``tmp_pk``: Temporary WOTS+ public key. This public key is afterwards
      compared with the provided public key.

   **Steps:**

   1. Convert the message ``m`` into base_w representation.
   2. Compute a checksum over the converted message and convert this
      checksum into base_w representation. Append the checksum to the
      message ``m``.
   3. Generate the temporary public key ``tmp_pk`` as follows:

      1. Set ``i=0;``
      2. While (``i<len``) do:

         1. Initialize ``tmp_pk`` with the signature data: ``tmp_pk[i] = sig[i]``
         2. ``ADRS.set_chain_address(i);``
         3. ``chain(tmp_pk[i], m[i], w-1-m[i], public_seed, ADRS);``

XMSS
^^^^

Signature Creation
~~~~~~~~~~~~~~~~~~

XMSS signature generation functionality is implemented in
:srcref:`src/lib/pubkey/xmss/xmss_privatekey.cpp` and
:srcref:`src/lib/pubkey/xmss/xmss_signature_operation.cpp`

The algorithm for signature generation follows methods ``treeSig`` and
``XMSS_sig`` from Algorithms 11 and 12 in [XMSS]_. The algorithm works as
follows:

.. admonition:: XMSS Signature Creation

   **Input:**

   -  ``m``: message to be signed
   -  ``SK``: XMSS secret key, ``SK = {idx, SK_PRF, root, public_seed}``

   **Output:**

   -  ``Sig``: XMSS signature

   **Steps:**

   1. Initialize the signature operation and reserve a new leaf index ``idx``
      of an *unused* WOTS+ signature. This index cannot be reused in
      further operations. Calculate a pseudorandom value ``r`` using the output
      of PRF on ``SK_PRF || idx``.
   2. Generate a hash over the output of the PRF function ``r``, Merkle tree ``root``, index ``idx``,
      and message ``m`` using the message hash function ``H()``.
   3. Build an authentication path ``auth_path`` by using the leaf index
      ``idx``, and address ``ADRS``.
   4. Derive the WOTS+ private key for the generated authentication path from
      ``public_seed`` and ``private_seed`` as described in :ref:`pubkey_key_generation/wotsp`.
   5. Compute a WOTS+ signature ``sig_ots`` over the constructed hash value
      as described in :ref:`WOTS+ Signature Creation <pubkey_signature/xmss/wotsp_sign>`.
   6. Set ``Sig = {idx, r, auth_path, sig_ots}``

**Remark:** Due to the complexity of managing the XMSS private key state it is
generally discouraged to use software for performing XMSS private key operations
in production. See also :ref:`pubkey_signature/xmss/leaf_index_registry`.

Signature Validation
~~~~~~~~~~~~~~~~~~~~

XMSS signature validation functionality is implemented in
:srcref:`src/lib/pubkey/xmss/xmss_publickey.cpp` and
:srcref:`src/lib/pubkey/xmss/xmss_verification_operation.cpp`.

The algorithm for signature verification follows methods
``XMSS_rootFromSig`` and ``XMSS_verify`` from Algorithms 13 and 14 in
[XMSS]_. The algorithm works as follows:

.. admonition:: XMSS Signature Validation

   **Input:**

   -  ``m``: message to be validated
   -  ``Sig``: XMSS signature
   -  ``PK``: XMSS public key, ``PK = {root, public_seed}``

   **Output:**

   -  ``true``, if the signature for message ``m`` is valid. ``false`` otherwise

   **Steps:**

   1. Generate a hash over randomness ``r``, Merkle tree root and index ``idx``
      stored in the signature ``Sig``, and message ``m``.
   2. Compute the root node ``node`` using the computed hash value, signature
      ``Sig``, address ``ADRS``, and public seed ``public_seed`` (the root node
      is computed using the ``XMSS_rootFromSig`` method from Algorithm 13
      [XMSS]_).
   3. Return ``(node == root)``

**Remark:** XMSS does not specify any format for the storage of
private and public keys. Currently, Botan serializes keys as plain byte
arrays.

.. _pubkey_signature/xmss/leaf_index_registry:

Leaf Index Registry
~~~~~~~~~~~~~~~~~~~

Handling the safe and persistent state update of XMSS private keys is crucial.
Botan manages the XMSS private key states in an ``XMSS_Index_Registry``, a
thread-safe "Singleton" object. That way, XMSS private key states are kept in
a centrally managed location during application execution.

The ``XMSS_Index_Registry`` singleton provides exactly one method:
``::get(private_seed, prf) -> std::shared_ptr<Atomic<size_t>>``.
The parameters uniquely identify the managed XMSS private key and the method
returns a pointer to an atomic variable keeping the respective leaf index state.
The signing algorithm now manipulates the XMSS state as needed *before* actually
signing with the respective WOTS+ leaf.
Since the state is manipulated with atomic memory access operations, it is safe
to use the same XMSS private key in multiple threads of the same process. A new
private key calling ``::get()`` for the first time lazily initializes the state
variable to "0".

When serializing private keys (using ``XMSS_PrivateKey::private_key_bits()``)
the next unused WOTS+ leaf index is persisted along with the private key data.
Loading a private key from a serialized buffer will initialize the leaf index in
the registry object.
No further infrastructure is provided to maintain persistent private XMSS state.

**WARNING:** Using the provided facilities, the transaction-safe usage of an
XMSS private key is not possible if the private key should outlive the operating
system process that generated it. It is therefore **strongly discouraged to use
Botan's XMSS signing implementation in production applications**. Similarly,
[SP800-208]_ demands the usage of dedicated hardware for XMSS private key
operations.

Note that validating XMSS signatures does not depend on this state management
and its usability is therefore *not affected* by this disclaimer.
