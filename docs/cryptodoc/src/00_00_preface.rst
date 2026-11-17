Preface
=======

**Summary**

This document has been created as part of Project P663 issued by the German Federal Office for
Information Security (BSI) and is based on the cryptographic documentation written as part of the previous Projects P197 and P481 of BSI. 
The aim of P663 is the enhancement and maintenance of the Botan
cryptographic library `Botan <https://github.com/randombit/botan>`_.  Botan provides building blocks
for a wide range of modern cryptographic applications.

As Botan may be used by manufacturers of VS-NfD products according to German national requirements,
one purpose of this document is to facilitate the evaluation of such products by the BSI.

This document describes the cryptographic implementations in Botan.

**Historical Authors**

The following persons are authors of previous versions of this document pertaining to earlier Botan releases. Parts of the document text and the tooling used to create the version at hand have been authored by them.

| René Fischer (RK)
| Juraj Somorovsky (JSo)
| Tobias Niemann (TN)
| Fabian Weißberg (FW)
| Sergii Cherkavskyi (SC)
| Philippe Lieser (PL)
| René Meusel (RM)
| Amos Treiber (AT)
| Fabian Albert (FA)

**Authors**

The authors of the present document version are listed in the table below.

| Johannes Roth,  MTG AG
| Falko Strenzke, MTG AG

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
