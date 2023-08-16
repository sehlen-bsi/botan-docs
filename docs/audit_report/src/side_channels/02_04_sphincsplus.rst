""""""""
SPHINCS+
""""""""

Analysierte Variante:

- SphincsPlus-sha2-128s-r3.1, deterministic & randomized

Für die Analyse von SPHINCS+ wurde ein Hilfsprogramm geschrieben, das ähnlich wie das Botan CLI die zu analysierenden Funktionen aufruft.
Für die Erzeugung der Signatur wird folgender Aufruf verwendet:

.. code-block:: cpp

    auto params = Botan::Sphincs_Parameters::create("SphincsPlus-sha2-128s-r3.1");
    Botan::SphincsPlus_PrivateKey priv_key(params.algorithm_identifier(), priv_key_bits);

    #if DETERMINISTIC
        Botan::PK_Signer sig(priv_key, rng, "Deterministic");
    #else
        Botan::PK_Signer sig(priv_key, rng, "Randomized");
    #endif
        signature = sig.sign_message(message, rng);

Der SPHINCS+ Standard verwendet innerhalb des Hypertrees eine Variante von XMSS und bezeichnet diese verkürzt als XMSS.
Dem Standard folgend wird dieses Verfahren auch in diesem Abschnitt als XMSS bezeichnet.

**Modifikation des Hypertrees**

Die Laufzeit zur Erzeugung einer Signatur hängt von der Höhe des Hypertrees und der Anzahl der Merkle-Bäume ab.
Um die Laufzeit zu reduzieren, wird die Gesamthöhe auf vier beschränkt und es werden zwei Merkle-Bäume mit jeweils einer Höhe von zwei verwendet.
Der Algorithmus selbst benötigt diese Einschränkung im Produktiveinsatz nicht.
Die Anpassung erfolgt lediglich, um die Analyse in angemessener Zeit durchführen zu können.
Diese Änderung hat keinen Einfluss auf die Code-Coverage der durchgeführten Seitenkanalanalyse.

**Leakage Zusammenfassung**

DATA detektiert keine Leaks in der analysierten SPHINCS+ Implementierung.
Es werden lediglich Unterschiede in der Programmausführung in Phase 1 von DATA gefunden.
In Phase 2 kann jedoch keine statistische Abhängigkeit zu den verwendeten, geheimen kryptografischen Schlüsseln nachgewiesen werden.

Als Hintergrundinformation sind in den folgenden Abschnitten die Gründe für die Ausführungsunterschiede erläutert.
Insgesamt zeigt die Analyse fünf Unterschiede in der Ausführung auf.
Ein Unterschied wurde innerhalb des FORS-Verfahrens gefunden, die restlichen vier Unterschiede betreffen das XMSS-Verfahren.

**Ausführungsunterschied: FORS - treehash**

Das FORS-Verfahren basiert auf der Verwendung von Merkle-Bäumen.
Der öffentliche FORS-Schlüssel ist der Wurzelknoten in einem Merkle-Baum.
Die Kinder dieses Knotens sind Wurzelknoten einzelner Merkle-Bäume, die zur Signatur einer Nachricht verwendet werden.

Die `treehash` Routine berechnet mithilfe der Blätter eines Merkle-Baums die darüber liegenden Knoten.
Während der Verifikation wird ein Teil der Blätter anhand der Nachricht und der Signatur berechnet.
Die restlichen Blätter oder Knoten eines Merkle-Baums, welche zur Verifikation benötigt werden, sind im sogenannten Authentisierungspfad enthalten.
Dieser ist Bestandteil einer FORS-Signatur und wird bei der Signaturerzeugung generiert.

Die `treehash` Routine detektiert während der Ausführung, ob der aktuell berechnete Knoten dem Authentisierungspfad hinzugefügt werden muss [BOTAN_SPHINCSPLUS_TREEHASH]_.
Ist dies der Fall, kommt es zur Erfüllung einer Kondition im Programmablauf und zu einer geänderten Programmausführung.
Dieser Kontrollflussunterschied wird durch DATA aufgezeigt.
Der Unterschied ist unkritisch, weil die Werte der Knoten innerhalb dieser Merkle-Bäume öffentlich sind.
Folglich ist es auch unkritsch, wenn anhand der Unterschiede ersichtlich ist, welche Knoten zum Authentisierungspfad gehören.
Dieses Wissen ist auch von einer Nachricht und der zugehörigen Signatur ableitbar.

