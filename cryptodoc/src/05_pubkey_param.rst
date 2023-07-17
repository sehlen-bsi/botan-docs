Parameter Generation for Public Key Algorithms
==============================================

In the following we describe the parameter generation for Diffie-Hellman (DH) and Digital Signature Algorithm (DSA).
Generation of parameters for elliptic curve algorithms is omitted since
we only recommend the usage of named curves or curves provided by a trusted authority.

.. _pubkey_param/rng:

Random Number Generation for Probabilistic Public Key Algorithms
----------------------------------------------------------------

The algorithms analyzed in this section and the following sections often
require random number generation from a specific range. Typical random
number generators only generate numbers from a range
:math:`r \in {\{{0,...,{2^{n} - 1}}\}}`
, where ``n`` is the maximum bit size of a generated number. This is not
suitable, for example, for the generation of random parameters for DSA
signatures.

In order to generate integers from an arbitrary range as required for the implemented public key algorithms,
Botan uses the ``BigInt::random_integer()`` method (implemented in :srcref:`src/lib/math/bigint/big_rand.cpp`).
It works as follows:

.. admonition:: ``BigInt::random_integer()``

   **Input:**

   -  ``rng``: random number generator (see :ref:`rng/main` for available algorithms)
   -  ``min``: integer lower bound of desired range
   -  ``max``: integer upper bound of desired range, excluding ``max``

   **Output:**

   -  ``r``: :math:`min \leq r < max`

   **Steps:**

   1. Preliminary parameter requirement checks are conducted. ``min`` must be
      smaller than ``max``, and neither can be negative.
   2. Retrieve the bit length ``n`` of the ``max`` value.
   3. Use ``rng`` to generate :math:`r \in {\{{0,...,{2^{n} - 1}}\}}`.
   4. if (:math:`min \leq r < max`) return ``r``.
   5. Go to Step 3.

**Conclusion:** The algorithm is a slight adaptation of Algorithm B.1 in Section B.4 of [TR-02102-1]_
and thus complies with the recommendations in [TR-02102-1]_.

DH/DSA
------

