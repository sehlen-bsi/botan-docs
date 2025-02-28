.. _tpm/main:

Trusted Platform Module
=======================

Botan provides a helper to use asymmetric key material hosted by a TPM. Once
initialized, such keys can be used in the same way as any other key in Botan.
There are independent wrappers for TPM 1.2 and TPM 2.0. The TPM 1.2 wrapper is
deprecated and will be removed in a future release. This chapter only covers
the TPM 2.0 wrapper and specifies the calls made to the ESAPI by Botan.

The TPM 2.0 support in Botan relies on the `TPM2-TSS library
<https://github.com/tpm2-software/tpm2-tss>` as specified by the Trusted
Computing Group. More specifically, it uses the Enhanced System API (ESAPI) of
the TPM2-TSS library.

Currently, this TPM wrapper is limited to basic functionality. Particularly,
it does not support:

 * Policy-driven access control
 * Reading or manipulating PCR measurements
 * Access of NVRAM
 * Remote attestation
 * ECDH key exchange
 * Fine grained control over the capabilities of created keys

.. _tpm/context:

TPM Context
-----------

The TPM context is the main entry point to the TPM functionality. It is required
for virtually all TPM operations. The context is created by calling
:srcref:`Botan::TPM_Context::create
<src/lib/prov/tpm2/tpm2_context.h:52|create>` and provides access to the TPM's
capabilities and fundamental key management operations.

.. admonition:: TPM2::Context::create()

   **Input:**

   - ``tcti_name``: (optional) The name of the TPM Command Transmission Interface (TCTI) to use.
   - ``tcti_conf``: (optional) The configuration string for the TCTI.

   **Steps:**

   - ``m_tcti_ctx = Tss2_TctiLdr_Initialize_Ex(tcti_name, tcti_conf)``
   - ``m_esys_ctx = Esys_Initialize(m_tcti_ctx)``

.. admonition:: TPM2::Context::persist()

   **Input:**

   - ``ctx``: The TPM context
   - ``key``: The (currently transient) TPM private key to persist
   - ``sessions``: The TPM session bundle
   - ``auth_value``: The TPM authorization value for the key
   - ``handle``: (Optional) The handle the key shall be persisted under

   **Output:**

   - ``handle``: The handle the key was persisted under

   **Steps:**

   - If no handle was provided, ``handle = next_free_handle()`` (via ``Esys_GetCapability``)
   - ``Esys_EvictControl(ctx, key.transient_handle(), sessions, handle, out(handle))``
   - ``Esys_TR_SetAuth(ctx, key.transient_handle(), auth_value)``
   - ``key.persistent_handle() = Esys_TR_GetTpmHandle(ctx, key.transient_handle())``
   - Return ``handle``

   **Notes:**

   - ``out(handle)`` indicates that ``handle`` is the output parameter to be written to.

.. admonition:: TPM2::Context::evict()

   **Input:**

   - ``ctx``: The TPM context
   - ``key``: The (currently persistent) TPM private key to be evicted
   - ``sessions``: The TPM session bundle

   **Steps:**

   - ``Esys_EvictControl(ctx, key.transient_handle(), sessions)``


.. _tpm/session:

TPM Sessions
------------

TPM sessions are used to authenticate TPM operations and enable secure
communication between the application and the TPM. They also facilitate policy
driven access control, which is currently not explicitly supported by this
wrapper.

Most TPM operations require one or more session objects to be passed as input,
via a so-called "session bundle" that can contain up to three such session
objects. Botan provides a helper type for creating these bundles.

Botan's TPM session wrapper is implemented in :srcref:`[src/lib/prov]/tpm2/tpm2_session.h`.

.. admonition:: TPM2::Session::unauthenticated_session()

   **Input:**

   - ``ctx``: The TPM context
   - ``sym_algo``: The symmetric algorithm to use for the session (default: ``CFB(AES-256)`` (Cipher Feedback Mode))
   - ``hash_algo``: The hash algorithm to use for the session (default: ``SHA-256``)

   **Output:**

   - ``session``: A session object that supports unauthenticated but encrypted communication with the TPM

   **Steps:**

   - ``m_session_handle = Esys_StartAuthSession(ctx, TPM2_SE_HMAC, sym_algo, hash_algo)``

   **Notes:**

   - This does not provide confidentiality against an attacker with access to the
     communication channel between the application and the TPM.

