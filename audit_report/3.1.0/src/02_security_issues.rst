Security and Vulnerabilities
============================

The following security issue is exposed and fixed in this iteration since
Botan 3.0.0-alpha1:

Missing Update of XMSS Private Keys in CLI for X.509
----------------------------------------------------

This security issue is an issue of the command line interface. It occurs when
signing an X.509 certificate or a Certificate Signing Request with XMSS. In
this case, the private key file of XMSS is not updated as it is necessary for
a stateful signature such as XMSS. This issue is discussed and fixed within
`pull request #3579 <https://github.com/randombit/botan/pull/3579>`_.

