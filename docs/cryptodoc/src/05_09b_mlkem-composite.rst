.. _pubkey/mlkem-composite:

ML-KEM-Composite
================


In the module ``ML-KEM-composite`` Botan implements the "ML-KEM with traditional
algorithm" composite KEM algorithms defined in
[draft-ietf-lamps-pq-composite-kem]_. This upcoming standard defines composite KEM
algorithms that have the property that their security is guaranteed as long as
at least one of the two component algorithms remains secure.

 **Key reuse is forbidden.**  According to [draft-ietf-lamps-pq-composite-kem]_ both component keys MUST be freshly generated;
 component keys MUST NOT be reused standalone or across composites.

Parameter Support
-----------------

All parameters from [draft-ietf-lamps-pq-composite-kem]_ are supported. Table  :ref:`pubkey/ml_kem_comp/params` gives an overview over these parameter sets. The "trad. KEM/encryption method" column reflects the draft's own "Traditional KEM
Algorithm" field. Note that neither algorithm name from [draft-ietf-lamps-pq-composite-kem]_, ``RSAOAEPKEM`` nor 
``DHKEM`` is a standalone PKIX algorithm. Both are a building blocks for the composite defined in that very specification. The
OIDs listed (id-RSAES-OAEP, id-ecDH, id-X25519, id-X448) identify the underlying primitive, not the KEM-variant specific to this specification.
SHA3-256 with full 32 byte output is the KDF defined in the specification for all parameter sets.

For the RSA rows, the RSA-OAEP parameters are identical across all key sizes. They are given in Table :ref:`pubkey/ml_kem_comp/oaep-params`. When generating keys, the RECOMMENDED exponent 65537 is used.



.. _pubkey/ml_kem_comp/params:

.. list-table:: Composite ML-KEM parameter sets (draft-ietf-lamps-pq-composite-kem-18)
   :header-rows: 1
   :widths: 30 12 20 10 14 20

   * - Parameter name
     - ML-KEM
     - Traditional scheme
     - Trad. key size
     - Trad. KEM / enc. method
     - OID
   * - id-MLKEM768-RSA2048-SHA3-256
     - 768
     - RSA
     - 2048 bit
     - id-RSAES-OAEP
     - 1.3.6.1.5.5.7.6.55
   * - id-MLKEM768-RSA3072-SHA3-256
     - 768
     - RSA
     - 3072 bit
     - id-RSAES-OAEP
     - 1.3.6.1.5.5.7.6.56
   * - id-MLKEM768-RSA4096-SHA3-256
     - 768
     - RSA
     - 4096 bit
     - id-RSAES-OAEP
     - 1.3.6.1.5.5.7.6.57
   * - id-MLKEM768-X25519-SHA3-256
     - 768
     - X25519
     - 255 bit
     - id-X25519 (DHKEM)
     - 1.3.6.1.5.5.7.6.58
   * - id-MLKEM768-ECDH-P256-SHA3-256
     - 768
     - ECDH, secp256r1
     - 256 bit
     - id-ecDH (DHKEM)
     - 1.3.6.1.5.5.7.6.59
   * - id-MLKEM768-ECDH-P384-SHA3-256
     - 768
     - ECDH, secp384r1
     - 384 bit
     - id-ecDH (DHKEM)
     - 1.3.6.1.5.5.7.6.60
   * - id-MLKEM768-ECDH-brainpoolP256r1-SHA3-256
     - 768
     - ECDH, brainpoolP256r1
     - 256 bit
     - id-ecDH (DHKEM)
     - 1.3.6.1.5.5.7.6.61
   * - id-MLKEM1024-RSA3072-SHA3-256
     - 1024
     - RSA
     - 3072 bit
     - id-RSAES-OAEP
     - 1.3.6.1.5.5.7.6.62
   * - id-MLKEM1024-ECDH-P384-SHA3-256
     - 1024
     - ECDH, secp384r1
     - 384 bit
     - id-ecDH (DHKEM)
     - 1.3.6.1.5.5.7.6.63
   * - id-MLKEM1024-ECDH-brainpoolP384r1-SHA3-256
     - 1024
     - ECDH, brainpoolP384r1
     - 384 bit
     - id-ecDH (DHKEM)
     - 1.3.6.1.5.5.7.6.64
   * - id-MLKEM1024-X448-SHA3-256
     - 1024
     - X448
     - 448 bit
     - id-X448 (DHKEM)
     - 1.3.6.1.5.5.7.6.65
   * - id-MLKEM1024-ECDH-P521-SHA3-256
     - 1024
     - ECDH, secp521r1
     - 521 bit
     - id-ecDH (DHKEM)
     - 1.3.6.1.5.5.7.6.66

