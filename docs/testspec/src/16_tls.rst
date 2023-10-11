Transport Layer Security
========================

TLS Protocol Execution
----------------------

TLS client and server are tested with positive tests by performing TLS
handshakes. In these tests basic credentials with TLS certificates and
TLS policy are first created. Afterwards, the client and the server
attempt to execute a TLS handshake with a specific TLS/DTLS protocol
version, key exchange method, and cipher algorithm.

The tests are implemented in :srcref:`src/tests/unit_tls.cpp`.

The following TLS handshake tests are executed:

-  TLS handshake with the following cipher suites, each once with and
   once without Encrypt-then-MAC (for TLS 1.0, TLS 1.1, TLS 1.2, DTLS
   1.0, DTLS 1.2):

   -  RSA_WITH_AES_128_CBC_SHA
   -  RSA_WITH_AES_128_CBC_SHA256
   -  ECDHE_ECDSA_WITH_AES_128_CBC_SHA
   -  ECDHE_ECDSA_WITH_AES_128_CBC_SHA256
   -  RSA_WITH_AES_256_CBC_SHA
   -  ECDHE_ECDSA_WITH_AES_256_CBC_SHA

-  TLS handshake with the following cipher suites (for TLS 1.2, DTLS
   1.2):

   -  DHE_RSA_WITH_AES_128_CBC_SHA256
   -  DHE_DSS_WITH_AES_128_CBC_SHA256

-  TLS handshake with the *Strict_Policy*

-  TLS handshake with the *NSA_Suite_B_128* policy

-  TLS handshake with the following GCM cipher suites (for TLS 1.2, DTLS
   1.2):

   -  ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
   -  ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
   -  ECDHE_RSA_WITH_AES_128_GCM_SHA256
   -  DHE_DSS_WITH_AES_128_GCM_SHA256
   -  DHE_DSS_WITH_AES_256_GCM_SHA384

-  TLS handshake using ECC point compression with the following cipher
   suites (for TLS 1.2, DTLS 1.2)

   -  ECDHE_ECDSA_WITH_AES_128_GCM_SHA256

-  TLS handshake using the specific curve secp521r1 with the following
   cipher suites (for TLS 1.2, DTLS 1.2)

   -  ECDHE_ECDSA_WITH_AES_256_GCM_SHA384

-  TLS handshake using the specific curve brainpool256r1 with the
   following cipher suites (for TLS 1.2, DTLS 1.2)

   -  ECDHE_ECDSA_WITH_AES_128_GCM_SHA256

-  TLS handshake with TLS client authentication with the following
   cipher suites (for TLS 1.2, DTLS 1.2):

   -  ECDHE_ECDSA_WITH_AES_256_GCM_SHA384

-  TLS handshake with pre-shared key with the following cipher suites
   (for TLS 1.2 and DTLS 1.2):

   -  PSK_WITH_AES_128_GCM_SHA256
   -  ECDHE_PSK_WITH_AES_128_CBC_SHA256
   -  DHE_PSK_WITH_AES_128_CBC_SHA

-  If a house curve is defined: TLS handshake using a custom curve (in
   this case, secp112r1) with the following cipher suites (for TLS 1.2,
   DTLS 1.2):

   -  ECDHE_ECDSA_WITH_AES_256_GCM_SHA256

TLS Policy Verification
-----------------------

TLS policy is used to validate correct cryptographic algorithms,
protocol versions, or cipher suites. Many of these properties are
already tested in the TLS handshake execution test described in the
previous section. We extended the test suite with positive and negative
tests validating correct certificate handling.

The tests are implemented in :srcref:`src/tests/unit_tls_policy.cpp`.

In the test different certificates with different key lengths are
created and tested against the default TLS policy. Only certificates
with appropriate key lengths can be accepted. Certificates with
insufficient key lengths must be rejected.

In the test the following certificates are tested:

-  RSA (1024 / 2048 bits)
-  ECDSA (192 / 256 bits)
-  DSA (1024 / 2048 bits)

TLS Protocol Message Parsing
----------------------------

