.. _pubkey/mldsa_composite:

ML-DSA-Composite
================

In the module ``ML-DSA-composite`` Botan implements the "ML-DSA with traditional
algorithm" composite signature algorithms defined in
[draft-ietf-lamps-pq-composite-sigs]_. This upcoming
standard defines composite signature algorithms that have the property that
their security is guaranteed as long as at least one of the two component
algorithms remains secure.


.. note::

 **Key reuse is forbidden.**  According to [draft-ietf-lamps-pq-composite-sigs]_ both component keys MUST be freshly generated;
 component keys MUST NOT be reused standalone or across composites. This has
 relevance to the security of the scheme, since for the case where the
 traditional component keys are reused, principal cross-algorithm EUF-CMA
 violations can be possible due to the application of the so-called signature
 combiner before the component signature generation or verification in the
 composite scheme.

Parameter Support
-----------------


All parameters from [draft-ietf-lamps-pq-composite-sigs]_ are supported. They are listed in Table :ref:`pubey/mldsa_composite/params_tab`.
Note that the availability of each parameter set depends not only on the
availability of the module ``ML-DSA-Composite``, but also on the respective
traditional component algorithm in Botan's build configuration.

.. _pubey/mldsa_composite/params_tab:

.. list-table:: Composite ML-DSA parameter sets
   :header-rows: 1
   :widths: 32 11 19 9 20 11 18

   * - Parameter name
     - ML-DSA
     - Traditional scheme
     - Trad. key size
     - Trad. signature algorithm
     - Pre-hash (PH)
     - OID
   * - id-MLDSA44-RSA2048-PSS-SHA256
     - 44
     - RSA (PSS)
     - 2048 bit
     - id-RSASSA-PSS
     - SHA-256
     - 1.3.6.1.5.5.7.6.37
   * - id-MLDSA44-RSA2048-PKCS15-SHA256
     - 44
     - RSA (PKCS#1 v1.5)
     - 2048 bit
     - sha256WithRSA Encryption
     - SHA-256
     - 1.3.6.1.5.5.7.6.38
   * - id-MLDSA44-Ed25519-SHA512
     - 44
     - Ed25519
     - 255 bit
     - id-Ed25519
     - SHA-512
     - 1.3.6.1.5.5.7.6.39
   * - id-MLDSA44-ECDSA-P256-SHA256
     - 44
     - ECDSA, secp256r1
     - 256 bit
     - ecdsa-with-SHA256
     - SHA-256
     - 1.3.6.1.5.5.7.6.40
   * - id-MLDSA65-RSA3072-PSS-SHA512
     - 65
     - RSA (PSS)
     - 3072 bit
     - id-RSASSA-PSS
     - SHA-512
     - 1.3.6.1.5.5.7.6.41
   * - id-MLDSA65-RSA3072-PKCS15-SHA512
     - 65
     - RSA (PKCS#1 v1.5)
     - 3072 bit
     - sha256WithRSA Encryption
     - SHA-512
     - 1.3.6.1.5.5.7.6.42
   * - id-MLDSA65-RSA4096-PSS-SHA512
     - 65
     - RSA (PSS)
     - 4096 bit
     - id-RSASSA-PSS
     - SHA-512
     - 1.3.6.1.5.5.7.6.43
   * - id-MLDSA65-RSA4096-PKCS15-SHA512
     - 65
     - RSA (PKCS#1 v1.5)
     - 4096 bit
     - sha384WithRSA Encryption
     - SHA-512
     - 1.3.6.1.5.5.7.6.44
   * - id-MLDSA65-ECDSA-P256-SHA512
     - 65
     - ECDSA, secp256r1
     - 256 bit
     - ecdsa-with-SHA256
     - SHA-512
     - 1.3.6.1.5.5.7.6.45
   * - id-MLDSA65-ECDSA-P384-SHA512
     - 65
     - ECDSA, secp384r1
     - 384 bit
     - ecdsa-with-SHA384
     - SHA-512
     - 1.3.6.1.5.5.7.6.46
   * - id-MLDSA65-ECDSA-brainpoolP256r1-SHA512
     - 65
     - ECDSA, brainpoolP256r1
     - 256 bit
     - ecdsa-with-SHA256
     - SHA-512
     - 1.3.6.1.5.5.7.6.47
   * - id-MLDSA65-Ed25519-SHA512
     - 65
     - Ed25519
     - 255 bit
     - id-Ed25519
     - SHA-512
     - 1.3.6.1.5.5.7.6.48
   * - id-MLDSA87-ECDSA-P384-SHA512
     - 87
     - ECDSA, secp384r1
     - 384 bit
     - ecdsa-with-SHA384
     - SHA-512
     - 1.3.6.1.5.5.7.6.49
   * - id-MLDSA87-ECDSA-brainpoolP384r1-SHA512
     - 87
     - ECDSA, brainpoolP384r1
     - 384 bit
     - ecdsa-with-SHA384
     - SHA-512
     - 1.3.6.1.5.5.7.6.50
   * - id-MLDSA87-Ed448-SHAKE256
     - 87
     - Ed448
     - 448 bit
     - id-Ed448
     - SHAKE256/64
     - 1.3.6.1.5.5.7.6.51
   * - id-MLDSA87-RSA3072-PSS-SHA512
     - 87
     - RSA (PSS)
     - 3072 bit
     - id-RSASSA-PSS
     - SHA-512
     - 1.3.6.1.5.5.7.6.52
   * - id-MLDSA87-RSA4096-PSS-SHA512
     - 87
     - RSA (PSS)
     - 4096 bit
     - id-RSASSA-PSS
     - SHA-512
     - 1.3.6.1.5.5.7.6.53
   * - id-MLDSA87-ECDSA-P521-SHA512
     - 87
     - ECDSA, secp521r1
     - 521 bit
     - ecdsa-with-SHA512
     - SHA-512
     - 1.3.6.1.5.5.7.6.54

Notes on the parameter sets
^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **RSASSA-PSS parameters depend on key size.** For 2048 and 3072 bit:
  ``hashAlgorithm = id-sha256``, ``maskGenAlgorithm = id-mgf1`` with
  ``id-sha256``, ``saltLength = 32``, ``trailerField = 1``. For 4096 bit:
  ``id-sha384`` / MGF1-``id-sha384``, ``saltLength = 48``,
  ``trailerField = 1``. The ``RSASSA-PSS-params`` ASN.1 type is **not**
  encoded — the values are fixed by the specification and the
  AlgorithmIdentifier parameters MUST be absent.

* **RSA exponent** is RECOMMENDED to be 65537 in the specification and the Botan implementation uses this exponent strictly in key generation.



The signature combiner
----------------------


Composite ML-DSA combines the message inputs of the component schemes: it constructs a single **message representative** ``M'``
and passes that same ``M'`` to both component signature algorithms. The
resulting signature value is the plain concatenation of the two component
signatures.

Message representative
^^^^^^^^^^^^^^^^^^^^^^

The message representative is given by 

.. math::

   M' := \mathrm{Prefix} \;\|\; \mathrm{Label} \;\|\;
         \mathrm{len}(ctx) \;\|\; ctx \;\|\; \mathrm{PH}(M)


Signature generation
^^^^^^^^^^^^^^^^^^^^

Composite signature generation employs the component signature generation algorithms  ML-DSA.Sign() and Trad.Sign() as follows:

.. math::

   \sigma_{\mathrm{ML\text{-}DSA}} &=
       \mathrm{ML\text{-}DSA.Sign}(sk_{\mathrm{ML\text{-}DSA}},\, M',\;
       ctx_{\mathrm{ML\text{-}DSA}} = \mathrm{Label}) \\
   \sigma_{\mathrm{Trad}} &=
       \mathrm{Trad.Sign}(sk_{\mathrm{Trad}},\, M') \\
   s &= \sigma_{\mathrm{ML\text{-}DSA}} \;\|\; \sigma_{\mathrm{Trad}}

Signature verification
^^^^^^^^^^^^^^^^^^^^^^

Verification recomputes ``M'`` from ``M`` and ``ctx``, splits ``s`` at the
fixed ML-DSA signature length, and requires **both** component
verifications to succeed:

.. math::

   \mathrm{Valid} \iff
     \mathrm{ML\text{-}DSA.Verify}(pk_{\mathrm{ML\text{-}DSA}},\, M',\,
       \sigma_{\mathrm{ML\text{-}DSA}},\;
       ctx_{\mathrm{ML\text{-}DSA}} = \mathrm{Label})
     \;\wedge\;
     \mathrm{Trad.Verify}(pk_{\mathrm{Trad}},\, M',\, \sigma_{\mathrm{Trad}})


Why each input is present
^^^^^^^^^^^^^^^^^^^^^^^^^

``Prefix``
    A fixed, algorithm-independent domain separator. It allows a cautious
    implementer to wrap an existing traditional ``Verify()`` with a guard
    that rejects any message beginning with this string, providing extra
    protection against splitting a composite signature back into usable
    component signatures. (Trade-off: such an implementation can then no
    longer sign a legitimate message that happens to start with this string.)

``Label``
    Binds the signature to one specific composite algorithm. It is
    additionally passed down as the ``ctx`` of the underlying **ML-DSA**
    primitive, which is what gives the ML-DSA component a limited form of
    *strong non-separability*: an ML-DSA signature stripped as the result of
    stripping away the traditional component will fail
    under ``ML-DSA.Verify(..., ctx="")``.

``len(ctx) || ctx``
    The application context, length-prefixed. Length-prefixing prevents the
    boundary between ``ctx`` and ``PH(M)`` from being ambiguous.

``PH(M)``
    The pre-hashed message. Pre-hashing avoids streaming the full message to
    *both* component signers, and permits digesting once and signing with
    several keys or contexts.

.. note::

   There are **two distinct context values** in play. The application context
   ``ctx`` is bound into ``M'``. Separately, the per-algorithm
   ``Label`` is passed as the ``ctx`` argument of the underlying
   ``ML-DSA.Sign``/``Verify``. Some EdDSA implementations also expose a
   context parameter — however, this context parameter is not used by Composite ML-DSA.


Symbols used in the combiner
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: Mathematical and algorithmic symbols
   :header-rows: 1
   :widths: 16 32 52

   * - Symbol
     - Name / type
     - Meaning
   * - ``||``
     - operator
     - Concatenation of two byte arrays.
   * - :math:`\wedge`
     - operator
     - Logical AND; all component verifications must succeed.
   * - ``M``
     - octet string
     - The message to be signed.
   * - ``M'``
     - octet string
     - The *message representative* actually passed to both component
       signature algorithms.
   * - ``Prefix``
     - fixed octet string (32 bytes)
     - ASCII ``"CompositeAlgorithmSignatures2025"``. 
   * - ``Label``
     - fixed octet string
     - Per-algorithm signature label, e.g.
       ``COMPSIG-MLDSA65-ECDSA-P384-SHA512``. Also used as the ML-DSA
       component's ``ctx``.
   * - ``ctx``
     - octet string, 0–255 bytes
     - Application context string; defaults to the empty string.
       ``len(ctx) > 255`` is an error.
   * - ``len(ctx)``
     - single unsigned byte
     - Length of ``ctx``, encoded as one byte (as in FIPS 204).
   * - ``PH``
     - hash function
     - Pre-hash function, fixed per composite algorithm (SHA-256, SHA-512,
       or SHAKE256/64 — see the parameter table).
   * - ``PH( M )``
     - octet string
     - Digest of the message under ``PH``.
   * - ``pk`` / ``sk``
     - composite key pair
     - Composite public / private key



Implementation in Botan
-----------------------

:ref:`pubkey/mldsa_composite/files` lists the header files that are part of Botan's public API and the implementation source code files. The cryptographic implementation of the component algorithms in all cases reuses the existing
implementations in Botan.

.. _pubkey/mldsa_composite/files:

.. table:: ML-DSA-Composite File Locations under the folder ``pubkey/mldsa-composite``

   +-----------------------------------------------------------------------+-----------------------------------------+
   | Header File                                                           | Purpose                                 |
   +=======================================================================+=========================================+
   | ``mldsa_comp.h``                                                      | Part of the public API: Public and      |
   |                                                                       | private key objects                     |
   +-----------------------------------------------------------------------+-----------------------------------------+
   | ``mldsa_comp_parameters.h``                                           | Part of the public API: Parameter type  |
   |                                                                       | for ML-DSA-Composite                    |
   +-----------------------------------------------------------------------+-----------------------------------------+
   | ``mldsa_comp.cpp``                                                    | Implementation of public and private    |
   |                                                                       | key objects                             |
   +-----------------------------------------------------------------------+-----------------------------------------+
   | ``mldsa_comp_parameters.cpp``                                         | Implementation of the parameter type    |
   |                                                                       | for ML-DSA-Composite                    |
   +-----------------------------------------------------------------------+-----------------------------------------+

Note that the context parameter is not available as an input parameter and thus
signature and verification operations will always use the empty context.,