.. admonition:: TPM2::Session::authenticated_session()

   **Input:**

   - ``ctx``: The TPM context
   - ``key``: A TPM-hosted key to use for the key exchange
   - ``sym_algo``: The symmetric algorithm to use for the session (default: ``CFB(AES-256)`` (Cipher Feedback Mode))
   - ``hash_algo``: The hash algorithm to use for the session (default: ``SHA-256``)

   **Output:**

   - ``session``: A session object that supports encrypted communication with the TPM using a secret established using ``key``

   **Steps:**

   - ``m_session_handle = Esys_StartAuthSession(ctx, TPM2_SE_HMAC, key, sym_algo, hash_algo)``

   **Notes:**

   - Assuming the public part of ``key`` is trustworthy due to external or
     organizational means, this provides confidentiality against an attacker
     with access to the communication channel between the application and the
     TPM.

.. _tpm/crypto_backend:

Crypto Backend
--------------

The communication between the application and the TPM can (and should) be
encrypted using :ref:`TPM2 Sessions <tpm/session>`. The protocol used for this
communication is specified by the Trusted Computing Group and implemented by the
TPM2-TSS library. Starting with version 4.0 the TPM2-TSS library provides
``Esys_SetCryptoCallbacks``, that allows overriding the cryptographic primitives
used for this encryption by the application at runtime.

Botan provides such a "crypto backend" to form a self-contained TPM wrapper that
does not depend on any other cryptographic library.

See
:srcref:`[src/lib/prov/tpm2/tpm2_crypto_backend]/tpm2_crypto_backend_impl.cpp:861|set_crypto_callbacks`
for the implementation of the crypto backend.


Random Number Generation
------------------------

TPMs come with a built-in random number generator. Botan provides a helper to
use this RNG in the same way as any other RNG in Botan. See :ref:`rng/tpm2` for
details.


.. _tpm/asym_keys:

Asymmetric Keys
---------------

A major use case for TPMs is to host asymmetric keys. Botan provides wrappers to
use these keys in the same way as any other key in Botan, namely via the
``Private_Key`` and ``Public_Key`` interfaces. For RSA, Botan supports
signing/verification and encryption/decryption. For ECC, Botan supports
signing/verification using ECDSA. ECDH is not supported at the moment.

Public key operations (encryption and verification) can be performed either
by the TPM, or by transforming the public key to a Botan key and performing the
operation in software using Botan's implementations. Private key operations
(decryption and signing) are always performed by the TPM.

Since the usage of RSA and ECC keys is very similar, this section provides an
overview of the functionality without distinguishing between RSA and ECC keys.

.. admonition:: Key pair generation

   **Code:**

   - RSA: :srcref:`TPM2::RSA_PrivateKey::create_unrestricted_transient <src/lib/prov/tpm2/tpm2_rsa/tpm2_rsa.cpp:68|create_unrestricted_transient>`
   - ECDSA: :srcref:`TPM2::ECDSA_PrivateKey::create_unrestricted_transient <src/lib/prov/tpm2/tpm2_ecc/tpm2_ecc.cpp:61|create_unrestricted_transient>`

   **Input:**

   - ``ctx``: The TPM context
   - ``sessions``: The TPM session bundle
   - ``auth_value``: The TPM authorization value for the key
   - ``parent_key``: The parent key under which the new key shall be created
   - ``key_spec``: RSA keylength and exponent or ECC curve spec

   **Output:**

   - ``key``: A transient private key object

   **Steps:**

   1. Create a ``TPM2B_SENSITIVE_CREATE`` structure ``sensitive_data`` with ``auth_value``
   2. Create a ``TPMT_PUBLIC`` key template ``template`` with ``key_spec`` that does not restrict the key for any specific use case
   3. ``pub_info, priv_bytes = Esys_CreateLoaded(ctx, parent_key, sessions, sensitive_data, template)``
   4. Return a ``TPM2::PrivateKey`` as a wrapper object

.. admonition:: Transient Key loading

   **Code:**

   - :srcref:`TPM2::PrivateKey::load_transient <src/lib/prov/tpm2/tpm2_key.cpp:187|load_transient>`

   **Input:**

   - `ctx`: The TPM context
   - `auth_value`: The TPM authorization value for the key
   - `parent_key`: The parent key under which the new key shall be created
   - `public_blob`: The public part of the key
   - `private_blob`: The private part of the key (previously encrypted by the TPM)
   - `sessions`: The TPM session bundle

   **Output:**

   - ``key``: A transient private key object

   **Steps:**

   1. ``handle = Esys_Load(ctx, parent_key, sessions, public_blob, private_blob)``
   2. ``Esys_TR_SetAuth(ctx, handle, auth_value)``
   3. Return a ``TPM2::PrivateKey`` as a wrapper object