.. code-block:: cpp

   void treehash(StrongSpan<SphincsTreeNode> out_root,
              StrongSpan<SphincsAuthenticationPath> out_auth_path,
              const Sphincs_Parameters& params,
              Sphincs_Hash_Functions& hashes,
              std::optional<TreeNodeIndex> leaf_idx,
              uint32_t idx_offset,
              uint32_t total_tree_height,
              const GenerateLeafFunction& gen_leaf,
              Sphincs_Address& tree_address) {
   ...
   for(TreeNodeIndex idx(0); true; ++idx) {
      ...

      // Now combine the freshly generated right node with previously generated
      // left ones
      ...

      for(TreeLayerIndex h(0); true; ++h) {
         // Check if we hit the top of the tree
         ...

         // Check if the node we have is a part of the authentication path; if
         // it is, write it out. The XOR sum of both nodes (at internal_idx and internal_leaf)
         // is 1 iff they have the same parent node in the FORS tree
         if(internal_leaf.has_value() && (internal_idx ^ internal_leaf.value()) == 0x01U) {
            ...
         }

**Ausführungsunterschied: WOTS - treehash**

Das XMSS-Verfahren basiert auf dem WOTS-Verfahren und der Verwendung von Merkle-Bäumen.
Ähnlich zum FORS-Verfahren verwendet auch das XMSS-Verfahren die `treehash` Routine.
Auch hier kommt es zu einem ähnlichen Unterschied in der Programmausführung bei dem Hinzufügen einzelner Knoten zu den Authentisierungsdaten einer Signatur [BOTAN_SPHINCSPLUS_TREEHASH]_.
Analog zum FORS-Verfahren ist dieser Unterschied auch beim XMSS-Verfahren unkritisch.

.. code-block:: cpp

   void treehash(StrongSpan<SphincsTreeNode> out_root,
              StrongSpan<SphincsAuthenticationPath> out_auth_path,
              const Sphincs_Parameters& params,
              Sphincs_Hash_Functions& hashes,
              std::optional<TreeNodeIndex> leaf_idx,
              uint32_t idx_offset,
              uint32_t total_tree_height,
              const GenerateLeafFunction& gen_leaf,
              Sphincs_Address& tree_address) {
     ...
     for(TreeNodeIndex idx(0); true; ++idx) {
        ...

        // Now combine the freshly generated right node with previously generated
        // left ones
        ...

        for(TreeLayerIndex h(0); true; ++h) {
           // Check if we hit the top of the tree
           ...

           // Check if the node we have is a part of the authentication path; if
           // it is, write it out. The XOR sum of both nodes (at internal_idx and internal_leaf)
           // is 1 iff they have the same parent node in the FORS tree
           if(internal_leaf.has_value() && (internal_idx ^ internal_leaf.value()) == 0x01U) {
              ...
           }

**Ausführungsunterschied: WOTS - wots_sign_and_pkgen**

Neben den Unterschieden in der `treehash` Routine werden auch drei Unterschiede in der Funktion `wots_sign_and_pkgen` detektiert.
Diese Funktion generiert die Signaturdaten für das WOTS-Verfahren und die öffentlichen WOTS-Schlüssel für die anderen Blätter im Merkle-Baum.

Der erste Unterschied ist ein Kontrollflussunterschied.
Die Implementierung unterscheidet, ob Signaturdaten für das WOTS-Verfahren erstellt werden müssen oder ob nur der öffentliche WOTS-Schlüssel benötigt wird [BOTAN_SPHINCSPLUS_WOTS_SIGN_AND_PKGEN_SIG_NODE]_.
Diese Information kann auch mithilfe der Nachricht und der zugehörigen Signatur berechnet werden, wodurch der Unterschied als unkritisch eingestuft wird.

.. code-block:: cpp

   void wots_sign_and_pkgen(StrongSpan<WotsSignature> sig_out,
                            StrongSpan<SphincsTreeNode> leaf_out,
                            const SphincsSecretSeed& secret_seed,
                            TreeNodeIndex leaf_idx,
                            std::optional<TreeNodeIndex> sign_leaf_idx,
                            const std::vector<WotsHashIndex>& wots_steps,
                            Sphincs_Address& leaf_addr,
                            Sphincs_Address& pk_addr,
                            const Sphincs_Parameters& params,
                            Sphincs_Hash_Functions& hashes) {
     ...
     for(WotsChainIndex i(0); i < params.wots_len(); i++) {
        // If the current leaf is part of the signature wots_k stores the chain index
        //   of the value neccessary for the signature. Otherwise: nullopt (no signature)
        const auto wots_k = [&]() -> std::optional<WotsHashIndex> {
           if(sign_leaf_idx.has_value() && leaf_idx == sign_leaf_idx.value()) {
              return wots_steps[i.get()];
           } else {
              return std::nullopt;
           }
        }();
        ...

Die anderen beiden Ausführungsunterschiede betreffen das Hinzufügen eines Zwischenwerts einer Hash-Kette zu den WOTS-Signaturdaten [BOTAN_SPHINCSPLUS_WOTS_SIGN_AND_PKGEN_SIG_NODE_HC]_.
Bei der Erstellung einer WOTS-Signatur werden die Hash-Ketten nur partiell durchlaufen.
Das Ergebnis wird der WOTS-Signatur hinzugefügt.
Dabei wird die Anzahl der durchgeführten Schritte in einer Hash-Kette ersichtlich.
Das ist unkritisch, weil diese Information auch während der Verifikation anhand der Nachricht und Signatur berechnet wird.

.. code-block:: cpp

   void wots_sign_and_pkgen(StrongSpan<WotsSignature> sig_out,
                            StrongSpan<SphincsTreeNode> leaf_out,
                            const SphincsSecretSeed& secret_seed,
                            TreeNodeIndex leaf_idx,
                            std::optional<TreeNodeIndex> sign_leaf_idx,
                            const std::vector<WotsHashIndex>& wots_steps,
                            Sphincs_Address& leaf_addr,
                            Sphincs_Address& pk_addr,
                            const Sphincs_Parameters& params,
                            Sphincs_Hash_Functions& hashes) {
     ...
     for(WotsChainIndex i(0); i < params.wots_len(); i++) {
     // If the current leaf is part of the signature wots_k stores the chain index
     //   of the value neccessary for the signature. Otherwise: nullopt (no signature)
     ...

     // Start with the secret seed
     ...

     // Iterates down the WOTS chain
     for(WotsHashIndex k(0);; k++) {
        // Check if this is the value that needs to be saved as a part of the WOTS signature
        if(wots_k.has_value() && k == wots_k.value()) {
           std::copy(buffer_s.begin(), buffer_s.end(), sig.next<WotsNode>(params.n()).begin());
        }