TLS message parsing is tested using byte sequences resulting in valid
and invalid messages. The test case is described in the following.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TLS-message-1                                                           |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Parses a byte sequence into a TLS protocol message                      |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Buffer: byte sequence                                                |
   |                        |                                                                         |
   |                        | -  Protocol: TLS protocol version                                       |
   |                        |                                                                         |
   |                        | -  Ciphersuite: cipher suite included in the protocol message           |
   |                        |                                                                         |
   |                        | -  AdditionalData: additional data used in the test case, for example a |
   |                        |    TLS extension bytes                                                  |
   |                        |                                                                         |
   |                        | -  Exception: exception thrown when parsing invalid byte sequence       |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | -  Out: parsed message                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Parse the byte sequence into a TLS protocol message                  |
   |                        |                                                                         |
   |                        | #. Check the protocol message properties or the exception that has been |
   |                        |    thrown during parsing                                                |
   +------------------------+-------------------------------------------------------------------------+

In the following we give examples of positive and negative tests for TLS
protocol messages.

The messages were generated with OpenSSL and TLS-Attacker.

ClientHello
^^^^^^^^^^^

The ClientHello message contains several fields. The following fields
are checked:

-  Protocol Version

-  Extensions

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/tls/client_hello.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TLS-ClientHello-1                                                       |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Parses a ClientHello message without any extension                      |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Buffer =                                                                |
   |                        | 030320f3dc33f90be6509e6133a1819f2b80fe6ccc6268d9195ca4ead7504ffe7e2     |
   |                        | a0000aac030c02cc028c024c014c00a00a500a300a1009f006b006a0069006800390038 |
   |                        | 003700360088008700860085c032c02ec02ac026c00fc005009d003d00350084c02fc02 |
   |                        | bc027c023c013c00900a400a200a0009e00670040003f003e0033003200310030009a00 |
   |                        | 99009800970045004400430042c031c02dc029c025c00ec004009c003c002f00960041c |
   |                        | 011c007c00cc00200050004c012c008001600130010000dc00dc003000a00ff01000000 |
   |                        |                                                                         |
   |                        | Protocol = 0303                                                         |
   |                        |                                                                         |
   |                        | AdditionalData = FF01                                                   |
   |                        |                                                                         |
   |                        | Exception =                                                             |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | The message can be successfully parsed. By default an empty             |
   |                        | renegotiation is generated inside of the ClientHello message (0xFF01)   |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Parse the message bytes.                                             |
   |                        |                                                                         |
   |                        | #. Verify successful processing, protocol version, and the extension    |
   |                        |    being generated.                                                     |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TLS-ClientHello-2                                                       |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Parses a ClientHello message with insufficient bytes                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Buffer = 00                                                             |
   |                        |                                                                         |
   |                        | Protocol = 0303                                                         |
   |                        |                                                                         |
   |                        | Exception = Invalid argument Decoding error: Client_Hello: Packet       |
   |                        | corrupted                                                               |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | The message cannot be parsed and the processing results into a “Packet  |
   |                        | corrupted” exception.                                                   |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Parse the message bytes.                                             |
   |                        |                                                                         |
   |                        | #. Verify the resulting exception content.                              |
   +------------------------+-------------------------------------------------------------------------+

ServerHello
^^^^^^^^^^^

The ServerHello message contains several fields. The following fields
are checked:

-  Protocol Version
-  Cipher suite

