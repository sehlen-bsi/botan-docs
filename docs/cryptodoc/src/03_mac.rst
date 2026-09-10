Message Authentication Codes
============================

The next section examines the Message Authentication Codes recommended
in [TR-02102-1]_: CMAC, HMAC and GMAC. All three algorithms are implemented
in Botan.

CMAC
----

The Cipher-based Message Authentication Code or One-Key MAC (OMAC1)
algorithm uses a block cipher to compute an authentication code. The
CMAC output length equals the block size of the used block cipher. Botan
implements the algorithm according to [NIST-OMAC]_. The class CMAC is in
:srcref:`src/lib/mac/cmac/cmac.cpp` and offers the following relevant functions:

-  ``CMAC(block cipher)``: Constructs a CMAC object with the passed block
   cipher. Only block ciphers with a block size of 64, 128, 192, 256, 512
   or 1024 bits are supported, i.e. the sizes for which the polynomial
   doubling in ``src/lib/utils/poly_dbl`` is implemented.
-  ``clear()``: Clears all sensitive data of the CMAC object.
-  ``start_msg(nonce)``: Since Botan 3.13.0 CMAC implements this method
   (invoked via ``start()``): it discards any partially processed message
   and begins a new one under the same key. As CMAC does not use a nonce,
   a non-empty nonce is rejected with an ``Invalid_IV_Length`` exception.
-  ``key_schedule(key, key length)``: Derives the subkeys :math:`k_1` and :math:`k_2` from
   :math:`E_k(0)`, where :math:`E_K()`
   is the encryption function of the specified block cipher.
-  ``add_data(data, data length)``: Computes the CMAC over the passed
   data.
-  ``final_result(buffer)``: Finalizes the MAC computation, pads the last
   message block with :math:`10 \ldots 0_2` if necessary, XORs the respective subkey and
   writes the calculated MAC to the passed buffer.

HMAC
----

The Keyed-Hashing for Message Authentication algorithm uses an
underlying cryptographic hash function to compute an authentication
code. The HMAC output length equals the output length of the underlying
hash function. Botan implements the HMAC algorithm [RFC2104]_ in
:srcref:`src/lib/mac/hmac/hmac.cpp`. The maximum supported key length is 8192
Bytes (since Botan 3.11.0; 4096 bytes before). The following functions of the class HMAC are provided:

-  ``HMAC(hash function)``: Constructs an HMAC object with the passed
   cryptographic hash function. The hash function's block size must not
   be smaller than its output length and, since Botan 3.13.0, the output
   length must be at least 8 bytes; otherwise an ``Invalid_Argument``
   exception is thrown.
-  ``clear()``: Clears all sensitive data of the HMAC object.
-  ``start_msg(nonce)``: Since Botan 3.13.0 HMAC implements this method
   (invoked via ``start()``): it discards any partially processed message
   and restarts the inner hash computation with the keyed inner block.
   A non-empty nonce is rejected with an ``Invalid_IV_Length`` exception.
-  ``key_schedule(key, key length)``: Creates ipad and opad with the
   length of hash output, compresses the passed key with the specified
   hash function if its length exceeds the hash function's block size,
   and computes :math:`key \oplus ipda`, :math:`key \oplus opad`.
-  ``add_data(data, data length)``: Adds data to inner hash input.
-  ``final_result(buffer)``: Computes inner hash and subsequently the
   outer hash. Writes output of the outer hash function to the passed
   buffer.

GMAC
----

GMAC combines counter mode of operation with a Galois field computation.
Botan implements GMAC according to the NIST specification [GCM]_.

The GMAC functionality is implemented in the class *GMAC* (located in
:srcref:`src/lib/mac/gmac/gmac.cpp`). This class offers the following public
methods and constructors, which are used by a developer when working
with GMAC:

-  ``GMAC(BlockCipher* cipher)``: Constructs a GMAC object with the
   underlying block cipher. Since Botan 3.13.0 block ciphers with a block
   size other than 128 bits are rejected with an ``Invalid_Argument``
   exception.
-  ``set_key(key)``: It initializes GMAC computation with a symmetric key.
   The key length depends on the underlying block cipher size.
-  ``start_msg(nonce)``: It initializes the GMAC computation with the
   provided nonce. It encrypts a block of zero bytes, which is later
   used as an input into the GHASH computation. Since Botan 3.13.0 an
   empty nonce is rejected with an ``Invalid_IV_Length`` exception, and
   any data of a previous message that was started but not finalized is
   discarded.
-  ``add_data(buffer)``: It takes the buffer value and updates the GHASH.
   Since Botan 3.13.0 calling this method without a preceding
   ``start_msg()`` for the current message throws an ``Invalid_State``
   exception.
-  ``final_result(mac)``: It finalizes the GHASH computation and creates
   an authentication tag. It fills the provided mac parameter array with
   the authentication tag data.

**Remark:** It is forbidden to re-use the same initialization vectors
(nonces) with the same GMAC key. Otherwise, the attacker could break the
authenticity of the constructed ciphertext [GCM-FA]_ [GCM-ND]_. It is up to
the application developer to choose the nonces properly. Botan ensures
that the developer sets the nonce before each new GMAC computation.

**Remark:** GMAC is generally used in AES-GCM. For different
encryption mechanisms HMAC and CMAC should be used in favor of GMAC.

KMAC
----

KMAC is a message authentication code based on the Keccak sponge construction,
and more specifically, on the cSHAKE function. Both are defined in [SP800-185]_.

Botan implements both KMAC-128 and KMAC-256 with a variable (user-defined)
output length. Note that the output length must be defined at the beginning,
Botan currently does not implement the XOF variants of KMAC.

KMAC is implemented in :srcref:`src/lib/mac/kmac/kmac.cpp`, and cSHAKE can be
found in :srcref:`src/lib/xof/cshake_xof/cshake_xof.cpp`. Note that cSHAKE is
an implementation detail that is not exposed to the library user.

-  ``KMAC128(output_bits)`` / ``KMAC256(output_bits)``: Constructs a KMAC object
   that will produce a MAC tag of ``output_bits`` length (divisible by 8).
-  ``set_key(key)``: It initializes KMAC computation with a symmetric key.
   The key length is not fixed. Botan supports a maximum key length of 192 bytes.
-  ``start_msg(nonce)``: It initializes the KMAC computation with an optional
   nonce that is absorbed into the Keccak sponge with a padding first.
   Since Botan 3.13.0 the internal cSHAKE state is cleared beforehand, so
   that a previously started but unfinished message is discarded.
-  ``add_data(buffer)``: It takes the buffer value and updates KMAC's Internal
   Keccak sponge state.
-  ``final_result(mac)``: It finalizes the KMAC computation and creates
   an authentication tag of length ``output_bits``. It fills the provided mac
   parameter array with the authentication tag data.

**Remark:** Botan does not prevent the user from using short keys and/or MAC
tags. It is the responsibility of the library user to select appropriate key
lengths and MAC tag lengths.

**Remark:** Before Botan 3.13.0 the ``bytepad`` operation of [SP800-185]_
(implemented in
:srcref:`src/lib/permutations/keccak_perm/keccak_helpers.h`) was applied
incorrectly when the encoded input strings already filled an exact multiple
of the sponge rate: in this case an additional all-zero block was absorbed.
This affected the encoding of the key and of the function name/customization
string in KMAC (and cSHAKE) for the respective key or customization string
lengths and led to outputs deviating from the specification. Botan 3.13.0
fixes the padding computation and adds corresponding test vectors.
