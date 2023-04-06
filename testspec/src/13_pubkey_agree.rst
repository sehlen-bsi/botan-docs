Public Key-based Key Agreement Schemes
======================================

Public-key based Key Agreement Schemes are tested using a known answer
test that derives a key from a set of input values and tests that
generate and unit test keys. However, the input values differ for the
tested algorithms Diffie Hellman and Elliptic Curve Diffie Hellman such
that these test cases are described separately for each algorithm.

Additionally, for each scheme unit tests make sure that encoding and
decoding private and public keys works correctly. These tests are
implemented in *src/tests/test\_pubkey.cpp*. These test cases are
described here in the following.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KA-KEY-1                                                                |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encode a key agreement keypair and decode a key agreement public key as |
   |                        | PEM                                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Group: The DL group, e.g., modp/ietf/1024 or                         |
   |                        |                                                                         |
   |                        | -  Curve: The elliptic curve, e.g., secp192r1                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random keypair on the *Group*/*Curve*                     |
   |                        |                                                                         |
   |                        | #. Check that the generated public key is valid and its estimated       |
   |                        |    strength satisfies the requirements                                  |
   |                        |                                                                         |
   |                        | #. Encode the keypair as PEM-encoded string                             |
   |                        |                                                                         |
   |                        | #. Create a Public_Key object from the PEM-encoded string, decoding the |
   |                        |    PEM-encoded keypair                                                  |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid                                   |
   |                        |                                                                         |
   |                        | #. Check that the key object algorithm name equals that of the          |
   |                        |    generated keypair                                                    |
   |                        |                                                                         |
   |                        | #. Check that the key is valid [#ka_mechanism]_                         |
   +------------------------+-------------------------------------------------------------------------+

.. [#ka_mechanism] The exact mechanism depends on the key type and is explained in the
                   corresponding key agreement section

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KA-KEY-2                                                                |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encode a key agreement keypair and decode a key agreement public key as |
   |                        | BER                                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Group: The DL group, e.g., modp/ietf/1024 or                         |
   |                        |                                                                         |
   |                        | -  Curve: The elliptic curve, e.g., secp192r1                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random keypair on the *Group*/*Curve*                     |
   |                        |                                                                         |
   |                        | #. Check that the generated public key is valid and its estimated       |
   |                        |    strength satisfies the requirements                                  |
   |                        |                                                                         |
   |                        | #. Encode the keypair as BER-encoded byte array                         |
   |                        |                                                                         |
   |                        | #. Create a Public_Key object from the BER-encoded byte array, decoding |
   |                        |    the BER-encoded keypair                                              |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid\ :sup:`1`                         |
   |                        |                                                                         |
   |                        | #. Check that the key object algorithm name equals that of the          |
   |                        |    generated keypair                                                    |
   |                        |                                                                         |
   |                        | #. Check that the key is valid                                          |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KA-KEY-3                                                                |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encode a key agreement keypair and decode a key agreement private key   |
   |                        | as PEM                                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Group: The DL group, e.g., modp/ietf/1024 or                         |
   |                        |                                                                         |
   |                        | -  Curve: The elliptic curve, e.g., secp192r1                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random keypair on the *Group*/*Curve*                     |
   |                        |                                                                         |
   |                        | #. Check that the generated public key is valid and its estimated       |
   |                        |    strength satisfies the requirements                                  |
   |                        |                                                                         |
   |                        | #. Encode the keypair as PEM-encoded string                             |
   |                        |                                                                         |
   |                        | #. Create a Private_Key object from the PEM-encoded string, decoding    |
   |                        |    the PEM-encoded keypair                                              |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid                                   |
   |                        |                                                                         |
   |                        | #. Check that the key object algorithm name equals that of the          |
   |                        |    generated keypair                                                    |
   |                        |                                                                         |
   |                        | #. Check that the key is valid (see KA-KEY-1)                           |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KA-KEY-4                                                                |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encode a key agreement keypair and decode a key agreement private key   |
   |                        | as BER                                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Group: The DL group, e.g., modp/ietf/1024 or                         |
   |                        |                                                                         |
   |                        | -  Curve: The elliptic curve, e.g., secp192r1                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random keypair on the *Group*/*Curve*                     |
   |                        |                                                                         |
   |                        | #. Check that the generated public key is valid and its estimated       |
   |                        |    strength satisfies the requirements                                  |
   |                        |                                                                         |
   |                        | #. Encode the keypair as BER-encoded byte array                         |
   |                        |                                                                         |
   |                        | #. Create a Private_Key object from the BER-encoded byte array,         |
   |                        |    decoding the BER-encoded keypair                                     |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid                                   |
   |                        |                                                                         |
   |                        | #. Check that the key object algorithm name equals that of the          |
   |                        |    generated keypair                                                    |
   |                        |                                                                         |
   |                        | #. Check that the key is valid (see KA-KEY-1)                           |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KA-KEY-5                                                                |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encode a key agreement keypair and decode a key agreement private key   |
   |                        | as PEM, protected with a password                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Group: The DL group, e.g., modp/ietf/1024 or                         |
   |                        |                                                                         |
   |                        | -  Curve: The elliptic curve, e.g., secp192r1                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random password string of length between 1-32 characters  |
   |                        |                                                                         |
   |                        | #. Generate a random keypair on the *Group*/*Curve*                     |
   |                        |                                                                         |
   |                        | #. Check that the generated public key is valid and its estimated       |
   |                        |    strength satisfies the requirements                                  |
   |                        |                                                                         |
   |                        | #. Encode the keypair as PEM-encoded string, protected with the         |
   |                        |    password                                                             |
   |                        |                                                                         |
   |                        | #. Create a Private_Key object from the PEM-encoded string, decoding    |
   |                        |    the PEM-encoded keypair                                              |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid                                   |
   |                        |                                                                         |
   |                        | #. Check that the key object algorithm name equals that of the          |
   |                        |    generated keypair                                                    |
   |                        |                                                                         |
   |                        | #. Check that the key is valid (see KA-KEY-1)                           |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KA-KEY-6                                                                |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encode a key agreement keypair and decode a key agreement private key   |
   |                        | as BER, protected with a password                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Group: The DL group, e.g., modp/ietf/1024 or                         |
   |                        |                                                                         |
   |                        | -  Curve: The elliptic curve, e.g., secp192r1                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random password string of length between 1-32 characters  |
   |                        |                                                                         |
   |                        | #. Check that the generated public key is valid and its estimated       |
   |                        |    strength satisfies the requirements                                  |
   |                        |                                                                         |
   |                        | #. Generate a random keypair on the *Group*/*Curve*                     |
   |                        |                                                                         |
   |                        | #. Encode the keypair as BER-encoded byte array, protected with the     |
   |                        |    password                                                             |
   |                        |                                                                         |
   |                        | #. Create a Private_Key object from the BER-encoded byte array,         |
   |                        |    decoding the BER-encoded keypair                                     |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid                                   |
   |                        |                                                                         |
   |                        | #. Check that the key object algorithm name equals that of the          |
   |                        |    generated keypair                                                    |
   |                        |                                                                         |
   |                        | #. Check that the key is valid (see KA-KEY-1)                           |
   +------------------------+-------------------------------------------------------------------------+

