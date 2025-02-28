Introduction
============

This audit report summarizes the review results of changes to the Botan library code
base between the tagged releases |botan_git_base_ref| and |botan_version|.
They were examined by considering the BSI technical guidelines' recommendations.
In the meantime, the development of Botan continues, e.g., new algorithms are added, or bugs are fixed.
Rohde & Schwarz Cybersecurity is part of this maintenance process as a contractor for this project.

Before switching to a new Botan version as part of the maintenance, all official and possibly hidden
changes to the code must be thoroughly checked. For this purpose, each reviewed version comes with an
audit report prepared by the contractor and submitted to the BSI with the source code.
This examination applies, in particular, to cryptography-related changes. The BSI needs a well-founded decision
basis for recommending a new Botan version. [PRM]_ describes the audit method that differs from the previous one.

This document contains the audit report of the changes between the Botan versions |botan_git_base_ref| and
|botan_version|. Evaluated are the changes to relevant parts of the source code, the results of the side-channel
analysis for Botan |botan_version|, and a list of updated documents.


Review Method
-------------

This document captures all changes to the library that led from a defined base
revision to the target revision of this review. To do this efficiently, we base
our review on the Git history between those revisions.

Botan is developed publicly on GitHub; hence, we take all individual pull
requests in the code base between the two revisions as the changeset
granularity. Additionally, all commits added by the maintainer straight to the
*master* branch are considered changesets to be reviewed. We refer to these
"atomic changesets" as *patches* in the remainder of this document.

For each patch, the influence on the library's security guarantees is determined
first. An in-depth review of the patch followed if the patch is considered
relevant and touches parts of the code base that are in scope for this review.
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
``src/build-data``), and documentation (in ``src/doc``).

The review in this document keeps track of changes in all the above-mentioned
components. For the library implementation itself (``src/lib``), all modules
that are *required* or *available* in the BSI build policy and their
dependencies are in the scope of this document. Additionally, we review the
following modules and its dependencies: ``certstor_flatfile``,
``certstor_system``, ``ml_dsa``, ``ffi``, ``frodokem``, ``frodokem_aes``,
``hss_lms``, ``jitter_rng``, ``kmac``, ``ml_kem``, ``pcurves_brainpool256r1``,
``pcurves_brainpool384r1``, ``pcurves_brainpool512r1``, ``pcurves_secp256r1``,
``pcurves_secp256k1``, ``pcurves_secp384r1``, ``pcurves_secp521r1``, ``pkcs11``,
``shake``, ``slh_dsa_sha2``, ``slh_dsa_shake``, ``tls_cbc``, ``tls12``,
``tls13_pqc``, ``tls13``, ``tpm2``, ``tpm2_crypto_backend``, ``tpm2_rsa``,
``tpm2_ecc``, ``xts``. Patches that don't alter any of the above-mentioned
components or relevant modules are considered out-of-scope.

Below is the full list of modules (from ``src/lib``) whose changes were
reviewed:

.. todo:: Update the module list below for the upcoming release

.. For each new document version, the list below should be sanity checked
   and potentially adapted using the script in scripts/audited_modules_list.py
   like so:

     1. Update the list of additional and platform dependent modules in
        the audited_modules_list.py script
     2. Check out the to-be-audited version of Botan "somewhere"
     3. poetry run python audited_modules_list.py --repo-location="somewhere"
     4. Copy the script's output over the list below
     5. Go through the `git diff` and sanity check
     6. Update the enumeration of "additional modules" above with the
        modules listed in the script.
     7. Adapt the paragraph under the enumeration of audited modules
        to reflect notable changes.

