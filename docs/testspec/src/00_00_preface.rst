Preface
=======

**Summary**

The objective of this project is the secure implementation of a universal crypto
library which contains all common cryptographic primitives that are necessary
for the wide use of cryptographic operations. These include symmetric and
asymmetric encryption and signature methods, PRFs, hash functions and RNGs.
Additionally, security standards such as X.509 and SSL/TLS have to be supported.
The project’s eventual goal is to add production-grade implementations of
post-quantum secure algorithms to Botan.

The library will be provided to manufacturers of VS-NfD products which will help
the Federal Office for Information Security (BSI) to evaluate these products.

This document specifies test cases implemented in the library's test suite.

**Authors**

| René Fischer (RK), Rohde & Schwarz Cybersecurity
| Juraj Somorovsky (JSo), Hackmanit GmbH
| Sergii Cherkavskyi (SC), Rohde & Schwarz Cybersecurity
| René Meusel (RM), Rohde & Schwarz Cybersecurity
| Fabian Albert (FA), Rohde & Schwarz Cybersecurity

**Document Revision**

This document was generated on |document_datestamp| based on the git revision |document_gitsha_short|.

.. todolist::

**Copyright**

This work is protected by copyright law. Every application outside of copyright
law without explicit permission by the Federal Office for Information Security
(BSI) is forbidden and will be prosecuted. This holds especially for the
reproduction, translation, microfilming and storing and processing in electronic
systems.
