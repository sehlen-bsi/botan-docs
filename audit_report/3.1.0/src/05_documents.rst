Documentation Update
====================

Work package 2 (AP2) defines several documents necessary to overview
the Botan library, its tests, cryptographic implementations, and its
development and maintenance process. With the continuous development of
the library, the documents must be kept up to date. It follows a list of
these documents.


Botan Reference Guide
---------------------

The reference guide [REFG]_ is a documentation manual for Botan users. Among other things, it describes the configuration of the library,
its interfaces, and its functions. If changes have been made to parts of the library that are documented in the handbook,
the documentation must be adapted accordingly. With this report,
an up-to-date manual is provided.


Library Architecture Overview
-----------------------------

The document "Library Architecture Overview" [ARCH]_ describes Botan's file structure, build system,
important programming interfaces,
CPU-specific optimizations, the provider interfaces, the command line interface,
and the test suite architecture. Changes to the library are adjusted accordingly in this documentation.


Test Specification
------------------

The document "Test Specification" [TESTSP]_ describes the tests implemented in Botans's test suite.
It contains both a description of the test cases and a partial listing of the test vectors. Deletions,
additions, and modifications of tests are addressed in this document.


Test Report
-----------

The document "Test Report" [TESTRP]_ lists the test results of Botan's test suite. For this review
it is executed for the version under examination, and the results are documented.


Cryptographic Documentation
---------------------------

The document "Cryptographic Documentation" [CRYPD3]_ describes the cryptographic implementations of the
library. This description includes the algorithms recommended by the BSI for hash functions, symmetric
encryption, message authentication codes, prime number generation, parameter generation for public key algorithms,
key generation for public key algorithms, asymmetric encryption and key exchange schemes, signatures,
random number generators, entropy sources, X.509 certificate support, and key derivation functions. Any
changes to the described implementations are adjusted accordingly in this documentation.
