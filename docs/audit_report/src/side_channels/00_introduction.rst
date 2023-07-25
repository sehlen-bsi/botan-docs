Language Disclaimer
-------------------

The following chapter is currently written in German.
A future version of this document will use English for the side channel analysis as well.
We apologize for the inconvenience.

Einleitung
----------

Dieses Kapitel beinhaltet die Analyse von ausgewählten Algorithmen in Botan
hinsichtlich der Seitenkanal-Leakage. Dafür kommt die Methodik *Differential
Address Trace Analysis* (DATA) und das gleichnamige Framework zum Einsatz. DATA
wurde auf der USENIX 2018 veröffentlicht [DATA]_ und wird als Open-source
Projekt auf GitHub entwickelt [DATA_GIT]_. Die nachfolgenden Kapitel beschreiben
die Methodik von DATA, die Anwendung in Botan und die Ergebnisse der Analyse.
