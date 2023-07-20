Security and Vulnerabilities
============================

The following security issues are relevant for this review iteration.


CVE-2021-24115: Missing OCSP Certificate Verification Check
-----------------------------------------------------------

This security issue causes Botan to accept responder certificates within OCSP
response messages, even if the issuing CA does not verify the certificate.
As a result, attackers may spoof OCSP responses to revoke legitimate certificates
or falsely accept revoked ones.

The issue affects Botan version 2.19.2 and older ones, with a
`quick fix in version 2.19.3 <https://github.com/randombit/botan/commit/a725799a638ef169bc26cb56ee6b85f276f0dec8>`_.
and a more clean fix in the 3.0.0 release. The issue is documented in
`Botan's GitHub security issues <https://github.com/randombit/botan/security/advisories/GHSA-4v9w-qvcq-6q7w>`_
and submitted as `CVE-2021-24115 <https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-24115>`_.


Missing Update of XMSS Private Keys in CLI for X.509
----------------------------------------------------

This security issue is an issue of the command line interface. It occurs when
signing an X.509 certificate or a Certificate Signing Request with XMSS. In
this case, the private key file of XMSS is not updated as it is necessary for
a stateful signature such as XMSS. This issue is discussed and fixed within
`pull request #3579 <https://github.com/randombit/botan/pull/3579>`_.
