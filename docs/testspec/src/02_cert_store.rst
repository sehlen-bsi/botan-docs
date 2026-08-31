Certificate Stores
==================

SQLite Certificate Store
------------------------

The Certificate Store SQLite interface is tested using unit tests that (1) insert, search and remove certificates and keys, (2) revokes certificates and (3) looks up subjects in the store. All the tests are implemented in :srcref:`src/tests/test_certstor.cpp`.

Insert, Search and Remove
~~~~~~~~~~~~~~~~~~~~~~~~~

These unit tests search and remove certificates and private keys stored in the store. The tests are executed with the following constraints:

    - Number of test cases: 6
    - Cert: X.509v3
    - Key: RSA, 2048 bits

The following table shows an example test case with one test vector. All test vectors are listed in :srcref:`src/tests/data/x509/certstor/`.

.. table::
   :class: longtable
   :widths: 20 80

   +---------------------+----------------------------------------------------------------------------+
   | **Test Case No.:**  | CERTSTOR-ISR-1                                                             |
   +---------------------+----------------------------------------------------------------------------+
   | **Type:**           | Positive Test                                                              |
   +---------------------+----------------------------------------------------------------------------+
   | **Description:**    | Look up and remove certificates and key in the store                       |
   +---------------------+----------------------------------------------------------------------------+
   | **Preconditions:**  | None                                                                       |
   +---------------------+----------------------------------------------------------------------------+
   | **Input Values:**   | -  Cert: Certificate stored in the store                                   |
   |                     |                                                                            |
   |                     | -  Key: Corresponding private key to Cert                                  |
   +---------------------+----------------------------------------------------------------------------+
   | **Expected          | None                                                                       |
   | Output:**           |                                                                            |
   +---------------------+----------------------------------------------------------------------------+
   | **Steps:**          | #. Look up *Cert* by subject DN                                            |
   |                     |                                                                            |
   |                     | #. Look up *Cert* by subject DN and subject key ID                         |
   |                     |                                                                            |
   |                     | #. Look up *Key* by *Cert*                                                 |
   |                     |                                                                            |
   |                     | #. Look up Cert by Key                                                     |
   |                     |                                                                            |
   |                     | #. Remove Cert from the store                                              |
   |                     |                                                                            |
   |                     | #. Look up Cert by subject DN and subject key ID                           |
   |                     |                                                                            |
   |                     | #. Remove Key from the store                                               |
   |                     |                                                                            |
   |                     | #. Look up Key by Cert                                                     |
   +---------------------+----------------------------------------------------------------------------+

Revocation
~~~~~~~~~~

These unit tests revoke certificates and generate a CRL on certificates stored in the store. The tests are executed with the following constraints:

    - Number of test cases: 1
    - Cert: X.509v3
    - Key: RSA, 2048 bits

The following table shows an example test case with one test vector. All test vectors are listed in :srcref:`src/tests/data/x509/certstor/`.

.. table::
   :class: longtable
   :widths: 20 80

   +---------------------+----------------------------------------------------------------------------+
   | **Test Case No.:**  | CERTSTOR-REV-1                                                             |
   +---------------------+----------------------------------------------------------------------------+
   | **Type:**           | Positive Test                                                              |
   +---------------------+----------------------------------------------------------------------------+
   | **Description:**    | Revoke certificate and generate a CRL                                      |
   +---------------------+----------------------------------------------------------------------------+
   | **Preconditions:**  | None                                                                       |
   +---------------------+----------------------------------------------------------------------------+
   | **Input Values:**   | -  Certs: Certificates stored in the store                                 |
   |                     | -  Keys: Corresponding private keys to Certs                               |
   +---------------------+----------------------------------------------------------------------------+
   | **Expected Output:**| None                                                                       |
   +---------------------+----------------------------------------------------------------------------+
   | **Steps:**          | #. Revoke *Certs[0]* with reason *CA Compromise*                           |
   |                     |                                                                            |
   |                     | #. Revoke *Certs[3]* with reason *CA Compromise*                           |
   |                     |                                                                            |
   |                     | #. Generate CRLs                                                           |
   |                     |                                                                            |
   |                     | #. Check that *Certs[0]* and *Certs[3]* are revoked                        |
   |                     |                                                                            |
   |                     | #. Reverse the revocation of *Cert[3]*                                     |
   |                     |                                                                            |
   |                     | #. Check that *Certs[0]* is still revoked                                  |
   |                     |                                                                            |
   |                     | #. Look up CRL for *Cert[0]*                                               |
   |                     |                                                                            |
   |                     | #. Check that no CRL exists for *Cert[3]*                                  |
   +---------------------+----------------------------------------------------------------------------+


