Key Derivation Functions
========================

HKDF (RFC 5869)
---------------

HKDF is a key derivation function defined in [RFC5869]_.
HKDF is implemented according to [RFC5869]_ with some additions.
The implementation can be found in :srcref:`src/lib/kdf/hkdf/hkdf.cpp`.

It can be instantiated with HMAC with any hash function.
It can also be instantiated with any other MAC,
such usage is however outside the specification in [RFC5869]_.

Note that the implementation of ``HKDF-Expand(PRK, info, L)``
takes in Botan a ``label`` and ``salt`` value instead of ``info``.
The ``info`` value is the concatenation of ``label | salt``.

Botan also includes a ``HKDF-Expand-Label()`` implementation,
used e.g. in TLS 1.3.

KDF1 (ISO 18033)
----------------

KDF1 is a key derivation function defined in [ISO-18033-2]_, section 6.2.2.
KDF1 is implemented according to [ISO-18033-2]_. It can be
instantiated with any hash function. The implementation can be found in
:srcref:`src/lib/kdf/kdf1_iso18033/kdf1_iso18033.cpp`.

NIST SP800-108
--------------

NIST [SP800-108]_ defines three functions for key derivation using
pseudorandom functions: KDF in Counter Mode (5.1), KDF in Feedback Mode
(5.2) and KDF in Double-Pipeline Iteration Mode. All three
implementations can be found in :srcref:`src/lib/kdf/sp800_108/sp800_108.cpp`.
They can all be instantiated with any message authentication code as a
PRF.

The implementations of KDF in Feedback Mode as well as Double-Pipeline Iteration
Mode always use the optional counter *i*.

The encoding bit widths of the desired output length :math:`[L]_2` and counter
value :math:`[i]_2` (the value ``r``) can be configured to be 8, 16, 24, or 32
bits in all implemented modes.

NIST SP800-56Cr2 One-Step KDM
-----------------------------

NIST [SP800-56Cr2]_ defines a one-step key derivation method based on a hash
function, HMAC, or KMAC. All three of these options are supported. The
implementation can be found in
:srcref:`src/lib/kdf/sp800_56a/sp800_56c_one_step.cpp`.

NIST SP800-56Cr2 Two-Step KDM
-----------------------------

NIST [SP800-56Cr2]_ defines a two-step key derivation using
extraction-then-expansion. The implementation can be found in
:srcref:`src/lib/kdf/sp800_56c/sp800_56c_two_step.cpp`. The implementation
fixes the context value for the expansion step to the empty string.
