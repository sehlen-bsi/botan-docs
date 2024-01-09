Changes Overview
================

Since the previously audited version (|botan_git_base_ref|), Botan
|botan_version| brings various extensions and fixes. The most relevant changes are outlined below.

FrodoKEM
--------

FrodoKEM is a post-quantum key encapsulation algorithm based on unstructured
lattices. In NIST's standardization process, it is a "Round 3 alternate
candidate"; therefore, it likely won't be standardized by NIST. However, it has
been recommended for usage by the BSI since 2020 [TR-02102-1]_.

Botan now includes a software implementation of FrodoKEM and eFrodoKEM as
drafted in the proposed ISO standard [FrodoKEM-ISO]_ document from March 2023.

Improvements to the TLS implementation
--------------------------------------

Botan |botan_version| supports the usage of raw public keys for authentication
of both servers and clients in TLS 1.3 (`RFC 7250
<https://www.rfc-editor.org/rfc/rfc7250>`_). This is especially useful for use
cases where the overhead of X.509 certificates is not needed.

Furthermore, the Boost ASIO wrapper gained improvements both in performance and
functionality. Most notably, it now allows the usage of C++20 coroutines when
sending and receiving data via the TLS socket.

Additionally, the BSI-specific TLS policy was updated to allow for TLS 1.3 by
default and to reflect the stricter requirements of the BSI TR-02102-2
[TR-02102-2]_.

See :ref:`changes/tls` for more information.

Fixes for Timing Side Channels in Kyber
---------------------------------------

In December 2023, potential timing side channel vulnerabilities were discovered
in several software implementations of Kyber. Botan prior to |botan_version| is
also affected. This release contains countermeasures against these attacks.

See :ref:`secinfo/kyberslash` for more information.

Fix an Exploitable Denial of Service Vulnerability
--------------------------------------------------

Botan versions prior to 2.19.4 and |botan_version| could be forced into a
resource intense primality check using a custom ECC group domain with an
excessively large parameter ``p``. This could be exploited by embedding a
maliciously cratfed custom domain into untrusted protocol data, such as an X.509
certificate.

This could be an effective DoS-amplifier for a vulnerable TLS server that
requires certificate-based client authentication.

See :ref:`secinfo/oversized_ecc` for more information.

Migration Guide from OpenSSL 1.1
--------------------------------

This is a noteworthy addition to Botan's documentation outlining how to migrate
application software from OpenSSL 1.1 to Botan. The guide is based on some
common use cases and provides example code snippets for both OpenSSL 1.1 and
Botan.

The document is online at: `docs.botan-crypto.org
<https://docs.botan-crypto.org/handbook/openssl_migration_guide.html>`_