-  Extensions

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/tls/server_hello.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TLS-ServerHello-1                                                       |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Parses a ServerHello message with session ticket, extended master       |
   |                        | secret, and renegotiation info                                          |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Buffer =                                                                |
   |                        | 03019f9cafa88664d9095f85dd64a39e5dd5c09f5a4a5362938af3718ee4e           |
   |                        | 818af6a00c03000001aff01000100000b00040300010200230000000f00010100170000 |
   |                        |                                                                         |
   |                        | Protocol = 0301                                                         |
   |                        |                                                                         |
   |                        | Ciphersuite = C030                                                      |
   |                        |                                                                         |
   |                        | AdditionalData = 00170023FF01                                           |
   |                        |                                                                         |
   |                        | Exception =                                                             |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | The message can be successfully parsed. The message contains the        |
   |                        | session ticket, extended master secret, and renegotiation info          |
   |                        | extensions.                                                             |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Parse the message bytes.                                             |
   |                        |                                                                         |
   |                        | #. Verify successful processing, protocol version, and the extensions.  |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TLS-ServerHello-2                                                       |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Parses a ServerHello message with invalid extension length              |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Buffer =                                                                |
   |                        | 03039f9cafa88664d9095f85dd64a39e5dd5c09f5a4a5362938af3718ee4e           |
   |                        | 818af6a00c03000001cff01000100000b00040300010200230000000f00010100170000 |
   |                        |                                                                         |
   |                        | Protocol = 0303                                                         |
   |                        |                                                                         |
   |                        | Ciphersuite = C030                                                      |
   |                        |                                                                         |
   |                        | AdditionalData = 00170023FF01                                           |
   |                        |                                                                         |
   |                        | Exception = Invalid argument Decoding error: Bad extension size         |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | The message cannot be parsed correctly and the processing results into  |
   |                        | a “Bad extension size” exception.                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Parse the message bytes.                                             |
   |                        |                                                                         |
   |                        | #. Verify the resulting exception content.                              |
   +------------------------+-------------------------------------------------------------------------+

CertificateVerify
^^^^^^^^^^^^^^^^^

The CertificateVerify message contains the following fields:

-  Signature and Hash algorithm (only in TLS 1.2)
-  Certificate length

-  Certificate

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/tls/cert_verify.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TLS-CertVerify-1                                                        |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Parses a correct CertificateVerify message in TLS 1.2.                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Buffer =                                                                |
   |                        | 06010080266481066a8431582157a9a591150d418b63d46154c                     |
   |                        | 4cd85bffcfdba8c7f6396f0ceb0402c2142c526a19659d58cd4111bf45f57a56e97d16e |
   |                        | eecd350f6e9dc93662e4361053666e5a53c74fe11bd6cf86a9cf7a2488704c512191582 |
   |                        | 0973280ed6afa3e8b79dfb799bddffb52caa2d1a0a895a0e7505d841a882bdd92ec9141 |
   |                        |                                                                         |
   |                        | Protocol = 0303                                                         |
   |                        |                                                                         |
   |                        | Exception =                                                             |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | The message can be successfully parsed.                                 |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Parse the message bytes.                                             |
   |                        |                                                                         |
   |                        | #. Verify successful processing.                                        |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TLS-CertVerify-2                                                        |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Parses a correct CertificateVerify message with an incomplete Signature |
   |                        | and Hash algorithm.                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Buffer = 06                                                             |
   |                        |                                                                         |
   |                        | Protocol = 0303                                                         |
   |                        |                                                                         |
   |                        | Exception = Invalid argument Decoding error: Invalid CertificateVerify: |
   |                        | Expected 1 bytes remaining, only 0 left                                 |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | The message cannot be parsed correctly and the processing results into  |
   |                        | an exception: “Invalid CertificateVerify: Expected 1 bytes remaining,   |
   |                        | only 0 left”.                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Parse the message bytes.                                             |
   |                        |                                                                         |
   |                        | #. Verify the resulting exception content.                              |
   +------------------------+-------------------------------------------------------------------------+

Hello Request
^^^^^^^^^^^^^

The HelloRequest message does not contain any data.

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/tls/hello_request.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TLS-HelloRequest-1                                                      |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Parses a correct HelloRequest message.                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Buffer =                                                                |
   |                        |                                                                         |
   |                        | Exception =                                                             |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | The message can be successfully parsed.                                 |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Parse the message bytes.                                             |
   |                        |                                                                         |
   |                        | #. Verify successful processing.                                        |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TLS-HelloRequest-2                                                      |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Parses a correct HelloRequest message with a non-zero size.             |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Buffer = 01                                                             |
   |                        |                                                                         |
   |                        | Exception = Invalid argument Decoding error: Bad Hello_Request, has     |
   |                        | non-zero size                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | The message cannot be parsed correctly and the processing results into  |
   |                        | an exception: “Bad Hello_Request, has non-zero size”.                   |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Parse the message bytes.                                             |
   |                        |                                                                         |
   |                        | #. Verify the resulting exception content.                              |
   +------------------------+-------------------------------------------------------------------------+

