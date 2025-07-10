Vorwort
=======

**Zusammenfassung**

Mit Botan steht eine vom BSI geprüfte Kryptobibliothek zur Verfügung. Mit
dem  Einsatz von Botan durch Herstellern von VS-Produkten kann der
Evaluierungsaufwand des BSI für solche Produkte erheblich reduziert werden. Ziel
des Projekts ist die Weiterentwicklung und Pflege des geprüften
BSI-Entwicklungszweigs der Kryptobibliothek Botan. Dafür soll der
BSI-Entwicklungszweig an die aktuelle Botan Version angeglichen werden.
Zusätzlich soll die Botan-Bibliothek um verschiedene Verfahren der
Post-Quanten-Kryptografie erweitert werden.

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
