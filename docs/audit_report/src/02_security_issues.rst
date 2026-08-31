Open Security and Compatibility Issues in the Audited Version
=============================================================

The following table lists the open security and compatibility issues in the
audited version |botan_version|, i.e. issues that are present in |botan_version|
and were not fixed within the range covered by this audit. The ``Type`` column
indicates whether an issue affects security and/or compatibility. The ``Source``
column records where the issue was identified: issues drawn from the upstream
Botan release notes are marked *Botan release notes*, while issues identified
during this project's audit are marked *P663 Audit*. For issues taken from the
release notes, the ``Fixed in Version`` column names the upstream release that
resolved them; the first release published after |botan_version| is Botan 3.13.0
(released 2026-08-13). None of the security issues listed below were assigned a
CVE in the official release notes.

.. list-table::
   :class: longtable
   :widths: 12 11 10 15 10 42
   :header-rows: 1

   * - Reference
     - Source
     - Type
     - Affected versions
     - Fixed in Version
     - Description
   * - `#5815 <https://github.com/randombit/botan/issues/5815>`__
     - Botan release notes
     - security
     - |botan_version| and likely earlier
     - 3.13.0
     - Blind server-side request forgery (SSRF) during OCSP request processing: a malicious OCSP responder or network attacker could cause the application to perform a blind GET request to an internal service.
   * - `#5838 <https://github.com/randombit/botan/issues/5838>`__, `#5839 <https://github.com/randombit/botan/issues/5839>`__
     - Botan release notes
     - security
     - |botan_version|, only on platforms without a system RNG
     - 3.13.0
     - A bug in ``AutoSeeded_RNG`` where the API sequence of ``clear()`` followed by ``randomize()`` writing into an empty buffer resulted in the RNG being considered seeded although it was not.
   * - `#5629 <https://github.com/randombit/botan/issues/5629>`__, `#5820 <https://github.com/randombit/botan/issues/5820>`__
     - Botan release notes
     - security
     - |botan_version|, only on 32-bit platforms
     - 3.13.0
     - An integer overflow in the handling of Scrypt parameters.
   * - Not referenced by a dedicated pull request in the release notes
     - Botan release notes
     - security
     - |botan_version| and likely earlier
     - 3.13.0
     - Certain Distinguished Name (DN) name constraints were not correctly enforced during X.509 certificate path validation.
   * - `#5805 <https://github.com/randombit/botan/issues/5805>`__
     - Botan release notes
     - security
     - |botan_version| and likely earlier
     - 3.13.0
     - An integer overflow in the FFI interface that might be exploitable in unusual scenarios involving attacker-controlled cipher specifiers and the raw block cipher (ECB) APIs.
   * - `#5614 <https://github.com/randombit/botan/issues/5614>`__
     - P663 Audit
     - security
     - up to 3.11.0 and presumably also 3.12.0
     -
     - Problematic behaviour of `Stateful_RNG::force_reseed()` with respect to the resulting RNG state with possible side effects to SCA countermeasures in ECC operations.
   * - `#5615 <https://github.com/randombit/botan/issues/5615>`__
     - P663 Audit
     - security
     - up to 3.11.0 and presumably also 3.12.0
     -
     - Control of SCA countermeasures in ECC operations depends implicitly on RNG seeding state. This is an obscure and error prone mechanism to control relevant security measure.
   * - `#5002 <https://github.com/randombit/botan/issues/5002>`__
     - P663 Audit
     - compatibility
     - All earlier versions featuring ML-DSA
     - Fix is pending. PR exists (`#5307 <https://github.com/randombit/botan/issues/5307>`__).
     - RFC 9881 specifies three alternative encodings of the ML-DSA private key. Botan still reads and writes the "pure seed" format, which is not compatible to any of those specified in RFC 9881.
   * - Not tracked in GitHub
     - P663 Audit
     - compatibility
     - All earlier versions featuring ML-KEM
     - Fix is pending.
     - RFC 9935 specifies three alternative encodings of the ML-KEM private key. Botan still reads and writes the "pure seed" format, which is not compatible to any of those specified in RFC 9935.



