Changes Overview
================

Regarding post-quantum cryptography, the most important changes since the last
audit are the addition of CRYSTALS Dilithium and the SPHINCS+ signature
algorithms. The crypto documentation [CRYPD]_ describes Botan's
implementation of these algorithms. Dilithium is added within the modules
`dilithium` and `dilithium_aes` for the modern and AES variant, respectively.
For SPHINCS+ the modules `sphincsplus_sha2` and `sphincsplus_shake` are added
for the respective hash instantiation. Both algorithms depend on SHAKE;
therefore, the module `shake` is added for review.

Another important area in this iteration is TLS 1.3. Most notably, TLS support
for versions below 1.2 is discontinued, while the TLS 1.3 implementation is
expanded. For this, the module `tls` of the last version is split into two
modules, `tls12` and `tls13`. Since TLS 1.3 uses the HKDF for its key
derivation, the module `hkdf` is added to the audit of this iteration.

Next, some algorithms were included in the list of modules relevant to this
project. For once, there is the password hashing scheme Argon2, also with
support for AVX2 and SSSE3. The modules `argon2`, `argon2_avx2`, and
`argon2_ssse3` contain the default software implementation and hardware
optimizations. Since Argon2 is based on the Blake2 hash algorithm, the module
`blake2` is also reviewed and added to the new BSI policy.

Also, the EMSA1 padding is no longer supported, so the `emsa1` module is
removed. The NewHope KEM is also no longer supported, removing `newhope`. The
`kyber_common` module is now marked as internal, so it can no longer be built
without one of `kyber` or `kyber_90s`.

The following chapter provides a more in-depth overview of the most recent
changes.
