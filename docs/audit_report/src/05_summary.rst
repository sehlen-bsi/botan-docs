Summary and Results
===================

This document contains the audit report for the changes between Botan version |botan_git_base_ref| and version
|botan_version|. The performed analysis includes a patch-based, manual audit of Botan's source code and
the results of several analysis tools.

The most significant changes are the following:

* Implementations for the post-quantum standards FIPS 203, 204, and 205
* A basic TPM 2.0 wrapper
* A new elliptic curve math library with much better performance

According to the observations of this audit, Botan version |botan_version| keeps the security level of
the previously reviewed version and complements the old version with various sensible and
high-quality features.

This audit report is part of the submission to the BSI, which includes the following documents:

* Audit Report (this document)
* Botan Reference Guide
* Library Architecture Overview
* Test Specification
* Test Report
* Cryptographic Documentation
* Coverage Report
* A signed archive of the audited Botan version
