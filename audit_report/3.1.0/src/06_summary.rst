Summary and Results
===================

This document contains the audit report for the changes between Botan version 3.0.0-alpha1 and version
3.1.1. The performed analysis includes a patch-based, manual audit of Botan's source code and
the results of several analysis tools.

The most significant changes include the following:

* Software implementation of CRYSTALS Dilithium and SPHINCS+
* Additional features for the TLS 1.3 implementation
* The application of clang-format on the source files
* Various polishing for the 3.0.0 release

According to the observations of this audit, Botan version 3.1.1 keeps the security level of
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
