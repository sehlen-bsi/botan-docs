-----------------------------------
Differential Address Trace Analysis
-----------------------------------

DATA is a methodology and framework for the automated detection of programme code in security-critical software that is vulnerable to side-channel attacks.
DATA works with the binary representation of a program as it is actually executed on target systems.
The source code is not needed for the analysis, but is important for the interpretation and for fixing any problems found.
The instructions vulnerable to side-channel attacks are called *leak* and the behaviour of the instructions is called *leakage*.
DATA finds *address-based* leaks, i.e. all control flow and data access operations that are executed depending on secret program inputs.
The following two diagrams illustrate this.

.. figure:: img/data-leak.png
   :scale: 15 %

   Leak dependent on data access.

.. figure:: img/cflow-leak.png
   :scale: 15 %

   Leak dependent on control flow.

The variable *sec* is secret, e.g. a cryptographic key or a password.
The first graphic shows a data leak.
This type of leak manifests itself in accesses to memory areas, e.g. look-up tables, depending on secret data.
The second graphic shows a control flow leak.
Here, the execution is changed depending on secret data and, for example, different functions are called.
Data leaks show up in different load/store addresses depending on the input.
Control flow leaks show up in different jump addresses depending on the input and in a change of the instruction pointer.

For additional details of the analysis please refer to the "Audit Methodology document".