These algorithms require both parties to agree on a finite
multiplicative cyclic group (**Z**/*p*\ **Z**)* where ``p`` is a prime, and a generator ``g`` of the
group or a subgroup. These parameters are called DH
parameters and are typically precomputed as their generation is
very resource-intensive. Botan implements a generic discrete logarithm
group class in :srcref:`src/lib/pubkey/dl_group/dl_group.cpp`. The class
``DL_Group`` offers the constructor ``DL_Group(RandomNumberGenerator&
rng, PrimeType type, size_t pbits, size_t qbits = 0)`` which can be used
to generate DH parameters. Alternatively, Botan offers several
precomputed Internet Engineering Task Force (IETF) standardized as well as some
domain-specific discrete logarithm groups via the
constructor ``DL_Group::DL_Group(const std::string& name)``.
The constructor generating a ``DL_Group`` operates as follows:

.. admonition:: DL_Group()

   **Input:**

   -  ``rng``: random number generator
   -  ``type``: defines characteristics of the prime ``p`` and the generation
      process (Options: Strong, Prime_Subgroup or DSA_Kosherizer; see below for details)
   -  ``pbits``: bit length of the prime ``p``
   -  ``qbits``: bit length of the prime ``q``, where ``q`` is the order of the subgroup
      (for ``type=Strong`` this must be either omitted or set to ``p-1``)

   **Output:**

   -  DL_Group (**Z**/*p*\ **Z**)\* and a generator ``g`` of the subgroup of
      order ``q``

   In any case, the algorithm initially ensures that the passed value ``pbits``
   is larger than 1023. Otherwise the generation process is
   terminated. Thus, only groups corresponding to a prime longer than 1023 bits can be
   generated with Botan.

   If the function is called with ``type=Strong`` a :ref:`safe prime<prim/random_safe_prime>` is used.
   This means that ``p`` is of the form :math:`p=2*q + 1`` for some prime ``q``,
   and the algorithm performs the following steps:

   **Steps:**

   1. Ensure that ``qbits`` is either 0 or ``pbits-1``.
   2. Sample a random safe prime ``p`` of length ``pbits`` using ``rng`` with the
      function ``random_safe_prime()``.
   3. Set generator ``g`` to 2. Since ``p`` is a safe prime, the order ``(p-1)``
      of (**Z**/*p*\ **Z**)\* has the prime factors :math:`q=\frac{p-1}{2}` and 2. Thus the
      selected generator has an order of ``q`` or :math:`2*q=p-1`. Note that the passed
      parameter ``qbits`` is irrelevant in this case as the length of ``q`` is
      always ``pbits-1``.
   4. Verify that the selected generator ``g`` is a quadratic residue modulo
      ``p`` and subsequently has order ``q``. That is the case if it is true that
      :math:`(\frac{g}{p})=g^{\frac{p-1}{2}}\bmod p=g^{q}\bmod p=1`
      where :math:`(\frac{g}{p})` is the Legendre symbol.
      Otherwise, the next prime from the first 6541 precomputed primes :math:`q_{i}`
      is selected as a candidate for the generator ``g``
      and the algorithm repeats Step 4.

   If the function is called with ``type=Prime_Subgroup``, the algorithm
   operates differently and without the need of a safe prime.

   **Steps:**

   1. If a ``qbits`` value of 0 is passed,
      the algorithm first finds a suitable value for the bit length of ``q``.
      This is done by redefining ``qbits`` according to the estimated difficulty
      of the discrete logarithm problem
      :math:`2*\log_{2} (e^{1.92*\sqrt[3]{ \ln{(2^{qbits})} * \ln{(\ln{(2^{qbits})})^{2}} }} *k)`
      found by calling ``dl_exponent_size()`` from
      :srcref:`src/lib/pubkey/workfactor.cpp`.
      Instead of calculating the estimate, the function uses the following predefined buckets:

      - :math:`pbits = 0`: this can not occur as :math:`pbits \geq 1024` is required
      - :math:`0 < pbits \leq 256`: this can not occur as :math:`pbits \geq 1024` is required
      - :math:`256 < pbits \leq 1024`: 192
      - :math:`1024 < pbits \leq 1536`: 224
      - :math:`1536 < pbits \leq 2048`: 256
      - :math:`2048 < pbits \leq 4096`: 384
      - :math:`pbits > 4096``: 512

      Hence the algorithm ensures the recommended bit length of ``q`` given in [RFC3766]_ is never subseeded
      (except for very large keys, see buckets above).
      Furthermore, it ensures that the length of ``q`` is at least 192 bits even when a small ``pbits`` value is
      passed.
   2. Sample the prime ``q`` of length ``qbits`` from the passed ``rng`` by
      calling ``random_prime()``.
   3. Sample ``X`` with length ``pbits`` from ``rng`` and set the highest bit.
   4. Calculate candidate ``p`` as :math:`X - (X \bmod (2*q)) + 1`. Thus ``q`` is a factor of :math:`p-1`.
   5. Verify if candidate ``p`` has length ``pbits``. Otherwise, return to Step 3 to generate a new candidate ``p``.
   6. Perform a primality test of ``p`` with the function ``is_prime()`` for
      random numbers and probability set to 128 (i.e. the chance of false positives is bounded by :math:`\frac{1}{2^{128}}`).
      If ``p`` fails the test,
      repeat from Step 3.
   7. Compute generator ``g`` of the subgroup with order ``q`` using the function ``make_dsa_generator()``.
      After receiving ``p`` and the subgroup order ``q``, ``g`` is computed as follows:

      1. Verify that :math:`p-1>q` holds. If not, the algorithm terminates with
         an invalid argument error.
      2. Verify that ``q`` is a factor of :math:`p-1`. If not, algorithm terminates
         with an invalid argument error.
      3. Iterate over the first 6541 precomputed primes :math:`q_{i}` (without 2) and
         compute ``g`` as :math:`q_i^{\frac{p-1}{q}} \bmod p`.
         If ``g`` is 1, choose the next prime :math:`q_{i}` and
         repeat the process. Once all available primes :math:`q_{i}` have been used and
         no suitable generator is found, the function terminates with an
         error.

   The function call with ``type=DSA_Kosherizer`` generates the primes
   ``p`` and ``q`` using one of the SHA-1 or SHA-2 hash functions. The implementation follows
   the algorithm described in Section A.1.1.2 in [FIPS-186-4]_ and operates
   as follows:

   **Steps:**

   1. If a ``qbits`` value of 0 is passed,
      fix a new bit length for ``q``:
      Assign ``qbits`` to 160 if :math:`pbits \leq 1024`, otherwise set ``qbits`` to 256.
   2. Sample a random ``seed`` of length :math:`\frac{qbits}{8}` bytes from the passed random number
      generator.
   3. Check if the sizes ``qbits`` and ``pbits`` are allowed by [FIPS-186-4]_.
      Only the length combinations listed below are valid. If another
      combination is passed, the algorithm terminates.

      -  If :math:`qbits=160` ``pbits`` must be 1024.
      -  If :math:`qbits=224` ``pbits`` must be 2048.
      -  If :math:`qbits=256` ``pbits`` must be 2048 or 3072.

   4. Choose hash function ``H()`` as SHA-\ ``qbits``.
   5. Compute prime candidate ``q`` as ``H(seed)`` and set the highest and
      lowest bit.
   6. Perform a primality test of ``q`` with the function ``is_prime()`` for
      random numbers and probability set to 128 (i.e. the chance of false positives is bounded by :math:`\frac{1}{2^{128}}`).
      If ``q`` fails the test,
      repeat from Step 2.
   7. Compute :math:`V_k = H(seed+1+k)` for all :math:`k` between 0 and
      :math:`n = \lfloor (pbits-1) / len(H) \rfloor` and construct ``X`` as
      :math:`V_n \| V_{n-1} \| \ldots \| V_0`.

      1. Set the highest bit of ``X``.
      2. Compute ``p`` as  :math:`X-(X \bmod (2*q)-1)`.
      3. Check if ``p`` has the desired bit length ``pbits``. Perform a primality
         test of ``p`` with the function ``is_prime()`` for random numbers and
         probability set to 128. If the check fails, increase :math:`seed` by :math:`n+1` and repeat Step 7.
         After :math:`4*pbits-1` failures, return to Step 2.

   8.  Compute generator ``g`` of the subgroup with order ``q`` using the function ``make_dsa_generator()``.
       After receiving ``p`` and the subgroup order ``q``, ``g`` is computed as follows:

       1. Verify that :math:`p-1>q` holds. If not, the algorithm terminates with
          respective error.
       2. Verify that ``q`` is a factor of :math:`p-1`. If not, algorithm terminates with
          respective error.
       3. Iterate over the first 6541 precomputed primes :math:`q_i` (without 2) and
          computes ``g`` as :math:`q_i^{\frac{p-1}{q}} \bmod p`.
          If ``g`` is 1, choose the next prime :math:`q_i` and
          repeat the process. Once all available primes :math:`q_i` have been used and
          no suitable generator is found, the function terminates with an
          error.