.. _pubkey/ml_kem_comp/oaep-params:

.. list-table:: OAEP parameters for Composite ML-KEM (draft-ietf-lamps-pq-composite-kem-18)
   :header-rows: 1
   :widths: 30 30 

   * - RSAES-OAEP-params 
     - Value
   * - hashAlgorithm 	
     - id-sha256
   * - MaskGenAlgorithm.algorithm 	
     - id-mgf1
   * - maskGenAlgorithm.parameters
     - id-sha256
   * - pSourceAlgorithm
     - pSpecifiedEmpty
   * - ss_len 
     - 256 bits

Note that the availability of each parameter set depends not only on the
availability of the module ``ML-KEM-Composite``, but also on the respective
traditional component algorithm in Botan's build configuration. 

.. _pubkey/ml_kem_comp/algo_details:

Algorithm-Details
-----------------

Composite ML-KEM is a PQ/T hybrid KEM that pairs ML-KEM [FIPS-203]_ with
one traditional key-establishment algorithm (RSA-OAEP, ECDH, X25519 or X448).
Both component KEMs are run independently; their shared secrets are then folded
into a single 256-bit shared secret by the *KEM combiner* described here.

The combiner is a single invocation of SHA3-256 over the concatenation of both
component shared secrets, the traditional ciphertext, the traditional public
key, and an algorithm-specific label:

.. math::

   \mathit{ss} \;=\; \mathrm{SHA3\text{-}256}\!\left(
       \mathit{ss}_{\mathrm{mlkem}} \;\|\;
       \mathit{ss}_{\mathrm{trad}}  \;\|\;
       \mathit{ct}_{\mathrm{trad}}  \;\|\;
       \mathit{pk}_{\mathrm{trad}}  \;\|\;
       \mathit{L}
   \right)



.. list-table::
   :header-rows: 1
   :widths: 14 22 18 46

   * - Symbol
     - Draft identifier
     - Length
     - Description
   * - :math:`\mathit{ss}`
     - ``ss``
     - 32 bytes
     - The composite shared secret key. A 256-bit key suitable for direct use
       with symmetric algorithms, at every security level, matching the output
       of ``ML-KEM.Encaps()``.
   * - :math:`\mathit{ss}_{\mathrm{mlkem}}`
     - ``mlkemSS``
     - 32 bytes
     - Shared secret produced by the ML-KEM component
       (``ML-KEM.Encaps()`` / ``ML-KEM.Decaps()``).
   * - :math:`\mathit{ss}_{\mathrm{trad}}`
     - ``tradSS``
     - fixed per algorithm
     - Shared secret produced by the traditional component: the value
       :math:`Z` for ECDH, :math:`K` for X25519/X448, or the 32-byte random
       value transported under RSA-OAEP.
   * - :math:`\mathit{ct}_{\mathrm{trad}}`
     - ``tradCT``
     - fixed per algorithm
     - Ciphertext of the traditional component: the ephemeral public key for
       the DH-based variants, or the RSA-OAEP ciphertext.
   * - :math:`\mathit{pk}_{\mathrm{trad}}`
     - ``tradPK``
     - fixed per algorithm
     - Public key of the traditional component, i.e. the recipient's static
       EC point or ``RSAPublicKey``.
   * - :math:`\mathit{L}`
     - ``Label``
     - fixed per algorithm
     - Byte string bound to the composite algorithm's OID.
   * - :math:`\|`
     - ``||``
     -
     - Concatenation of byte strings.

Component values are used in the wire encodings mandated for the composite:
uncompressed X9.62 points for ECDH, raw encodings per :rfc:`7748` for
X25519/X448, and DER ``RSAPublicKey`` / OAEP ciphertext for RSA.


.. _composite_mlkem_rejection:

Rejection Behaviour of Composite ML-KEM
---------------------------------------


[draft-ietf-lamps-pq-composite-kem]_ does not classify Composite ML-KEM as
either an implicitly or an explicitly rejecting KEM. Instead, §3.5 states a
propagation rule: the composite MUST be explicitly rejecting whenever any of
its components is. 
The resulting behaviour is therefore a property of the individual parameter that
defines a specific algorithm combination.


