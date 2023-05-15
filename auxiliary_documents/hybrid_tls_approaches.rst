Existing Proposals for Hybrid Key Exchange in TLS 1.3
=====================================================

Introduction
------------

Typically, the TLS protocol uses an asymmetric key exchange algorithm to
establish a shared session key and a certificate-backed asymmetric signature for
session authentication. Existing algorithms are well studied and their security
guarantees are widely trusted and relied upon. In the future quantum computers
have the potential to break these classical algorithms, leading to the need for
quantum-resistant approaches.

However, quantum-safe algorithms, are relatively new and, thus, less mature and
trustworthy compared to their classical counterparts. As a result, the adoption
of hybrid key exchange approaches has gained traction, as they aim to combine
the reliability of classical algorithms with the quantum resistance of emerging
quantum-safe alternatives.

Interactive protocols like TLS are subject to "store now decrypt later"-attacks
where an adversary could store encrypted transcripts today and break their
confidentiality in retrospect once capable quantum computers are available in
the future. Such attacks do not threaten the authenticity of sessions provided
by cryptographic signatures today.

This document focuses on the key exchange and leaves signatures out of scope. It
aims to be an overview of the proposed approches for incorporating hybrid key
exchange capability into the TLS protocols. It provides the basis for the
to-be-developed hybrid key exchange approach in Botan's TLS implementation.

Relevant Hybrid Key Exchange Approaches in TLS 1.3
--------------------------------------------------

Hybrid key exchange in TLS 1.3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This IETF draft [IETF_Stebila]_ aims at integrating hybrid key exchange to TLS 1.3 as
a simple "concatenation"-based approach. The draft specifically aims for
**backward-compatibility** with existing (non-hybrid-aware) TLS 1.3
implementations by using the existing protocol flexibility to implement a hybrid
key exchange.

Note that major network infrastructure providers such as [Amazon]_ and
[Cloudflare]_ already implemented this draft and provide the hybrid key exchange
capability to their customers as public betas.

During the TLS handshake, pre-defined combinations of supported algorithms are
identified as "NamedGroups" (TLS terminology) just like the existing
Diffie-Hellman-based approaches. In other words: Every combination of algorithms
must be assigned a unique code-point in TLS's "NamedGroup" enumeration. Examples
of such combinations may be x25519+Kyber512 or secp384r1+Kyber768. Combinations
of more than two algorithms are possible, but are out of scope for this
document.

For the transmission of hybrid public keys and ciphertexts a simple
concatenation encoding is used. Both the order of the values and their lengths
are known from the "NamedGroup" selection; therefore no additional type or
length encoding is used. The concatenated data is then transmitted as the
payload of a "KeyShareEntry" in the Client Hello or Server Hello, as usual.

After the first full roundtrip (Client Hello and Server Hello), both parties are
in possession of two shared secrets each from one of the hybrid algorithms.
Again, both secrets are simply concatenated without any additional encoding
information. This concatenation is then inserted into the usual TLS 1.3 key
schedule which utilizes a "HKDF-Extract" to securely condense both secrets into
session key material.

For instance, using x25519+Kyber512 a client would generate ephemeral keys for
both and concatenate the x25519 public value with the Kyber public key and
transmit them in its Client Hello. The server would then generate an ephemeral
x25519 key pair and calculate the shared secret as usual. It would then
encapsulate an additional shared secret with the received Kyber public key. In
its Server Hello it would reply with the concatenation of its own x25519 public
value and the resulting Kyber ciphertext. Now, both client and server should
obtain both shared secrets, combine them as described and start encrypting their
consecutive messages.

While this approach is fully backward compatible to non-hybrid-aware peers (TLS
demands unknown "NamedGroups" to be ignored), it has a few limitations:

 * Large keys: Due to protocol limitations the concatenation of public value
               and/or ciphertext must fit into 2^16-1 bytes. That excludes
               algorithms with longer key sizes such as Classic McEliece.

 * Failures: Some post-quantum algorithms have a non-zero failure probability,
             meaning that the peers might derive different shared secrets in
             rare cases. This would result in a handshake-failure that would
             demand some kind of retry-mechanism by the client.

 * Wasted bandwidth: Clients wishing to offer multiple combinations of the same
                     algorithm (e.g. x25519+Kyber512, secp256r1+Kyber512) are
                     forced to send multiple large post-quantum public keys in
                     their Client Hello.

 * Limited Combinations: All algorithm combinations must be pre-defined and
                         require standardized code-points in "NamedGroup". This
                         renders the approach somewhat inflexible.

