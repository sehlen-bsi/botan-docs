Preface
=======


**Summary**

This document provides the result of the audit review of the Botan releases following version 3.11 up to and including 3.12 as part of Project P663 issued by
the German Federal
Office for Information Security (BSI). It is based on the previous versions of the Audit Report that
were created in the scope of the projects P197 and P481.
The aim of this project is the enhancement and maintenance of the cryptographic library
`Botan <https://github.com/randombit/botan>`_.
Botan provides building blocks for a wide
range of modern cryptographic applications.

As Botan may be used by manufacturers of VS-NfD products according to German national requirements, one purpose of this document is to facilitate the evaluation of such products by the BSI.

This document tracks the changes and their audit results between two library
revisions. Typically audit iterations are performed starting from the previous
audit target revision to establish a new audited revision.

**Historical Authors**

The following persons are authors of previous versions of this document pertaining to earlier Botan releases. Parts of the document text and the tooling used to create the version at hand have been authored by them.

| Fabian Albert (FA), Rohde & Schwarz Cybersecurity
| René Meusel (RM), Rohde & Schwarz Cybersecurity
| Tudor Soroceanu (TS), Fraunhofer AISEC
| Amos Treiber (AT), Rohde & Schwarz Cybersecurity
| Andreas Seelos-Zankl (ASZ), Fraunhofer AISEC
| Alexander Wagner (AW), Fraunhofer AISEC

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