**Remark:** If the DL_Group is generated with ``type=Strong`` the check in Step 4 is necessary to prevent small subgroup attacks effectively.

**Remark:** The guideline [TR-02102-1]_ recommends that ``p`` should have a
bit-length of at least 3000 bits. It is therefore advisable to choose ``pbits``
accordingly. If the DL_Group is generated with ``type=Prime_Subgroup``, this
means the only valid bit lengths of ``p`` and ``q`` are 3072 and 256 respectively.

**Remark:** At the time of this writing [FIPS-186-4]_ from 2013 is still the
latest revision. However [FIPS-186-5-draft]_ from 2019 is available which no
longer recommends DSA as a signature algorithm. Hence, the usage of
``type=DSA_Kosherizer`` for the generation of ``DL_Group`` objects might be
unfavorable.

**Conclusion:** Botan does still allow the generation of 1024 bit DH
parameters. This lower bound should be increased to 3072 bit-length
for conformance with [TR-02102-1]_ starting from 2023.

Elliptic Curve Algorithms
-------------------------

In order to compute a shared secret with ECDH, it is required that both
participating parties agree on a domain, which consists of an elliptic
curve, a base point of the curve, the order of the base point and the cofactor.
[#ecc_domain_parameters]_
Theoretically, it is possible to generate a new elliptic curve suitable for
ECDH. As this process is very costly and comes with many pitfalls, only
precomputed standardized curves are used in Botan. Thus the feature of
elliptic curve parameter generation is not implemented. 27 standardized
curves are provided in :srcref:`src/lib/pubkey/ec_group/ec_named.cpp`. All curves
recommended in [TR-02102-1]_ are included.

It is possible to import custom elliptic curves at run time. However, it is the
application developer's responsibility to ensure that such custom curves are
trustworthy and cryptographically strong. Botan *does not* contain means to
ensure that automatically.

Nevertheless, custom elliptic curve domains can and should be validated with
the provided ``EC_Group::verify_group()`` function. It provides basic sanity
checks but does not check the curve's cryptographic strength.
The verification function operates as follows.

.. [#ecc_domain_parameters]
   Elliptic curve domain parameters, their typical symbols and their inter-
   dependence:

   - :math:`p`: prime size of the underlying field :math:`\mathbb{F}_p`
   - :math:`a, b \in \mathbb{F}_p`: curve coefficients in short Weierstrass form:
     :math:`E_{a,b}: y^2 = x^3 + a*x + b`
   - :math:`G_{x,y}` on :math:`E_{a,b}(\mathbb{F}_p)`: the base point of the curve :math:`E_{a,b}`
   - :math:`n = ord(G_{x,y})`: the order of the base point :math:`G_{x,y}`
   - :math:`h = \#E_{a,b}(\mathbb{F}_p)/n`: the cofactor of the curve

.. admonition:: ``EC_Group::verify_group()``

   **Input:**

   -  ``EC_Group (curve parameters (first coefficient a, second coefficient
      b, prime p), base point G, ord(G) n, cofactor of the curve h)``
   -  ``rng``: random number generator
   -  ``source``: builtin or external source
   -  ``strong``: strong verification (default false)

   **Ouput:**

   -  ``true`` if group ``EC_Group`` is valid. ``false`` otherwise

   **Steps:**

   1. If ``source`` is builtin and ``strong`` is false, return true.
   2. Preliminary parameter requirement checks are conducted. ``a`` must be
      non-negative, ``b`` and ``n`` must be positive, and ``p`` must be larger than 3.
      Both ``a`` and ``b`` must be smaller than ``p``.
   3. Perform a primality test of ``p`` with the function ``is_prime()``
      with the passed random number generator ``rng`` and probability
      [#ecc_prime_prob_details]_ set to 128, assuming that ``p`` was randomly generated
      for builtin groups. [#ecc_prime_check_details]_
      If the test fails return false.
   4. Perform a primality test of ``n`` with the function ``is_prime()``
      with the passed random number generator rng and probability set to 128
      assuming that ``n`` was randomly generated for builtin groups.
      If the test fails return false.
   5. Compute :math:`D=(4*a^3 + 27*b^2) \bmod p`. If :math:`D=0` the curve is
      singular and thus invalid. In this case false is returned.
   6. Check that the cofactor ``h`` is at least 1. If not return false.
   7. Verify that ``G`` is on the curve. If not return false.
   8. Assure that ``G`` has the correct order ``n``. This is the case if
      :math:`h*G \neq P_{\infty}` and :math:`n*G = P_{\infty}`.
      If one of the equations does not hold, return false.

.. [#ecc_prime_prob_details]
   Chance of the number being composite is at most :math:`\sfrac{1}{2^{128}}`

.. [#ecc_prime_check_details]
   See :ref:`prim` for further details of the primality checks

The ``verify_group()`` function follows the main recommendations from
[ReqEC]_. Note however that this function performs basic sanity checks on the
construction of the curve only. In particular it cannot ensure that the passed
parameters are cryptographically strong and/or are not maliciously chosen to
contain a backdoor.

Botan implements the elliptic curve standard [ISO-15946-1]_ for ellipic curves
over :math:`\mathbb{F}_p`. The standard additionally defines curves over
:math:`\mathbb{F}_{2^m}` and :math:`\mathbb{F}_{3^m}` that are not implemented.

*Internally* the representation differs between NIST reduction and Montgomery
reduction curves and implements the reduction algorithms and curve
operations in the respective classes ``CurveGFp_NIST`` and
``CurveGFp_Montgomery``. These representations are an implementation detail that
is not made available or configurable by the application developer.
For efficiency purposes Botan uses Jacobian projective
coordinates for all elliptic curve points and point operations as
described in [ISO-15946-1]_ with the line at infinity defined as ``[0,Y,0]``.
The affine coordinates can be obtained by using the conversion
functions ``PointGFp::get_affine_x()`` and ``PointGFp::get_affine_y()``.

The function ``PointGFp::get_affine_x()`` operates as follows.

.. admonition:: ``PointGFp::get_affine_x()``

   **Input:**

   -  ``CurveGFp_Montgomery`` or ``CurveGFp_NIST``: elliptic curve
   -  ``[X,Y,Z]``: point in Jacobian projective coordinates

   **Ouput:**

   -  ``x``: affine ``x``-coordinate of the input point ``[X,Y,Z]``

   **Steps:**

   1. Verify that the input point is not on the line at infinity with the
      coordinates ``[0,Y,0]``. As the point at infinity has no representative
      in affine coordinates, terminate with respective error if a
      representative of the point at infinity is passed.
   2. If ``Z = 1``, the affine coordinate can be taken simply from the Jacobian
      coordinates. Return ``X``.
   3. Otherwise compute affine ``x`` coordinate as
      :math:`\frac{X}{Z^{2}}`.

The conversion function ``PointGFp::get_affine_y()`` performs the following steps.

.. admonition:: ``PointGFp::get_affine_y()``

   **Input:**

   -  ``CurveGFp_Montgomery`` or ``CurveGFp_NIST``: elliptic curve
   -  ``[X,Y,Z]``: point in Jacobian projective coordinates

   **Ouput:**

   -  ``y``: affine ``y``-coordinate of the input point ``[X,Y,Z]``

   **Steps:**

   1. Verify that the input point is not on the line at infinity with the
      coordinates ``[0,Y,0]``. As the point at infinity has no representative
      in affine coordinates, terminate with respective error if a
      representative of the point at infinity is passed.
   2. If ``Z = 1``, the affine coordinate can be taken simply from the Jacobian
      coordinates. Return ``Y``.
   3. Otherwise, compute affine ``y`` coordinate as
      :math:`\frac{Y}{Z^{3}}`.

**Conclusion:** Botan defines all the elliptic curve parameters
recommended in [TR-02102-1]_.
Note however that application developers need to take special care when using
custom curves. Botan's ``verify_group()`` implementation cannot guarantee that
the parameters of such curves are cryptographically strong.