Subject DN Listing
~~~~~~~~~~~~~~~~~~

These unit tests test retrieval of subject DNs of all certificates stored in the store. The tests are executed with the following constraints:

    - Number of test cases: 1
    - Cert: X.509v3

The following table shows an example test case with one test vector. All test vectors are listed in :srcref:`src/tests/data/x509/certstor/`.

.. table::
   :class: longtable
   :widths: 20 80

   +----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**   | CERTSTOR-SDN-1                                                           |
   +----------------------+--------------------------------------------------------------------------+
   | **Type:**            | Positive Test                                                            |
   +----------------------+--------------------------------------------------------------------------+
   | **Description:**     | List subject DNs of all certificates                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**   | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Input Values:**    | -  Certs: Certificates stored in the store                               |
   +----------------------+--------------------------------------------------------------------------+
   | **Expected Output:** | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Steps:**           | #. List the distinguished names of all certificates in the certificate   |
   |                      |    store and compare each subject DN with the subject DN from *Certs*    |
   +----------------------+--------------------------------------------------------------------------+


Finding all Certificates
~~~~~~~~~~~~~~~~~~~~~~~~

These unit tests test search of certificates matching a given subject DN and Subject Key Identifier, including the case of multiple certificates sharing the same subject DN. The tests are executed with the following constraints:

    - Number of test cases: 1
    - Cert: X.509v3

The following table shows an example test case with one test vector. All test vectors are listed in :srcref:`src/tests/data/x509/certstor/`.

.. table::
   :class: longtable
   :widths: 20 80

   +----------------------+----------------------------------------------------------------------------------+
   | **Test Case No.:**   | CERTSTOR-FAC-1                                                                   |
   +----------------------+----------------------------------------------------------------------------------+
   | **Type:**            | Positive Test                                                                    |
   +----------------------+----------------------------------------------------------------------------------+
   | **Description:**     | Look up certificates matching given subject DN and the Subject Key Identifier    |
   +----------------------+----------------------------------------------------------------------------------+
   | **Preconditions:**   | None                                                                             |
   +----------------------+----------------------------------------------------------------------------------+
   | **Input Values:**    | -  Certs: Certificates stored in the store                                       |
   |                      |                                                                                  |
   |                      | -  SameDNCerts: Two certificates sharing the same subject DN                     |
   |                      |    (*common_14_sub_ca.ca.pem.crt* and *common_14_wrong_sub_ca.ca.pem.crt*        |
   |                      |    from :srcref:`src/tests/data/x509/bsi/common_14/`)                            |
   +----------------------+----------------------------------------------------------------------------------+
   | **Expected Output:** | None                                                                             |
   +----------------------+----------------------------------------------------------------------------------+
   | **Steps:**           | #. For each certificate from *Certs*, look up the certificates matching its      |
   |                      |    subject DN and subject key ID                                                 |
   |                      |                                                                                  |
   |                      | #. Check that exactly one match with the expected subject DN is found            |
   |                      |                                                                                  |
   |                      | #. Insert both certificates from *SameDNCerts* into the store                    |
   |                      |                                                                                  |
   |                      | #. Look up all certificates matching their shared subject DN (without            |
   |                      |    specifying a subject key ID)                                                  |
   |                      |                                                                                  |
   |                      | #. Check that both certificates are returned and that both carry the expected    |
   |                      |    subject DN                                                                    |
   +----------------------+----------------------------------------------------------------------------------+


