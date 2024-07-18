Hybrid Encryption Schemes
=========================

A hybrid encryption scheme is a combination of an asymmetric and a
symmetric cryptosystem. In detail the participating parties agree on a
shared secret, which is then used to encrypt or decrypt data with a
symmetric cipher. In addition, the authenticity of the data is secured
with a MAC. The following schemes are both Integrated Encryption Schemes
and standardized by the IEEE, ANSI and ISO.

DLIES
-----

.. warning::

   As of Botan 3.5.0 the DLIES implementation is considered deprecated and
   will be removed in a future release.

The Discrete Logarithm Integrated Encryption Scheme (DLIES) utilizes the
Diffie-Hellman key exchange as the asymmetric component of the scheme.
The symmetric cipher and MAC can be chosen. Botan implements the DLIES
encryption scheme in :srcref:`src/lib/pubkey/dlies/dlies.cpp`, providing the
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
-----

The Elliptic Curve Integrated Encryption Scheme (ECIES) resembles the
DLIES algorithm. Instead of the Diffie-Hellman key exchange, the
Diffie-Hellman key exchange over elliptic curves is used as the
asymmetric component of the hybrid scheme. Botan implements the scheme
according to [ISO-18033-2]_. The implementation offers the operator
classes ``ECIES_Encryptor`` and ``ECIES_Decryptor`` and the ``ECIES_System_Params``
class in :srcref:`src/lib/pubkey/ecies/ecies.cpp`. [ISO-18033-2]_ requires the
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
   :srcref:`src/lib/pubkey/ecies/ecies.cpp`. The agreement without cofactor
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
