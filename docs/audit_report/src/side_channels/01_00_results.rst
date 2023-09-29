------------------------------------------
Evaluation of selected algorithms in Botan
------------------------------------------

This chapter describes the results of the analysis of selected algorithms and protocols in Botan [BOTAN_GIT]_.
The first two phases of DATA were used for this purpose.
The third phase was not initially required for the evaluation of the results.
In the following chapters, the analysis parameters used are explained and the leaks found are described.

^^^^^^^^^^^^^^^^^^
Analysis parameter
^^^^^^^^^^^^^^^^^^

For the first phase of DATA, three executions with three randomly selected keys are observed in the DBI Framework Intel Pin and the corresponding address traces are generated.
These traces are compared and any differences are recorded.
In the second phase of DATA, three fixed keys are selected and a fixed set of 100 traces is generated for each.
The random set also consists of 100 traces and is generated with randomly selected keys.
The Kuiper test is performed for all differences found in phase 1.
For this purpose, each fixed set is compared with the random set.
If the test metric for a difference is above the significance threshold, it is registered as a leak.
The confidence level for the Kuiper test in phase 2 is 99.99 %.

The number of traces differs from side-channel analyses based on power consumption or electromagnetic radiation.
The DBI framework allows the observation of Botan's execution without interfering factors, equivalent to a measurement without noise or overlapping by other components.
This makes it possible to generate robust results with significantly fewer traces.
Address-based side channel attacks in practice are usually based on lower quality observations.
The number of traces for the analysis with DATA therefore usually corresponds to a multiple of the traces that are needed for an attack in practice.

^^^^^^^
Results
^^^^^^^

The following chapters contain the results of the analysed implementations for x25519 and TLS 1.3 PQ-Hybrid.
If there are several implementations of an algorithm, they are listed at the beginning of the chapters.
If the Botan CLI is used, the command prompt is listed.
Details on compiling Botan and using the algorithm without the CLI, if needed, are also given.
Leaks found are described in separate sections.
The descriptions usually also include the associated source code and, if applicable, the call hierarchy.

.. toctree::

   01_01_pq_tls
   01_02_x25519
