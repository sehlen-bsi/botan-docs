Key Derivation Functions
========================

KDF1 (ISO 18033)
----------------

KDF1 is a key derivation function defined in [ISO-18033-2]_, section 6.2.2.
KDF1 is implemented according to [ISO-18033-2]_. It can be
instantiated with any hash function. The implementation can be found in
``src/lib/kdf/kdf1_iso18033/kdf1_iso18033.cpp``.

NIST SP800-108
--------------

NIST [SP800-108]_ defines three functions for key derivation using
pseudorandom functions: KDF in Counter Mode (5.1), KDF in Feedback Mode
(5.2) and KDF in Double-Pipeline Iteration Mode. All three
implementations can be found in ``src/lib/kdf/sp800_108/sp800_108.cpp``.
They can all be instantiated with any message authentication code as a
PRF.

The implementation of KDF in Counter Mode fixes the length of
:math:`[L]_2` and :math:`[i]_2` (the value ``r``) to 32 bits.

The implementation of KDF in Feedback Mode uses the optional counter *i*
and fixes the length of :math:`[L]_2` and :math:`[i]_2` (the value
``r``) to 32 bits.

The implementation of KDF in Double-Pipeline Iteration Mode uses the
optional counter *i* and fixes the length of :math:`[L]_2` and
:math:`[i]_2` (the value ``r``) to 32 bits.

NIST SP800-56C
--------------

NIST [SP800-56C]_ defines a key derivation using extraction-then-expansion.
The implementation can be found in
``src/lib/kdf/sp800_56c/sp800_56c.cpp``. The implementation fixes the
context value for the expansion step to the empty string.