HelloVerify
^^^^^^^^^^^

The HelloVerify message contains the following fields:

-  Protocol version
-  Cookie length

-  Cookie

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/tls/hello_verify.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TLS-HelloVerify-1                                                       |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Parses a correct HelloVerify message.                                   |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Buffer = feff14925523e7539a13d9782af6d771b97d0032c61800                 |
   |                        |                                                                         |
   |                        | Exception =                                                             |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | The message can be successfully parsed.                                 |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Parse the message bytes.                                             |
   |                        |                                                                         |
   |                        | #. Verify successful processing.                                        |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TLS-HelloVerify-2                                                       |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Parses a correct CertificateVerify message with an incomplete cookie.   |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Buffer = FEFD0500                                                       |
   |                        |                                                                         |
   |                        | Exception = Invalid argument Decoding error: Bad length in hello verify |
   |                        | request                                                                 |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | The message cannot be parsed correctly and the processing results into  |
   |                        | an exception: “Invalid CertificateVerify: Bad length in hello verify    |
   |                        | request”.                                                               |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Parse the message bytes.                                             |
   |                        |                                                                         |
   |                        | #. Verify the resulting exception content.                              |
   +------------------------+-------------------------------------------------------------------------+

NewSessionTicket
^^^^^^^^^^^^^^^^

The NewSessionTicket message contains the following fields:

-  Lifetime (4 bytes)
-  Length (2 bytes)
-  Session ticket

The following table shows an example test case with one test vector. All
test vectors are listed in :srcref:`src/tests/data/tls/new_session_ticket.vec`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TLS-NewSessionTicket-1                                                  |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Parses a correct NewSessionTicket message.                              |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Buffer = 0000000000051122334455                                         |
   |                        |                                                                         |
   |                        | Exception =                                                             |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | The message can be successfully parsed.                                 |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Parse the message bytes.                                             |
   |                        |                                                                         |
   |                        | #. Verify successful processing.                                        |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TLS-NewSessionTicket-2                                                  |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Parses a correct NewSessionTicket message with an incomplete session    |
   |                        | ticket.                                                                 |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Buffer = 00010203000500                                                 |
   |                        |                                                                         |
   |                        | Exception = Invalid argument Decoding error: Invalid SessionTicket:     |
   |                        | Expected 5 bytes remaining, only 1 left                                 |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | The message cannot be parsed correctly and the processing results into  |
   |                        | an exception: “Invalid SessionTicket: Expected 5 bytes remaining, only  |
   |                        | 1 left”.                                                                |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Parse the message bytes.                                             |
   |                        |                                                                         |
   |                        | #. Verify the resulting exception content.                              |
   +------------------------+-------------------------------------------------------------------------+

TLS Stream Integration
----------------------

*TLS::Stream* offers a boost-asio compatible wrapper around
*TLS::Client* and *TLS::Server* and the integration of Client-Server
communication is covered with four tests whereas each of them are
executed in both asynchronous and synchronous ways, so as a result eight
test cases exist.

