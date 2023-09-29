Changes Overview
================

This is an intermediate document revision. Most notably since the last audited
version (|botan_git_base_ref|), the TLS 1.3 implementation is now capable of
establishing secure connections using a post-quantum secure KEM and/or
user-defined Preshared Keys.

Additionally, Botan now implements KMAC -- a message authentication code based
on the Keccak permutation specified by NIST.

Hybrid TLS using PQ-KEM + classical key exchange
------------------------------------------------

At the time of this writing, the post-quantum hybrid TLS pull request was not
yet merged into the upstream main branch. As a result, this patch does not show
up in the detailed patch lists of this document. For your reference and
convenience, please find the relevant changes here:

* `Pull Request: Hybrid PQ/T key establishment <https://github.com/randombit/botan/pull/3609>`_

Botan supports hybrid key exchanges with the following algorithm combinations:

+--------------------------------+--------------------------------+
| PQ KEM                         | Classical Key Exchange         |
+--------------------------------+--------------------------------+
| | Kyber R3 512                 | | X25519                       |
| | Kyber R3 512                 | | NIST P-256                   |
| | Kyber R3 768                 | | X25519                       |
| | Kyber R3 768                 | | NIST P-384                   |
| | Kyber R3 1024                | | NIST P-1024                  |
+--------------------------------+--------------------------------+

Additionally, handshakes with just Kyber as a PQ KEM and without any classical
key exchange algorithm is supported as well.

Note that this implementation is based on preliminary specifications that are
proposed for standardization. We `successfully tested interoperability with
various important cloud providers
<https://github.com/randombit/botan/pull/3609#issuecomment-1620039445>`_, but
any aspect of this implementation might be subject to change in the future.
