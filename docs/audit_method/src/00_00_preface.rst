Vorwort
=======

**Zusammenfassung**

Dieses Dokument ist das direkte Ergebnis der Projekte 481 und 197 des
Bundesamtes für Sicherheit in der Informationstechnik (BSI) mit dem Ziel die
quelloffene Kryptobibliothek `Botan <https://github.com/randombit/botan>`_ zu
unterstützen. Botan bietet sichere, wartbare und gut dokumentierte
Implementierungen von kryptografischen Basiskomponenten für ein breites
Spektrum moderner kryptografischer Anwendungen. Insbesondere werden Verfahren
der Post-Quanten-Kryptografie unterstützt um eine langlebige Sicherheit
der verarbeiteten Daten sicherstellen zu können.

Botan ist insbesondere für den Einsatz in sicherheitskritischen Produkten
geeignet, die im VS-NfD Umfeld eingesetzt werden sollen. Dieses Dokument soll
dem BSI helfen, die Verwendung von Botan in diesen Produkten zu bewerten.

Dieser Bericht erläutert die Prüfmethodik, die für die Freigabe neuer
Botan-Versionen zum Einsatz kommt.

**Autoren**


| René Fischer (RK)
| Juraj Somorovsky (Jso)
| Daniel Neus (DN)
| Philippe Lieser (PL)
| René Meusel (RM)
| Andreas Seelos-Zankl (ASZ), Fraunhofer AISEC
| Alexander Wagner (AW), Fraunhofer AISEC

**Dokumentrevision**

Dieses Dokument wurde am |document_datestamp| aus der Git Revision |document_gitsha_short| erzeugt.

.. todolist::

.. raw:: latex

   \vfill

.. sharedimg:: legal/cc-by.png
   :alt: License: CC-BY
   :align: left

.. raw:: latex

   \pagebreak

**Copyright**

Das Material ist urheberrechtlich geschützt und wurde unter der `Creative Commons
Attribution 4.0 International <https://creativecommons.org/licenses/by/4.0/deed.de>`_
Lizenz veröffentlicht.

*Sie dürfen:*

* **Teilen** - das Material in jedwedem Format oder Medium vervielfältigen und
  weiterverbreiten und zwar für beliebige Zwecke, sogar kommerziell.

* **Bearbeiten** - das Material remixen, verändern und darauf aufbauen und zwar
  für beliebige Zwecke, sogar kommerziell.

Der Lizenzgeber kann diese Freiheiten nicht widerrufen solange Sie sich an die
Lizenzbedingungen halten.

*Unter folgenden Bedingungen:*

* **Namensnennung** - Sie müssen angemessene Urheber- und Rechteangaben machen,
  einen Link zur Lizenz beifügen und angeben, ob Änderungen vorgenommen wurden.
  Diese Angaben dürfen in jeder angemessenen Art und Weise gemacht werden,
  allerdings nicht so, dass der Eindruck entsteht, der Lizenzgeber unterstütze
  gerade Sie oder Ihre Nutzung besonders.

* **Keine weiteren Einschränkungen** - Sie dürfen keine zusätzlichen Klauseln
  oder technische Verfahren einsetzen, die anderen rechtlich irgendetwas
  untersagen, was die Lizenz erlaubt.
