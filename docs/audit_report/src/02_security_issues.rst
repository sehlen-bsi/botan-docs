Security and Vulnerabilities
============================

Insufficient Input Parameter Validation in ECDH
-----------------------------------------------

Both [TR-03111]_ Section 4.3.1 and [TR-02102-1]_ Section 2.3.6 specify that
implementations should check that the calculated shared secret point is an
ordinary point on the curve and not the identity element. Only then should the
calculated shared secret be used, otherwise an error should be emitted.

This situation cannot occur in any correct execution of the ECDH protocol,
especially given that [TR-02102-1]_ Section 2.3.6 also mandates that the key
agreement "must be secured by means of strong authentication". Nevertheless, the
missing sanity check was added in `GH
#4794 <https://github.com/randombit/botan/pull/4794>`_ and will be released in a
future Botan 3.8.0 release. Additionally, the patch was back-ported into Botan
|botan_version|, which is reviewed in this document.
