Einleitung
==========

Mit der Version Botan-2.14.0-RSCS1 liegt derzeit eine Version von Botan vor, die
die Empfehlungen aus den technischen Richtlinien des BSI berücksichtigt. In der
Zwischenzeit wird Botan durch die Maintainer weiterentwickelt, etwa neue
Algorithmen hinzugefügt oder Fehler in Botan behoben. Auch werden Änderungen
durch den Auftragnehmer Rohde & Schwarz Cybersecurity im Rahmen der Wartung der
Bibliothek für das BSI vorgenommen.

Bevor im Rahmen der Wartung auf eine neue Botan-Version umgestellt wird, müssen
alle offiziellen und eventuell versteckten Änderungen am Code genau geprüft
werden. Dazu wird vom Auftragnehmer für jede Version ein Prüfbericht erstellt
und zusammen mit dem Quelltext dem BSI vorgelegt. Dies betrifft insbesondere
Änderungen an kryptographischen Aspekten. Hier benötigt das BSI für eine
Umstellung auf eine neue Botan-Version eine fundierte Entscheidungsgrundlage.

Dieses Dokument beschreibt die Prüfmethodik. Beschrieben werden der Prozess der
Verfolgung der Änderungen, Untersuchungen aus Arbeitspaket 1 und 2 die
wiederholt werden müssen und schlussendlich Dokumente die aktualisiert werden
müssen.
