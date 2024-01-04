Security and Vulnerabilities
============================

.. _secinfo/kyberslash:

KyberSlash
----------

This is a series of potential side channel vulnerabilities discovered in several
software implementations of Kyber. It was initially discovered by Goutam
Tamvada, Franziskus Kiefer, and Karthikeyan Bhargavan and later `independently
reported by Daniel Bernstein
<https://groups.google.com/a/list.nist.gov/g/pqc-forum/c/hWqFJCucuj4/m/-Z-jm_k9AAAJ>`_.
A `similar issue was discovered by Prasanna Ravi and Matthias Kannwischer
<https://groups.google.com/a/list.nist.gov/g/pqc-forum/c/ldX0ThYJuBo/m/ovODsdY7AwAJ>`_
in a different part of the implementation shortly after.

The timing side channels stem from divisions by a constant integer (`q`) in the
C++ code. On some target configurations (compiler, processor architecture, build
flags) this division operation is represented by a variable-time division
instruction, which leaks information.

Affected are the compression of Kyber's shared secret value during
decapsulation, as well as the compression of the ciphertext during
encapsulation. The latter is relevant for the security of the scheme, because
the encapsulation is used in the FO transformation for re-encryption.
Under certain circumstances, an attacker might be able to extract information
about the secret key from the timing of these operations.
