Introduction
============

This document specifies test cases implemented in the test suite.

It covers AEAD modes, block ciphers, hash functions, public key-based key
agreement schemes, key derivation functions, message authentication codes, block
cipher modes of operation, password-based key derivation functions, PKCS#11,
public key signature schemes, random number generation, TLS and X.509 tests.

All tests are implemented in the src/tests directory. Test vectors are located
in src/tests/data.

Tests of the TLS configuration using external tools such as TLS Attacker and
side channel tests are not covered by this document.