Note that the bandwidth and flexibility drawbacks were addressed by other (more
involved) approaches ([IETF_Schanck]_, [IETF_Whyte]_). However, those require
additional TLS message extensions and/or changes to the protocol's internals and
are their IETF draft documents are expired for years.

Botan 3.0 recently introduced customization points for the key exchange
mechanisms during the handshake. These should provide enough flexibility for
applications that use Botan to implement the necessary adaptions. The relevant
customizations can be done by deriving ``TLS::Callbacks`` and overriding
``tls_generate_ephemeral_key()`` and ``tls_ephemeral_key_agreement()``.
Additionally, an application would need to derive ``TLS::Policy`` and override
``key_exchange_groups()`` and ``choose_key_exchange_group()`` to define custom
code-points for the hybrid key exchange schemes it wishes to use.

Though, this customization requires a deep understanding of the relevant IETF
draft and TLS 1.3 internals. It would therefore be worthwhile to integrate the
drafted hybrid key exchange support directly into the library. The required
adaptions are relatively minor and can be applied in a clean way.

Establishing an Additional Shared Secret
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This IETF draft [IETF_Schanck]_ allows negotiating an additional shared secret
by essentially duplicating TLS 1.3's "KeyShare" extension in both the Client
Hello and the Server Hello. This allows clients to independently offer key
exchange information for classical and post-quantum algorithms. The underlying
IETF draft expired in October 2017.

The "additional_key_share" extension simply establishes a second shared secret
that is combined with the ordinary shared secret by extending TLS 1.3's key
schedule with an additional HKDF-Extract/Derive-Secret stage (see `Section 3 in
the draft
<https://datatracker.ietf.org/doc/html/draft-schanck-tls-additional-keyshare-00#section-3>`_).

The semantics of the "additional_key_share" extension are equivalent to the
ordinary "key_share" extension. Clients wishing to use Kyber as an additional
key exchange method would simply add a KeyShareEntry with an ephemeral Kyber
public key to the "additional_key_share" extension in their Client Hello.
Compatible servers would then reply with a Kyber ciphertext in the
"additional_key_share" extension in their Server Hello. In turn, both peers
would obtain two shared secrets and utilize the extended TLS 1.3 key schedule to
derive session key material from them.

This approach can be backward compatible, as TLS message extensions typically
work in a "request-response" fashion and unknown extensions must be ignored.
E.g. an incompatible server would simply ignore the "additional_key_share"
extension. The client could then either discard its additional ephemeral key and
perform an ordinary handshake without a hybrid key exchange or abort.

Similarly to the approach described above ([IETF_Stebila]_), large keys cannot
be accomodated in the "additional_key_share" extension due to protocol
limitations and rare algorithm failures may result in failed handshakes and
require a retry-mechanism. However, the approach is somewhat more flexible: Any
key exchange algorithms can be combined as needed without registering additional
code-points in "NamedGroup".

Adding new TLS message extensions to Botan is easily possible (even for using
applications). However, the extended key schedule would need to be implemented
in the library itself, as no customization point is provided for this.
Nevertheless, from a technical perspective there are no particular challenges in
supporting this approach in Botan.

AuthKEM
~~~~~~~

This approach was formerly known as KEM-TLS [IETF_Celi]_ and must be seen as a
major change in TLS's protocol design. It aims at replacing both the key
exchange and the signature-based authentication with a single Key Encapsulation
Mechanism. KEM public keys used in such a handshake would be long-lived and
certified by a CA. Authenticity would be established by demonstrating a
successful decapsulation of a shared secret encapsulated with the certified
public key. This removes the need for an authenticating signature in the TLS
handshake and would safe substantial bandwidth as signatures of post-quantum
algorithms tend to be rather large. Additional changes to the protocol are
proposed to relieve the server from sending its certificate chain under certain
conditions, aiming at further bandwidth reductions.

Additional to the KEM-based key exchange, this approach uses the standard
(EC)DHE key exchange to encrypt all TLS handshake messages after the initial
Client Hello/Server Hello exchange. As a result, it can be seen as a hybrid
approach by default.

