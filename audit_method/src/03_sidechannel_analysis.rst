Seitenkanalanalysen
===================

Mit den Änderungen der Bibliothek an den kryptografischen Verfahren wird auch
der aktuelle Stand der Wissenschaft hinsichtlich der Sicherheit gegenüber
Seitenkanalangriffen ermittelt.

Dafür findet eine Literaturrecherche zu den jeweiligen geänderten Verfahren
statt. Dabei liegt der Fokus der Recherche auf Software-basierten Angriffen und
Gegenmaßnahmen.

Daraus werden konkrete implementierungsspezifische Maßnahmen für die jeweiligen
Verfahren abgeleitet.

Nach der Anpassung der kryptographischen Verfahren durch den Auftragnehmer
unterlaufen diese einen Code-Review Prozess, der auf die Härtung der
Seitenkanalresistenz hinsichtlich der Unterschiede zwischen den beiden
Entwicklungszweigen ausgelegt ist. Dabei wird zuerst auf die Umsetzung
allgemeiner implementierungsspezifischer Maßnahmen geachtet, die allgemeine
Seitenkanalangriffe verhindern. Dazu gehören z.B. vom eingesetzten Schlüssel
unabhängige Berechnungszeiten und Programmverzweigungen.

Im Anschluss wird die Implementierung auf Umsetzung von Maßnahmen untersucht,
die gegen Seitenkanalangriffe härtet, die speziell auf die Änderungen an den
jeweiligen Verfahren ausgerichtet sind. Der Maßnahmenkatalog hierfür ergibt
sich aus der im Vorfeld des Code-Review stattfindenden Literaturrecherche zum
aktuellen Stand der Wissenschaft.

Es werden die folgenden Methoden und Tools genutzt um Untersuchungen zu
Seitenkanälen durchzuführen.

Timing-basierte Seitenkanalanalysen
-----------------------------------

In Botan existieren zwei Möglichkeiten um Timing-basierte Seitenkanalanalysen
durchzuführen. Bei der ersten Variante wird Valgrind genutzt. Hierzu reicht es
Botan mit ``--with-valgrind`` zu konfigurieren, die Bibliothek anschließend zu
kompilieren und im Anschluss die Testsuite auszuführen. Gefundene Fehler werden
während der Ausführung der Tests von Valgrind auf die Konsole ausgegeben.

Bei der zweiten Variante werden die in AP2 des Projekt 197 entwickelten
erweiterten Tests genutzt. Diese wurden in das CLI-Tool mit dem Kommando
``timing_test`` integriert (*src/cli/timing_tests.cpp*). Sie umfassen Tests für
RSA (Bleichenbacher, Manger), TLS (Lucky13) und ECDSA. Nach der Ausführung der
Tests müssen die Ergebnisse manuell anhand von generierten Graphen evaluiert
werden. Die Graphen werden mit der Mona Timing Reporting Bibliothek [MONA]_
erstellt.

Differential Address Trace Analysis (DATA)
------------------------------------------

Differential Address Trace Analysis (DATA) ist eine Methode und ein
Evaluationsframework [DATA]_ für die automatisierte Suche nach Schwachstellen in
sicherheitskritischer Software, die durch Seitenkanäle zur Extraktion von
sensiblen Daten genutzt werden können. DATA basiert auf der Analyse von
Sequenzen von Speicheradressen, auf die bei der Ausführung eines Programms
zugegriffen wird. Konkret versucht DATA, statistische Zusammenhänge zwischen
sensiblen Daten, die vom Programm verarbeitet werden, und zugegriffenen
Speicheradressen zu finden. Dabei kommen nichtparametrische Statistiken auf
Basis des Kolmogorov-Smirnov-Tests und Abhängigkeitstests vergleichbar zur
Mutual Information zum Einsatz. Die von DATA identifizierten Schwachstellen,
auch Leaks oder Points-of-Interest genannt, stellen grundlegende Bausteine für
Seitenkanalangriffe dar, die zum Beispiel die Mikroarchitektur von Prozessoren
oder das Speichermanagement von Betriebssystemen ausnutzen. Gefundene
Schwachstellen sind unabhängig von konkreten Angriffen, geben jedoch konkrete
Hinweise auf datenabhängiges Verhalten des Codes. Die Testergebnisse von DATA
erlauben auch die Bewertung einer Implementierung bezüglich des Zeitverhaltens
(Ist der Code constant-time?) inklusive möglicher Cache-basierter Angriffe. Die
Analyse von Programmen ist nach einer Anpassung des DATA Frameworks an Botan und
das jeweils zu untersuchende Verfahren vollautomatisiert durchführbar. Die
Analyse ist parallelisierbar und lässt sich auch nach gewünschter statistischer
Konfidenz skalieren. Im Anschluss an die Analysephase findet ein Code-Review
statt, in dem der Code der Points-of-Interest untersucht wird.
