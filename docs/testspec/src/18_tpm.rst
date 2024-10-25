Trusted Platform Module Wrapper
===============================

Session Management
------------------

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TPM-session-1                                                           |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Create an unauthenticated session                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | The TPM 2.0 software emulator is running and provisioned properly       |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | - TCTI name and config                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | No created session reports an error or shows an invalid handle          |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create a TPM2 context                                                |
   |                        |                                                                         |
   |                        | #. Create an unauthenticated session with default symmetric algorithms  |
   |                        |                                                                         |
   |                        | #. Create an unauthenticated session with CFB(AES-128) and default hash |
   |                        |                                                                         |
   |                        | #. Create an unauthenticated session with CFB(AES-128) and SHA-384      |
   |                        |                                                                         |
   |                        | #. Create an unauthenticated session with CFB(AES-128) and SHA-1        |
   +------------------------+-------------------------------------------------------------------------+


.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TPM-session-2                                                           |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Create an authenticated session using the Storage Root Key              |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | The TPM 2.0 software emulator is running and provisioned properly       |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | - TCTI name and config                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | No created session reports an error or shows an invalid handle          |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create a TPM2 context                                                |
   |                        |                                                                         |
   |                        | #. Fetch the Storage Root Key (SRK) from the TPM2 context               |
   |                        |                                                                         |
   |                        | #. Create an authenticated session using the SRK with default           |
   |                        |    symmetric algorithms                                                 |
   |                        |                                                                         |
   |                        | #. Create an authenticated session using the SRK with CFB(AES-128) and  |
   |                        |    default hash                                                         |
   |                        |                                                                         |
   |                        | #. Create an authenticated session using the SRK with CFB(AES-128) and  |
   |                        |    SHA-384                                                              |
   |                        |                                                                         |
   |                        | #. Create an authenticated session using the SRK with CFB(AES-128) and  |
   |                        |    SHA-1                                                                |
   +------------------------+-------------------------------------------------------------------------+


.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TPM-session-3                                                           |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Create an authenticated session using a persistent ECC key              |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | The TPM 2.0 software emulator is running and provisioned properly       |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | - TCTI name and config                                                  |
   |                        | - persistent key ID of an ECC key                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | No created session reports an error or shows an invalid handle          |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create a TPM2 context                                                |
   |                        |                                                                         |
   |                        | #. Load the ECC key persisted under the given handle                    |
   |                        |                                                                         |
   |                        | #. Check that the key is loaded properly and has expected properties    |
   |                        |                                                                         |
   |                        | #. Create an authenticated session using the ECC key with default       |
   |                        |    symmetric algorithms                                                 |
   |                        |                                                                         |
   |                        | #. Create an authenticated session using the ECC key with CFB(AES-128)  |
   |                        |    and default hash                                                     |
   |                        |                                                                         |
   |                        | #. Create an authenticated session using the ECC key with CFB(AES-128)  |
   |                        |    and SHA-384                                                          |
   |                        |                                                                         |
   |                        | #. Create an authenticated session using the ECC key with CFB(AES-128)  |
   |                        |    and SHA-1                                                            |
   +------------------------+-------------------------------------------------------------------------+


Random Number Generator
-----------------------

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TPM-RNG-1                                                               |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Basic functional test of the TPM's Random Number Generator              |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | The TPM 2.0 software emulator is running and provisioned properly       |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | - TCTI name and config                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | n/a                                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create a TPM2 context                                                |
   |                        |                                                                         |
   |                        | #. Create a ``TPM2::RandomNumberGenerator`` object                      |
   |                        |                                                                         |
   |                        | #. Confirm that the RNG accepts application-provided entropy            |
   |                        |                                                                         |
   |                        | #. Confirm that the RNG reports to be seeded                            |
   |                        |                                                                         |
   |                        | #. Confirm that the RNG identifies itself as "TPM2_RNG"                 |
   |                        |                                                                         |
   |                        | #. Confirm that the ``clear()`` function does not report an error       |
   +------------------------+-------------------------------------------------------------------------+


.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TPM-RNG-2                                                               |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | The TPM's Random Number Generator produces random output                |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | The TPM 2.0 software emulator is running and provisioned properly       |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | - TCTI name and config                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | The TPM's RNG never produces an all-zero output                         |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create a TPM2 context                                                |
   |                        |                                                                         |
   |                        | #. Create a ``TPM2::RandomNumberGenerator`` object                      |
   |                        |                                                                         |
   |                        | #. Create a random buffer of 8 bytes                                    |
   |                        |                                                                         |
   |                        | #. Create a random buffer of 15 bytes                                   |
   |                        |                                                                         |
   |                        | #. Create a random buffer of 256 bytes                                  |
   +------------------------+-------------------------------------------------------------------------+


