Preface
=======

**Summary**

This document is a direct result of Projects 481 and 197 of the German Federal
Office for Information Security (BSI) with the aim to support
`Botan <https://github.com/randombit/botan>`_ - a secure, maintained and
well-documented cryptographic library. Botan provides building blocks for a wide
range of modern cryptographic applications that may have to protect their data
against the upcoming threat of a quantum computer.

Botan may be used by manufacturers of VS-NfD products and this document will help
the BSI to evaluate these products.

This document describes the cryptographic implementations of Botan.

**Authors**

| René Fischer (RK)
| Juraj Somorovsky (JSo)
| Tobias Niemann (TN)
| Fabian Weißberg (FW)
| Sergii Cherkavskyi (SC)
| Philippe Lieser (PL)
| René Meusel (RM)
| Amos Treiber (AT)
| Fabian Albert (FA)

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
