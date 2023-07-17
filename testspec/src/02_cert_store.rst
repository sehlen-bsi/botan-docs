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

These unit tests test search certificates matching given subject DN and Subject Key Identifier. The tests are executed with the following constraints:

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
   +----------------------+----------------------------------------------------------------------------------+
   | **Expected Output:** | None                                                                             |
   +----------------------+----------------------------------------------------------------------------------+
   | **Steps:**           | #. Look up Certs by subject DN and subject key ID                                |
   |                      | #.  Check that only one match is found                                           |
   +----------------------+----------------------------------------------------------------------------------+

Finding Certificate by hashed Subject DN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These unit tests test search certificates by the hashed subject DN. The tests are executed with the following constraints:

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
   | **Description:**     | Searches certificate by hashed subject DNs of all certificates           |
   +----------------------+--------------------------------------------------------------------------+
   | **Preconditions:**   | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Input Values:**    | -  Certs: Certificates stored in the store                               |
   +----------------------+--------------------------------------------------------------------------+
   | **Expected Output:** | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Steps:**           | #. For each certificate from Certs, build hash value from the subject DN |
   |                      |    of the given certificate                                              |
   |                      |                                                                          |
   |                      | #. Check if certificate can be found in the store by using the built     |
   |                      |    hash.                                                                 |
   +----------------------+--------------------------------------------------------------------------+

System Certificate Store
------------------------

The system certificate store provides a read-only interface to the operating system’s root certificate trust chains. Supported are the trust chain APIs of Windows and macOS as well as Linux. Applications can fetch trust chain certificates via various query-parameters. Each of which are covered by unit tests.
Note that the tests are relying on certain (common) certificates to be installed in the host’s trust chain. Each of those certificates have particular features needed for testing. Namely:


    - **„ISRG Root X1“**
        - valid until: 4th of June 2035
        - *contains „PrintableString“ encodings in its Distinguished Name fields*
    - **„D-TRUST Root Class 3 CA 2 EV 2009“**
        - valid until: 5th of November 2029
        - *contains UTF-8 encoded strings in its Distinguished Name fields*
    - „SecureTrust CA“
        - valid until: 31st of December 2029
        - *defines a Subject Key Identifier that is different from the public key's SHA-1 hash
          (hence, does not adhere to* |RFC-3280-link|_\ *)*

.. _RFC-3280-link: https://datatracker.ietf.org/doc/html/rfc3280#section-4.2.1.2
.. |RFC-3280-link| replace:: *the respective suggestion in RFC 3280*

All tests are implemented in :srcref:`src/tests/test_certstor_system.cpp`.

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
   | **Preconditions:**   | | Certificates „ISRG Root X1“ and „D-TRUST Root Class 3 CA 2 EV 2009“    |
   |                      |   are installed in the system root certificate store.                    |
   |                      | | Note that „D-TRUST Root Class 3 CA 2 EV 2009“ was not available in the |
   |                      |   CI provider’s trust store on Windows. Hence, this part of the test is  |
   |                      |   currently disabled for Windows entirely.                               |
   +----------------------+--------------------------------------------------------------------------+
   | **Input Values:**    | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Expected Output:** | None                                                                     |
   +----------------------+--------------------------------------------------------------------------+
   | **Steps:**           | #. Query certificates by their public key’s SHA-1                        |
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
