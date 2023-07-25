"""""""""""""""
CRYSTALS-Kyber
"""""""""""""""

Analysierte Variante:

- 512

Aufgrund der vorangegangenen Analyse von CRYSTALS-Kyber für die drei Parameter 512, 768 und 1024 sowie den Original- und 90s-Modus wurde für diese Analyse nur die Variante 512 untersucht.
Da die Ergebnisse für diese Variante übertragbar sind und sich keine Änderungen ergeben haben, ist eine zusätzliche Analyse der anderen Varianten nicht notwendig.
Für die Analyse von Kyber wurde ein Hilfsprogramm geschrieben, das ähnlich wie das Botan CLI die zu analysierenden Funktionen aufruft.
Für die Verschlüsselung wird folgender Aufruf verwendet:

.. code-block:: cpp

      Botan::AutoSeeded_RNG rng;
      auto encryptor = Botan::PK_KEM_Encryptor(pub_key, "HKDF(SHA-256)", "");
      encryptor.encrypt(cipher_text, sym_key, shared_secret_length, rng);

Zur Entschlüsselung wird folgender Aufruf verwendet:

.. code-block:: cpp

      Botan::AutoSeeded_RNG rng;
      auto decryptor = Botan::PK_KEM_Decryptor(priv_key, rng, "HKDF(SHA-256)", "");
      sym_key = decryptor.decrypt(cipher_text.data(), cipher_text.size(), shared_secret_length);

**Leak: Polynommatrix.**

In der Funktion ``generate()`` der Klasse ``PolynomialMatrix`` wurde bei der Analyse ein Datenleak gefunden [BOTAN_KYBER_MATRIX]_.
Dieser Aufruf erfolgt im Konstruktor der Klasse ``Kyber_KEM_Cryptor`` [BOTAN_KYBER_KEM_CRYPTOR]_.
Der folgende Ausschnitt zeigt den Konstruktor der Klasse ``Kyber_KEM_Cryptor`` und den darin enthaltenen Aufruf der Funktion ``generate()``.

.. code-block:: cpp

  class Kyber_KEM_Cryptor
     {
     protected:
        Kyber_KEM_Cryptor(std::shared_ptr<const Kyber_PublicKeyInternal> public_key) :
           m_public_key(std::move(public_key)),
           m_mode(m_public_key->mode()),
           m_at(PolynomialMatrix::generate(m_public_key->seed(), true, m_mode))
           {
           }

Die Erzeugung der Polynommatrix erfolgt unter Verwendung des öffentlichen Schlüssels.
Es handelt sich also lediglich um ein Leak des öffentlichen Schlüssels, was als unproblematisch einzustufen ist.
Bei der Entschlüsselung mit dem privaten Schlüssel wurden keine Leaks gefunden.
