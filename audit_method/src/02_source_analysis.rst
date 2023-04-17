Codeanalyse
===========

Botan wird mit der Botan Modulpolicy konfiguriert und anschließend der sich
daraus resultierende Source-Code mittels statischer und dynamischer Codeanalyse
analysiert.

Statische Codeanalyse
---------------------

Die folgenden Tools werden zur statischen Codeanalyse eingesetzt.

Cppcheck
~~~~~~~~

Zur statischen Analyse wird das Tool Cppcheck [CPPCHECK]_ eingesetzt. Dieses Tool
kann beispielsweise Out of Bounds Zugriffe, Speicherlecks und Nullpointer
Dereferenzierungen finden.

clang-tidy
~~~~~~~~~~

Zur statischen Analyse wird das Tool clang-analyzer [CLANGSA]_
eingesetzt. Dieses Tool kann beispielsweise Dead Assignments und Nullpointer
Dereferenzierungen finden.

Visual Studio 2019 Code Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Zur statischen Analyse wird das Code Analysis Tool aus Visual Studio 2022
[MSVCSA]_ eingesetzt. Dieses Tool kann beispielsweise Nullpointer
Dereferenzierungen finden.

Compiler Warnings
~~~~~~~~~~~~~~~~~

Warnungen des Compilers deuten oft auf mögliche Fehler im Programm hin. Es
können jedoch auch Warnungen angezeigt werden obwohl der Programmcode korrekt
ist (sogenannte False Positives). Daher gilt es, eine ausgewogene Auswahl an
Warning Flags zu finden, die dem Compiler übergeben werden. Botan setzt derzeit
für GCC folgende Flags ein:

.. code-block:: none

   -Wall -Wextra -Wpedantic -Wstrict-aliasing -Wcast-align
   -Wmissing-declarations -Wpointer-arith -Wcast-qual
   -Wzero-as-null-pointer-constant -Wnon-virtual-dtor -Wold-style-cast
   -Wsuggest-override -Wshadow -Wextra-semi

Im Maintainer Mode, einem speziellen Modus für Library Maintainer,
werden zusätzlich die folgenden Flags gesetzt:

.. code-block:: none

   -Werror -Wno-error=zero-as-null-pointer-constant
   -Wno-error=strict-overflow -Wno-error=non-virtual-dtor
   -Wstrict-overflow=5

Dynamische Codeanalyse
----------------------

Die folgenden Tools werden zur dynamischen Codeanalyse eingesetzt.

Address Sanitizer
~~~~~~~~~~~~~~~~~

Der Address Sanitizer kann beispielsweise Use-After-Free und Buffer Overflows
detektieren.

Undefined Behaviour Sanitizer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Der Undefined Behaviour Sanitizer kann beispielsweise Integer Overflows und
Undefined Shift Operation detektieren.
