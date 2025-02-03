Literature Overview of Side-Channel Analysis for the Implemented PQC-Schemes
============================================================================

Introduction
------------

This chapter contains a short literature review for side-channel analysis for post-quantum cryptography (PQC) algorithms that will be implemented in the crypto libray Botan.
Since the implementations and their scope in the P481 project are only software-based, we will focus the literature review mainly on timing and cache side-channel attacks (SCAs).

Classic McEliece
----------------

Classic McEliece is a code-based key encapsulation mechanism (KEM) submitted to the NIST PQC competition.
The hardness relies on the ability to decode a binary Goppa code, a type of error-correcting code.
A public key consists of a random binary Goppa code and a ciphertext is a codeword xor-ed with some random error $e$.
Code-based cryptosystems were introduced by Robert J. McEliece in 1978 [McE78].
Against unprotected implementations of McEliece, there are multiple timing-based side-channel attacks.
See, for example, the attacks in [AHP+11;BCD+16;COT17;STM+08;Str10], targeting different parts of the scheme. In particular, [BCM+23] discovers timing side channels in the deprecated McEliece implementation in Botan.

The implementations of Classic McEliece to the NIST PQC competition are designed "to avoid all data flow from secrets to timing" [ABC+22] and mitigate the attacks listed above.
The Classic McEliece specification [ABC+22] contains guidelines for secure implementations of the scheme.
Encapsulation and decapsulation are especially prone to timing leakage. The side channel analysis of [BCM+23] regarding Classic McEliece only considers a physical attack surface.
One has to be careful when handling the error vector $e$, either when writing the value of $e$ into RAM, or during matrix-vector multiplications of $e$.
Hence, all bits of secret data should be processed uniformly, regardless of their value.

ML-KEM
------

ML-KEM (formerly Kyber) is a key-encapsulation mechanism (KEM) based on the learning with errors problem in module lattices (MLWE problem).
ML-KEM is designed to be resistant against timing-based and cache-based side-channel attacks [ABD+20b].
For this, neither the reference implementations nor the optimized implementations use branching depending on the secret key or table lookups at source code level.

Nonetheless, Bernstein et al. [BBB] discovered multiple timing vulnerabilities (called KyberSlash1 and KyberSlash2) that are introduced by compilers during code optimization.
Compilers often optimize division operations by transforming them into much faster multiplication operations.
The KyberSlash attacks use the fact that the division by the ML-KEM-constant KYBER_Q uses the C-language division operator.
This division is compiled into an instruction that is not constant-time and is used to recover the secret key.
This attack is mitigated in Botan version 3.3 and is done by manually changing the critical division into multiple, smaller operations that are constant-time.
The new set of operations is constructed so that a compiler will not create code with variable execution time.

An overview of side-channel attacks on ML-DSA and ML-KEM based on power and electromagnetic radiation can be found in [RCD+24].

FrodoKEM
--------

FrodoKEM [ABD+20a] is a key encapsulation mechanism (KEM) whose security is based on the learning with errors problem (LWE).
Unlike ML-KEM and ML-DSA, the underlying LWE problem of FrodoKEM is based on generic, algebraically unstructured lattices.
The structured variants of the LWE problem are more compact and computationally efficient, but can also lead to additional attacks exploiting the extra structure.
In general FrodoKEM is designed to be easy to implement and yields implementations that are compact and execute in constant time.

Nevertheless, one has to be careful while implementing FrodoKEM.
Guo et al. [GJN20] demonstrated a key-recovery timing attack targeting FrodoKEM's implementation of the Fujisaki-Okamoto transformation in the Round 2 submission to the NIST PQC competition.
Their attack exploits timing variations in the rejection sampling step of the KEM decapsulation process.
The attack can be mitigated by implementing comparisons in the decapsulation that run in constant time and do not terminate early.
The Round 3 submission of FrodoKEM mitigates this attack.

ML-DSA
------

ML-DSA [Nat24a] (formerly Dilithium [BDK+20]) is a digital signature scheme based on the module learning-with-errors (MLWE problem) problem and the module short integer solution (MSIS problem) problem.
ML-DSA is designed to be executed in constant time.
The specification states that polynomial multiplications, rounding, and other critical operations are "easily implemented in constant time" to prevent timing side-channels.
This includes, for example, the use of the C-language "\%" operator.
Instead, ML-DSA uses Montgomery reductions that are constant time.
Additionally, in order to avoid side-channel attacks from the generation of randomness, ML-DSA uses only uniform sampling instead of Gaussian sampling.

An overview of side-channel attacks on ML-DSA and ML-KEM based on power and electromagnetic radiation can be found in [RCD+24].

SLH-DSA
-------

SLH-DSA [Nat24b] (formerly SPHINCS+ [ABB+20]) is a stateless hash-based digital signature scheme.
The security of SLH-DSA is based on the properties of the used hash function.
SLH-DSA is based on the stateful hash signature scheme eXtended Merkle Signature Scheme (XMSS) [HBG+18], but works with larger keys and signatures to eliminate the state.
Additionally, a few-time signature scheme, forest of random subsets (FORS), is used.
The resistance of SLH-DSA (and other hash-based signature schemes such as XMSS and LMS) against time- and cache-based SCA is mainly based on the underlying used hash function.
The submitted reference-implementations of SLH-DSA are naturally free of secret-dependent branching or cache-accesses.
One must be careful to use side-channel resistant hash functions:
The former SPHINCS+ specification lists a variant that uses the Haraka hash function, which is based on AES instructions.
Pure software-based implementations of Haraka/AES can lead to timing leakage.
Hence, SPHINCS+ with Haraka should only be used if AES-hardware support is available.

FIPS 205 lists only SHAKE and SHA2 as possible instantiations for SLH-DSA, which allow for constant-time software implementations.

