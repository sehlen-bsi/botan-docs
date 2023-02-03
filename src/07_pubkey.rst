Asymmetric Encryption and Key Exchange Schemes
==============================================

RSA
---

Botan implements RSA in ``src/lib/pubkey/rsa/rsa.cpp``. RSA encryption
and decryption are implemented in classes ``RSA_Encryption_Operation``
and ``RSA_Decryption_Operation``.

The RSA encryption operation is implemented as follows:

.. admonition:: RSA encryption

   **Input:**

   - ``m``: plain text message
   -  RSA_PublicKey: the exponent ``e``, the modulus ``N``

   **Output:**

   - ``ct``: ciphertext

   **Steps:**

   1. Calculate :math:`ct = m^e \bmod N` using non-constant-time Montgomery
      exponentiation

The RSA decryption operation is implemented as follows:

.. admonition:: RSA decryption

   **Input:**

   -  ``rng``: random number generator
   -  ``ct``: ciphertext
   -  RSA_PrivateKey: the first prime ``p``, the second prime ``q``, the exponent ``e``,
      the modulus :math:`N = p*q`,
      :math:`d = e^{-1} \bmod \text{lcm}(p-1, q-1)`,
      :math:`d_1 = d \bmod (p-1)`,
      :math:`d_2 = d \bmod (q-1)`,
      :math:`c = q^{-1} \bmod p`

   **Output:**

   -  ``m``: decrypted message

   **Steps:**

   0. Before the first decryption: The random number generator ``rng`` is
      used to initialize the blinding values :math:`m_e` and its inverse :math:`m_d`. Their length
      is set to ``(m_modulus_bits - 1)``.
   1. Blind ciphertext: :math:`ct' = ct*{m_e}^e \bmod N`
   2. Use Chinese Remainder Theorem (CRT) to decrypt ``ct'`` and retrieve ``m'``

      1. | Calculate :math:`S_p` and :math:`S_q` using constant-time Montgomery
           exponentiation and masking for :math:`d_1` and :math:`d_2` as:
         | :math:`C_p = ct' \bmod p`
         | :math:`C_q = ct' \bmod q`
         | :math:`S_p = {C_p}^{d_1} \bmod p`
         | :math:`S_q = {C_q}^{d_2} \bmod q`
      2. | Use Garner's algorithm to reconstruct ``m'`` as:
         | :math:`S = c * ((p + S_p) - S_q) \bmod p`
         | :math:`m' = S * q + C_q`
         | *Note that* :math:`p + S_p` *is done to avoid a negative result for*
           :math:`S_p - S_q` *that would otherwise have required handling with
           a leaking branch.*

   3. Unblind message ::math:`m = m' * m_d \bmod N`

**Remark:** After each blinding step, the blinding values change:
:math:`m_e = m_e * m_e \bmod N`, :math:`m_d = m_d * m_d \bmod N`.
This is performed at most 64 times (defined in
``BOTAN_BLINDING_REINIT_INTERVAL``). Afterwards, ``rng`` is used to
generate new blinding values.

**Conclusion:** The algorithm complies with [TR-02102-1]_
as long as a suitable padding function was applied to the message input.
Note that currently only RSA-OAEP is recommended.

RSA-PKCS#1 v1.5
^^^^^^^^^^^^^^^

The PKCS#1 v1.5 padding has the form:

.. code-block:: none

   0x00 0x02    0xPP 0xPP 0xPP ....            0x00         0xMM 0xMM 0xMM ....
   ^~ constant  ^~ random non-zero fill bytes  ^~ constant  ^~ message bytes
                   (must be at least 8 bytes)

The RSA-PKCS#1 v1.5 padding functionality is implemented in
``src/lib/pk_pad/eme_pkcs1/eme_pkcs.cpp``, in the methods ``pad`` and
``unpad``.

Padding a message ``k`` for a maximum input length ``l`` works as follows:

