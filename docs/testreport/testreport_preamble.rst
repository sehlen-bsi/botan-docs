=================
Botan Test Report
=================

.. list-table::
   :header-rows: 0

   * - Botan Version
     - %{botan_version}
   * - Git Revision
     - %{botan_git_sha}
   * - Git Reference
     - %{botan_git_ref}
   * - Generation Date
     - %{date_today}

.. raw:: latex

   \pagebreak

Preface
=======

**Summary**

The objective of this project is the secure implementation of a universal crypto
library which contains all common cryptographic primitives that are necessary for
the wide use of cryptographic operations. These include symmetric and asymmetric
encryption and signature methods, PRFs, hash functions and RNGs. Additionally,
security standards such as X.509 and SSL/TLS have to be supported. The library will
be provided to manufacturers of VS-NfD products which will help the Federal Office
for Information Security (BSI) to evaluate these products.

This document reports the test results of the Botan test suite.

**Authors**

| Daniel Neus (DN)
| René Fischer (RK)
| René Meusel (RM)
| Philippe Lieser (PL)

**Copyright**

This work is protected by copyright law. Every application outside of
copyright law without explicit permission by the
Federal Office for Information Security (BSI) is forbidden and will be prosecuted.
This holds especially for the reproduction, translation, microfilming and
storing and processing in electronic systems.

.. raw:: latex

   \pagebreak

Test Report
===========

The following report lists the test results for the Botan test suite.
The following information is given for each test run:

 * Information about the test environment

    * Botan configuration
    * Date and time of execution
    * Operating system
    * Compiler and compiler version
    * Target architecture

 * Number of tests executed

    * Of these, the number of tests executed successfully
    * Of these, the number of failed tests

 * A list of failed tests and the reason for each test failure

.. raw:: latex

   \pagebreak

.. role:: raw-latex(raw)
   :format: latex