Diffie-Hellman
--------------

The Diffie-Hellman key agreement scheme is tested with a known answer
test as follows. The test is implemented in *src/tests/test\_dh.cpp*.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KA-DH-1                                                                 |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Derives a shared key from the Diffie Hellman Key Agreement Scheme       |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  P: The prime p (varying length)                                      |
   |                        |                                                                         |
   |                        | -  G: The base g (varying length)                                       |
   |                        |                                                                         |
   |                        | -  X: The key's secret value (varying length)                           |
   |                        |                                                                         |
   |                        | -  Y: The other party's public value (varying length)                   |
   |                        |                                                                         |
   |                        | -  KDF: The underlying key derivation function, e.g., KDF2(SHA-1)       |
   |                        |    (optional)                                                           |
   |                        |                                                                         |
   |                        | -  Output Length: The desired length of the derived shared secret       |
   |                        |    (optional, only used when a KDF is used; otherwise the full output   |
   |                        |    of DH is used)                                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | -  K: The derived shared secret (length depending on the desired output |
   |                        |    length)                                                              |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the DH object (input *P*, *G*, *X*)                           |
   |                        |                                                                         |
   |                        | #. Input *Output Length* (optional) and *P*, *G*, *Y* into the DH and   |
   |                        |    compare the result with the expected output value *K*                |
   +------------------------+-------------------------------------------------------------------------+

Diffie-Hellman key agreement is tested with the following constraints:

-  Number of test cases: 40
-  Sources: NIST CAVP file 20.1, other

