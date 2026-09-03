Appendix: Review of Botan PR #5742
==================================


The review in this section was entirely written by Anthropic's Fable 5 model. Please treat it with care as appropriate for AI generated content.

All findings of this review were reported upstream as GitHub issues; each
finding below names its issue. At the time of writing, upstream has closed
finding F1 as a valid observation but a non-issue in practice (see the
remark in that finding); the remaining issues are open.

**"Various minor bug fixes in symmetric algorithm implementations"**

- **PR:** `randombit/botan#5742 <https://github.com/randombit/botan/pull/5742>`_
  (``jack/sym-algo-fixes``), merged 2026-07-18 — this is a retrospective
  review; the findings apply to current master
- **Code links:** pinned to master commit
  `4f40410b6 <https://github.com/randombit/botan/commit/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd>`_;
  all excerpts were verified against that tree
- **Scope of the PR:** 15 commits, 20 files (+97/-28) across block ciphers,
  MACs, AEAD modes, stream ciphers, KDF/MAC factories, and providers
- **Upstream issues filed from this review:**
  `#5904 <https://github.com/randombit/botan/issues/5904>`_ (F1, closed),
  `#5905 <https://github.com/randombit/botan/issues/5905>`_ (F2),
  `#5906 <https://github.com/randombit/botan/issues/5906>`_ (F3),
  `#5907 <https://github.com/randombit/botan/issues/5907>`_ (F4),
  `#5908 <https://github.com/randombit/botan/issues/5908>`_ (F5),
  `#5909 <https://github.com/randombit/botan/issues/5909>`_ (F6),
  `#5910 <https://github.com/randombit/botan/issues/5910>`_ (F7),
  `#5911 <https://github.com/randombit/botan/issues/5911>`_ (F8),
  `#5912 <https://github.com/randombit/botan/issues/5912>`_ (F9, F10)

Summary of the change
---------------------

A grab-bag of hardening fixes: missing key/nonce state checks (CMAC, OFB,
GMAC), input validation (XMD empty DST, SIV S2V component limit, malformed
``cipher/mode`` strings, CBC NoPadding, RC4 skip cap), key hygiene
(Ascon-AEAD128 scrubbing), factory provider-string filtering (KDF, MAC), an
out-of-bounds write fix in the CommonCrypto provider, the RFC 8439 length
limit on one-shot ChaCha20Poly1305 decryption, CCM reset-on-failure, and SM4
``parallelism()``/``provider()`` reporting for the x86 SM4 extension.

Findings
--------

Eleven deduplicated candidates were verified by independent agents; ten
survived (seven correctness, three cleanup/contract), one was refuted. The
most severe items cluster around three of the PR's own hardening commits
introducing new hazards.

F1 — SP800-56C extraction-MAC fallback order silently swapped: KAT-breaking behavior change
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reported upstream as issue
`#5904 <https://github.com/randombit/botan/issues/5904>`_. Upstream closed
it as "valid but I think non-issue in practice considering these KDFs only
make sense in the context of NIST/BSI and they don't allow BLAKE2".

Code:
`kdf.cpp#L184-L197 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/kdf/kdf.cpp#L184-L197>`_