.. list-table::
   :header-rows: 1
   :widths: 20 26 54

   * - Component
     - Behaviour
     - Error condition
   * - RSA-OAEP
     - Explicitly rejecting
     - ``RSAES-OAEP-DECRYPT`` fails on incorrect padding or on a ciphertext
       whose length does not match the modulus size.
   * - ECDH
     - Explicitly rejecting for malformed input only
     - Deserialisation fails if ``tradCT`` is not a valid uncompressed point
       on the named curve. A well-formed point on the curve yields a shared
       secret without error.
   * - X25519 / X448
     - Effectively implicitly rejecting
     - None. Any ciphertext of the correct length is accepted; the all-zero
       output check of :rfc:`7748` is optional and is not mandated by the
       draft.

ML-KEM itself is implicitly rejecting by construction ([FIPS-203]_, Algorithms 18 and 21), but may still
return an error for a ciphertext or decapsulation key of incorrect size.

Consequence for the API
^^^^^^^^^^^^^^^^^^^^^^^

Implementations that use ML-composites in Botan with generic parameterization
must be prepared handle both the case where an invalid ciphertext leads to an
error during decapsulation and where it leads to the output of a rejection key. 
Note that for ML-KEM-composite with RSA, in Botan, the explicit rejection will surface as an
exception of the type `Botan::Decoding_Error`.


Implementation in Botan
-----------------------

Table :ref:`pubkey/mlkem_composite/files` lists the header files that are part of Botan's public API and the implementation source files of ML-KEM-composite in Botan. The cryptographic implementation of the component algorithms in all cases reuses the existing
implementations in Botan.

.. _pubkey/mlkem_composite/files:

.. table:: ML-KEM-Composite Header File Locations under the folder ``pubkey/mlkem-composite``

   +-----------------------------------------------------------+-----------------------------------------+
   | Component                                                 | Purpose                                 |
   +===========================================================+=========================================+
   | ``mlkem_comp.h``                                          | Part of the public API: Public and      |
   |                                                           | Private key objects                     |
   +-----------------------------------------------------------+-----------------------------------------+
   | ``mlkem_comp_parameters.h``                               | Part of the public API: Parameter type  |
   |                                                           | for ML-KEM-Composite                    |
   +-----------------------------------------------------------+-----------------------------------------+
   | ``mlkem_comp.cpp``                                        | Implementation of Public and Private    |
   |                                                           | key objects and all cryptographic       |
   |                                                           | operations                              |
   +-----------------------------------------------------------+-----------------------------------------+
   | ``mlkem_comp_parameters.cpp``                             | Implementation of the Parameter type    |
   |                                                           | for ML-KEM-Composite                    |
   +-----------------------------------------------------------+-----------------------------------------+

Conformance to TR-02102
-----------------------

For PQ/T hybrid solutions for ML-KEM [TR-02102-1]_ makes specific requirements as to how the component algorithms have to be combined. As one option, [TR-02102-1]_ refers to the key combiner construction given in [SP-800-227]_ of the form 

.. math::

  K \leftarrow  \mathrm{KeyCombine}( K_1, K_2, c_1, c_2, ek_1, ek_2, p )

where :math:`K_i` refers to the shared keys, :math:`c_i` to the ciphertexts, :math:`ek_i` to the encapsulation (i.e., public) keys and :math:`p = (p_1, p_2)` to 
the parameters of component schemes 1 and 2, respectively. The construction [draft-ietf-lamps-pq-composite-kem]_, deviates from this form by omitting :math:`c_\textrm{mlkem}` and :math:`ek_\textrm{mlkem}`, where the subscript `mlkem` refers to the index of the ML-KEM component algorithm.
In summary, the following deviations of ML-KEM-composite specification can be identified:

- Dropping of the ML-KEM ciphertext as an input. This is justified in
  [draft-ietf-lamps-pq-composite-kem]_ with reference to [XWING]_.
- Dropping the ML-KEM public-key. 
- As the function KeyCombine(), the construction in [draft-ietf-lamps-pq-composite-kem]_ uses SHA3-256. [TR-02102-1]_ approves the use of KMAC as the key combiner but not specifically SHA3-256; 

In so far, [draft-ietf-lamps-pq-composite-kem]_ deviates from the requirements
for multi-algorithm KEM constructions in the current
version of [TR-02102-1]_.

Note that placing both shared secrets first lets the remaining inputs be treated as
``OtherInput`` under the NIST SP 800-227 key-combiner form, and the SP 800-56C
counter may be omitted because the hash is invoked exactly once
([FIPS-140-3-IG]_, p. 202).