The required changes for this approach are quite substantial and we won't go
into any further detail in this document. The adaptions to Botan's TLS 1.3
implementation would be extensive and far above the scope of this project's main
objective: namely to just allow for a hybrid key exchange. Furthermore, it seems
questionable that any other production-ready implementation would be available
in the near future.

Major differences to TLS 1.3 (and the associated infrastructure) include:

 * Certified public keys are KEM algorithms: CAs would need to start issuing
   certificates for such public keys.
 * Adapted TLS state machine with new handshake message types and altered
   message sequences.
 * Extended key schedule to mix in additional shared secrets from the
   authenticating KEM decapsulation (typically one; two for client
   authentication)

General Implementation Challenges
---------------------------------

With neither the quantum-secure algorithms nor any of the presented TLS
adaptions being committed standards, a production-ready implementation is
challenging. Particularly when aiming at interoperability with other
implementations. Here are a few points to consider:

 * Algorithm specifications may evolve during the standardization process: That
   may involve both the algorithm's mechanics as well as value encodings
 * Algorithm identifiers (e.g. code-points in TLS' "NamedGroup") are not yet
   defined: The current drafts leave them open and beta implementations define
   incompatible code-points (e.g. in a dedicated private region of the value
   space) [NAMEDGROUP_OQS]_, [NAMEDGROUP_CLOUDFLARE]_, [NAMEDGROUP_S2N]_.

Due to the transient nature of those drafts, an implementation should not claim
long-term support and potential users should see it as beta-quality. Therefore,
we suggest to disable these to-be-developed TLS extensions by default at build
time in Botan.

Legacy: a Word on TLS 1.2
-------------------------

With TLS 1.3 the protocol became more flexible in strategic places simplifying
the implementation of such hybrid key exchanges significantly. Also, the
handshake in TLS 1.3 is faster and resists downgrade attacks against the key
exchange algorithm negotiation by default.

Despite that there is some work on retrofitting hybrid key exchange schemes to
the legacy TLS 1.2 protocol. However, early-adoption pick-up by the industry
seems to be slim. Adaption of TLS 1.2 is therefore explicitly out of scope for
this project.

References
----------

.. [IETF_Stebila] Douglas Stebila, Scott Fluhrer, Shay Gueron
                  "Hybrid key exchange in TLS 1.3", Internet Engineering Task Force, February 2023
                  https://datatracker.ietf.org/doc/draft-ietf-tls-hybrid-design/06/

.. [IETF_Schanck] John M. Schanck, Douglas Stebila
                  "A Transport Layer Security (TLS) Extension For Establishing An Additional Shared Secret", Internet Engineering Task Force, April 2017
                  https://datatracker.ietf.org/doc/draft-schanck-tls-additional-keyshare/00/

.. [IETF_Whyte] William Whyte, Zhenfei Zhang, Scott Fluhrer, Oscar Garcia-Morchon
                "Quantum-Safe Hybrid (QSH) Key Exchange for Transport Layer Security (TLS) version 1.3", Internet Engineering Task Force, October 2017
                https://datatracker.ietf.org/doc/draft-whyte-qsh-tls13/06/

.. [IETF_Celi] Sofia Celi, Peter Schwabe, Douglas Stebila, Nick Sullivan, Thom Wiggers
               "KEM-based Authentication for TLS 1.3", Internet Engineering Task Force, March 2022
               https://datatracker.ietf.org/doc/draft-celi-wiggers-tls-authkem/01/

.. [Cloudflare] Bas Westerbaan, Cefan Daniel Rubin
                "Defending against future threats: Cloudflare goes post-quantum", The Cloudflare Blog, October 2022
                https://blog.cloudflare.com/post-quantum-for-all/

.. [Amazon] "Using hybrid post-quantum TLS with AWS KMS"
            Amazon AWS KMS Developer Guide
            https://docs.aws.amazon.com/kms/latest/developerguide/pqtls.html

.. [NAMEDGROUP_OQS] https://github.com/open-quantum-safe/openssl/blob/728b0171923b5c29846e23a28c3be7e65fb4d5ab/oqs-template/oqs-kem-info.md

.. [NAMEDGROUP_CLOUDFLARE] https://blog.cloudflare.com/post-quantum-for-all/ (see section "What we deployed")

.. [NAMEDGROUP_S2N] https://github.com/aws/s2n-tls/blob/8584b89d306c03fa108d1a3e9dae079658013bbb/tls/s2n_tls_parameters.h#L66-L70