Finding Certificate by hashed Subject DN or by Issuer DN and Serial Number
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These unit tests test search of certificates by the hashed subject DN and by the issuer DN and serial number. The test operates on an in-memory certificate store (``Certificate_Store_In_Memory``) filled with the test certificates. The tests are executed with the following constraints:

    - Number of test cases: 1
    - Cert: X.509v3

The following table shows an example test case with one test vector. All test vectors are listed in :srcref:`src/tests/data/x509/certstor/`.

.. table::
   :class: longtable
   :widths: 20 80

   +----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**   | CERTSTOR-SCH-1                                                           |
   +----------------------+--------------------------------------------------------------------------+
   | **Type:**            | Positive Test                                                            |
   +----------------------+--------------------------------------------------------------------------+
   | **Description:**     | Searches certificates by hashed subject DN and by issuer DN and          |
   |                      | serial number                                                            |
   +----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**   | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Input Values:**    | -  Certs: Certificates stored in the store                               |
   +----------------------+--------------------------------------------------------------------------+
   | **Expected Output:** | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Steps:**           | #. For each certificate from Certs, build the SHA-256 hash value of the  |
   |                      |    raw subject DN of the given certificate                               |
   |                      |                                                                          |
   |                      | #. Check if certificate can be found in the store by using the built     |
   |                      |    hash.                                                                 |
   |                      |                                                                          |
   |                      | #. For each certificate from Certs, look up the certificate by its       |
   |                      |    issuer DN and serial number                                           |
   |                      |                                                                          |
   |                      | #. Check that the certificate with the expected serial number is found   |
   |                      |                                                                          |
   |                      | #. Look up a certificate using a dummy hash consisting of 32 zero bytes  |
   |                      |    and check that no certificate is found                                |
   +----------------------+--------------------------------------------------------------------------+

System Certificate Store
------------------------

The system certificate store provides a read-only interface to the operating system’s root certificate trust chains. Supported are the trust chain APIs of Windows and macOS as well as Linux. Applications can fetch trust chain certificates via various query-parameters. Each of which are covered by unit tests.
Note that the tests are relying on certain (common) certificates to be installed in the host’s trust chain. Each of those certificates have particular features needed for testing. Namely:


    - **„ISRG Root X1“**
        - valid until: 4th of June 2035
        - *contains „PrintableString“ encodings in its Distinguished Name fields*
    - at least one of the following certificates, all of which *contain UTF-8
      encoded strings in their Distinguished Name fields*:

        - **„SSL.com TLS ECC Root CA 2022“** (valid until: 12th of February 2041)
        - **„D-TRUST Root Class 3 CA 2 EV 2009“** (valid until: 5th of November 2029)
        - **„TrustAsia Global Root CA G3“** (valid until: 19th of May 2046)
        - **„T-TeleSec GlobalRoot Class 2“** (valid until: 1st of October 2033)
        - **„Atos TrustedRoot Root CA ECC TLS 2021“** (valid until: 17th of April 2041)
    - „SecureTrust CA“
        - valid until: 31st of December 2029
        - *defines a Subject Key Identifier that is different from the public key's SHA-1 hash
          (hence, does not adhere to* |RFC-3280-link|_\ *)*

.. _RFC-3280-link: https://datatracker.ietf.org/doc/html/rfc3280#section-4.2.1.2
.. |RFC-3280-link| replace:: *the respective suggestion in RFC 3280*

All tests are implemented in :srcref:`src/tests/test_certstor_system.cpp`.

Since the rework of the certificate store search operations in Botan 3.12.0
(GH #5510, #5539), the tests for the find operations (by subject DN, by
subject DN and key ID, by issuer DN and serial number, and with DN
normalization) additionally verify that every returned certificate is also
reported as contained in the store by ``Certificate_Store::contains()``.

Find Certificate by SHA-1 Hash of its Public Key
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This test uses two root certificates, one „typical“ – i.e. Subject Key ID and the public key’s SHA-1 hash are equal – and one „exceptional“. In both cases, the System Certificate Store must be able to find the correct root certificate.