.. list-table::

   * - aead
     - aes
     - aes_armv8
     - aes_ni
   * - aes_power8
     - aes_vaes
     - aes_vperm
     - argon2
   * - argon2_avx2
     - argon2_ssse3
     - argon2fmt
     - asn1
   * - auto_rng
     - base
     - base64
     - bigint
   * - blake2
     - block
     - cbc
     - ccm
   * - certstor_flatfile
     - certstor_sql
     - certstor_sqlite3
     - certstor_system
   * - certstor_system_macos
     - certstor_system_windows
     - cmac
     - cpuid
   * - cshake_xof
     - ctr
     - dh
     - dilithium_common
   * - dilithium_shake
     - dl_algo
     - dl_group
     - dsa
   * - dyn_load
     - ec_group
     - ecc_key
     - ecdh
   * - ecdsa
     - ecgdsa
     - ecies
     - eckcdsa
   * - eme_oaep
     - eme_pkcs1
     - eme_raw
     - emsa_pkcs1
   * - emsa_pssr
     - entropy
     - ffi
     - frodokem
   * - frodokem_aes
     - frodokem_common
     - gcm
     - getentropy
   * - ghash
     - ghash_cpu
     - ghash_vperm
     - gmac
   * - hash
     - hash_id
     - hex
     - hkdf
   * - hmac
     - hmac_drbg
     - hss_lms
     - http_util
   * - iso9796
     - jitter_rng
     - kdf
     - kdf1_iso18033
   * - keccak_perm
     - keccak_perm_bmi2
     - keypair
     - kmac
   * - kyber_common
     - locking_allocator
     - mac
     - mdx_hash
   * - mem_pool
     - mgf1
     - ml_dsa
     - ml_kem
   * - mode_pad
     - modes
     - mp
     - numbertheory
   * - pbkdf
     - pcurves
     - pem
     - pk_pad
   * - pkcs11
     - poly_dbl
     - pqcrystals
     - prf_tls
   * - processor_rng
     - pubkey
     - rdseed
     - rng
   * - rsa
     - sha1
     - sha1_armv8
     - sha1_sse2
   * - sha1_x86
     - sha2_32
     - sha2_32_armv8
     - sha2_32_bmi2
   * - sha2_32_x86
     - sha2_64
     - sha2_64_armv8
     - sha2_64_bmi2
   * - sha3
     - shake
     - shake_xof
     - simd
   * - slh_dsa_sha2
     - slh_dsa_shake
     - socket
     - sp800_108
   * - sp800_56c
     - sphincsplus_common
     - sphincsplus_sha2_base
     - sphincsplus_shake_base
   * - stateful_rng
     - stream
     - system_rng
     - tls
   * - tls12
     - tls13
     - tls13_pqc
     - tls_cbc
   * - tpm2
     - tpm2_crypto_backend
     - tpm2_ecc
     - tpm2_rsa
   * - tree_hash
     - trunc_hash
     - utils
     - x509
   * - xmss
     - xof
     - xts
     -

Here are some notable module changes compared to the last review (Botan |botan_git_base_ref|):

.. todo:: Update this section for each new version of the document.

Patch Description Content
-------------------------

The changes for this document's review iteration for all relevant topics are found in :ref:`changes`.
Patches are sorted in a semantically meaningful way by assigning each one to a sensible topic.
Each topic provides a brief description and lists the authors for the contained patches.
Afterward, an extensive table with all related patches is provided.

The table contains the pull request IDs on GitHub or individual commit hashes of the reviewed patches with a link to GitHub.
For reference, a brief description or title of the patch is provided. Note that
this description is usually just a summary and might not cover all patch changes in detail. Most
pull requests and commits feature a sufficient description on GitHub that is not repeated in this document.
Also, each patch within the table is assigned a security category, and information about the approvers
and auditors is given.


Security Categories
~~~~~~~~~~~~~~~~~~~

For this audit, four security categories are distinguished. The category *critical* labels patches
that apply substantial changes to cryptographic functionality, e.g., implementing a new algorithm
or updating an old one to a new standard. Patches labeled as *relevant* are changes to cryptographic
algorithms without altering the algorithm's observable behavior. Mostly, this category contains
optimizations or refactoring of cryptographic modules. All changes with no direct effect on
cryptographic operations are categorized as *info*. The *out of scope* category identifies patches
that only affect modules not in this review's scope. Patches of the last type are not reviewed
in detail.


Approvals and Auditors
~~~~~~~~~~~~~~~~~~~~~~

The audit process is based on two requirements:

* **The four-eye principle:** At least two individuals must inspect each patch
* **Audit quality:** At least one of the inspectors must be involved in this audit process.

Therefore, pull requests that were either authored or reviewed on GitHub by one
of the members of this audit project do not require an additional in-depth
review for this particular audit process. Other patches are evaluated and
reviewed by an auditor retrospectively, with the results stated
in this document. The distinction between "approvers" (of pull requests on
GitHub) and "auditors" (in retrospect, explicitly for this project) is visualized
by setting the latter into parenthesis in the patch tables below.

Auditing members of this project and their GitHub handles are: |auditors_list|
