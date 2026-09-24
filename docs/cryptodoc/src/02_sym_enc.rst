Symmetric Encryption
====================

In the following we describe symmetric encryption algorithms and
schemes. We first present the implementation of Advanced Encryption Standard (AES) in Botan.
Afterwards, we give an overview of modes of operations and padding
schemes used in symmetric encryption algorithms.
Unless mentioned they are also recommend by the BSI [TR-02102-1]_.

AES Block Cipher
----------------

Botan provides six AES implementations: software, assembly, three
hardware alternatives (Advanced Encryption Standard New Instructions (AES-NI),
AES-ARMV8, AES-POWER8) and, since Botan 3.6.0, an implementation based on
the x86 Vector AES (VAES) instructions.

The software implementation (located in :srcref:`src/lib/block/aes/aes.cpp`) is
using a constant time bitsliced implementation with 32bit words.
Essentially, bit slicing emulates strategies of hardware-implementations in
software. Instead of using precomputed lookup tables, AES S-Boxes are
computed on-the-fly using bit-logical instructions. The runtime of these
instructions is inherently independent of their inputs, making the implementation
immune to timing attacks at the expense of oveall performance [KaesperSchwabe09]_.

Improving the performance of the bitsliced implementation by using 64bit or even
128bit words (i.e. SIMD) would be possible but is currently not implemented.
[#aes_64_128_bit_bitsliced_impl]_ The rational being that the software
implementation is usually a last-resort fallback. Processors with 64bit or SIMD
will typically also have instructions to support one of the hardware-backend
implementations nowadays.

.. [#aes_64_128_bit_bitsliced_impl]
   https://github.com/randombit/botan/blob/3.1.1/src/lib/block/aes/aes.cpp#L30-L39

The assembly implementation is based on vector permutation instructions. It
supports the Supplemental Streaming SIMD Extensions 3 (SSSE3)
instruction set created by Intel, ARM's Advanced SIMD (Neon) instruction
set and PowerPC's AltiVec instruction set. The implementation is based
on the code of Mike Hamburg, which provides protection against cache and
timing side channel attacks [AES-SSSE3]_. The code is located in
:srcref:`src/lib/block/aes/aes_vperm/aes_vperm.cpp`.

Additionally, Botan provides interfaces to cryptographic hardware extensions
in some widespread commodity processor instruction sets. They are hardened
against side channel attacks and are usually faster than the above-mentioned
software implementations. Specifically, Botan supports:

- | Intel's AES-NI
  | (code in :srcref:`src/lib/block/aes/aes_ni/aes_ni.cpp`)
- | ARMv8 AES extensions
  | (code in :srcref:`src/lib/block/aes/aes_armv8/aes_armv8.cpp`)
- | Power8 AES extensions
  | (code in :srcref:`src/lib/block/aes/aes_power8/aes_power8.cpp`)
- | x86 VAES (AVX2 vector AES instructions, processing several blocks per
    instruction)
  | (code in :srcref:`src/lib/block/aes/aes_vaes/aes_vaes.cpp`)

An application developer can enable and disable a specific
implementation at compile time by using macros:

-  ``BOTAN_HAS_AES_VAES``
-  ``BOTAN_HAS_AES_NI``
-  ``BOTAN_HAS_AES_ARMV8``
-  ``BOTAN_HAS_AES_POWER8``
-  ``BOTAN_HAS_AES_VPERM``
-  ``BOTAN_HAS_AES``

All AES implementations are enabled by default and application developers do not need to worry about which AES implementation is used.
The order in which the macros appear in the list above also indicates the order in which enabled implementations are used for encryption and decryption.
Botan uses the first enabled implementation
for which the corresponding instruction set is available on the
processor used. The key schedule is computed by the AES-NI code if
available and by a common generic key schedule function otherwise. The code
invoking a specific AES implementation is in
:srcref:`src/lib/block/aes/aes.cpp`.

AES-CCM
-------

AES-CCM is an authenticated encryption scheme which combines the AES
Counter (CTR) mode with authentication using the Cipher Block
Chaining-Message Authentication Code (CBC-MAC). Botan implements AES-CCM
according to the NIST specification [CCM]_.

The AES-CCM functionality is implemented in the classes ``CCM_Encryption``
and ``CCM_Decryption`` (located in :srcref:`src/lib/modes/aead/ccm/ccm.cpp`). Both
classes extend functionality of the ``CCM_Mode``, ``AEAD_Mode`` and
``Cipher_Mode`` abstract classes. The following public methods are used by
a developer when working with AES-CCM:

-  ``set_key(key)``: It initializes AES-CCM encryption / decryption with a
   symmetric key. The key length depends on the underlying AES block
   cipher size.
-  ``set_associated_data(ad)``: It sets optional associated data that is
   not included in the ciphertext but that should be authenticated.
-  ``start(nonce)``: It initializes the AES-CCM computation and the
   underlying counter mode with the provided nonce.
-  ``process(buffer)``: It saves the buffer to the internally stored
   message for later processing.
-  ``finish(buffer)``: It does the encryption/decrption of the message. It
   creates/verifies the authentication tag.

**Remark:** It is forbidden to re-use the same initialization vectors
(nonces) with the same AES-CCM key. Otherwise, the confidentiality of
the ciphertext is not ensured. It is up to the application developer to
choose the nonces properly.

**Remark:** It is forbidden to re-use the AES-CCM key for anything
else than AES-CCM.

**Remark:** The used tag length :math:`t` should be at least 64 bit.
This is a recommendation from [TR-02102-1]_ as an attacker can successfully
change authenticated data or a ciphertext with a success probability of
:math:`2^{-t}` per try.
The default in Botan is 128 bit.

**Remark:** In Botan the default maximum length of the message is
2\ :sup:`24` - 1 bytes (with a nonce size of 12 byte).
The maximum length can be configured to be 2\ :sup:`8\*L` - 1 by initializing L with a value between 2 and 8.
Note that this parameter is denoted q in [CCM]_.
The size of the nonce is then (15-L) bytes. Since Botan 3.12.0, a
message exceeding the above length limit is already rejected with an
``Invalid_State`` exception while it is buffered in ``process()``;
previously the overflow was only detected when the length was encoded
during ``finish()``.

**Remark:** In Botan the maximum size for the associated data is 65279
bytes.

**Remark:** Since Botan 3.13.0 the AES-CCM classes enforce their state
transitions. The associated data must be set before ``start()`` is called
for a message; ``start()`` must not be called again before the current
message has been finished with ``finish()``. Setting a new key resets any
pending message but preserves the associated data. If the tag verification
in ``finish()`` fails, the decryption object is reset to its initial state
and can be reused for a subsequent message. Violations of these rules are
reported with an ``Invalid_State`` exception.

**Remark:** Since Botan 3.12.0, if the decryption fails due to an
invalid authentication tag, the output buffer is zeroized before the
``Invalid_Authentication_Tag`` exception is thrown. This applies to all
AEAD modes (CCM, GCM, EAX, SIV, ChaCha20Poly1305). In earlier versions
the output buffer could still contain parts of the decrypted ciphertext
and it was up to the application developer to ensure it was not leaked.

**Remark:** Botan implements AES-CCM cipher suites in TLS. When
encrypting TLS records, Botan sets the nonce value to zero and
increments the nonce value with each new record. This effectively
prevents nonce reuse attacks [GCM-ND]_.

**Remark:** The total number of invocations of the underlying AES block
cipher using the same key shall be limited to 2\ :sup:`61`. If the
combined total length of the additional data and the plaintext processed
does not exceed 2\ :sup:`59` bytes, this limit will not be reached.

AES-GCM
-------

AES-GCM is an authenticated encryption scheme which combines AES
counter mode with authentication over Galois fields. Botan implements
AES-GCM according to the NIST specification [GCM]_.

The AES-GCM functionality is implemented in the classes ``GCM_Encryption``
and ``GCM_Decryption`` (located in :srcref:`src/lib/modes/aead/gcm/gcm.cpp`). Both
classes extend functionality of the ``GCM_Mode``, ``AEAD_Mode`` and ``Cipher_Mode``
abstract classes. These classes offer the following public methods,
which are used by a developer when working with AES-GCM:

-  ``set_key(key)``: It initializes AES-GCM encryption / decryption with a
   symmetric key. The key length depends on the underlying AES block
   cipher size.
-  ``set_associated_data(ad)``: It performs a GHASH computation over this
   data.
-  ``start(nonce)``: It initializes the AES-GCM computation and the
   underlying Counter mode with the provided nonce. It encrypts the
   zeroth counter value, which is later used to compute the
   authentication tag.
-  ``process(buffer)``: It takes the buffer value, encrypts it in the
   counter mode and updates the GHASH.
-  ``finish(buffer)``: It finalizes the counter mode encryption and GHASH
   computation. It creates an authentication tag.

The GHASH computation is implemented in the GHASH class (located in
``src/lib/utils/ghash/ghash.{cpp,h}``). Botan supports multiple
providers for Galois field multiplication. An application developer can
enable and disable a specific implementation at compile time by using
macros:

-  ``BOTAN_HAS_GHASH_AVX512_CLMUL`` (since Botan 3.11.0, code in
   :srcref:`src/lib/utils/ghash/ghash_avx512_clmul/ghash_avx512_clmul.cpp`)
-  ``BOTAN_HAS_GHASH_CLMUL_CPU``
-  ``BOTAN_HAS_GHASH_CLMUL_VPERM``

The order of check whether an implementation is enabled corresponds to
the order the macros appear in the list above. Botan uses the first
enabled implementation for which the corresponding instruction set is
available on the processor used. The software implementation is used in
case no hardware implementation is available. Since Botan 3.13.0 the
software table precomputation and multiplication of the GHASH class are
also shared with the Polyval implementation used by the (out of scope)
GCM-SIV mode; this refactoring does not change the GHASH computation.

**Remark:** Since Botan 3.13.0 the AES-GCM classes enforce their state
transitions: ``process()`` and ``finish()`` require a preceding
``start()`` for the current message, and ``start()`` must not be called
again before the current message has been finished. Setting a new key
resets any pending message. Violations are reported with an
``Invalid_State`` exception. Furthermore, the underlying counter mode
(``CTR_BE`` in :srcref:`src/lib/stream/ctr/ctr.cpp`), which is
instantiated with a 32-bit counter for GCM, since Botan 3.13.0 refuses to
generate keystream beyond the point where its counter would wrap around.
For AES-GCM this check is subsumed by the stricter message length limit
enforced by the GHASH computation (see below).

**Remark:** It is forbidden to re-use the same initialization vectors
(nonces) with the same AES-GCM key. Otherwise, the attacker could break
authenticity of the constructed ciphertext [GCM-FA]_ [GCM-ND]_. It is up to
the application developer to choose the nonces properly.

**Remark:** The AES-GCM specification [GCM]_ prescribes a maximum
length of (2\ :sup:`39` - 256) bits, i.e. (2\ :sup:`32` - 2) blocks,
for the message to be encrypted. Since Botan 3.12.0 this limit is
enforced: the GHASH computation throws an ``Invalid_State`` exception
("GCM message length limit exceeded") once the processed plaintext or
ciphertext exceeds (2\ :sup:`39` - 256) / 8 bytes. The limit applies to
the message only, not to the associated data. In earlier versions Botan
did not check the plaintext length explicitly and it was up to the
application developer to choose correct data lengths.

**Remark:** Botan implements AES-GCM cipher suites in TLS. When
encrypting TLS records, Botan sets the nonce value to zero and
increments the nonce value with each new record. This effectively
prevents nonce reuse attacks [GCM-ND]_.

**Remark:** We refer to [TR-02102-1]_ for further security considerations
on AES-GCM.

AES-CBC
-------

AES-CBC [CBC]_ is implemented in classes ``CBC_Encryption`` and
``CBC_Decryption`` (located in :srcref:`src/lib/modes/cbc/cbc.cpp`). The
constructors of these classes offer usage of different padding schemes.
When using AES-CBC, the AES cipher has to be provided as a parameter.

The following public methods are used by a developer when working with
AES-CBC:

-  ``set_key(key)``: It initializes AES-CBC encryption / decryption with a
   symmetric key.
-  ``start(nonce)``: It initializes the AES-CBC computation with the
   provided nonce.
-  ``process(buffer)``: It takes the buffer value, encrypts / decrypts it
   in the CBC mode, and puts the result into the buffer.
-  ``finish(buffer)``: It finalizes the CBC encryption / decryption
   process, and puts the result into the buffer.

**Remark:** AES-CBC does not provide authentication. Generated
ciphertexts must be protected by MACs or signatures.

**Remark:** The developer must always use fresh unpredictable
initialization vectors.

**Remark:** Since Botan 3.13.0, if the padding check during decryption
fails, the decrypted data in the output buffer is zeroized before the
``Decoding_Error`` exception is thrown, analogous to the behavior of the
AEAD modes on an invalid authentication tag. Also since Botan 3.13.0,
encrypting an input that is not a multiple of the block size with the
``NoPadding`` scheme is rejected with an ``Invalid_Argument`` exception
instead of triggering an internal assertion.

**Remark:** We refer to [TR-02102-1]_ for further security considerations
on AES-CBC.

XTS
---

The XEX-based tweaked-codebook mode with ciphertext stealing is a block
cipher mode of operation. [TR-02102-1]_ does not cover the XTS mode.
Nevertheless, it mentions XTS to have good efficiency and security
properties for raw storage media encryption. Referring to
[SP800-38E]_ it should be avoided in other scenarios such as transit data
encryption. In addition, it is recommended that the length of the
ciphertext, protected with the same key should not exceed the length of :math:`2^{20}`
cipher blocks. Botan implements XTS in :srcref:`src/lib/modes/xts/xts.cpp`
according to [IEEE-1619]_. The following functions are available:

-  ``XTS_Mode(cipher)``: Constructs a XTS_Mode object with the passed
   block cipher. Only block ciphers with a block size of 64, 128, 192,
   256, 512 or 1024 bits are supported, i.e. the sizes for which the
   polynomial doubling in ``src/lib/utils/poly_dbl`` is implemented.
-  ``key_schedule(key, key length)``: Splits the passed key in half and
   sets the cipher and the tweak key. If the key length is odd or the
   underlying cipher does not support a key with length :math:`\frac{key}{2}`, the function
   throws an error. Since Botan 3.13.0 setting a new key also discards
   the tweak computed from a previous nonce, so that ``start_msg()`` has
   to be called again before further data can be processed.
-  ``start_msg(nonce, nonce length)``: Sets nonce as input of tweak
   computation and compute initial tweak as :math:`E_{k_{2}}(nonce)`.
-  ``process(buffer, buffer length)``: Processes the data from the passed
   buffer. Note that the function is only able to processes full
   plaintext blocks.
-  ``finish(buffer)``: Finalizes the data processing. Since Botan 3.13.0
   an ``Invalid_State`` exception is thrown if no tweak has been set
   before via ``start_msg()``.

Padding Schemes
---------------

Botan implements the following block cipher padding schemes (see
:srcref:`src/lib/modes/mode_pad/mode_pad.cpp`):

-  PKCS#7 [RFC5652]_: The last byte in the padded block defines the
   padding length *p*, the remaining padding bytes are set to *p* as
   well.
-  ANSI X9.23: The last byte in the padded block defines the padding
   length, the remaining padding is filled with 0x00.
   Note that this padding scheme is not recommended by the BSI.
-  ISO/IEC 7816-4 / ISO/IEC 9797-1: The first padding byte is set to 0x80, the remaining
   padding bytes are set to 0x00.
-  ESP [RFC4304]_: The first padding byte is set to 0x01, the remaining
   padding bytes each increase by one.
-  Null: No padding.

**Remark:** By processing a decrypted message, the padding is validated
in constant time. If the padding is invalid, Botan sets the padding
length to 0. This is a countermeasure against side channel attacks.
However, in specific cases this countermeasure is not sufficient and
padding oracle attacks can be mounted [Lucky13]_. The application
developer is thus responsible for a proper design of his application:
the application has to validate message authenticity before it is
decrypted.

**Remark:** The TLS implementation introduces a constant time CBC
unpadding functionality to prevent the Lucky 13 attack [Lucky13]_. This
can be found in :srcref:`src/lib/tls/tls12/tls_cbc/tls_cbc.cpp`. It is important to
note that for DTLS there still exists a timing channel that may be
exploitable in a Lucky13 variant.
