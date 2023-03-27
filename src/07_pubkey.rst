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

Key Encapsulation Mechanisms
----------------------------

A Key Encapsulation Mechanism (KEM) can be used to produce a shared key between parties.
A KEM works with an asymmetric key pair. Using the public key of Alice, Bob encapsulates a secret key that can only be decapsulated by Alice's private key.

Kyber
^^^^^

Botan implements CRYSTALS-Kyber in ``src/lib/pubkey/kyber/`` according to the specification in [Kyber-R3]_.
Refer to :ref:`Kyber Key Generation <pubkey_key_generation/kyber>` for more information on the key generation, parameters, and implementations of polynomial functions.

**Structure**

Kyber is given as a KEM but is built via a modified Fujisaki–Okamoto transform of an IND-CPA encryption scheme.
The class ``Kyber_KEM_Cryptor`` found in ``src/lib/pubkey/kyber/kyber_common/kyber.cpp`` realizes the IND-CPA encryption.
The child classes ``Kyber_KEM_Encryptor`` and ``Kyber_KEM_Decryptor`` respectively realize the IND-CCA2 KEM encapsulation/decapsulation [#kyber_cryptor_class]_.

.. [#kyber_cryptor_class]
   The IND-CPA encryption is a member of ``Kyber_KEM_Cryptor`` because both en- and decapsulation require it, whereas the IND-CPA decryption is only needed by the decapsulation and is, therefore, a member of ``Kyber_KEM_Decryptor``.

**Keys**

The class ``Kyber_KEM_Cryptor`` has a ``Kyber_PublicKeyInternal`` member ``public_key`` that supplies the value ``seed`` and the member function ``polynomials()``, which gives a decoded transpose of :math:`\mathbf{\hat{t}}` (L.2, Alg. 5 [Kyber-R3]_).
In the following, we denote the output of ``polynomials()`` as ``pk_t`` and the public key as ``pk = (pk_t, seed)``.

The class ``Kyber_KEM_Decryptor`` has a ``Kyber_PrivateKey`` member ``key``.
It supplies the hash value of the public key via ``H_public_key_bits_raw()`` (:math:`h`, L.2, Alg. 9, [Kyber-R3]_).
In the following, we call this ``sk_h``.
It also supplies the already decoded secret polynomial vector via ``polynomials()`` (:math:`\mathbf{\hat{s}}`, L.3, Alg. 6, [Kyber-R3]_), which we call ``sk_s`` in the following.
We, therefore, denote the secret key as ``sk=(sk_s, pk, sk_h, z)``, where ``z`` is the random value from the key generation.

**Ciphertexts**

The ``Ciphertext`` class is given a ``PolynomialVector b``, a ``Polynomial v``, and a ``KyberMode mode``. A ciphertext instance is represented via the members ``b`` and ``v`` (corresponding to :math:`\textbf{u}` and :math:`v` of [Kyber-R3]_, respectively).

Furthermore, the ``Ciphertext`` class provides ciphertext compression and encoding.
The implementation of the algorithms :math:`\textrm{Compress}_q(x,d)` and :math:`\textrm{Decompress}_q(x,d)` of [Kyber-R3]_ are optimized for all occurring values of :math:`d`.
The compression with :math:`d=d_u` and :math:`d=d_v` [#kyber_du_dv]_ is implemented in two respective ``Ciphertext::compress`` methods, i.e., one for polynomial vectors and one for polynomials. The same holds for decompression via ``Ciphertext::decompress_polynomial_vector`` and ``Ciphertext::decompress_polynomial``.
The public member functions ``Ciphertext::from_bytes`` and ``Ciphertext::to_bytes`` use this to realize **L. 1/L. 2 of Alg. 6** [Kyber-R3]_ and **L. 21/L. 22 of Alg. 5** [Kyber-R3]_, respectively.
The compression and decompression with :math:`d=1` are performed simultaneously with :math:`\textrm{Encode}_1` and :math:`\textrm{Decode}_1` within the methods ``Polynomial::to_message`` and ``Polynomial::from_message``, respectively (used in **L. 4, Alg. 6** and **L. 20, Alg. 5** [Kyber-R3]_). All compressions and decompressions are constant time.

.. [#kyber_du_dv]
   The values of :math:`d_u` and :math:`d_v` are not given as ``KyberConstants`` but are rather computed in place based on the value of `k`.

Kyber IND-CPA
"""""""""""""

**Encryption**

IND-CPA encryption works as follows, realizing **Algorithm 5** of [Kyber-R3]_:

.. admonition:: Kyber_KEM_Cryptor::indcpa_enc()

   **Input:**

   - ``pk = (pk_t, seed)``: public key
   - ``m``: message
   - ``coins``: randomness (input :math:`r` in Alg. 5 [Kyber-R3]_)

   **Output:**

   - ``c``: ciphertext bytes

   **Steps:**

   1. ``at = PolynomialMatrix::generate(seed, True, mode)`` (L. 3-8, Alg. 5 [Kyber-R3]_)
   2. ``sp = PolynomialVector::getnoise_eta1(coins, 0, mode)`` (performs ``k`` invocations of ``Polynomial::getnoise_eta1`` for each vector element; L. 9-12, Alg. 5 [Kyber-R3]_)
   3. ``ep = PolynomialVector::getnoise_eta2(coins, k, mode)`` (performs ``k`` invocations of ``Polynomial::getnoise_eta2`` for each vector element; L. 13-16, Alg. 5 [Kyber-R3]_)
   4. ``epp = Polynomial::getnoise_eta2(coins, 2*k, mode)`` (L. 17, Alg. 5 [Kyber-R3]_)
   5. ``sp.ntt()`` (L. 18, Alg. 5 [Kyber-R3]_)
   6. ``bp = (at * sp).invntt() + ep`` (L. 19, Alg. 5 [Kyber-R3]_)
   7. ``v = (pk_t * sp).invntt() + epp + Polynomial::from_message(m)`` (L. 20, Alg. 5 [Kyber-R3]_)
   8. ``c = Ciphertext(bp, v, mode).to_bytes()`` (L. 21-23, Alg. 5 [Kyber-R3]_)

   **Notes:**

   - The member function ``Polynomial::getnoise_eta1(seed, nonce, mode)`` uses ``PRF`` on the seed with incremented nonce values to call ``Polynomial::getnoise_cbd2`` or ``Polynomial::getnoise_cbd3`` depending on ``eta1``.
   - The member function ``Polynomial::getnoise_eta2(seed, nonce, mode)`` uses ``PRF`` on the seed with incremented nonce values to call ``Polynomial::getnoise_cbd2`` (as for all parameter sets ``eta2 = 2``).

**Decryption**

IND-CPA decryption works as follows, realizing **Algorithm 6** of [Kyber-R3]_:

.. |step_3_formular| replace:: :math:`\mathbf{\hat{s}}^T \circ \textrm{NTT}(\mathbf{u})`
.. |step_4_formular| replace:: :math:`\textrm{NTT}^{-1}(\mathbf{\hat{s}}^T \circ \textrm{NTT}(\mathbf{u}))`
.. |step_5_formular| replace:: :math:`v - \textrm{NTT}^{-1}(\mathbf{\hat{s}}^T \circ \textrm{NTT}(\mathbf{u}))`
.. admonition:: Kyber_KEM_Decryptor::indcpa_dec()

   **Input:**

   -  ``sk=(sk_s, pk, sk_h, z)``: secret key
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

   - The sign of ``mp`` is swapped in comparison with the specification. However, for the following compression only absolute values are relevant.

Kyber IND-CCA2
""""""""""""""

**Encapsulation**

IND-CCA2 encapsulation works as follows, realizing **Algorithm 8** of [Kyber-R3]_:

.. admonition:: Kyber_KEM_Encryptor::raw_kem_encrypt()

   **Input:**

   - ``pk = (pk_t, seed)``: public key
   - ``out_encapsulated_key``: ciphertext of shared key (to be overwritten)
   - ``out_shared_key``: plaintext shared key (to be overwritten)
   - ``rng``: random number generator

   **Output:**

   -  Overwritten ``out_encapsulated_key``, ``out_shared_key``

   **Steps:**

   1. ``shared_secret = H(m)`` where ``m`` is generated using ``rng`` (L. 1-2, Alg. 8 [Kyber-R3]_)
   2. ``(shared_secret || coins) = G(shared_secret || H(pk))`` where ``coins`` is the second half of the output of ``G`` (L. 3, Alg. 8 [Kyber-R3]_)
   3. ``out_encapsulated_key = Kyber_KEM_Cryptor::indcpa_enc(pk, shared_secret, coins)`` (L. 4, Alg. 8 [Kyber-R3]_)
   4. ``out_shared_key = KDF(shared_secret || H(out_encapsulated_key))`` (L. 5, Alg. 8 [Kyber-R3]_)

   **Notes:**

   - ``H(pk)`` is computed already in the constructor of the ``Kyber_PublicKeyInternal`` object and accessible via ``H_public_key_bits_raw()``.
   - The input/output structure corresponds to Botan's ``KEM_Encryption`` interface.

**Decapsulation**

IND-CCA2 decapsulation works as follows, realizing **Algorithm 9** of [Kyber-R3]_:

.. admonition:: Kyber_KEM_Decryptor::raw_kem_decrypt()

   **Input:**

   -  ``sk=(sk_s, pk, sk_h, z)``: secret key
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

**Remark:** [Kyber-R3]_ notes that implementations of the 90s variant may be vulnerable to timing attacks if the used AES is not constant time. However, like all of Botan's AES implementations, the one used for Kyber's 90s versions is.

**Remark:** Modular operations are performed with Barrett and Montgomery reductions.
