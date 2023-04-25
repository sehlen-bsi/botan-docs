Verfolgen der Änderungen
========================

Ziel der Änderungsverfolgung ist es, alle Änderungen an der Bibliothek zu
identifizieren, nach ihrer Relevanz zu klassifizieren und relevante Änderungen
genauer zu untersuchen. Dazu wird die Bibliothek zunächst in Komponenten
aufgeteilt. Zu den Komponenten gehören die Module der Bibliothek selbst
(Verzeichnis src/lib), die Testsuite (Verzeichnis src/tests), das Command Line
Interface (Verzeichnis src/cli), der Python-Wrapper (Verzeichnis src/python),
das Buildsystem (Skript configure.py und Verzeichnis src/build-data) sowie die
Dokumentation (Verzeichnis doc). Für jede dieser Komponenten wird ein
textbasiertes Diff erstellt. Zur Erzeugung des Diffs kommt das Linux
Kommandozeilentool *diff* zum Einsatz. Jedes Diff wird analysiert und die darin
enthaltenen Änderungen werden für jede der Komponenten dokumentiert. Jede
Änderung wird dabei klassifiziert, d.h., einer Kategorie zugeordnet, die die
Relevanz der Änderung für die Sicherheit der gesamten Bibliothek anzeigt.

Klassifizierung
---------------

Ob eine Änderung sicherheitsrelevant ist wird anhand von verschiedenen Kriterien
entschieden. Bei Änderungen am Buildsystem hängt es von der Natur der Änderungen
ab ob sie kritisch sind. Das Buildsystem stellt unter Anderem sicher, dass nur
die Module im Kompilat vorhanden sind, die während der Konfiguration des Builds
angewählt wurden, ist also bei Änderungen an dieser Logik als kritisch zu
betrachten. Änderungen an der Testsuite sind als kritisch zu betrachten, sobald
sie Module betreffen die in der BSI-Modulpolicy enthalten sind oder sobald sie
abhängige Module betreffen. Auch Änderungen an Modulen der Bibliothek die in der
BSI-Modulpolicy enthalten sind oder die abhängige Module betreffen können als
kritisch betrachtet werden.

Jede Änderung wird in eine von drei Kategorien eingeordnet. Änderungen der
Kategorie I bezeichnen dabei sicherheitskritische Änderungen, d.h., Änderungen
die den ordnungsgemäßen Betrieb der kryptographischen Funktionen
beeinträchtigen. Änderungen der Kategorie II bezeichnen sicherheitsrelevante
Änderungen, d.h., Änderungen die die Effizienz oder Effektivität der
kryptographischen Funktionen erhöhen. Änderungen der Kategorie III bezeichnen
weitere, nicht-sicherheitskritische Änderungen, d.h., Änderungen aus anderen
Gründen als bezogen auf die Sicherheit.

Zur Herstellung des Kontextes oder der Absicht einer Änderung, oder zur
Identifizierung einer Änderung als gleichzeitige Änderung an mehreren,
miteinander verbundenen Modulen, kann es notwendig sein den Git Commit, dem die
Änderung zugrunde liegt, zu identifizieren und das Diff des jeweiligen Commits
anzusehen. Nachfolgend findet sich daher eine kurze Erläuterung zur
Vertrauenswürdigkeit von Git.

Sicherheit und Vertrauenswürdigkeit von Git
-------------------------------------------

Der SHA-1 Hash eines Git Commits berechnet sich aus dem Source-Tree des Commits
(dem Delta) und diversen Header Informationen, wie dem Commit SHA-1 Hash des
Vorgängercommits, der Autoren Informationen, den Committer Informationen und der
Commit Beschreibung.

Die Integrität des Repositories wird über den Commit SHA-1 Hash des
Vorgängercommits sichergestellt. Da im Header des Vorgängercommits dessen
Vorgängercommit SHA-1 Hash vorhanden ist kann die Kette bis zum initialen Commit
gebildet und sichergestellt werden. Das heißt, dass die Veränderung eines
Commits dazu führt, dass sich alle nachfolgenden Commit Hashes ändern und diese
Veränderung erkannt wird. Um sicherzustellen, dass eine lokale Repository-Kopie
nicht verändert wurde, muss daher der SHA-1 Hash des letzten bzw. aktuellsten
Commits des lokalen Repositories mit dem entfernten Repository (bspw. auf
GitHub) verglichen werden.

Da derzeit noch SHA-1 als Hash Funktionen zum Einsatz kommt beruht die
Sicherheit darauf, dass es einem Angreifer nicht gelingt eine Kollision also
einen Commit mit identischem SHA-1 Hash zu berechnen.

Weiterhin bietet Git die Möglichkeit einzelne Commits mittels GPG zu signieren.
Auf diese Weise wird die Authentizität der Commits sichergestellt.
