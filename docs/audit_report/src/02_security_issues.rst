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
resolved them.

.. TODO: During the review, check the release notes of the releases following
   |botan_version| for issues that are present in |botan_version| and list them
   here (with the release that fixes them in the "Fixed in Version" column).
   Also re-validate the entries carried over from the previous audit below.

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



