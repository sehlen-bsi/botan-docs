Changes Overview
================

Since the previously audited version (|botan_git_base_ref|), Botan
|botan_version| brings some extensions and fixes. The most relevant changes are outlined below.

Transport Layer Security
------------------------

The TLS 1.3 implementation is now capable of establishing secure connections
using post-quantum secure KEMs. Botan |botan_version| supports hybrid key
exchanges with the following algorithm combinations:

+--------------------------------+--------------------------------+
| **PQ KEM**                     | **Classical Key Exchange**     |
+--------------------------------+--------------------------------+
| Kyber R3 512                   | X25519                         |
+--------------------------------+--------------------------------+
| Kyber R3 512                   | NIST P-256                     |
+--------------------------------+--------------------------------+
| Kyber R3 768                   | X25519                         |
+--------------------------------+--------------------------------+
| Kyber R3 768                   | NIST P-384                     |
+--------------------------------+--------------------------------+
| Kyber R3 1024                  | NIST P-1024                    |
+--------------------------------+--------------------------------+

Additionally, handshakes with just Kyber as a PQ KEM and without any classical
key exchange algorithm are supported as well. Future versions of Botan will
extend this with additional quantum-secure KEMs like eFrodoKEM.

Apart from these new asymmetric key exchange mechanisms, Botan's TLS 1.3
implementation can now make use of user-defined symmetric Preshared Keys.

New Algorithms and APIs
-----------------------

Keccak-based Algorithms
~~~~~~~~~~~~~~~~~~~~~~~

This release of Botan supports KMAC -- a message authentication code based on
the Keccak permutation specified by NIST. In turn, KMAC relies on "customizable
SHAKE" (cSHAKE), which is now available internally.

eXtendable Output Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

With ``XOF``, Botan now has a base-class API (cf. ``HashFunction`` or
``BlockCipher``) to support eXtendable Output Functions (XOF). The public API provides
"SHAKE-128" and "SHAKE-256" as XOFs.

Kuznyechik
~~~~~~~~~~

The National Standard of the Russian Federation GOST R 34.12-2015 defines
Kuznyechik [RFC7801]_ as a block cipher with a block length of 128 bits. This
algorithm is *prohibited* in the "BSI" build policy.

Deprecations
------------

Given that NIST is not planning to standardize Kyber in 90s-mode, this was
deprecated in Botan |botan_version|.