.. admonition:: Persistent Key loading

   **Code:**

   - :srcref:`TPM2::PrivateKey::load_persistent <src/lib/prov/tpm2/tpm2_key.cpp:177|load_persistent>`

   **Input:**

   - ``ctx``: The TPM context
   - ``persistent_handle``: The handle of the persistent key to load
   - ``auth_value``: The TPM authorization value for the key
   - ``sessions``: The TPM session bundle

   **Output:**

   - ``key``: A persistent private key object

   **Steps:**

   1. ``handle = Esys_TR_FromTPMPublic(ctx, persistent_handle, sessions)``
   2. ``Esys_TR_SetAuth(ctx, handle, auth_value)``
   3. Return a ``TPM2::PrivateKey`` as a wrapper object


Signature Generation and Verification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Signatures are supported for both RSA and ECC keys. The implementation is
largely the same for both wrappers. Therefore, we provide a unified description
here.

.. admonition:: Signature Generation

   **Input:**

   - ``ctx``: The TPM context
   - ``key``: The TPM private key
   - ``sessions``: The TPM session bundle
   - ``hash_name``: The hash algorithm to use for the signature
   - ``data``: The data to sign

   **Output:**

   - ``signature``: The signature of the data

   **Steps:**

   1. Calculate the digest of ``data``:

      1. If ``key`` is *not marked* as "restricted", use Botan's software implementation of ``hash_name`` and create a dummy ``validation_ticket``
      2. Otherwise, use the TPM to calculate the digest (see :srcref:`[src/lib/prov/tpm2]/tpm2_hash.cpp`):

         1. ``hash_obj = Esys_HashSequenceStart(ctx, sessions, hash_name)``
         2. ``Esys_SequenceUpdate(ctx, hash_obj, sessions, data)``
         3. ``(digest, validation_ticket) = Esys_SequenceComplete(ctx, hash_obj, sessions)``

   2. ``sig = Esys_Sign(ctx, key, sessions, digest, validation_ticket)`` (see :srcref:`[src/lib/prov/tpm2]/tpm2_pkops.cpp:51|sign`)
   3. Marshal the signature into its canonical byte encoding
   4. Return the signature

.. admonition:: Signature Verification

   **Input:**

   - ``ctx``: The TPM context
   - ``key``: The TPM public key
   - ``sessions``: The TPM session bundle
   - ``hash_name``: The hash algorithm to use for the signature
   - ``data``: The data to verify
   - ``signature``: The signature to verify

   **Output:**

   - ``valid``: Whether the signature is valid

   **Steps:**

   1. Calculate the digest of ``data`` using Botan's software implementation of ``hash_name``
   2. Unmarshal the signature from bytes into a ``TPMT_SIGNATURE`` object
   3. ``valid = Esys_Verify(ctx, key, sessions, digest, signature)`` (see :srcref:`[src/lib/prov/tpm2]/tpm2_pkops.cpp:103|is_valid_signature`)
   4. Return ``valid`` (either ``true`` or ``false``)


RSA Encryption and Decryption
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Currently only RSA encryption and decryption are supported. ECDH is not
supported at the moment.

.. admonition:: Encryption

   **Input:**

   - ``ctx``: The TPM context
   - ``key``: The TPM public key
   - ``sessions``: The TPM session bundle
   - ``padding``: The RSA padding to be used
   - ``plaintext``: The data to encrypt

   **Output:**

   - ``ciphertext``: The encrypted data

   **Steps:**

   1. ``ciphertext = Esys_RSA_Encrypt(ctx, key, sessions, padding, plaintext)`` (see :srcref:`[src/lib/prov/tpm2]/tpm2_rsa/tpm2_rsa.cpp:269|encrypt`)
   2. Return the ciphertext

.. admonition:: Decryption

   **Input:**

   - ``ctx``: The TPM context
   - ``key``: The TPM private key
   - ``sessions``: The TPM session bundle
   - ``padding``: The RSA padding to be used
   - ``ciphertext``: The data to decrypt

   **Output:**

   - ``plaintext``: The decrypted data

   **Steps:**

   1. ``plaintext = Esys_RSA_Decrypt(ctx, key, sessions, padding, ciphertext)`` (see :srcref:`[src/lib/prov/tpm2]/tpm2_rsa/tpm2_rsa.cpp:352|decrypt`)
   2. Return the plaintext