-  P: 512 bits, 768 bits, 1024 bits, 1536 bits, 2048 bits
-  G: 2, 3, 5 (Zahlenwerte), 2045 bits, 2048 bits
-  X: 119 bits – 1535 bits
-  Y: 254 bits – 2048 bits
-  KDF: None
-  Output Length: None, 40 bits, 128 bits, 152 bits, 264 bits
-  K: 40 bits, 128 bits, 152 bits, 256 bits, 264 bits, 512 bits, 1024
   bits, 1536 bits

The following table shows an example test case with one test vector. All
test vectors are listed in *src/tests/data/pubkey/dh.vec*.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KA-DH-1                                                                 |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Derives a shared key from the Diffie Hellman Key Agreement Scheme       |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    P = 5845800209553609465868375525852336296142120075143945615975616419 |
   |                        |    1494576279467                                                        |
   |                        |    G = 2                                                                |
   |                        |    X = 4620566309358961266874616386087096391222637913119081216351934984 |
   |                        |    8291472898748                                                        |
   |                        |    Y = 2682140057229807435837507392271549840327358336761740278194677313 |
   |                        |    2088456286733                                                        |
   |                        |    KDF = None                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    K = 0x5D9A64F9E54B011381308CF462C207CB0DB7630EAB026E06E5B893041207DB |
   |                        |    D8                                                                   |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the DH object (input *P*, *G*, *X*)                           |
   |                        |                                                                         |
   |                        | #. Input *Output Length* (optional) and *P*, *G*, *Y* into the DH and   |
   |                        |    compare the result with the expected output value *K*                |
   +------------------------+-------------------------------------------------------------------------+

Additional two unit tests check that DH only accept public key values 1
<= Y <= P-1.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KA-DH-2                                                                 |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Makes sure Diffie Hellman Key Agreement Scheme does not accept a public |
   |                        | key value Y > P-1                                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    P = 5845800209553609465868375525852336296142120075143945615975616419 |
   |                        |    1494576279467                                                        |
   |                        |    G = 2                                                                |
   |                        |    X = 4620566309358961266874616386087096391222637913119081216351934984 |
   |                        |    8291472898748                                                        |
   |                        |    Y = 5845800209553609465868375525852336296142120075143945615975616419 |
   |                        |    14945762794672                                                       |
   |                        |    Output Length = 128 bits                                             |
   |                        |    KDF = None                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | DH outputs an error                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the DH object (input *P*, *G*, *X*)                           |
   |                        |                                                                         |
   |                        | #. Input *Output Length* and *P*, *G*, *Y* into the DH and compute the  |
   |                        |    shared secret                                                        |
   +------------------------+-------------------------------------------------------------------------+

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KA-DH-3                                                                 |
   +========================+=========================================================================+
   | **Type:**              | Negative Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Makes sure Diffie Hellman Key Agreement Scheme does not accept a public |
   |                        | key value Y <= 1                                                        |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    P = 5845800209553609465868375525852336296142120075143945615975616419 |
   |                        |    1494576279467                                                        |
   |                        |    G = 2                                                                |
   |                        |    X = 4620566309358961266874616386087096391222637913119081216351934984 |
   |                        |    8291472898748                                                        |
   |                        |    Y = 1                                                                |
   |                        |    Output Length = 128 bits                                             |
   |                        |    KDF = None                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | DH outputs an error                                                     |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the DH object (input *P*, *G*, *X*)                           |
   |                        |                                                                         |
   |                        | #. Input *Output Length* and *P*, *G*, *Y* into the DH and compute the  |
   |                        |    shared secret                                                        |
   +------------------------+-------------------------------------------------------------------------+

The following example shows a DH-specific KA-KEY-1 test case. The
constraints for this test case are:

-  Group: modp/ietf/1024, modp/ietf/2048

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KA-KEY-DH-1                                                             |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encode and decode a DH key agreement public key as PEM                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Group = modp/ietf/1024                                                  |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random keypair on the DH *Group*                          |
   |                        |                                                                         |
   |                        | #. Encode the public key as PEM-encoded string                          |
   |                        |                                                                         |
   |                        | #. Create a DH_Public_Key object from the PEM-encoded string, decoding  |
   |                        |    the PEM-encoded key                                                  |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid                                   |
   |                        |                                                                         |
   |                        | #. Check that the key object algorithm name equals that of the          |
   |                        |    generated keypair                                                    |
   |                        |                                                                         |
   |                        | #. Check that the key is valid by checking that:                        |
   |                        |                                                                         |
   |                        |    #. 1 < Y < P                                                         |
   |                        |                                                                         |
   |                        |    #. G >= 2                                                            |
   |                        |                                                                         |
   |                        |    #. P >= 3                                                            |
   |                        |                                                                         |
   |                        |    #. If Q is given:                                                    |
   |                        |                                                                         |
   |                        |       a. (P - 1) % Q = 0                                                |
   |                        |                                                                         |
   |                        |       b. G\ :sup:`Q` mod P = 1                                          |
   |                        |                                                                         |
   |                        |       c. Q is prime using a Miller-Rabin test with 50 rounds            |
   |                        |                                                                         |
   |                        |    #. P is prime using a Miller-Rabin test with 50 rounds               |
   +------------------------+-------------------------------------------------------------------------+

