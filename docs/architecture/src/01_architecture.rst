Botan Architecture
==================

Introduction
------------

Botan consists of three main parts: the library itself, a CLI tool, and the test suite.
The library itself is divided into separate modules.
Botan uses a custom build system allowing for fine-grained configuration of the desired algorithms being built.
This document relies heavily on Botan's public documentation merely providing guidance and pointers to get accustomed to the library and its architecture.

Repository Anatomy
------------------

`Botan's upstream repository <https://github.com/randombit/botan>`_ has the following rough directory and file structure:

================ ===============================================================
File/Dir. Name   Description
================ ===============================================================
doc              The Botan Reference Guide [REFG]_ and more general information, like a roadmap
src              The actual source code for all provided software artefacts
configure.py     Build system configuration script
license.txt      BSD-2-Clause license information
news.rst         Release notes
readme.rst       The repository landing page with pointers to the documentation
================ ===============================================================


The ``src`` directory contains the following sub-structure:

================ ===============================================================
File/Dir. Name   Description
================ ===============================================================
bogo_shim        Adapter to test Botan's TLS with BoringSSL's test suite
build-data       All build system related files
cli              Command Line Tool
configs          Various configuration files for e.g. pylint and sphinx
ct_selftest      Ensures fundamental assumptions on the constant-time test tool
editors          Code editor integrations (e.g. for vim or sublime)
examples         Many small usage examples illustrating typical use cases
fuzzer           Fuzz targets for various modules of the library
lib              The library source code
python           Python bindings of the library's FFI layer
scripts          Helpers and continuous integration scripts
tests            Test suite and test data
================ ===============================================================


The ``lib`` directory has a fine-grained structure into modules and sub-modules.
Botan's `online documentation <https://botan.randombit.net/doxygen/topics.html>`_ provides a comprehensive overview of those modules and their interdependencies.
For further details, please see [REFG]_ Section 19.1 or the online documentation:
`Notes for New Contributors <https://botan.randombit.net/handbook/dev_ref/contributing.html#library-layout>`_

Botan Build System
==================

The library follows the usual configure, build, test, install compilation workflow.
Though, Botan does rely on its own custom build system implemented in python.
This enables the library to provide a flexible module system as well as advanced build features like an amalgamation build.

Users can specify fine-grained selections on which cryptographic algorithms,
hardware-specific optimized implementations, protocols, operating system adapters
and more should be part of their custom built library.
This module selection can also be driven by a build policy.
E.g. the BSI build policy :srcref:`src/build-data/policy/bsi.txt` can be used to create a Botan build that contains algorithms compliant with BSI's technical specifications only.

Further details on the usage and implementation of Botan's build system are available here:

 * [REFG]_, Sections 4 and 19.2 or
 * the online documentation

   * `Building the library <https://botan.randombit.net/handbook/building.html>`_
   * `Understanding configure.py <https://botan.randombit.net/handbook/dev_ref/configure.html>`_


Library Fundamentals
====================

Abstract Base Classes and Algorithm Instantiation
-------------------------------------------------

Usually, Botan groups algorithms behind generic interfaces.
This allows implementations to instantiate different algorithms at runtime via a simple algorithm identifier.
Details can be found in the [REFG]_, Section 8, the API reference documentation or online:

 * `API Reference Handbook <https://botan.randombit.net/handbook/api_ref/contents.html>`_
 * `Doxygen Documentation <https://botan.randombit.net/doxygen/>`_

   * `Cipher_Mode <https://botan.randombit.net/doxygen/classBotan_1_1Cipher__Mode.html>`_
   * `HashFunction <https://botan.randombit.net/doxygen/classBotan_1_1HashFunction.html>`_
   * `MessageAuthenticationCode <https://botan.randombit.net/doxygen/classBotan_1_1MessageAuthenticationCode.html>`_
   * `KDF <https://botan.randombit.net/doxygen/classBotan_1_1KDF.html>`_
   * `RandomNumberGenerator <https://botan.randombit.net/doxygen/classBotan_1_1RandomNumberGenerator.html>`_
   * `PasswordHash <https://botan.randombit.net/doxygen/classBotan_1_1PasswordHash.html>`_
   * ...

Providers
---------

Both the abstract factory methods above as well as various constructors allow specifying a "provider".
This allows exchanging certain implementations in Botan with either other software implementations from 3rd party libraries or hardware-backed implementations such as HSMs, smart cards or TPMs.
Currently, Botan ships four providers: PKCS #11, TPM 2.0, CommonCrypto and a deprecated TPM 1.2 provider.
Previous versions of Botan also supported OpenSSL but this was dropped when OpenSSL 3.0 was released with significant API changes.


Command Line Interface
======================

Botan offers a set of command line tools to handle some common tasks on the command line.
Note that the implementations of those CLI commands usually serve as good usage examples of the library aspect they provide.

The command line tool is invoked with ``./botan <cmd> <cmd-options>``.

Further details about the available commands and functionality can be found in [REFG]_ Section 9 or the online documentation:
`Command Line Interface <https://botan.randombit.net/handbook/cli.html>`_


Test Suite
==========

Unit and Integration Tests
--------------------------

Botan contains an extensive test suite that aims to cover the library source code with positive and negative tests.
The test framework is homegrown and provides functionality for both typical "Arrange-Act-Assert"-style unit tests as well as more elaborate integration tests and external test-vector based KAT tests.

Further details are in the [REFG]_ section 19.3 or the online documentation:
`Test Framework <https://botan.randombit.net/handbook/dev_ref/test_framework.html>`_


TLS Integration Tests
---------------------

The components of Botan's TLS implementation are well covered by unit tests.
To verify proper implementation of the TLS specifications, including common error
cases, it integrates with `BoringSSL's integration test framework "BoGo" <https://github.com/google/boringssl/tree/master/ssl/test>`_.
Essentially, BoGo contains a highly instrumented and customizable TLS implementation (both client and server).
With that, BoringSSL ships an elaborate integration test suite that is reusable for 3rd party TLS implementations like Botan.
Further implementation details of BoGo are beyond the scope of this document.

To interface with the BoGo tests, Botan provides a so-called "shim".
This configurable program serves as an adapter and is configured by the BoGo test suite (e.g. to act as a TLS client or server and the socket to connect to).
BoGo then exercises the TLS protocol implementation by communicating with the shim via the established socket and observing success or failure codes the shim produces.