.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TPM-RNG-3                                                               |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | The TPM's RNG produces random output and consumes input entropy         |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | The TPM 2.0 software emulator is running and provisioned properly       |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | - TCTI name and config                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | The TPM's RNG never produces an all-zero output                         |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create a TPM2 context                                                |
   |                        |                                                                         |
   |                        | #. Create a ``TPM2::RandomNumberGenerator`` object                      |
   |                        |                                                                         |
   |                        | #. Create a random buffer of 8 bytes and pass 30 bytes of entropy       |
   |                        |                                                                         |
   |                        | #. Create a random buffer of 66 bytes and pass 64 bytes of entropy      |
   |                        |                                                                         |
   |                        | #. Create a random buffer of 256 bytes and pass 196 bytes of entropy    |
   +------------------------+-------------------------------------------------------------------------+


RSA
---

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TPM-RSA-1                                                               |
   +========================+=========================================================================+
   | **Type:**              | Positive/Negative Test                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Signing and Verification using RSA                                      |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | The TPM 2.0 software emulator is running and provisioned properly       |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | - TCTI name and config                                                  |
   |                        | - persistent key ID of an RSA key                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | n/a                                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create a TPM2 context and an unauthenticated session                 |
   |                        |                                                                         |
   |                        | #. Instantiate the passed persistent RSA key pair                       |
   |                        |                                                                         |
   |                        | #. Create a signature for a random message using the TPM                |
   |                        |                                                                         |
   |                        | #. Verify that the created signature is verifiable with Botan's         |
   |                        |    software implementation of RSA                                       |
   |                        |                                                                         |
   |                        | #. Verify that the created signatures is verifiable using the TPM       |
   |                        |                                                                         |
   |                        | #. Slightly alter the signed message                                    |
   |                        |                                                                         |
   |                        | #. Verify that the created signatures is not verifiable using the TPM   |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TPM-RSA-2                                                               |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Signing with the wrong authentication value (RSA)                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | The TPM 2.0 software emulator is running and provisioned properly       |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | - TCTI name and config                                                  |
   |                        | - persistent key ID of an RSA key                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | n/a                                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create a TPM2 context and an unauthenticated session                 |
   |                        |                                                                         |
   |                        | #. Instantiate the passed persistent RSA key pair using an incorrect    |
   |                        |    authentication value                                                 |
   |                        |                                                                         |
   |                        | #. Check that the signature creatino fail with a "TPM2 Error"           |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TPM-RSA-3                                                               |
   +========================+=========================================================================+
   | **Type:**              | Positive/Negative Test                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encryption/Decryption of a message using RSA                            |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | The TPM 2.0 software emulator is running and provisioned properly       |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | - TCTI name and config                                                  |
   |                        | - persistent key ID of an RSA key                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | n/a                                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create a TPM2 context and an unauthenticated session                 |
   |                        |                                                                         |
   |                        | #. Instantiate the passed persistent RSA key pair using an incorrect    |
   |                        |    authentication value                                                 |
   |                        |                                                                         |
   |                        | #. Encrypt the plaintext message "feedc0debaadcafe" using RSA-OAEP      |
   |                        |    on the TPM                                                           |
   |                        |                                                                         |
   |                        | #. Decrypt the ciphertext using RSA-OAEP on the TPM                     |
   |                        |                                                                         |
   |                        | #. Check that the plaintext and the decrypted ciphertext match          |
   |                        |                                                                         |
   |                        | #. Encrypt the plaintext message "feedface" using RSA-OAEP in software  |
   |                        |                                                                         |
   |                        | #. Decrypt the ciphertext using RSA-OAEP on the TPM                     |
   |                        |                                                                         |
   |                        | #. Slightly alter the ciphertext                                        |
   |                        |                                                                         |
   |                        | #. Decrypt the ciphertext using RSA-OAEP on the TPM and expext it to    |
   |                        |    fail due to a padding failure.                                       |
   +------------------------+-------------------------------------------------------------------------+


