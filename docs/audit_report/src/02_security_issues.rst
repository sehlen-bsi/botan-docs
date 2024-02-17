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
encapsulation. Both side channels may leak enough sensitive information to be
exploitable by an attacker under certain circumstances.

These side channels are present in Botan 3.0.0 to 3.2.0, and was fixed in
|botan_version|. The fix essentially hard-codes the division by `q` as a series
of constant-time bit shift and multiplication operations. See also :ref:`changes/fixes`.
