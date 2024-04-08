Changes Overview
================

Botan |botan_version| is a minor release that does not introduce a lot of new
functionality. In particular, it does not introduce any new post-quantum
algorithms. Therefore, this report does not contain a side-channel analysis
report.

Below are the most notable changes.

X448 and Ed448
--------------

Botan now supports the X448 and Ed448 elliptic curves and the associated
key exchange and signature algorithms.

Preparations for Elliptic Curve Cryptography Support at Compile Time
--------------------------------------------------------------------

Particularly the multi-precision integer arithmetic code has been extended
to be ``constexpr``-friendly. This is a preparation for future work on making
the ECC code ``constexpr``-friendly.

For details see :ref:`changes/multiprecision_integers` and the follow-up pull
request introducing ``constexpr``-ECC that has not landed in |botan_version|:
`GH #3979 <https://github.com/randombit/botan/pull/3979>`_.
