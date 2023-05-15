Symmetric Encryption
====================

In the following we describe symmetric encryption algorithms and
schemes. We first present the implementation of Advanced Encryption Standard (AES) in Botan.
Afterwards, we give an overview of modes of operations and padding
schemes used in symmetric encryption algorithms.
Unless mentioned they are also recommend by the BSI [TR-02102-1]_.

AES Block Cipher
----------------

Botan provides five AES implementations: software, assembly and three
hardware alternatives (Advanced Encryption Standard New Instructions (AES-NI), AES-ARMV8, AES-POWER8).

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
   https://github.com/randombit/botan/blob/3.0.0-alpha1/src/lib/block/aes/aes.cpp#L29-L38

The assembly implementation is based on vector permutation instructions. It
supports the Supplemental Streaming SIMD Extensions 3 (SSSE3)
instruction set created by Intel, ARM's Advanced SIMD (Neon) instruction
set and PowerPC's AltiVec instruction set. The implementation is based
on the code of Mike Hamburg, which provides protection against cache and
timing side channel attacks [AES-SSSE3]_. The code is located in
:srcref:`src/lib/block/aes_vperm/aes_vperm.cpp`.

Additionally, Botan provides interfaces to cryptographic hardware extensions
in some widespread commodity processor instruction sets. They are hardened
against side channel attacks and are usually faster than the above-mentioned
software implementations. Specifically, Botan supports:

- | Intel's AES-NI
  | (code in :srcref:`src/lib/block/aes_ni/aes_ni.cpp`)
- | ARMv8 AES extensions
  | (code in :srcref:`src/lib/block/aes_armv8/aes_armv8.cpp`)
- | Power8 AES extensions
  | (code in :srcref:`src/lib/block/aes_power8/aes_power8.cpp`)

An application developer can enable and disable a specific
implementation at compile time by using macros:

-  ``BOTAN_HAS_AES_NI``
-  ``BOTAN_HAS_AES_ARMV8``
-  ``BOTAN_HAS_AES_POWER8``
-  ``BOTAN_HAS_AES_VPERM``
-  ``BOTAN_HAS_AES``

All AES implementations are enabled by default and application developers do not need to worry about which AES implementation is used.
The order in which the macros appear in the list above also indicated the order in which enabled implementations are used.
Botan uses the first enabled implementation
for which the corresponding instruction set is available on the
processor used. The code invoking a specific AES implementation is in
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
a developer when working with AES-CBC:

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
2\ :sup:`24` bytes (with a nonce size of 12 byte).
The maximum length can be configured to be 2\ :sup:`8\*L` by initializing L with a value between 2 and 8.
Note that this parameter is denoted q in [CCM]_.
The size of the nonce is then (15-L) bytes.

**Remark:** In Botan the maximum size for the associated data is 65279
bytes.

**Remark:** If the decryption in Botan fails, the output buffer can
still contain parts of the decrypted ciphertext. It is up to the
application developer to ensure it is not leaked.

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

-  ``BOTAN_HAS_GCM_CLMUL_CPU``
-  ``BOTAN_HAS_GHASH_CLMUL_VPERM``

The order of check whether an implementation is enabled corresponds to
the order the macros appear in the list above. Botan uses the first
enabled implementation for which the corresponding instruction set is
available on the processor used. The software implementation is used in
case no hardware implementation is available.

**Remark:** It is forbidden to re-use the same initialization vectors
(nonces) with the same AES-GCM key. Otherwise, the attacker could break
authenticity of the constructed ciphertext [GCM-FA]_ [GCM-ND]_. It is up to
the application developer to choose the nonces properly.

**Remark:** AES-GCM specification prescribes the maximum length of the
message to be encrypted to (2\ :sup:`32` - 1) blocks. Botan does not
check the plaintext length explicitly. It is currently up to the
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
   block cipher. Only the block sizes 64 and 128 bit are supported.
-  ``key_schedule(key, key length)``: Splits the passed key in half and
   sets the cipher and the tweak key. If the key length is odd or the
   underlying cipher does not support a key with length :math:`\frac{key}{20}`, the function
   throws an error.
-  ``start_msg(nonce, nonce length)``: Sets nonce as input of tweak
   computation and compute initial tweak as :math:`E_{k_{2}}(nonce)`.
-  ``process(buffer, buffer length)``: Processes the data from the passed
   buffer. Note that the function is only able to processes full
   plaintext blocks.
-  ``finish(buffer)``: Finalizes the data processing,

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
can be found in :srcref:`src/lib/tls/tls_cbc/tls_cbc.cpp`. It is important to
note that for DTLS there still exists a timing channel that may be
exploitable in a Lucky13 variant.
