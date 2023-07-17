Aktualisierung der Dokumentation
================================

Es bestehen verschiedene Dokumente zur Dokumentation der Bibliothek. Bei
Änderungen an der Bibliothek kann eine Aktualisierung der Dokumentation
erforderlich sein. Dies betrifft die im Folgenden genannten Dokumente.

Handbuch
--------

Das Handbuch stellt die Anwenderdokumentation zur Verfügung. Es beschreibt u.A.
die Konfiguration der Bibliothek, ihre Schnittstellen und Funktionen. Wurden an
Teilen der Bibliothek Änderungen vorgenommen die im Handbuch dokumentiert sind,
so muss die Dokumentation dazu entsprechend angepasst werden. Wurden neue
Funktionen hinzugefügt, aber nicht im Handbuch dokumentiert, so wird
entsprechende Dokumentation hinzugefügt.

Architekturbeschreibung
-----------------------

Das Dokument „Architecture Description“ [ARCH]_ beschreibt die Dateistruktur,
das Buildsystem, wichtige Programmierschnittstellen, CPU-spezifische
Optimierungen, die Providerschnittstellen, das Kommandozeilenprogramm und die
Testsuite. Wurden an diesen Teilen der Bibliothek Änderungen vorgenommen, so
muss die Dokumentation dazu entsprechend angepasst werden.

Durch kontinuierliche Erweiterung des User Manuals im Hauptentwicklungszweig
sind viele Informationen aus der Architekturbeschreibung nach derzeitigem Stand
bereits im User Manual enthalten. Die redundanten Information werden aus der
Architekturbeschreibung entfernt. Es wird angestrebt auch die restlichen
Informationen in das offizielle Botan User Manual zu überführen

Testspezifikation
-----------------

Das Dokument „Test Specification“ [TESTSP]_ beschreibt die in der Testsuite der
Bibliothek implementierten Tests. Die Tests bestehen zum großen Teil aus Known
Answer Tests (KAT), enthalten aber auch sowohl positive wie negative Unit-Tests.
Das Dokument enthält sowohl eine Beschreibung der Testfälle als auch bei KAT
eine teilweise Auflistung der Testvektoren. Wurden an den Tests Änderungen
vorgenommen, beispielsweise durch Hinzufügen oder Entfernen von Testfällen oder
Testvektoren oder das Ändern von Testfällen oder Testvektoren, so muss die
Dokumentation entsprechend angepasst werden.

Test Report
-----------

Das Dokument „Test Report“ [TESTRP]_ listet die Testresultate der Testsuite auf.
Da die Testsuite in jedem Fall mit der neuen Version der Bibliothek ausgeführt
wird, muss auch der Testreport entsprechend der Testergebnisse angepasst werden.

Kryptodokumentation
-------------------

Das Dokument „Cryptographic Documentation“ [CRYPD]_ beschreibt die
kryptographischen Implementierungen der Bibliothek. Dazu gehören die
Implementierungen der vom BSI empfohlenen Verfahren für Hashfunktionen,
Symmetrische Verschlüsselung, Message Authentication Codes, Primzahlerzeugung,
Parameter für Public-Key Verfahren, Schlüsselerzeugung für Public-Key Verfahren,
Asymmetrische Verschlüsselung, Schlüsselaustauschverfahren, Signaturverfahren,
Zufallsgeneratoren, Entropiequellen, X.509 Zertifikatsvalidierung und Key
Derivation Functions. Wurden an den beschriebenen Implementierungen Änderungen
vorgenommen, so muss die Dokumentation entsprechend angepasst werden. Die
Ergebnisse der Literaturrecherche zu Seitenkanal-Angriffen werden festgehalten.
Sollten neue kryptografische Implementierungen hinzukommen wird die
Dokumentation für diese ergänzt.