.. table::
   :class: longtable
   :widths: 20 80

   +----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**   | CERTSTOR-SYSTEM-1                                                        |
   +----------------------+--------------------------------------------------------------------------+
   | **Type:**            | Positive Test                                                            |
   +----------------------+--------------------------------------------------------------------------+
   | **Description:**     | Look up root certificates given the SHA-1 hash of their Public Key. In   |
   |                      | most cases, this is equal to the certificate’s Subject Key Identifier    |
   |                      | (see also RFC 3280 4.2.1.2).                                             |
   +----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**   | Certificates „ISRG Root X1“ and „SecureTrust CA“ are installed in the    |
   |                      | system root certificate store.                                           |
   +----------------------+--------------------------------------------------------------------------+
   | **Input Values:**    | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Expected Output:** | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Steps:**           | #. Query certificates by their public key’s SHA-1                        |
   |                      |                                                                          |
   |                      | #. Check that:                                                           |
   |                      |                                                                          |
   |                      |    (a) the correct certificate is found                                  |
   |                      |    (b) no other certificate is returned                                  |
   +----------------------+--------------------------------------------------------------------------+

Find Certificate by its Subject Distinguished Name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This test uses two root certificates, (1) with its Subject Distinguished Name containing strings encoded as „PrintableString“ [#]_ and (2) with it containing an UTF-8 encoded string. In both cases, the System Certificate Store must be able to find the correct root certificate.

.. [#] `https://en.wikipedia.org/wiki/PrintableString <https://en.wikipedia.org/wiki/PrintableString>`_

.. table::
   :class: longtable
   :widths: 20 80

   +----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**   | CERTSTOR-SYSTEM-2                                                        |
   +----------------------+--------------------------------------------------------------------------+
   | **Type:**            | Positive Test                                                            |
   +----------------------+--------------------------------------------------------------------------+
   | **Description:**     | Look up root certificates given their Subject Distinguished Name         |
   +----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**   | | Certificate „ISRG Root X1“ is installed in the system root certificate |
   |                      |   store.                                                                 |
   |                      | | At least one of the certificates „SSL.com TLS ECC Root CA 2022“,       |
   |                      |   „D-TRUST Root Class 3 CA 2 EV 2009“, „TrustAsia Global Root CA G3“,    |
   |                      |   „T-TeleSec GlobalRoot Class 2“ and „Atos TrustedRoot Root CA ECC TLS   |
   |                      |   2021“ (all with UTF-8 encoded strings in their DN) is installed in the |
   |                      |   system root certificate store.                                         |
   +----------------------+--------------------------------------------------------------------------+
   | **Input Values:**    | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Expected Output:** | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Steps:**           | #. Query certificates by their Subject Distinguished Name                |
   |                      |                                                                          |
   |                      | #. Check that:                                                           |
   |                      |                                                                          |
   |                      |    (c) the correct certificate is found                                  |
   |                      |    (d) no other certificate is returned                                  |
   |                      |    (e) no duplicate certificates are returned                            |
   +----------------------+--------------------------------------------------------------------------+

Find Certificates by Subject Distinguished Name and Key ID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This tests queries certificates by both their Subject Distinguished Name and their Key ID.

.. table::
   :class: longtable
   :widths: 20 80

   +----------------------+--------------------------------------------------------------------------------+
   | **Test Case No.:**   | CERTSTOR-SYSTEM-3                                                              |
   +----------------------+--------------------------------------------------------------------------------+
   | **Type:**            | Positive Test                                                                  |
   +----------------------+--------------------------------------------------------------------------------+
   | **Description:**     | Look up root certificates given their Subject Distinguished Name and Key ID    |
   +----------------------+--------------------------------------------------------------------------------+
   | **Preconditions:**   | Certificate „ISRG Root X1“ is installed in the system root certificate store.  |
   +----------------------+--------------------------------------------------------------------------------+
   | **Input Values:**    | None                                                                           |
   +----------------------+--------------------------------------------------------------------------------+
   | **Expected Output:** | None                                                                           |
   +----------------------+--------------------------------------------------------------------------------+
   | **Steps:**           | #. Query certificate by its Key ID and Subject Distinguished Name              |
   |                      |                                                                                |
   |                      | #. Check that:                                                                 |
   |                      |                                                                                |
   |                      |     (f) the correct certificate is found                                       |
   |                      |                                                                                |
   |                      |     (g) no other certificate is returned                                       |
   +----------------------+--------------------------------------------------------------------------------+

List all available Subject Distinguished Names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. table::
   :class: longtable
   :widths: 20 80

   +----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**   | CERTSTOR-SYSTEM-4                                                        |
   +----------------------+--------------------------------------------------------------------------+
   | **Type:**            | Positive Test                                                            |
   +----------------------+--------------------------------------------------------------------------+
   | **Description:**     | Lists all available root certificate DNs and makes sure that at least    |
   |                      | one well-known certificate is among them                                 |
   +----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**   | Certificate „ISRG Root X1“ is installed in the system root certificate   |
   |                      | store.                                                                   |
   +----------------------+--------------------------------------------------------------------------+
   | **Input Values:**    | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Expected Output:** | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Steps:**           | #. Request a list of all available Subject DNs                           |
   |                      |                                                                          |
   |                      | #. Check that:                                                           |
   |                      |                                                                          |
   |                      |     (h) the list is not empty                                            |
   |                      |     (i) „ISRG Root X1“ is among the certificates in the result list      |
   +----------------------+--------------------------------------------------------------------------+

Query non-existent Certificates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. table::
   :class: longtable
   :widths: 20 80

   +----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**   | CERTSTOR-SYSTEM-5                                                        |
   +----------------------+--------------------------------------------------------------------------+
   | **Type:**            | Negative Test                                                            |
   +----------------------+--------------------------------------------------------------------------+
   | **Description:**     | Expose all available interfaces with fantasy-queries and ensure that the |
   |                      | module returns empty results.                                            |
   +----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**   | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Input Values:**    | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Expected Output:** | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Steps:**           | #. Request a fantasy certificate via:                                    |
   |                      |                                                                          |
   |                      |     (a) Key ID and Subject Distinguished Name                            |
   |                      |                                                                          |
   |                      |     (b) via SHA-1 hash of Public Key                                     |
   |                      |                                                                          |
   |                      | #. Check that:                                                           |
   |                      |                                                                          |
   |                      |     (a) all query results are empty                                      |
   |                      |                                                                          |
   |                      |     (b) no unexpected error occurs                                       |
   +----------------------+--------------------------------------------------------------------------+

Find Certificate by Issuer Distinguished Name and Serial Number
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This test queries a certificate by its Issuer Distinguished Name and its serial number. Since the queried certificate is a self-signed root certificate, its issuer DN equals its subject DN.

.. table::
   :class: longtable
   :widths: 20 80

   +----------------------+--------------------------------------------------------------------------+
   | **Test Case No.:**   | CERTSTOR-SYSTEM-6                                                        |
   +----------------------+--------------------------------------------------------------------------+
   | **Type:**            | Positive Test                                                            |
   +----------------------+--------------------------------------------------------------------------+
   | **Description:**     | Look up a root certificate given its Issuer Distinguished Name and its   |
   |                      | serial number                                                            |
   +----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**   | Certificate „ISRG Root X1“ is installed in the system root certificate   |
   |                      | store.                                                                   |
   +----------------------+--------------------------------------------------------------------------+
   | **Input Values:**    | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Expected Output:** | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Steps:**           | #. Query the certificate by the issuer DN and the serial number of       |
   |                      |    „ISRG Root X1“                                                        |
   |                      |                                                                          |
   |                      | #. Check that:                                                           |
   |                      |                                                                          |
   |                      |     (a) the correct certificate with the expected serial number is found |
   |                      |                                                                          |
   |                      |     (b) the returned certificate is reported as contained in the store   |
   +----------------------+--------------------------------------------------------------------------+
