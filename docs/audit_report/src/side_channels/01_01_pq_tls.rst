"""""""""""""""""
TLS 1.3 PQ-Hybrid
"""""""""""""""""

Analysed variant:

- x25519/Kyber-512-r3/cloudflare

For the analysis of TLS 1.3 PQ-Hybrid the Botan CLI was used.
To create the needed key and certificate files, the following command prompts were used:

.. code-block:: shell

    $ ./botan keygen --algo=ECDSA --params=secp256r1 --output=server_key.pem
    $ ./botan gen_self_signed server_key.pem CA --ca --country=VT --dns=ca.example --hash=SHA-256 --output=ca.crt
    $ ./botan gen_pkcs10 server_key.pem localhost --output=crt.req
    $ ./botan sign_cert ca.crt server_key.pem crt.req --output=server_cert.crt

To start the server and start a connection between a client and the server, the following command prompts were used:

.. code-block:: shell

    $ ./botan tls_server server_cert.crt server_key.pem --port=12345 --policy=pqc_tls.txt
    $ ./botan tls_client  localhost --port=12345 --tls-version=1.3 --policy=pqc_tls.txt

The pqc_tls.txt file contained the following lines:

.. code-block::

    allow_tls13 = true
    allow_tls12 = false
    key_exchange_groups = x25519/Kyber-512-r3/cloudflare


The DATA framework analyses the client.
As the underlying cryptographic algorithms for key exchange and encapsulation were analysed within other separate projects, the analysis was focused on the hybrid part of the protocol implementation.
For this part the code path of the client does not the differ from the server.
Hence analysing only the client implementation is sufficient.

The current report reflects the results of the differences identified in first phase of DATA.
The listed differences are an excerpt of the found differences.
The differences were selected if they are deemed important for the implementation security.

:::::
Kyber
:::::

Similar to the results of the analysis of Kyber, DATA shows several differences within the PolynomialMatrix function.
This difference is not critical.
Refer to the relevant section in the analysis regarding Kyber for more details.

:::::::::::::::::::::::::::::::::::::::
ChaCha20Poly1305_Decryption::finish_msg
:::::::::::::::::::::::::::::::::::::::

The `cipher_bytes()` function [BOTAN_CHACHA_CIPHER_BYTES]_ in the `ChaCha20Poly1305_Decryption::finish_msg()` routine [BOTAN_CHACHAPOLY_DECRYPTION_FINISH_MSG]_ calls the `xor_buf()` function [BOTAN_MEMOPS_XOR_BUF]_ with differently sized input.
This is reflected as differences in the execution.
With this difference an adversary is only able to estimate the length of the ciphertext.
Hence, this difference is not critical.

.. code-block:: cpp

    inline void xor_buf(uint8_t out[], const uint8_t in[], size_t length) {
       const size_t blocks = length - (length % 32);

       for(size_t i = 0; i != blocks; i += 32) {
          [...]
       }

       for(size_t i = blocks; i != length; ++i) {
          out[i] ^= in[i];
       }
    }

:::::::::::::::::::::::::::::
Certificate_Verify_13::verify
:::::::::::::::::::::::::::::

In the `Certificate_Verify_13::verify()` routine several differences were identified by DATA.
The differences were located in several functions of the `BER_decoder` [BOTAN_BER_DECODER]_, the `BigInt::encode_1363()` function [BOTAN_BIGINT_ENCODE_1363]_, and the `ECDSA_verification_operation::verify()` routine [BOTAN_ECDSA_VERIFICATION_OPERATION_VERIFY]_.
The received ECDSA signature is decoded with the help of the BER decoder and the big integer encoder functions.
This signature is verified within the ECDSA verification routine.
As all three routines only handle public data, any difference in execution is not critical.

:::::::::::::::::::::::::::::::::::::::::::::::::
Channel_Impl_13::AggregatedHandshakeMessages::add
:::::::::::::::::::::::::::::::::::::::::::::::::

In the `Channel_Impl_13::AggregatedHandshakeMessages::add()` routine [BOTAN_HANDSHAKE_MESSAGES_ADD]_ differences were identified by DATA within the `MDx_HashFunction` functions.
While the hash is finalised a padding is applied.
In the function `MDx_HashFunction::final_result()` [BOTAN_MDX_FINAL_RESULT]_ this is detected as difference.
This difference is not critical.

.. code-block:: cpp

    void MDx_HashFunction::final_result(uint8_t output[]) {
       const size_t block_len = static_cast<size_t>(1) << m_block_bits;

       clear_mem(&m_buffer[m_position], block_len - m_position);
       m_buffer[m_position] = m_pad_char;
