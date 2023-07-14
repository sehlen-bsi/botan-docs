Introduction
============

Botan version 3.0.0-alpha1 is the latest available version, with a special recommendation by the BSI.
It was examined by considering the BSI technical guidelines' recommendations.
In the meantime, the development of Botan continues, e.g., new algorithms are added, or bugs are fixed.
Rohde & Schwarz Cybersecurity is part of this maintenance process as a contractor for this project.

Before switching to a new Botan version as part of the maintenance, all official and possibly hidden
changes to the code must be thoroughly checked. For this purpose, each recommended version comes with an
audit report prepared by the contractor and submitted to the BSI with the source code.
This examination applies, in particular, to cryptography-related changes. The BSI needs a well-founded decision
basis for recommending a new Botan version. [TODO: Reference] describes the audit method that differs from the previous one.

This document contains the audit report of the changes between the Botan versions 3.0.0-alpha1 and
3.1.1. Evaluated are the changes to relevant parts of the source code, the results of the side-channel
analysis for Botan 3.1.1, and a list of updated documents.


Review Method
-------------

The method for this audit differs from the processes of the previous audit.
[TODO: Reference] describes the audit method in detail. The following gives
a summary of the new audit method.

This document aims at capturing all changes to the library that led from a
defined base revision of version 3.0.0-alpha1 to the target revision of this
review. To do this efficiently, we base our review on the Git history between
those revisions.

Botan is developed publicly on GitHub; hence, we take all individual pull
requests that landed in the code base between the two revisions as the changeset
granularity. Additionally, all commits added by the maintainer straight to the
*master* branch are considered changesets to be reviewed. We refer to these
"atomic changesets" as *patches* in the remainder of this document.

For each patch, the influence on the library's security guarantees was determined
first. An in-depth review of the patch followed if the patch was considered
relevant and touched parts of the code base that are in scope for this review.
This document lists *all* patches along with links to their representation on
GitHub, our classification, and optionally noteworthy remarks from the
in-depth review.


Scope of the Review
-------------------

The library's code repository is structured into fine-grained modules
(sub-directories in ``src/lib``). Additionally, the repository contains various
unit and integration tests (in ``src/tests``, ``src/bogo_shim``,
``src/fuzzer``), a command line interface (in ``src/cli``), python wrapper (in
``src/python``), build system-related files and scripts (in ``configure.py``,
``src/build-data``) and documentation (in ``src/doc``).

The review in this document keeps track of changes in all the above-mentioned
components. For the library implementation itself (``src/lib``), all modules that
are *required* or *available* in the BSI build policy, and their dependencies are
in the scope of this document. Additionally, we review the following modules and
its dependencies: `getentropy`, `ffi`, `xts`, `pkcs11`, `tls12`, `tls13`,
`tls_cbc`, `x509`, `certstor_windows`, `certstor_macos`, `certstor_flatfile`,
`certstor_sql`, `certstor_sqlite3`, `certstor_system_macos`, `certstor_system_windows`,
`dilithium`, `dilithium_aes`, `dilithium_common`,
`kyber`, `kyber_90s`, `kyber_common`,
`sha1_armv8`, `sha1_sse2`, `sha1_x86`,
`sphincsplus_common`, `sphincsplus_sha2`, `sphincsplus_shake`.
Patches that don't alter any of the above-mentioned components or relevant
modules are considered out-of-scope.

Below is the full list of modules (from ``src/lib``) whose changes were
reviewed:

.. list-table::

   * - aead
     - aes
     - aes_armv8
     - aes_ni
     - aes_power8
   * - aes_vperm
     - argon2
     - argon2_avx2
     - argon2_ssse3
     - argon2fmt
   * - asn1
     - auto_rng
     - base
     - base64
     - bigint
   * - blake2
     - block
     - cbc
     - ccm
     - certstor
   * - certstor_flatfile
     - certstor_macos
     - certstor_sql
     - certstor_sqlite3
     - certstor_system
   * - certstor_system_macos
     - certstor_system_windows
     - certstor_windows
     - cmac
     - cpuid
   * - ctr
     - dh
     - dilithium
     - dilithium_aes
     - dilithium_common
   * - dl_algo
     - dl_group
     - dlies
     - dsa
     - dyn_load
   * - ec_group
     - ecc_key
     - ecdh
     - ecdsa
     - ecgdsa
   * - ecies
     - eckcdsa
     - eme_oaep
     - eme_pkcs1
     - emsa_pkcs1
   * - emsa_pssr
     - entropy
     - ffi
     - gcm
     - getentropy
   * - ghash
     - ghash_cpu
     - ghash_vperm
     - gmac
     - hash
   * - hash_id
     - hex
     - hkdf
     - hmac
     - hmac_drbg
   * - http_util
     - iso9796
     - kdf
     - kdf1_iso18033
     - keypair
   * - kyber
     - kyber_90s
     - kyber_common
     - locking_allocator
     - mac
   * - mdx_hash
     - mem_pool
     - mgf1
     - mode_pad
     - modes
   * - mp
     - numbertheory
     - pbkdf
     - pem
     - pk_pad
   * - pkcs11
     - poly_dbl
     - prf_tls
     - processor_rng
     - pubkey
   * - rdseed
     - rng
     - rsa
     - sha1
     - sha1_armv8
   * - sha1_sse2
     - sha1_x86
     - sha2_32
     - sha2_32_armv8
     - sha2_32_bmi2
   * - sha2_32_x86
     - sha2_64
     - sha2_64_bmi2
     - sha3
     - sha3_bmi2
   * - shake
     - shake_cipher
     - simd
     - socket
     - sp800_108
   * - sp800_56c
     - sphincsplus_common
     - sphincsplus_sha2
     - sphincsplus_shake
     - stateful_rng
   * - stream
     - system_rng
     - thread_utils
     - tls
     - tls_cbc
   * - tls12
     - tls13
     - trunc_hash
     - utils
     - win32_stats
   * - x509
     - xmss
     - xts
     -
     -

The following previously existing modules are now in scope
and were fully reviewed:

- argon2, argon2_avx2, argon2_ssse3
- blake2
- hkdf
- shake


Patch Description Content
-------------------------

Chapter 4 shows the changes for this document's review iteration for all topics in scope.
Patches are sorted in a semantically meaningful way by assigning each one to a sensible topic.
Each topic provides a brief description and lists the authors for the contained patches.
Afterward, an extensive table with all related patches is provided.

The table contains the pull request ids or commit hashes of the reviewed patches with a GitHub link.
For orientation, a brief description of the patch is given. Note that
this description is only on a summary level and does not cover all patch changes in detail. Most
pull requests and commits are sufficiently described at the provided GitHub link.
Also, each patch within the table is assigned a security category, and information about the approvers
and auditors is given.


Security Categories
~~~~~~~~~~~~~~~~~~~

For this audit, four security categories are distinguished. The category *critical* labels patches
that apply breaking changes to cryptographic functionality, e.g., implementing a new algorithm
or updating an old one to a new standard. Patches labeled as *relevant* are changes to cryptographic
algorithms without breaking the algorithm's specification. Mostly, this category contains
optimizations or major refactoring of cryptographic modules. All changes with no direct effect on
cryptographic operations are categorized as *info*. The *out of scope* category identifies patches
that only affect modules not in this review's scope. Patches of the last type are not reviewed
in detail.


Approvals and Auditors
~~~~~~~~~~~~~~~~~~~~~~

The audit process is based on two requirements. The first one is the four-eye principle, i.e., at least two individuals must vision each patch. In the best-case scenario, this is the author and a separate approver
who performs an in-depth review. The second principle requires that at least one of the two participants
must be involved in this audit process so that we can guarantee that the review meets the desired
quality standard.

If a patch has no participating approver, the patch is visioned in a later review by an auditor. The patch table lists this auditor in brackets, while real approvers are listed without them.
Note that authors can edit pull requests after approval. Therefore, auditors vision additional changes after
approval for this audit.