Additional tests are executed for invalid public keys failing the key
checks. These tests are executed with the following constraints:

-  Number of test cases: 7
-  Source: NIST CAVP (NIST CAVS file 20.1)
-  P: 2,048 bits
-  Q: 224 bits
-  G: 2,045 bits
-  InvalidKey: 2,043 bits - 2,047 bits

The following table shows an example test case with one test vector. All
test vectors are listed in *src/tests/data/pubkey/dh_invalid.vec*.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KA-KEY-DH-INVALID-1                                                     |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Load a public key and perform the key checks                            |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    P = 0xa25cb1199622be09d9f473695114963cbb3b109f92df6da1b1dcab5e8511e9 |
   |                        |    a117e2881f30a78f04d6a3472b8064eb6416cdfd7bb8b9891ae5b5a1f1ee1da0cace |
   |                        |    11dab3ac7a50236b22e105dbeef9e45b53e0384c45c3078acb6ee1ca983511795801 |
   |                        |    da3d14fa9ed82142ec47ea25c0c0b7e86647d41e9f55955b8c469e7e298ea30d88fe |
   |                        |    acf43ade05841008373605808a2f8f8910b195f174bd8af5770e7cd85380d198f4ed |
   |                        |    2a0c3a2f373436ae6ce9567846a79275765ef829abbc6171718f7746ebd167d406e2 |
   |                        |    546acdea7299194a613660d5ef721cd77e7722095c4ca42b29db3d4436325b47f850 |
   |                        |    af05d411c7a95ccc54555c193384a6eeebb47e6f0f                           |
   |                        |    Q = 0xa944d488de8c89567b602bae44478632604f8bf7cb4deb851cf6e22d       |
   |                        |                                                                         |
   |                        |    G = 0x1e2b67448a1869df1ce57517dc5e797b62c5d2c832e23f954bef8bcca74489 |
   |                        |    db6caed2ea496b52a52cb664a168374cb176ddc4bc0068c6eef3a746e561f8dc6519 |
   |                        |    5fdaf12b363e90cfffdac18ab3ffefa4b2ad1904b45dd9f6b76b477ef8816802c7bd |
   |                        |    7cb0c0ab25d378098f5625e7ff737341af63f67cbd00509efbc6470ec38c17b7878a |
   |                        |    463cebda80053f36558a308923e6b41f465385a4f24fdb303c37fb998fc1e49e3c09 |
   |                        |    ce345ff7cea18e9cd1457eb93daa87dba8a31508fa5695c32ce485962eb183414441 |
   |                        |    3b41ef936db71b79d6fe985c018ac396e3af25054dbbc95e56ab5d4d4b7b61a70670 |
   |                        |    e789c336b46b9f7be43cf6eb0e68b40e33a55d55cc                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | Public key fails key checks                                             |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create a DH_Public_Key object from P, Q, G                           |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid                                   |
   |                        |                                                                         |
   |                        | #. Check that the key is invalid by checking that at least one of the   |
   |                        |    following does not hold:                                             |
   |                        |                                                                         |
   |                        |    #. 1 < Y < P                                                         |
   |                        |                                                                         |
   |                        |    #. G >= 2                                                            |
   |                        |                                                                         |
   |                        |    #. P >= 3                                                            |
   |                        |                                                                         |
   |                        |    #. (P - 1) % Q = 0                                                   |
   |                        |                                                                         |
   |                        |    #. G\ :sup:`Q` mod P = 1                                             |
   |                        |                                                                         |
   |                        |    #. Q is prime using a Miller-Rabin test with 50 rounds               |
   |                        |                                                                         |
   |                        |    #. P is prime using a Miller-Rabin test with 50 rounds               |
   +------------------------+-------------------------------------------------------------------------+