.. admonition:: ``EME_PKCS1v15::pad()``

   **Input:**

   - ``k``: the message to be padded
   - ``l``: the maximum raw input length for the given algorithm parameters [#rsa_pkcs1_input_length]_
   - ``rng``: a random number generator

   **Output**

   - ``m``: padded message

   **Steps:**

   1. Check that :math:`len(k) <= l - 10`
   2. Create an output buffer matching the maximum raw input length: :math:`l`
   3. Set the first byte to ``0x02`` [#rsa_pkcs1_leading_zero]_
   4. Fill the buffer with random non-zero values up to :math:`len(k) - 2`
   5. Insert a ``0x00`` to separate padding and message bytes
   6. Append the message bytes in ``k`` -- fully filling up the buffer

.. [#rsa_pkcs1_input_length]
   The maximum input length is defined as the RSA key length in bytes minus one.

.. [#rsa_pkcs1_leading_zero]
   PKCS #1 v1.5 mandates a leading zero byte. This is not reflected in the
   padding implementation as it is implicitly added once the padded message is
   cast into a ``BigInteger`` for RSA-encryption.

From the security perspective, the unpadding method is crucial since it
has to resist the Bleichenbacher attack [Blei]_, and has to provide
timing constant validation. This method is implemented as follows:

.. admonition:: ``EME_PKCS1v15::unpad()``

   **Input:**

   -  ``valid_mask``: message validity mask indicating whether the padding
      structure was valid
   -  ``m``: padded message
   -  ``in_len``: message length

   **Output:**

   -  ``k``: unpadded message
   -  ``valid_mask``: message validity mask indicating whether the padding
      structure was valid

   **Steps:**

   1. ``bad_input_m = 0``
   2. ``seen_zero_m = 0``
   3. ``delim_idx = 2``
   4. ``bad_input_m |= (m[0] != 0x00)``
   5. ``bad_input_m |= (m[0] != 0x02)``
   6. ``for (i = 2; i < |m|; i++)``

      -  ``delim_idx += (seen_zero_m == 0) & 1``
      -  ``seen_zero_m |= (m[i] == 0x00)``

   7. ``bad_input_m |= ~seen_zero``
   8. ``bad_input_m |= (delim_idx < 11)``
   9. ``valid_mask = ~bad_input_m;``
   10. Set ``k`` to the byte array behind the first ``0x00``
   11. ``return k, valid_mask``

**Remark:** For TLS, Botan uses a different unpadding function
``decrypt_or_random()``, which is located in ``src/lib/pubkey/pubkey.cpp``.

RSA-OAEP
^^^^^^^^

The RSA-OAEP functionality is implemented in
``src/lib/pk_pad/eme_oaep/oaep.cpp``, in the functions ``pad()`` and
``unpad()``.

Padding a message ``k`` for a key length ``l`` works as follows:

.. admonition:: ``EME_PKCS1v15::pad()``

   **Input:**

   - ``k``: the message to be padded
   - ``l``: the maximum raw RSA encryption input length for the given
     algorithm parameters [#rsa_oaep_input_length]_
   - ``rng``: a random number generator
   - ``H()``: the utilized hash function (``len(H())`` denoting the hash's output length)

   **Output**

   - ``m``: padded message

   **Steps:**

   1. Check that :math:`len(k) <= l - 2 * len(H()) - 1`
   2. Create an output buffer of length :math:`l` and pre-fill it with:

      - a random seed ``s`` of length :math:`len(H())`
      - the output of ``H("")`` [#oaep_label]_
      - some zero bytes to fill the buffer entirely (as needed)
      - ``0x01``
      - the message ``k``

   3. Generate and apply the MGF masks according to the RSA-OAEP specification.
      First using the random seed in the buffer as input to ``H()`` xor-ing over
      the remaining buffer. Then vice versa.

   4. Return ``m`` as the resulting buffer  [#rsa_oaep_leading_zero]_

.. [#rsa_oaep_input_length]
   The maximum input length is defined as the RSA key length in bytes minus one.

.. [#oaep_label]
   The OAEP specification supports an optional "label" whose hash is incorporated
   into the output buffer before applying the padding masks. Typically this is
   left as the default: an empty string. For the sake of simplicity we assume
   the typical case.

.. [#rsa_oaep_leading_zero]
   RSA-OAEP mandates a leading zero byte. This is not reflected in the padding
   implementation as it is implicitly added once the padded message is cast into
   a ``BigInteger`` for RSA-encryption.

From the security perspective, the unpadding method is crucial since it
has to resist Manger's attack [Man]_, and has to provide timing constant
validation. The decryption process cannot provide any information
whether the first message byte was zero or not. This method is
implemented as follows:

.. admonition:: ``OAEP::unpad()``

   **Input:**

   -  ``valid_mask``: message validity mask indicating whether the padding
      structure was valid
   -  ``m``: padded message
   -  ``in_len``: message length

   **Output:**

   -  ``k``: unpadded message
   -  ``valid_mask``: message validity mask indicating whether the padding
      structure was valid

   **Steps:**

   The first byte is extracted as follows:

   1. ``leading_0 = (in[0]==0) & 0x01;``
   2. ``m' = array(m + 1, m + in_len);``

   The remaining steps operate on the message ``m'``, and proceed according
   to the RSA-OAEP specification.

   If ``leading_0`` is false the ``valid_mask`` is set to false.

.. _pubkey/dh:

Diffie-Hellman (DH)
-------------------

In the following section we describe the implementation of the
Diffie-Hellman key exchange over cyclic groups (**Z**/*p*\ **Z**)*. The
respective classes and functions can be found in
``src/lib/pubkey/dh/dh.cpp``.

Botan computes the shared Diffie-Hellman secret with the following
algorithm, implemented in ``raw_agree(const byte w[], size_t w_len)``
which is part of the respective DH operation class ``DH_KA_Operation``.
The function receives the other parties public value :math:`y_b` and computes the
shared secret as follows:

.. admonition:: ``DH_KA_Operation::raw_agree()``

   **Input:**

   -  :math:`y_b`: DH public value of the other party
   -  DH_PrivateKey: ``x``, ``y``, DL_Group (**Z**/*p*\ **Z**)\* : ``p``,
      generator ``g`` with order ``q``

   **Output:**

   -  ``s``: shared DH secret

   **Steps:**

   1. Sample a blinding nonce :math:`m_e` and compute its inverse :math:`m_d`.
      :math:`m_e` has a length of :math:`length(p)-1`.
   2. Verify that :math:`y_b` is valid. That is the case if :math:`1<y_b<p-1` applies. The algorithm
      terminates with an exception, if :math:`y_b` is invalid.
   3. Blind :math:`y_b` as :math:`y_b' = y_b * m_e \bmod p`.
   4. Compute the blinded shared secret ``s'`` as :math:`s' = y_b'^x \bmod p`.
   5. Unblind the shared secret :math:`s=s' * m_d * \bmod p`

Optionally a specified KDF is applied to the shared secret.

**Conclusion:** The algorithm fulfills all DH criteria listed in
[TR-02102-1]_.

.. _pubkey/ecdh:

Elliptic Curve Diffie-Hellman (ECDH)
------------------------------------

The elliptic curve variant of the Diffie-Hellman key exchange is
implemented in ``src/lib/pubkey/ecdh/ecdh.cpp``.

The shared secret is computed by calling ``raw_agree(const byte w[],
size_t w_len)`` from the respective ECDH operation class
``ECDH_KA_Operation``. The algorithm receives the public point of the
other party and computes the shared secret as follows:

.. admonition:: ``ECDH_KA_Operation::raw_agree()``

   **Input:**

   -  ``rng``: random number generator
   -  :math:`Q_b`: ECDH public point of the other party
   -  EC_Privatekey: ``d``, ``Q``, domain (curve parameters (first coefficient
      ``a``, second coefficient ``b``, prime ``p``), base point ``G``, ``ord(G) n``,
      cofactor of the curve ``h``)

   **Output:**

   -  ``S``: shared ECDH secret point

   **Steps:**

   1. Compute intermediate value :math:`i=(h^{-1} \bmod n)*d`, where ``h`` is the cofactor taken from the
      agreed domain.
   2. Verify that the received public point :math:`Q_b` is on the elliptic curve. This
      check is part of the decode function ``OS2ECP()``.
   3. Sample a :math:`\lceil \frac{length(n)}{2} \rceil` bit long random blinding ``mask`` from ``rng`` and compute
      :math:`i' = i+n*mask`.
   4. Compute the shared secret point ``S`` as :math:`S = (h*Q_b)*i' = (h*Q_b)*(h^{-1} \bmod n )*d = Q_b*d`.
      This computation utilizes
      randomized Jacobian point coordinates with a blinding masks that is
      equal in size to the underlying field.
   5. Verify that the computed shared secret point ``S`` is on the selected
      elliptic curve (``on_the_curve()``).
   6. Return affine x coordinate of shared point ``S`` as shared secret.
      Before the transformation to affine coordinates is carried out, it is
      checked, if the shared point S is the point at infinity
      (``is_zero()``). If that is the case, a respective error is thrown.

Optionally a specified KDF is applied to the shared secret.

**Conclusion:** The implemented ECDH key agreement algorithm complies
with the algorithm shown in chapter 4.3.1 of [TR-03111]_ and thus fulfills
the ECDH criteria listed in [TR-02102-1]_, if a recommended curve was
chosen. Furthermore, it is recommended to utilize the optional KDF to
derive a symmetric key.

Hybrid Encryption Schemes
-------------------------

A hybrid encryption scheme is a combination of an asymmetric and a
symmetric cryptosystem. In detail the participating parties agree on a
shared secret, which is then used to encrypt or decrypt data with a
symmetric cipher. In addition, the authenticity of the data is secured
with a MAC. The following schemes are both Integrated Encryption Schemes
and standardized by the IEEE, ANSI and ISO.

DLIES
^^^^^

The Discrete Logarithm Integrated Encryption Scheme (DLIES) utilizes the
Diffie-Hellman key exchange as the asymmetric component of the scheme.
The symmetric cipher and MAC can be chosen. Botan implements the DLIES
encryption scheme in ``src/lib/pubkey/dlies/dlies.cpp``, providing the
classes DLIES_Decryptor and DLIES_Encryptor. DLIES can be used in either
stream or block cipher mode. Both modes are implemented according to
[ISO-18033-2]_.

The DLIES_Encryptor constructor requires a ``KDF``, ``MAC`` and ``cipher``
algorithm and a *DH private key*. The class offers the following
functions:

-  ``set_other_key(key)``: Sets the other parties public Diffie-Hellman
   public key.
-  ``set_initialization_vector(IV)``: Sets the ``IV`` to use for the
   plaintext encryption.
-  ``enc(plaintext, plaintext length)``: Encryption function.

   -  Ensure that the other parties DH public key has been set correctly.
      If not terminate with respective error.

   1. Compute the Diffie-Hellman secret ``s`` using the provided DH
      private key and the other party's public value. Confer section
      :ref:`pubkey/dh`.
   2. Pass ``s`` to the specified KDF and derive keybits for usage with
      the cipher and extra keybits for the ``MAC``. If the KDF did not
      provide enough output bits, terminate with respective error.
   3. Encrypt the passed ``plaintext`` using the specified symmetric
      ``cipher`` and the derived encryption key.
   4. Compute the tag over the ciphertext using the specified ``MAC``
      function and the derived MAC key.
   5. Return the concatenation of the own DH public key, the ciphertext
      and the computed tag.

   -  If no cipher is passed, the algorithm operates in stream mode. In
      this mode, the ciphertext is computed as :math:`plaintext \oplus keybits`.

The DLIES_Decryptor requires similar parameters. DLIES_Decryptor offers
the following functions:

-  ``set_initialization_vector(IV)``: Sets the ``IV`` to use for the
   ciphertext decryption.
-  ``do_decrypt(input, input length)``:

   1. Perform preliminary length checks of the input.
   2. Extract the other parties public Diffie-Hellman key from
      ``input`` and calculate the shared DH secret ``s``.
   3. Derive the ``cipher`` and ``MAC`` key from the specified ``KDF``. If the
      KDF did not provide enough output bits, terminate with respective
      error.
   4. Extract the ciphertext from ``input`` and calculate the ``MAC``
      function using the derived ``MAC`` key.
   5. Validate that the calculated tag and the tag provided with input
      are equal. If they are not equal, return an empty plaintext
      vector.
   6. Decrypt the cipthertext using the derived cipher key.

   -  If no cipher is passed, the algorithm operates in stream mode. In
      this mode, the ciphertext is computed as :math:`plaintext \oplus keybits`.

**Conclusion:** The algorithms for encryption and decryption comply with [TR-02102-1]_.
Botan however does not restrict the used ``KDF``, ``MAC`` and ``cipher`` to the ones allowed in [TR-02102-1]_.

ECIES
^^^^^

The Elliptic Curve Integrated Encryption Scheme (ECIES) resembles the
DLIES algorithm. Instead of the Diffie-Hellman key exchange, the
Diffie-Hellman key exchange over elliptic curves is used as the
asymmetric component of the hybrid scheme. Botan implements the scheme
according to [ISO-18033-2]_. The implementation offers the operator
classes ``ECIES_Encryptor`` and ``ECIES_Decryptor`` and the ``ECIES_System_Params``
class in ``src/lib/pubkey/ecies/ecies.cpp``. [ISO-18033-2]_ requires the
definition of ECIES specific system parameters, called ECIES flags. The
available ECIES flags dictate certain computation rules:

-  SINGLE_HASH_MODE: Prefix the input of the ECDH key exchange with the
   encoded public point.
-  COFACTOR_MODE: Use cofactor multiplication during ECDH key exchange
   for decryption.
-  OLD_COFACTOR_MODE: Use ECDH cofactor multiplication on both sides.
-  CHECK_MODE: Test if the received point is on the curve.
-  To support all ECIES flags defined in [ISO-18033-2]_, two distinct
   implementations of the ECDH key agreement are required. The agreement
   function with cofactor multiplication is part of Botans default ECDH
   implementation. The ECIES specific implementation without cofactor
   multiplication is implemented in class ``ECIES_ECDH_KA_Operation`` of
   ``src/lib/pubkey/ecies/ecies.cpp``. The agreement without cofactor
   mode operates as follows:

   .. admonition:: ``ECIES_ECDH_KA_Operation::raw_agree()``

      **Input:**

      -  ``rng``: random number generator
      -  :math:`Q_b`: ECDH public point of the other party
      -  EC_Privatekey: ``d``, ``Q``, domain(curve parameters(first coefficient
         ``a``, second coefficient ``b``, prime ``p``), base point ``G``, ord(G) ``n``,
         cofactor of the curve ``h``)

      **Output:**

      -  ``S``: shared ECDH secret point

      **Steps:**

      1. Verify that the received public point :math:`Q_b` is on the elliptic curve. This
         check is part of the decode function ``OS2ECP()``.
      2. Sample a :math:`\lceil \frac{length(n)}{2} \rceil` bit long random blinding
         ``mask`` from ``rng`` and compute :math:`d'=d+n*mask`.
      3. Compute the shared secret point ``S`` as :math:`S=Q_b*d'`. This computation utilizes
         randomized Jacobian point coordinates with a blinding masks that is
         equal in size to the underlying field.
      4. Verify that the computed shared secret point ``S`` is on the selected elliptic curve
         (``on_the_curve()``).
      5. Return affine x coordinate of shared point ``S`` as
         shared secret. Before the transformation to affine coordinates is
         carried out, it is checked, if the shared point S is the point at
         infinity (``is_zero()``). If that is the case, a respective error is
         thrown.

The ECIES_Encryptor constructor requires a ECDH private key and ECIES
system parameters, which consist of the ECIES flags, a EC domain, a KDF,
a Cipher and a MAC algorithm. The class offers the following functions:

-  ``set_other_key(key)``: Sets the other parties public key.
-  ``set_initialization_vector(IV)``: Sets the ``IV`` to use for the
   plaintext encryption.
-  ``enc(plaintext, plaintext length)``:

   1. Ensure that the other parties ECDH public point has been set
      correctly and is not the point at infinity. If not terminate with
      respective error.
   2. Compute the ECDH secret ``s`` using the provided ECDH private key
      and the other parties public point. This operation honors the
      defined ECIES flags. Thus the implementation uses either the ECDH
      implementation described in section :ref:`pubkey/ecdh`, if OLD_COFACTOR_MODE is
      set or else the custom implementation without cofactor mode
      ``ECIES_ECDH_KA_Operation``, described above.
   3. Pass ``s`` to the specified KDF and derive keybits for the usage
      with the cipher and additional bits for the ``MAC``. If the KDF did
      not provide enough output bits, terminate with respective error.
   4. Encrypt the passed ``plaintext`` using the specified symmetric
      ``cipher`` and the derived encryption key.
   5. Compute the tag over the ciphertext using the specified ``MAC``
      function and the derived MAC key.
   6. Return the concatenation of the own encoded ECDH public point, the
      ciphertext and the computed tag.

The ECIES_Decryptor of the integrated scheme requires similar
parameters. The class offers the following functions:

-  ``set_initialization_vector(IV)``: Sets the ``IV`` to use for the
   ciphertext decryption.
-  ``do_decrypt(input, input length)``:

   1. Peform preliminary length checks of the input.
   2. Extract the public point from input and compute the ECDH secret
      ``s`` using the provided ECDH private key and the other parties
      public point. This operation honors the defined ECIES flags. Thus
      the implementation uses either the ECDH implementation described
      in section :ref:`pubkey/ecdh`, if OLD_COFACTOR_MODE or COFACTOR_MODE is set.
      Else the custom implementation without cofactor mode
      ``ECIES_ECDH_KA_Operation``, described above, is used.
   3. Pass ``s`` to the specified KDF and derive key bits for the usage
      with the cipher and additional bits for the ``MAC``. If the KDF did
      not provide enough output bits, terminate with respective error.
   4. Extract the ciphertext from ``input`` and calculate the ``MAC``
      function using the derived ``MAC`` key.
   5. Validate that the calculated tag and the tag provided in input are
      equal. If they are not equal, return an uninitialized plaintext
      vector.
   6. Decrypt the ciphertext using the derived cipher key.

**Conclusion:** The algorithms for encryption and decryption comply with [TR-02102-1]_.
Botan however does not restrict the used ``KDF``, ``MAC`` and ``cipher`` to the ones allowed in [TR-02102-1]_.
No special ECIES flags are required for compliance with the technical guideline.