The tests are implemented in
:srcref:`src/tests/test_tls_stream_integration.cpp`.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | Test_Conversation/Test_Conversation_Sync                                |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Client and Server exchange a message during a TLS handshake and do a    |
   |                        | full shutdown in the end.                                               |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | A message: "Time is an illusion. Lunchtime doubly so."                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | The Server echoes the message the Client sent and both participants     |
   |                        | shut down the connection in the end properly.                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | 1. A connection between Client and Server is established.               |
   |                        |                                                                         |
   |                        | 2. A TLS handshake between Client and Server is performed.              |
   |                        |                                                                         |
   |                        | 3. The Client sends the message to the Server.                          |
   |                        |                                                                         |
   |                        | 4. The Server sends the same message back.                              |
   |                        |                                                                         |
   |                        | 5. The Client compares the sent and received messages for equality.     |
   |                        |                                                                         |
   |                        | 6. The Client initiates a connection shutdown.                          |
   |                        |                                                                         |
   |                        | 7. The Server receives a close_notify message and shuts down with the   |
   |                        |    error code *Success*.                                                |
   |                        |                                                                         |
   |                        | 8. The Client receives a close_notify message and shuts down with the   |
   |                        |    error code *EOF*.                                                    |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | Test_Eager_Close/Test_Eager_Close_Sync                                  |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | The Client initiates a connection shutdown but closes the socket before |
   |                        | receiving any responses from the Server.                                |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | The Client does not receive a close_notify message from the Server.     |
   |                        |                                                                         |
   |                        | The Server shuts down properly anyways.                                 |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | 1. A connection between Client and Server is established.               |
   |                        |                                                                         |
   |                        | 2. A TLS handshake between Client and Server is performed.              |
   |                        |                                                                         |
   |                        | 3. The Client initiates a connection shutdown.                          |
   |                        |                                                                         |
   |                        | 4. The Client closes the socket.                                        |
   |                        |                                                                         |
   |                        | 5. It is confirmed the Client did not receive a close_notify message.   |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | Test_Close_Without_Shutdown/Test_Close_Without_Shutdown_Sync            |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | The Client closes the socket before properly shutting down the          |
   |                        | connection with the Server.                                             |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | The Server sees a StreamTruncated error.                                |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | 1. A connection between Client and Server is established.               |
   |                        |                                                                         |
   |                        | 2. A TLS handshake between Client and Server is performed.              |
   |                        |                                                                         |
   |                        | 3. The Client sends a specific message to the Server to trigger a       |
   |                        |    short-read.                                                          |
   |                        |                                                                         |
   |                        | 4. The Client closes the socket.                                        |
   |                        |                                                                         |
   |                        | 5. It is confirmed the Client did not receive a close_notify message.   |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | Test_No_Shutdown_Response/Test_No_Shutdown_Response_Sync                |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | The Server shuts down the connection, the Client does not send a        |
   |                        | close_notify and closes the socket immediately.                         |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | The Server sees a short-read error.                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | 1. A connection between Client and Server is established.               |
   |                        |                                                                         |
   |                        | 2. A TLS handshake between Client and Server is performed.              |
   |                        |                                                                         |
   |                        | 3. The Client sends a shutdown message to the Server.                   |
   |                        |                                                                         |
   |                        | 4. The Server sends a close_notify message.                             |
   |                        |                                                                         |
   |                        | 5. The Client confirms the entrance of the close_notify message.        |
   |                        |                                                                         |
   |                        | 6. The Client closes the socket.                                        |
   +------------------------+-------------------------------------------------------------------------+

Additional TLS Tests
--------------------

TLS is further tested using various system tests, as listed in the
following.

The tests are implemented in :srcref:`src/tests/test_tls.cpp`.

-  Session handling: A test that encrypts and decrypts static session
   test data

-  CBC padding: Tests that check TLS padding of a TLS CBC encrypted
   record. Test vectors are listed in
   :srcref:`src/tests/data/tls_cbc_padding.vec`.

-  CBC: Tests that check parsing of valid and invalid TLS CBC encrypted
   ciphertexts. Test vectors are listed in :srcref:`src/tests/data/tls_cbc.vec`.

-  TLS alert: A test that checks the correct string representation of a
   TLS alert type

-  TLS policy text: A test that checks the correct string representation
   of a TLS policy for all TLS policies

-  TLS algorithms: Tests that check the correct string representation
   of:

   -  TLS signature schemes
   -  TLS authentication methods
   -  TLS key exchange algorithms

|  Apart from internal tests, Botan integrates with BoringSSL's system tests
  [#boring_bogo]_. These tests utilize a heavily instrumented TLS implementation
  that can be configured to behave inconsistently with the TLS RFCs in a
  plethora of ways. Explicitly note that BoringSSL does also implement a hybrid
  TLS handshake using Kyber in its latest revision. To interface with this test
  suite, Botan provides an adapter that is implemented in:
  :srcref:`src/bogo_shim/bogo_shim.cpp` and a configuration in
  :srcref:`src/bogo_shim/config.json`.
| Further details of this test integration are beyond the scope of this
  document, please refer to the public documentation in the BoringSSL
  repository.

.. [#boring_bogo] BoringSSL BoGo Test Suite:
                  https://github.com/google/boringssl/tree/master/ssl/test
