Security and Vulnerabilities
============================

The security issues that were identified between |botan_git_base_ref| and
|botan_version| are listed in the following table.

.. list-table::
   :class: longtable
   :widths: 10 20 10 50
   :header-rows: 1

   * - Security Issue
     - Affected versions
     - Fixed in Version
     - Description
   * - CVE-2026-35580
     - Regarding general certification path validation only 3.11 is affected. Regarding certificate matching in a certificate store, the issue affects earlier versions as well. Earliest affected version is not known.
     - 3.11.1
     - The certificate store's function to search for a given certificate within the store returns any certificate whose SubjectDN matches that of the sought certificate.
   * - CVE-2026-35582
     - Earliest affected version is unknown
     - 3.11.1
     - TLS 1.3 client authentication can by trivially bypassed.
   * - `#5454 <https://github.com/randombit/botan/issues/5454>`_, `#5455 <https://github.com/randombit/botan/issues/5455>`_
     - Earliest affected version is unknown
     - 3.11.1
     - The verification operation class of EdDSA and ECDSA handles the case of a too short signature in an erroneous manner. This leads to the verification object remaining in a state with an already non-empty hashed message after a failed
       signature verification. While the
       caller assumes that a new verification is started, the verification operation instance appends the new message for verification to the previous one. This allows attacks where the attacker first deliberately causes a failed
       verification for some prefix A. In the second step he submits the message B together with a valid signature for the message A || B. The verification of B succeeds due to the pending message in the internal hash context, even though
       the legitimate signer only signed A || B, and never signed B.
   * - `#5614 <https://github.com/randombit/botan/issues/5614>`_
     - up to 3.11.0 and presumably also 3.12.0
     -
     - Problematic behaviour of `Stateful_RNG::force_reseed()` with respect to the resulting RNG state with possible side effects to SCA countermeasures in ECC operations.
   * - `#5615 <https://github.com/randombit/botan/issues/5615>`_
     - up to 3.11.0 and presumably also 3.12.0
     -
     - Control of SCA countermeasures in ECC operations depends implicitly on RNG seeding state. This is an obscure and error prone mechanism to control an important security measure.



Non-Security Critical Issues
============================

The following known issues are present in Botan |botan_version|.

.. list-table::
   :class: longtable
   :widths: 10 20 10 50
   :header-rows: 1

   * - Reference
     - Affected versions
     - Fixed in Version
     - Description
   * - #5002
     - All earlier versions featuring ML-DSA
     - Fix is pending. PR exists (#5307).
     - RFC 9881 specifies three alternative encodings of the ML-DSA private key. Botan still reads and writes the "pure seed" format, which is not compatible to any of those specified in RFC 9881.

   * - Not tracked in GitHub
     - All earlier versions featuring ML-KEM
     - Fix is pending.
     - RFC 9935 specifies three alternative encodings of the ML-KEM private key. Botan still reads and writes the "pure seed" format, which is not compatible to any of those specified in RFC 9935.


