Verfolgen der Änderungen
========================

Einsatz von Git und GitHub bei der Entwicklung der Bibliothek
-------------------------------------------------------------

Die Bibliothek wird öffentlich auf GitHub [#botangithub]_ entwickelt. Größere
Änderungen am Code werden in der Regel über themenspezifische "Pull Requests"
[#botanpulls]_ nach einem technischen Review-Prozess durch einen der
Kern-Entwickler der Bibliothek (GitHub "Collaborator") vorgenommen. In
Ausnahmefällen pflegt der Hauptentwickler (Jack Lloyd) kleinere Änderungen
direkt in den Entwicklungszweig der Bibliothek ein. Insbesondere diese direkten
Änderungen sind stets vom Hauptentwickler mittels GPG signiert [#jackgpg]_.

In beiden Fällen erlauben die "Pull Requests" und die direkten Änderungen eine
transparente und verhältnismäßig leicht nach Themen klassifizierbare
Nachverfolgung aller Änderungen in der Bibliothek. Im Folgenden bezieht sich der
Begriff "Patch" sowohl auf Änderungen die mittels eines Pull Requests
eingeflossen sind als auch auf direkte Änderungen durch den Hauptentwickler.

Das Datenmodell von "Git" stellt dabei sicher, dass die Anwendung aller Patches
zwischen zwei Quelltext-Versionen eindeutig von der älteren zur neueren Version
führt. Damit sind alle tatsächlichen Änderungen zwischen zwei Versionen mit der
Gesamtheit aller Patches abgebildet, die von der älteren zur neueren Version
geführt haben.

Dieser Auditierungs-Ansatz setzt die Vertrauenswürdigkeit von "Git" und dessen
Datenmodell voraus. Am Ende dieses Kapitels findet sich daher eine kurze
Erläuterung zur Vertrauenswürdigkeit von Git (siehe :ref:`about_git`).

.. [#botangithub] `github.com/randombit/botan <https://github.com/randombit/botan>`_
.. [#botanpulls] `github.com/randombit/botan/pulls <https://github.com/randombit/botan/pulls>`_
.. [#jackgpg] GPG Schlüssel ID von Jack Lloyd: ``9F:FD:59:6F:AB:50:F9:0D``

Nachträgliche Änderungsverfolgung
---------------------------------

Die Bibliothek wurde für einzelne Versionen bereits in der Vergangenheit einem
Audit unterzogen. Ziel der Änderungsverfolgung ist es, alle Änderungen an der
Bibliothek zu identifizieren die seit dem letzten Audit hinzugekommen sind,
diese nach ihrer Relevanz zu klassifizieren und relevante Änderungen genauer zu
untersuchen.

Dazu werden wie oben beschrieben mithilfe von "Git" alle Patches der Bibliothek
identifiziert, die von einer bereits auditierten Version zur neuen Zielversion
geführt haben. Einzelne Patches haben dabei meist einen thematischen Bezug und
eine technische Beschreibung ("Commit" Nachricht oder "Pull Request"
Beschreibung). Beispielsweise: "Add XMSS Parameter sets defined in NIST
SP.800-208" [#xmssparams]_ enthält die Quelltext-Änderungen um die XMSS
Implementierung um die vom NIST spezifizierten Parameter zu erweitern.

Jeder Patch kann dabei prinzipiell beliebige Komponenten der Bibliothek
betreffen. Die hier betrachteten Komponenten sind die Bibliothek selbst
(Verzeichnis *src/lib*), die Testsuite (Verzeichnis *src/tests*), das Command Line
Interface (Verzeichnis *src/cli*), der Python-Wrapper (Verzeichnis *src/python*),
das Buildsystem (Skript *configure.py* und Verzeichnis *src/build-data*) sowie die
Dokumentation (Verzeichnis *doc*).

Alle identifizierten Patches werden manuell thematisch vorsortiert und danach
einzeln analysiert, nach Sicherheitsrelevanz klassifiziert und die enthaltenen
Änderungen dokumentiert. Das Ergebnis ist ein detailierter themenbezogener
Änderungsbericht mit Referenzen zu allen relevanten Patches. Eine spätere
Nachvollziehbarkeit (etwa durch Dritte) ist damit leicht zu gewährleisten.

.. [#xmssparams] GitHub Pull Request: `#3292 <https://github.com/randombit/botan/pull/3292>`_

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

Thematische Einordnung
----------------------

Zur besseren Übersicht und zur Vereinfachung des Audit-Prozesses werden Patches
soweit möglich thematisch sortiert. Dabei besteht ausdrücklich keine
eins-zu-eins Beziehung von Patches und Themen. Ein Patch kann durchaus Relevanz
für mehr als ein betrachtetes Thema haben und damit mehrmals zugeordnet werden.

Denkbare Themen sind etwa "Hinzufügen einer Implementierung von CRYSTALS-Kyber",
"Schließen einer Sicherheitslücke in der Validierung von X.509 Zertifikaten"
oder "Beschleunigung der Continuous Integration Pipeline". Für jedes Thema
werden die relevanten Patches aufgezählt und die enthaltenen Änderungen
übergreifend dokumentiert.

Themen können ebenfalls eine Klassifizierung der Sicherheitsrelevanz erhalten.
Danach richtet sich gegebenenfalls die Betrachtungstiefe der Patches im Kontext
des Themas.

.. _about_git:

Sicherheit und Vertrauenswürdigkeit von Git
-------------------------------------------

Git verwendet für die Datenverwaltung und Integritätsprüfung von Repositorys
eine kryptographische Hashfunktion. Aus historischen Gründen wird dafür nach wie
vor SHA-1 verwendet. Da SHA-1 nicht mehr als grundsätzlich sicher angesehen wird
begründen die folgenden Ausführungen warum Git zum aktuellen Zeitpunkt trotzdem
vertrauenswürdig einsetzbar ist.

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

Git ist also inhärent von der Kollisionsresistenz in SHA-1 abhängig. Durch eine
Hash-Kollision könnten Commit-Paare mit gleichem SHA-1 Hash verwendet werden, um
Schadcode unbemerkt vom oben beschriebenen Audit-Prozess in ein Repository
einzuschleusen. Ein Angreifer müsste dafür ein Paar von validen Git Commit
Objekten mit einerseits harmlosen (aber funktionsfähigen) Änderungen und
andererseits einem Schadcode erzeugen, die denselben Commit Hash besitzen. Eine
2017 von Stevens et al. veröffentlichte Schwachstelle in SHA-1 [SHATRD]_
ermöglicht dies zwar theoretisch; es ist uns zum aktuellen Zeitpunkt aber kein
Beispiel bekannt, wo dies erfolgreich für Git Commit Objekte demonstriert wurde.

Dabei ist es wichtig zu wissen, dass für eine erfolgreiche Kollision beide
Commits (der Harmlose wie auch der Manipulierte) vom Angreifer erzeugt werden
müssten. Es ist also ausdrücklich *nicht* möglich einen existierenden legitimen
Commit des Repositorys nachträglich auszutauschen. Der Angreifer müsste den
harmlosen Commit also schon frühzeitig in Botan einschleusen.

Mittels Counter-Kryptoanalyse lassen sich Objekte die Teil eines solchen
Angriffs sind aber sicher erkennen (siehe SHA-1-DC [SHA1DC]_). Seit
Bekanntwerden der Schwachstelle verwenden sowohl GitHub [#githubsha1]_ als auch
Git [#gitsha1]_ SHA-1-DC und lehnen Objekte ab die Teil einer so erzeugten
Kollision sind. Das Einschleusen würde also nicht unentdeckt bleiben und damit
einen erfolgreichen Angriff verhindern.

Langfristig sollte selbstverständlich eine Migration auf eine sichere
Hashfunktion angestrebt werden. Dies liegt aber mangels Unterstützung der Git
Hosting-Provider (wie etwa GitHub) [#lwngitsha1]_ nicht in der Hand der
Botan-Entwickler oder den Auditoren in diesem Projekt. Durch die wirksamen
Gegenmaßnahmen mittels SHA-1-DC ist es zum gegebenen Zeitpunkt aber vertretbar
Git für den beschriebenen Audit-Prozess zu vertrauen.

Weiterhin bietet Git die Möglichkeit einzelne Commits mittels GPG zu signieren.
Auf diese Weise wird die Authentizität der Commits sichergestellt. Die Botan
Entwickler machen von dieser Möglichkeit weitestgehend Gebrauch.

Teil :ref:`des Abgabe-Paketes <deliverables>` jedes Audits ist ein signiertes
Quellcode-Archiv der auditierten Bibliotheksversion. Nutzer der Bibliothek haben
somit auch ohne die Verwendung von Git Zugriff auf den gesamten Quellcode.

.. [#githubsha1] `github.blog/2017-03-20-sha-1-collision-detection-on-github-com <https://github.blog/2017-03-20-sha-1-collision-detection-on-github-com>`_
.. [#gitsha1] `github.blog/2017-05-10-git-2-13-has-been-released <https://github.blog/2017-05-10-git-2-13-has-been-released/#sha-1-collision-detection>`_
.. [#lwngitsha1] `lwn.net/Articles/898522 <https://lwn.net/Articles/898522>`_