Elliptic Curve Diffie Hellman
-----------------------------

The Elliptic Curve Diffie-Hellman key agreement scheme is tested with a
known answer test as follows. The test is implemented in
*src/tests/test\_ecdh.cpp*.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KA-ECDH-1                                                               |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Derives a shared key from the Elliptic Curve Diffie Hellman Key         |
   |                        | Agreement Scheme                                                        |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | -  Curve: The elliptic curve, e.g., secp192r1                           |
   |                        |                                                                         |
   |                        | -  Secret: The key's secret value (varying length)                      |
   |                        |                                                                         |
   |                        | -  CounterKey: The other party's public value (varying length)          |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | -  K: The derived shared secret (varying length)                        |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the ECDH_KA object (input *Curve*, *Secret*)                  |
   |                        |                                                                         |
   |                        | #. Input *CounterKey* into the ECDH and compare the result with the     |
   |                        |    expected output value *K*                                            |
   +------------------------+-------------------------------------------------------------------------+

.. _section-3:

Elliptic Curve Diffie-Hellman key agreement is tested with the following
constraints:

-  Number of test cases: 150
-  Source: NIST CAVS file 14.1

-  Curve: secp192r1, secp224r1, secp256r1, secp384r1, secp521r1,
   frp256v1
-  Secret: 190 bits - 521 bits
-  CounterKey: 192 bits, 224 bits, 256 bits, 384 bits, 521 bits
-  K: 192 bits, 224 bits, 256 bits, 384 bits, 521 bits

The following table shows an example test case with one test vector. All
test vectors are listed in *src/tests/data/pubkey/ecdh.vec*.

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KA-ECDH-1                                                               |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Derives a shared key from the Elliptic Curve Diffie Hellman Key         |
   |                        | Agreement Scheme                                                        |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | .. code-block:: none                                                    |
   |                        |                                                                         |
   |                        |    Curve = secp192r1                                                    |
   |                        |    Secret = 0xf17d3fea367b74d340851ca4270dcb24c271f445bed9d527 (192 bit |
   |                        |    s)                                                                   |
   |                        |    CounterKey = 0x0442ea6dd9969dd2a61fea1aac7f8e98edcc896c6e55857cc0dfb |
   |                        |    e5d7c61fac88b11811bde328e8a0d12bf01a9d204b523 (192 bits)             |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | K = 0x803d8ab2e5b6e6fca715737c3a82f7ce3c783124f6d51cd0 (192 bits)       |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Create the ECDH_KA object (input *Curve*, *Secret*)                  |
   |                        |                                                                         |
   |                        | #. Input *CounterKey* into the ECDH and compare the result with the     |
   |                        |    expected output value *K*                                            |
   +------------------------+-------------------------------------------------------------------------+

The following example shows an ECDH-specific KA-KEY-1 test case. The
constraints for all the key-related test cases are:

-  Curve: secp256r1, secp384r1, secp521r1, brainpool256r1,
   brainpool384r1, frp256v1

.. table::
   :class: longtable
   :widths: 20 80

   +------------------------+-------------------------------------------------------------------------+
   | **Test Case No.:**     | KA-KEY-ECDH-1                                                           |
   +========================+=========================================================================+
   | **Type:**              | Positive Test                                                           |
   +------------------------+-------------------------------------------------------------------------+
   | **Description:**       | Encode and decode an ECDH key agreement public key as PEM               |
   +------------------------+-------------------------------------------------------------------------+
   | **Preconditions:**     | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Input Values:**      | Curve = secp256r1                                                       |
   +------------------------+-------------------------------------------------------------------------+
   | **Expected Output:**   | None                                                                    |
   +------------------------+-------------------------------------------------------------------------+
   | **Steps:**             | #. Generate a random keypair on the *Curve*                             |
   |                        |                                                                         |
   |                        | #. Encode the public key as PEM-encoded string                          |
   |                        |                                                                         |
   |                        | #. Create an ECDH_Public_Key object from the PEM-encoded string,        |
   |                        |    decoding the PEM-encoded key                                         |
   |                        |                                                                         |
   |                        | #. Check that the key object is valid                                   |
   |                        |                                                                         |
   |                        | #. Check that the key object algorithm name equals that of the          |
   |                        |    generated keypair                                                    |
   |                        |                                                                         |
   |                        | #. Check that the public key is valid by checking that the public point |
   |                        |    is on the *Curve*                                                    |
   +------------------------+-------------------------------------------------------------------------+