.. code-block:: cpp

   if(req.algo_name() == "SP800-56C" && req.arg_count() == 1) {
      if(provider.empty() || provider == "base") {
         std::unique_ptr<KDF> exp(kdf_create_mac_or_hash<SP800_108_Feedback>(req.arg(0), 32, 32));
         if(exp) {
            if(auto mac = MessageAuthenticationCode::create(fmt("HMAC({})", req.arg(0)))) {   // now tried FIRST
               return std::make_unique<SP800_56C_Two_Step>(std::move(mac), std::move(exp));
            }
            if(auto mac = MessageAuthenticationCode::create(req.arg(0))) {                    // was tried first pre-PR
               return std::make_unique<SP800_56C_Two_Step>(std::move(mac), std::move(exp));
            }

The provider-filter commit also reordered the SP800-56C two-step lookup to
try ``HMAC(arg)`` before ``MessageAuthenticationCode::create(arg)``. For
``KDF::create("SP800-56C(Blake2b)")`` both lookups succeed (Blake2b is
registered as both a MAC and a hash), so the extraction PRF changed from
BLAKE2bMAC to HMAC(Blake2b): **the same algorithm string now derives
different key bytes.** No changelog entry, no test (sp800_56c.vec only
covers ``HMAC(...)`` spellings), no mention in the commit message ("filter
by provider string"). The new order is arguably more consistent with the
expand step, but it is an unannounced KAT-breaking change; keys derived
before the change no longer reproduce.

F2 — SIV: new S2V limit throws after CTR decryption — unauthenticated plaintext release and wedged object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reported upstream as issue
`#5905 <https://github.com/randombit/botan/issues/5905>`_.

Code:
`siv.cpp#L134-L141 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/modes/aead/siv/siv.cpp#L134-L141>`_
(the new check) and
`siv.cpp#L218-L237 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/modes/aead/siv/siv.cpp#L218-L237>`_
(decrypt-before-S2V):

.. code-block:: cpp

   secure_vector<uint8_t> SIV_Mode::S2V(const uint8_t* text, size_t text_len) {
      // S2V processes at most block_size()*8 - 1 (127 for a 128-bit block) components; ...
      const size_t s2v_components = m_ad_macs.size() + (m_nonce.empty() ? 0 : 1) + 1;
      if(s2v_components > block_size() * 8 - 1) {
         throw Invalid_Argument(name() + ": too many S2V components");   // NEW in PR 5742
      }

.. code-block:: cpp

   // SIV_Decryption::finish_msg
      if(buffer.size() != offset + V.size()) {
         set_ctr_iv(V);
         ctr().cipher(/* ... */);          // L225: plaintext already recovered in caller's buffer
      }
      const secure_vector<uint8_t> T = S2V(/* ... */);   // L228: new check throws HERE
      reset();                                           // L232: skipped on throw -> m_in_msg stays true
      if(!CT::is_equal<uint8_t>(T, V).as_bool()) {
         clear_mem(/* ... */);                           // L235: scrub also skipped
         throw Invalid_Authentication_Tag("SIV tag check failed");
      }

``SIV_Decryption::finish_msg`` CTR-decrypts the ciphertext in place (L225)
*before* calling ``S2V`` (L228). With 126 ADs (all accepted by
``set_associated_data_n``) plus a nonce, the new component-count check
throws — and the ``clear_mem`` scrub on the tag-failure path (L235) never
runs, so the caller's buffer holds fully decrypted, never-authenticated
plaintext, under ``Invalid_Argument`` rather than
``Invalid_Authentication_Tag``. ``reset()`` (L232) is also skipped, so
``m_in_msg`` stays true and every later ``start_msg`` /
``set_associated_data_n`` trips ``BOTAN_STATE_CHECK(!m_in_msg)`` until a
full ``clear()``/re-key. Fix: enforce the bound in
``set_associated_data_n``/``start_msg``, or at minimum hoist it above the
CTR pass.

F3 — ChaCha20Poly1305: length-limit throw fires after in-place decryption — unauthenticated plaintext release and stuck state
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reported upstream as issue
`#5906 <https://github.com/randombit/botan/issues/5906>`_.

Code:
`chacha20poly1305.cpp#L154-L182 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/modes/aead/chacha20poly1305/chacha20poly1305.cpp#L154-L182>`_

.. code-block:: cpp

   size_t ChaCha20Poly1305_Decryption::process_msg(uint8_t buf[], size_t sz) {
      BOTAN_STATE_CHECK(m_nonce_len > 0);
      m_poly1305->update(buf, sz);  // poly1305 of ciphertext
      m_chacha->cipher1(buf, sz);   // L157: decrypts in place FIRST
      m_ctext_len += sz;

      constexpr uint64_t MAX_CHACHA20POLY1305_INPUT = (static_cast<uint64_t>(1) << 38) - 64;
      if(cfrg_version() && m_ctext_len > MAX_CHACHA20POLY1305_INPUT) {
         throw Invalid_State("ChaCha20Poly1305 message length limit exceeded");  // L162: throws SECOND
      }
      return sz;
   }

   void ChaCha20Poly1305_Decryption::finish_msg(secure_vector<uint8_t>& buffer, size_t offset) {
      /* ... */
      if(remaining > 0) {
         // Route through process_msg so the RFC 8439 length limit is enforced for
         // one-shot decryption too (finish() calls finish_msg() directly).
         process_msg(buf, remaining);   // L181: NEW in PR 5742
      }

Routing decryption ``finish_msg`` through ``process_msg`` was meant to
enforce the RFC 8439 limit on the one-shot path, but ``process_msg`` runs
``m_chacha->cipher1(buf, sz)`` *first* (L157) and only then throws
``Invalid_State`` when ``m_ctext_len`` exceeds 2^38-64 (L162). On the final
chunk the caller's ``secure_vector`` already holds decrypted plaintext; the
tag check and its clear-on-failure (L203–205) are never reached, and
``m_ctext_len``/``m_nonce_len`` are not reset (only zeroed on the success
path, L200–201), so the next ``start()`` trips
``BOTAN_STATE_CHECK(m_nonce_len == 0)``. Requires ~256 GiB in one message —
exactly the boundary the check exists to police. Check the limit before
``cipher1``, or reset and scrub on the throw path.

F4 — SIV: limit contradicts ``maximum_associated_data_inputs()`` by one
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reported upstream as issue
`#5907 <https://github.com/randombit/botan/issues/5907>`_.

Code:
`siv.cpp#L85-L92 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/modes/aead/siv/siv.cpp#L85-L92>`_
vs.
`siv.cpp#L138-L140 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/modes/aead/siv/siv.cpp#L138-L140>`_

.. code-block:: cpp

   size_t SIV_Mode::maximum_associated_data_inputs() const {
      return block_size() * 8 - 2;                      // advertises 126 ADs
   }

   void SIV_Mode::set_associated_data_n(size_t n, std::span<const uint8_t> ad) {
      BOTAN_STATE_CHECK(!m_in_msg);
      const size_t max_ads = maximum_associated_data_inputs();
      if(n >= max_ads) {                                // accepts indices 0..125

.. code-block:: cpp

   const size_t s2v_components = m_ad_macs.size() + (m_nonce.empty() ? 0 : 1) + 1;
   if(s2v_components > block_size() * 8 - 1) {       // 126 ADs + nonce + plaintext = 128 > 127

``maximum_associated_data_inputs()`` advertises ``block_size()*8-2 = 126``
AD inputs, and ``set_associated_data_n`` accepts all 126. With any nonce the
new check computes 126+1+1 = 128 > 127 and throws from ``finish()`` —
rejecting a call sequence the public API explicitly permits, and only at
finalization time. The test suite only probes the first rejected index, so
it never hits this. Fix: ``maximum_associated_data_inputs()`` should reserve
slots for nonce and plaintext (return ``block_size()*8-3``) and rejection
should happen eagerly in ``set_associated_data_n``.

F5 — GMAC: the new nonce guard cannot fire for its stated purpose
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reported upstream as issue
`#5908 <https://github.com/randombit/botan/issues/5908>`_.

Code:
`gmac.cpp#L51-L54 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/mac/gmac/gmac.cpp#L51-L54>`_,
flag set at
`gmac.cpp#L90 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/mac/gmac/gmac.cpp#L90>`_,
never cleared in
`final_result, gmac.cpp#L93-L104 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/mac/gmac/gmac.cpp#L93-L104>`_

.. code-block:: cpp

   void GMAC::add_data(std::span<const uint8_t> input) {
      if(!m_initialized) {                                        // NEW in PR 5742
         throw Invalid_State("GMAC was not used with a fresh nonce");
      }
      /* ... */
   }

   void GMAC::final_result(std::span<uint8_t> mac) {
      if(!m_initialized) { /* throw */ }
      m_ghash->final(mac.first(output_length()));
      m_ghash->reset_associated_data();
      // m_initialized is NOT set to false here
   }

``m_initialized`` is set in ``start_msg`` (L90) and cleared only in
``clear()`` — ``final_result()`` leaves it true. So ``set_key; start(iv);
update; final; update; final`` passes the new guard on the second ``update``
(absorbing data into scrubbed GHASH state) and then throws an opaque
``BOTAN_STATE_CHECK(m_nonce)`` from ``GHASH::final`` instead of the intended
"GMAC was not used with a fresh nonce". ``final_result()`` should set
``m_initialized = false`` so the guard fires at the point of misuse with the
right message.

F6 — Ascon-AEAD128: destructor scrubs the key copy but not the key-derived sponge state
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reported upstream as issue
`#5909 <https://github.com/randombit/botan/issues/5909>`_.

Code:
`ascon_aead128.cpp#L50-L54 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/modes/aead/ascon_aead128/ascon_aead128.cpp#L50-L54>`_;
state type at
`sponge.h#L26-L29 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/permutations/sponge/sponge.h#L26-L29>`_

.. code-block:: cpp

   Ascon_AEAD128_Mode::~Ascon_AEAD128_Mode() {
      if(m_key.has_value()) {
         secure_scrub_memory(*m_key);     // scrubs the key copy...
      }
   }                                      // ...but m_ascon_p (key-derived state) is destroyed unscrubbed

.. code-block:: cpp

   class Sponge {
      /* ... */
      using state_t = std::array<word, words>;   // plain array, no scrubbing destructor

``start_msg`` loads IV||K||N into the Ascon permutation state and XORs the key
into state words 3–4; ``Ascon_p`` is a ``Sponge<...>`` whose state is a
plain ``std::array`` with no scrubbing destructor. Destroying the object
between ``start()`` and ``finish()`` (e.g. the "input did not include the
tag" ``BOTAN_ARG_CHECK`` throw, or simply dropping the mode mid-message)
leaves 320 bits of key-derived state in freed memory — enough to
decrypt/forge for that nonce. ``reset()`` would not help: its plain
re-assignment is compiler-elidable. Scrub ``m_ascon_p.state()`` in the
destructor or give ``Sponge`` a scrubbing destructor. (Side note: the
defaulted public copy/move constructors with deleted assignments are a
rule-of-five asymmetry a self-scrubbing member would remove.)

F7 — ``cipher/mode`` parsing hardening is incomplete: trailing slash still throws
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reported upstream as issue
`#5910 <https://github.com/randombit/botan/issues/5910>`_.

Code:
`aead.cpp#L87-L89 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/modes/aead/aead.cpp#L87-L89>`_,
duplicated at
`cipher_mode.cpp#L85-L87 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/modes/cipher_mode.cpp#L85-L87>`_;
the throw is in
`split_on, parsing.cpp#L141-L162 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/utils/parsing.cpp#L141-L162>`_

.. code-block:: cpp

      const std::vector<std::string> algo_parts = split_on(algo, '/');   // throws for "AES-128/"
      if(algo_parts.size() < 2) {                                        // NEW guard: unreachable for that input
         return std::unique_ptr<AEAD_Mode>();
      }

.. code-block:: cpp

   // split_on: empty leading components are dropped, but...
      if(substr.empty()) {
         throw Invalid_Argument(fmt("Unable to split string '{}", str));    // trailing delimiter throws
      }

The new ``algo_parts.size() < 2`` guard fixes the leading-slash
out-of-bounds read (real UB, since ``split_on`` drops empty leading
components), but a *trailing* empty component makes ``split_on`` itself
throw ``Invalid_Argument`` before the guard is reached. So
``Cipher_Mode::create("AES-128/", dir)`` still throws out of a factory
documented to return nullptr for unknown names; through FFI,
``botan_cipher_init`` returns ``EXCEPTION_THROWN`` instead of
``NOT_IMPLEMENTED``. Reject names ending in ``/`` before splitting, or wrap
``split_on``.

F8 — RC4 skip cap throws through nullptr-contract factories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reported upstream as issue
`#5911 <https://github.com/randombit/botan/issues/5911>`_.

Code:
`rc4.cpp#L141-L143 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/stream/rc4/rc4.cpp#L141-L143>`_

.. code-block:: cpp

   RC4::RC4(size_t s) : m_SKIP(s) {
      BOTAN_ARG_CHECK(m_SKIP <= 64 * 1024, "Invalid skip parameter for RC4");
   }

The new cap propagates through ``StreamCipher::create("RC4(100000)")``,
``probe_providers_of``, and ``BlockCipher::create("Lion(SHA-1,RC4(70000),64)")``
— all documented to return nullptr for unsupported names. Mitigating:
pre-existing convention (``ChaCha(7)``, ``CTR-BE(...,99)`` already throw
through create), so a contract-consistency nit rather than a new regression;
validating in ``StreamCipher::create`` and returning nullptr would be
cleaner.

F9 — Cleanup: provider filter copy-pasted per algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reported upstream, together with F10, as issue
`#5912 <https://github.com/randombit/botan/issues/5912>`_.

Code: 13 guards in
`kdf.cpp <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/kdf/kdf.cpp>`_
and 9 in
`mac.cpp <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/mac/mac.cpp>`_
(e.g.
`mac.cpp#L56-L58 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/mac/mac.cpp#L56-L58>`_);
the single-guard idiom exists at
`hash.cpp#L122 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/hash/hash.cpp#L122>`_
and
`block_cipher.cpp#L111 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/block/block_cipher.cpp#L111>`_

.. code-block:: cpp

   // repeated 13x in kdf.cpp / 9x in mac.cpp:
         if(provider.empty() || provider == "base") { /* construct */ }

   // vs. the idiom hash.cpp/block_cipher.cpp already use, once at the top:
      if(provider.empty() == false && provider != "base") {
         return nullptr;
      }

Neither ``create()`` has any non-base provider branch (both end with
``BOTAN_UNUSED(provider); return nullptr;``), so a single top-of-function
early return is behaviorally identical and deletes every copy. As written,
each future algorithm must remember the wrapper; forgetting it is exactly
the bug class this PR fixes.

F10 — Cleanup: duplicated CBC NoPadding check
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reported upstream, together with F9, as issue
`#5912 <https://github.com/randombit/botan/issues/5912>`_.

Code:
`cbc.cpp#L135-L137 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/modes/cbc/cbc.cpp#L135-L137>`_
vs.
`cbc.cpp#L103 <https://github.com/randombit/botan/blob/4f40410b6bc2c7c7426482b3091e7d0f9c2faddd/src/lib/modes/cbc/cbc.cpp#L103>`_

.. code-block:: cpp

   // finish_msg (NEW in PR 5742):
   BOTAN_ARG_CHECK(buffer.size() % BS == offset % BS, "CBC input is not full blocks (NoPadding)");
   update(buffer, offset);          // forwards to process_msg, whose first line is:

   // process_msg (pre-existing):
   BOTAN_ARG_CHECK(sz % BS == 0, "CBC input is not full blocks");

The new check duplicates the identical condition that fires one call later
in ``process_msg`` — same ``Invalid_Argument`` type, fires before any state
is touched. Deleting the old ``BOTAN_ASSERT_EQUAL`` alone would have
achieved the commit's goal; the codebase now carries two near-identical
messages for one condition. (Side note: ``CBC_Decryption`` throws
``Decoding_Error`` for the same condition — the encrypt/decrypt exception
types remain asymmetric.)

Refuted during verification
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **CCM reset-comment claim** ("matching GCM/SIV/ChaCha20Poly1305"): the GCM
  and EAX failure paths were shown to already be equivalent to ``reset()``,
  so the comment's parity claim holds semantically. Dropped.

Verdict
-------

Most of the PR's fixes are sound and worthwhile (the CommonCrypto OOB write
fix, the missing state checks, the parsing UB fix, CCM reset). But since the
PR is already merged, findings F1–F3 deserve follow-up on master as real
defects introduced by the hardening itself: an unannounced key-derivation
change (SP800-56C), and two throw-after-decrypt paths (SIV,
ChaCha20Poly1305) that release unauthenticated plaintext and wedge the mode
object. Findings F4–F8 are smaller correctness/contract gaps; F9–F10 are
cleanups. All findings were reported upstream as the GitHub issues listed
above.
