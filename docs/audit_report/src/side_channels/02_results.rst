---------------------------------------------
Evaluierung ausgewählter Algorithmen in Botan
---------------------------------------------

Dieses Kapitel beschreibt die Ergebnisse der Analyse ausgewählter Algorithmen in Botan Version 3.
Dazu wurden die ersten beiden Phasen von DATA verwendet.
Die dritte Phase wurde für die Auswertung der Ergebnisse zunächst nicht benötigt.
Die betrachteten Algorithmen sind CRYSTALS-Kyber, CRYSTALS-Dilithium, XMSS und SPHINCS+.
Die Code-Basis für Kyber, Dilithium und XMSS ist Botan Version 3.0.0 [BOTAN_GIT_300]_.
Die Code-Basis für SPHINCS+ ist Botan Version 3.1.0 [BOTAN_GIT_310]_.
Für jeden Algorithmus wurde ein Hilfsprogramm geschrieben.
In den folgenden Kapiteln werden die verwendeten Analyseparameter erläutert und die gefundenen Leaks beschrieben.

^^^^^^^^^^^^^^^^^
Analyse-Parameter
^^^^^^^^^^^^^^^^^

Für die erste Phase von DATA werden drei Ausführungen mit drei zufällig ausgewählten Schlüsseln im DBI Framework Intel Pin beobachtet und die entsprechenden Address Traces erzeugt.
Diese Traces werden verglichen und alle Unterschiede erfasst.
In der zweiten Phase von DATA werden drei fixe Schlüssel ausgewählt, für die jeweils ein Fixed-Set von 100 Traces erzeugt wird.
Das Random-Set besteht ebenfalls aus 100 Traces und wird mit zufällig ausgewählten Schlüsseln erzeugt.
Der Kuiper-Test wird für alle in Phase 1 festgestellten Unterschiede durchgeführt.
Dazu wird jedes Fixed-Set mit dem Random-Set verglichen.
Liegt die Testmetrik für einen Unterschied über der Signifikanzschwelle, so wird dieser als Leak registriert.
Das Konfidenzniveau für den Kuiper-Test in Phase 2 beträgt 99,99 %.


Die Anzahl der Traces unterscheidet sich von Seitenkanalanalysen, die auf dem Stromverbrauch oder der elektromagnetischen Abstrahlung basieren.
Das DBI Framework erlaubt die Beobachtung der Ausführung von Botan ohne Störfaktoren, äquivalent zu einer Messung ohne Rauschen oder Überlagerung durch andere Komponenten.
Dadurch ist es möglich, mit deutlich weniger Traces belastbare Ergebnisse zu generieren.
Adressbasierte Seitenkanalangriffe in der Praxis basieren in der Regel auf Beobachtungen geringerer Qualität.
Die Anzahl der Traces für die Analyse mit DATA entspricht daher in der Regel einem Vielfachen der Traces, die in der Praxis für einen Angriff benötigt werden.

^^^^^^^^^^
Ergebnisse
^^^^^^^^^^

Die folgenden Kapitel enthalten die Ergebnisse der analysierten Implementierungen für CRYSTALS-Kyber, CRYSTALS-Dilithium, XMSS und SPHINCS+.
Wenn es mehrere Implementierungsvarianten eines Algorithmus gibt, werden diese am Anfang der Kapitel aufgeführt.
Wenn das Botan CLI verwendet wird, ist das Kommando für den Aufruf angegeben.
Details zur Kompilierung von Botan und zum Aufruf außerhalb der CLI sind ebenfalls angegeben.
Gefundene Leaks werden in eigenen Abschnitten beschrieben.
Die Beschreibungen enthalten in der Regel auch den zugehörigen Quellcode und ggf. die Aufrufhierarchie.

.. toctree::
   :includehidden:

   02_01_kyber
   02_02_dilithium
   02_03_xmss
   02_04_sphincsplus
