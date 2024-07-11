Security and Vulnerabilities
============================

X.509 Denial of Service Due to Excessive Name Constraints (CVE-2024-34702)
--------------------------------------------------------------------------

Botan's processing runtime for checking name constraints in X.509 certificates
has quadratic complexity, which means it becomes much slower as the number of
alternative names and name constraints in the certificate and its signing CA
certificate increases. This can be exploited by an attacker to launch a denial
of service attack. By creating a certificate chain with a large number of
alternative names (leaf certificate) and name constraints (intermediate certificate),
the attacker can overwhelm the system. It's important to note that the attacker
doesn't need to have a certificate signed by a trusted CA for this attack to be
effective.

This vulnerability affects all Botan 3.x versions prior to 3.5.0 and all 2.x
versions prior to 2.19.5. The fix contained in 3.5.0/2.19.5 limits the number
of alternative names and name constraints, optimizes the processing runtime,
and implements early abortion for invalid certificate chains.

If an application in a previous directly or indirectly calls the method
``Name_Constraints::validate`` with an untrusted certificate chain, it becomes
vulnerable. Important Botan functions that call this method are:

- ``PKIX::check_chain``
- ``x509_path_validate``
- ``PKIX::check_ocsp``

It's worth mentioning that TLS is also affected by this vulnerability. Although
the record limit of 2^14 bytes for a TLS record can mitigate the attack to some
extent, it doesn't entirely prevent it.

X.509 Authorization Error due to Name Constraint Decoding Bug (CVE-CVE-2024-39312)
----------------------------------------------------------------------------------

Botan has a flaw in processing X.509 name constraints when both permitted and
excluded name subtrees are present in the name constraints extension. In such
cases, the excluded name subtrees are ignored. Typically, a name is considered a
match only if it falls within the permitted name subtrees and is not within the
excluded name subtrees. This vulnerability allows a malicious intermediate CA to
sign an invalid certificate in a setting like the following:

Permitted name subtrees: .example.com
Excluded name subtrees: .super-secret.example.com
Malicious certificate possible for name: evil.super-secret.example.com

If the list of permitted name subtrees is empty, the verification works as intended.

This vulnerability affects all Botan 3.x versions prior to 3.5.0 and all 2.x
versions prior to 2.19.5.

If an application in a previous version creates a ``Name_Constraints`` object from
an untrusted certificate that contains both permitted and excluded name subtrees,
it becomes vulnerable. The issue is introduced during the decoding of the
certificate from bytes. As a result, the NameConstraints object obtained from
``Name_Constraints::get_name_constraints()`` does not contain the correct name
constraints, and the ``Name_Constraints::validate`` method does not function as
intended. Important Botan functions that indirectly use name constraints and are
therefore affected by this vulnerability include:

- ``PKIX::check_chain``
- ``x509_path_validate``
- ``PKIX::check_ocsp``

Furthermore, certificate chains in TLS are also affected by this vulnerability.