.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TPM-RSA-4                                                               |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Create a Key Pair, Use it, Make it Persistent, Evict it                 |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | The TPM 2.0 software emulator is running and provisioned properly       |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | - TCTI name and config                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | n/a                                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create a TPM2 context and an authenticated session via the Storage   |
   |                        |    Root Key                                                             |
   |                        |                                                                         |
   |                        | #. Create a transient unrestricted key with the auth_value "secret" and |
   |                        |    a bit length of 2048                                                 |
   |                        |                                                                         |
   |                        | #. Encrypt the plaintext message "feedc0debaadcafe" using RSA-OAEP      |
   |                        |    via Botan's software RSA implementation                              |
   |                        |                                                                         |
   |                        | #. Decrypt the ciphertext using RSA-OAEP on the TPM                     |
   |                        |                                                                         |
   |                        | #. Encrypt the plaintext message "feedc0debaadcafe" using RSA-PKCSv1.5  |
   |                        |    via Botan's software RSA implementation                              |
   |                        |                                                                         |
   |                        | #. Decrypt the ciphertext using RSA-RSA-PKCSv1.5 on the TPM             |
   |                        |                                                                         |
   |                        | #. Check that the (encrypted) private blob of the key is exportable     |
   |                        |                                                                         |
   |                        | #. Destruct the key object and load it again from the encrypted private |
   |                        |    blob                                                                 |
   |                        |                                                                         |
   |                        | #. Sign a message with the TPM and check that it can be validated with  |
   |                        |    both the TPM and Botan's RSA software implementation                 |
   |                        |                                                                         |
   |                        | #. Make the key persistent in the TPM under a free key slot             |
   |                        |                                                                         |
   |                        | #. Ensure that no other key can be persistent in the same key slot on   |
   |                        |    the TPM                                                              |
   |                        |                                                                         |
   |                        | #. Sign a message with the TPM and check that it can be validated with  |
   |                        |    Botan's RSA software implementation                                  |
   |                        |                                                                         |
   |                        | #. Evict the key and make sure that the previously occupied key slot    |
   |                        |    is available again                                                   |
   +------------------------+-------------------------------------------------------------------------+


ECDSA
-----

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TPM-ECDSA-1                                                             |
   +========================+=========================================================================+
   | **Type:**              | Positive/Negative Test                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Signing and Verification using ECDSA                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | The TPM 2.0 software emulator is running and provisioned properly       |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | - TCTI name and config                                                  |
   |                        | - persistent key ID of an ECDSA key                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | n/a                                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create a TPM2 context and an unauthenticated session                 |
   |                        |                                                                         |
   |                        | #. Instantiate the passed persistent ECDSA key pair                     |
   |                        |                                                                         |
   |                        | #. Create a signature for a random message using the TPM                |
   |                        |                                                                         |
   |                        | #. Verify that the created signature is verifiable with Botan's         |
   |                        |    software implementation of ECDSA                                     |
   |                        |                                                                         |
   |                        | #. Verify that the created signatures is verifiable using the TPM       |
   |                        |                                                                         |
   |                        | #. Slightly alter the signed message                                    |
   |                        |                                                                         |
   |                        | #. Verify that the created signatures is not verifiable using the TPM   |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TPM-ECDSA-2                                                             |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Signing with the wrong authentication value (ECDSA)                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | The TPM 2.0 software emulator is running and provisioned properly       |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | - TCTI name and config                                                  |
   |                        | - persistent key ID of an ECDSA key                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | n/a                                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create a TPM2 context and an unauthenticated session                 |
   |                        |                                                                         |
   |                        | #. Instantiate the passed persistent ECDSA key pair using an incorrect  |
   |                        |    authentication value                                                 |
   |                        |                                                                         |
   |                        | #. Check that the signature creatino fail with a "TPM2 Error"           |
   +------------------------+-------------------------------------------------------------------------+


.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | TPM-ECDSA-3                                                             |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Create a Key Pair, Use it, Make it Persistent, Evict it                 |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | The TPM 2.0 software emulator is running and provisioned properly       |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | - TCTI name and config                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | n/a                                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create a TPM2 context and an authenticated session via the Storage   |
   |                        |    Root Key                                                             |
   |                        |                                                                         |
   |                        | #. Create a transient unrestricted key with the auth_value "secret" and |
   |                        |    the elliptic curve "secp521r1"                                       |
   |                        |                                                                         |
   |                        | #. Sign a random message using the new private key on the TPM           |
   |                        |                                                                         |
   |                        | #. Verify the signature with Botan ECDSA software implementation        |
   |                        |                                                                         |
   |                        | #. Check that the (encrypted) private blob of the key is exportable     |
   |                        |                                                                         |
   |                        | #. Destruct the key object and load it again from the encrypted private |
   |                        |    blob                                                                 |
   |                        |                                                                         |
   |                        | #. Sign a message with the TPM and check that it can be validated with  |
   |                        |    both the TPM and Botan's ECDSA software implementation               |
   |                        |                                                                         |
   |                        | #. Make the key persistent in the TPM under a free key slot             |
   |                        |                                                                         |
   |                        | #. Ensure that no other key can be persistent in the same key slot on   |
   |                        |    the TPM                                                              |
   |                        |                                                                         |
   |                        | #. Sign a message with the TPM and check that it can be validated with  |
   |                        |    Botan's ECDSA software implementation                                |
   |                        |                                                                         |
   |                        | #. Evict the key and make sure that the previously occupied key slot    |
   |                        |    is available again                                                   |
   +------------------------+-------------------------------------------------------------------------+
