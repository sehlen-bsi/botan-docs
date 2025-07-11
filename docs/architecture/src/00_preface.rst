Preface
=======

**Summary**

The objective of this project is the secure implementation of a universal crypto
library that contains all common cryptographic primitives that are necessary
for the wide use of cryptographic operations. These include symmetric and
asymmetric encryption and signature methods, PRFs, hash functions, and RNGs.
Additionally, security standards such as X.509 and SSL/TLS have to be supported.
The project’s eventual goal is to add production-grade implementations of
post-quantum secure algorithms to Botan.

The library will be provided to manufacturers of VS-NfD products, which will help
the Federal Office for Information Security (BSI) to evaluate these products.

This document provides a high-level overview of the library's architecture and
refers to various places of its documentation. It is meant to act as an starting
point for users that are new to the library.

**Authors**

| René Meusel (RM), Rohde & Schwarz Cybersecurity

**Document Revision**

This document was generated on |document_datestamp| based on the git revision |document_gitsha_short|.

.. todolist::

.. raw:: latex

   \vfill

.. sharedimg:: legal/cc-by.png
   :alt: License: CC-BY
   :align: left

.. raw:: latex

   \pagebreak

**Copyright**

This material is protected by copyright law and was released under the `Creative
Commons Attribution 4.0 International <https://creativecommons.org/licenses/by/4.0/deed.en>`_
license.

*You are free to:*

* **Share** - copy and redistribute the material in any medium or format for any
  purpose, even commercially.
* **Adapt** - remix, transform, and build upon the material for any purpose,
  even commercially.

The licensor cannot revoke these freedoms as long as you follow the license terms.

*Under the following terms:*

* **Attribution** - You must give appropriate credit, provide a link to the
  license, and indicate if changes were made. You may do so in any reasonable
  manner, but not in any way that suggests the licensor endorses you or your
  use.

* **No additional restrictions** - You may not apply legal terms or
  technological measures that legally restrict others from doing anything the
  license permits.
