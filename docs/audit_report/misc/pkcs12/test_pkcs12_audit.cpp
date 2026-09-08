/*
* PKCS#12 audit tests: state transitions, parameter variations and
* hostile-input behaviour of the PKCS#12/PFX implementation.
*
* (C) 2026 Falko Strenzke (cryptosource GmbH), written with Anthropic's Fable
*
* Botan is released under the Simplified BSD License (see license.txt)
*/

#include "tests.h"

#if defined(BOTAN_HAS_PKCS12) && defined(BOTAN_HAS_ECDSA) && defined(BOTAN_HAS_PKCS5_PBES2) && \
   defined(BOTAN_HAS_X509_CERTIFICATES)

   #include <botan/asn1_obj.h>
   #include <botan/ber_dec.h>
   #include <botan/bigint.h>
   #include <botan/cipher_mode.h>
   #include <botan/der_enc.h>
   #include <botan/ec_group.h>
   #include <botan/ecdsa.h>
   #include <botan/exceptn.h>
   #include <botan/hash.h>
   #include <botan/mac.h>
   #include <botan/pkcs12.h>
   #include <botan/pkcs8.h>
   #include <botan/pubkey.h>
   #include <botan/pwdhash.h>
   #include <botan/rng.h>
   #include <botan/x509cert.h>
   #include <botan/x509self.h>
   #include <botan/internal/fmt.h>
   #include <botan/internal/pkcs12_kdf.h>

   #include <algorithm>
   #include <chrono>
   #include <map>
   #include <set>
   #include <typeinfo>

namespace Botan_Tests {

namespace {

// --------------------------------------------------------------------------
// Generic helpers
// --------------------------------------------------------------------------

using Bytes = std::vector<uint8_t>;

Bytes bytes_of(std::string_view s) {
   return Bytes(s.begin(), s.end());
}

// A stable fingerprint of everything an application can observe in a bundle.
Bytes bundle_fingerprint(const Botan::PKCS12& p) {
   Bytes fp;
   for(const auto& k : p.private_keys()) {
      const auto bits = k->private_key_bits();
      fp.insert(fp.end(), bits.begin(), bits.end());
      fp.push_back(0xAA);
   }
   for(const auto& c : p.certificates()) {
      const auto der = c.BER_encode();
      fp.insert(fp.end(), der.begin(), der.end());
      fp.push_back(0xBB);
   }
   if(p.friendly_name()) {
      const auto n = bytes_of(*p.friendly_name());
      fp.insert(fp.end(), n.begin(), n.end());
   }
   fp.push_back(0xCC);
   if(p.local_key_id()) {
      fp.insert(fp.end(), p.local_key_id()->begin(), p.local_key_id()->end());
   }
   fp.push_back(0xDD);
   for(const auto& oid : p.unknown_bag_types()) {
      const auto n = bytes_of(oid.to_string());
      fp.insert(fp.end(), n.begin(), n.end());
   }
   return fp;
}

double elapsed_ms(const std::chrono::steady_clock::time_point& start) {
   const auto d = std::chrono::steady_clock::now() - start;
   return static_cast<double>(std::chrono::duration_cast<std::chrono::microseconds>(d).count()) / 1000.0;
}

struct TestCredentials {
      std::shared_ptr<Botan::ECDSA_PrivateKey> key;
      Botan::X509_Certificate cert;
};

TestCredentials generate_credentials(Botan::RandomNumberGenerator& rng, const std::string& cn) {
   TestCredentials creds;
   creds.key = std::make_shared<Botan::ECDSA_PrivateKey>(rng, Botan::EC_Group::from_name("secp256r1"));

   Botan::X509_Cert_Options opts;
   opts.common_name = cn;
   opts.country = "DE";
   opts.organization = "P663 Audit";
   opts.dns = "localhost";

   creds.cert = Botan::X509::create_self_signed_cert(opts, *creds.key, "SHA-256", rng);
   return creds;
}

// UCS-2 BE + two byte terminator, as required by RFC 7292 Appendix B.1
Bytes rfc7292_password_bytes(std::string_view ascii_password) {
   Bytes out;
   for(const char c : ascii_password) {
      out.push_back(0x00);
      out.push_back(static_cast<uint8_t>(c));
   }
   out.push_back(0x00);
   out.push_back(0x00);
   return out;
}

// --------------------------------------------------------------------------
// DER builders for hand-crafted PFX structures
// --------------------------------------------------------------------------

struct BagAttrs {
      std::optional<std::string> friendly_name = std::nullopt;
      bool friendly_name_as_utf8string = false;
      std::optional<Bytes> local_key_id = std::nullopt;
      bool add_unknown_attribute = false;
      bool duplicate_friendly_name_value = false;
      bool emit_empty_set = false;

      bool any() const {
         return friendly_name.has_value() || local_key_id.has_value() || add_unknown_attribute || emit_empty_set;
      }
};

void encode_bmp(Botan::DER_Encoder& enc, std::string_view s) {
   Bytes ucs2;
   for(const char c : s) {
      ucs2.push_back(0x00);
      ucs2.push_back(static_cast<uint8_t>(c));
   }
   enc.add_object(Botan::ASN1_Type::BmpString, Botan::ASN1_Class::Universal, ucs2);
}

void encode_attrs(Botan::DER_Encoder& enc, const BagAttrs& attrs) {
   if(!attrs.any()) {
      return;
   }
   enc.start_set();
   if(attrs.friendly_name) {
      enc.start_sequence();
      enc.encode(Botan::OID::from_string("PKCS9.FriendlyName"));
      enc.start_set();
      if(attrs.friendly_name_as_utf8string) {
         enc.encode(Botan::ASN1_String(*attrs.friendly_name, Botan::ASN1_Type::Utf8String));
      } else {
         encode_bmp(enc, *attrs.friendly_name);
      }
      if(attrs.duplicate_friendly_name_value) {
         encode_bmp(enc, "second value");
      }
      enc.end_cons();
      enc.end_cons();
   }
   if(attrs.local_key_id) {
      enc.start_sequence();
      enc.encode(Botan::OID::from_string("PKCS9.LocalKeyId"));
      enc.start_set();
      enc.encode(*attrs.local_key_id, Botan::ASN1_Type::OctetString);
      enc.end_cons();
      enc.end_cons();
   }
   if(attrs.add_unknown_attribute) {
      enc.start_sequence();
      enc.encode(Botan::OID("1.2.840.113549.1.9.99"));
      enc.start_set();
      enc.encode(Bytes{1, 2, 3}, Botan::ASN1_Type::OctetString);
      enc.end_cons();
      enc.end_cons();
   }
   enc.end_cons();
}

Bytes der_cert_bag(const Botan::X509_Certificate& cert, const BagAttrs& attrs = {}, bool unknown_cert_type = false) {
   Bytes out;
   Botan::DER_Encoder enc(out);
   enc.start_sequence();
   enc.encode(Botan::OID::from_string("PKCS12.CertBag"));
   enc.start_context_specific(0);
   enc.start_sequence();
   if(unknown_cert_type) {
      enc.encode(Botan::OID("1.2.840.113549.1.9.22.2"));  // sdsiCertificate
      enc.start_context_specific(0);
      enc.encode(Botan::ASN1_String("not a cert", Botan::ASN1_Type::Ia5String));
      enc.end_cons();
   } else {
      enc.encode(Botan::OID::from_string("PKCS9.X509Certificate"));
      enc.start_context_specific(0);
      enc.encode(cert.BER_encode(), Botan::ASN1_Type::OctetString);
      enc.end_cons();
   }
   enc.end_cons();
   enc.end_cons();
   encode_attrs(enc, attrs);
   enc.end_cons();
   return out;
}

Bytes der_key_bag_raw(const Bytes& pkcs8_der, const BagAttrs& attrs = {}) {
   Bytes out;
   Botan::DER_Encoder enc(out);
   enc.start_sequence();
   enc.encode(Botan::OID::from_string("PKCS12.KeyBag"));
   enc.start_context_specific(0);
   enc.raw_bytes(pkcs8_der);
   enc.end_cons();
   encode_attrs(enc, attrs);
   enc.end_cons();
   return out;
}

Bytes der_key_bag(const Botan::Private_Key& key, const BagAttrs& attrs = {}) {
   const auto p8 = Botan::PKCS8::BER_encode(key);
   return der_key_bag_raw(Bytes(p8.begin(), p8.end()), attrs);
}

Bytes der_shrouded_key_bag(const Botan::AlgorithmIdentifier& alg, const Bytes& ciphertext, const BagAttrs& attrs = {}) {
   Bytes out;
   Botan::DER_Encoder enc(out);
   enc.start_sequence();
   enc.encode(Botan::OID::from_string("PKCS12.PKCS8ShroudedKeyBag"));
   enc.start_context_specific(0);
   enc.start_sequence();
   enc.encode(alg);
   enc.encode(ciphertext, Botan::ASN1_Type::OctetString);
   enc.end_cons();
   enc.end_cons();
   encode_attrs(enc, attrs);
   enc.end_cons();
   return out;
}

Bytes der_safe_contents(const std::vector<Bytes>& bags) {
   Bytes out;
   Botan::DER_Encoder enc(out);
   enc.start_sequence();
   for(const auto& b : bags) {
      enc.raw_bytes(b);
   }
   enc.end_cons();
   return out;
}

Bytes der_safe_contents_bag(const Bytes& inner_safe_contents, const BagAttrs& attrs = {}) {
   Bytes out;
   Botan::DER_Encoder enc(out);
   enc.start_sequence();
   enc.encode(Botan::OID::from_string("PKCS12.SafeContentsBag"));
   enc.start_context_specific(0);
   enc.raw_bytes(inner_safe_contents);
   enc.end_cons();
   encode_attrs(enc, attrs);
   enc.end_cons();
   return out;
}

Bytes der_content_info_data(const Bytes& safe_contents) {
   Bytes out;
   Botan::DER_Encoder enc(out);
   enc.start_sequence();
   enc.encode(Botan::OID::from_string("PKCS7.Data"));
   enc.start_context_specific(0);
   enc.encode(safe_contents, Botan::ASN1_Type::OctetString);
   enc.end_cons();
   enc.end_cons();
   return out;
}

Bytes der_content_info_encrypted(const Botan::AlgorithmIdentifier& alg,
                                 const Bytes& ciphertext,
                                 size_t version = 0,
                                 const Botan::OID& inner_type = Botan::OID::from_string("PKCS7.Data")) {
   Bytes out;
   Botan::DER_Encoder enc(out);
   enc.start_sequence();
   enc.encode(Botan::OID::from_string("PKCS7.EncryptedData"));
   enc.start_context_specific(0);
   enc.start_sequence();
   enc.encode(version);
   enc.start_sequence();
   enc.encode(inner_type);
   enc.encode(alg);
   enc.add_object(Botan::ASN1_Type(0), Botan::ASN1_Class::ContextSpecific, ciphertext);
   enc.end_cons();
   enc.end_cons();
   enc.end_cons();
   enc.end_cons();
   return out;
}

Bytes der_authenticated_safe(const std::vector<Bytes>& content_infos) {
   Bytes out;
   Botan::DER_Encoder enc(out);
   enc.start_sequence();
   for(const auto& ci : content_infos) {
      enc.raw_bytes(ci);
   }
   enc.end_cons();
   return out;
}

Bytes pkcs12_mac_key(std::string_view password,
                     const std::string& hash_name,
                     const Bytes& salt,
                     size_t iterations,
                     bool openssl_empty_pwd) {
   auto hash = Botan::HashFunction::create_or_throw(hash_name);
   Bytes key(hash->output_length());
   if(openssl_empty_pwd) {
      Botan::pkcs12_kdf(key, {}, salt, iterations, 3, *hash);
   } else {
      auto fam = Botan::PasswordHashFamily::create_or_throw(Botan::fmt("PKCS12-KDF({},3)", hash_name));
      auto pwhash = fam->from_iterations(iterations);
      pwhash->derive_key(key.data(), key.size(), password.data(), password.size(), salt.data(), salt.size());
   }
   return key;
}

Bytes compute_pkcs12_mac(const Bytes& auth_safe_der,
                         std::string_view password,
                         const std::string& hash_name,
                         const Bytes& salt,
                         size_t iterations,
                         bool openssl_empty_pwd = false) {
   const auto key = pkcs12_mac_key(password, hash_name, salt, iterations, openssl_empty_pwd);
   auto hmac = Botan::MessageAuthenticationCode::create_or_throw(Botan::fmt("HMAC({})", hash_name));
   hmac->set_key(key);
   hmac->update(auth_safe_der);
   return Botan::unlock(hmac->final());
}

struct MacSpec {
      std::string hash = "SHA-256";
      Bytes salt = Bytes(32, 0x5A);
      size_t iterations = 1;
      bool omit_iterations = false;  // rely on DEFAULT 1
      bool openssl_empty_pwd = false;
      std::optional<Bytes> override_mac_value = std::nullopt;
      std::optional<Botan::BigInt> override_iterations_integer = std::nullopt;
      std::optional<Botan::OID> override_digest_oid = std::nullopt;
      bool digest_null_param = false;
};

Bytes der_pfx(const Bytes& auth_safe_der,
              std::string_view password,
              const std::optional<MacSpec>& mac,
              size_t pfx_version = 3) {
   Bytes out;
   Botan::DER_Encoder enc(out);
   enc.start_sequence();
   enc.encode(pfx_version);
   enc.raw_bytes(der_content_info_data(auth_safe_der));
   if(mac) {
      const Bytes mac_value =
         mac->override_mac_value
            ? *mac->override_mac_value
            : compute_pkcs12_mac(auth_safe_der, password, mac->hash, mac->salt, mac->iterations, mac->openssl_empty_pwd);
      const Botan::OID digest_oid = mac->override_digest_oid ? *mac->override_digest_oid : Botan::OID::from_string(mac->hash);
      enc.start_sequence();
      enc.start_sequence();
      if(mac->digest_null_param) {
         enc.encode(Botan::AlgorithmIdentifier(digest_oid, Botan::AlgorithmIdentifier::USE_NULL_PARAM));
      } else {
         enc.encode(Botan::AlgorithmIdentifier(digest_oid, Botan::AlgorithmIdentifier::USE_EMPTY_PARAM));
      }
      enc.encode(mac_value, Botan::ASN1_Type::OctetString);
      enc.end_cons();
      enc.encode(mac->salt, Botan::ASN1_Type::OctetString);
      if(mac->override_iterations_integer) {
         enc.encode(*mac->override_iterations_integer);
      } else if(!mac->omit_iterations) {
         enc.encode(mac->iterations);
      }
      enc.end_cons();
   }
   enc.end_cons();
   return out;
}

// Convenience: single Data content info holding the given bags
Bytes simple_pfx(const std::vector<Bytes>& bags, std::string_view password, const std::optional<MacSpec>& mac) {
   return der_pfx(der_authenticated_safe({der_content_info_data(der_safe_contents(bags))}), password, mac);
}

// PKCS#12 PBE (RFC 7292 B.2) 3DES-CBC encryption, implemented here from the
// public API to independently cross-check the library's shrouded key bags.
struct PbeResult {
      Botan::AlgorithmIdentifier alg;
      Bytes ciphertext;
};

PbeResult pbe_sha1_3des_encrypt(const Bytes& plaintext,
                                const Bytes& kdf_password_bytes,
                                const Bytes& salt,
                                size_t iterations,
                                bool two_key) {
   auto sha1 = Botan::HashFunction::create_or_throw("SHA-1");
   Bytes key(two_key ? 16 : 24);
   Bytes iv(8);
   Botan::pkcs12_kdf(key, kdf_password_bytes, salt, iterations, 1, *sha1);
   Botan::pkcs12_kdf(iv, kdf_password_bytes, salt, iterations, 2, *sha1);
   if(two_key) {
      key.insert(key.end(), key.begin(), key.begin() + 8);  // K1 || K2 || K1
   }
   auto enc = Botan::Cipher_Mode::create_or_throw("TripleDES/CBC", Botan::Cipher_Dir::Encryption);
   enc->set_key(key);
   enc->start(iv);
   Botan::secure_vector<uint8_t> buf(plaintext.begin(), plaintext.end());
   enc->finish(buf);

   Bytes params;
   Botan::DER_Encoder(params).start_sequence().encode(salt, Botan::ASN1_Type::OctetString).encode(iterations).end_cons();
   const std::string oid_name = two_key ? "PBE-SHA1-2DES" : "PBE-SHA1-3DES";
   return {Botan::AlgorithmIdentifier(Botan::OID::from_string(oid_name), params), Botan::unlock(buf)};
}

Bytes pbe_sha1_3des_decrypt(const Bytes& ciphertext,
                            const Bytes& kdf_password_bytes,
                            const Bytes& salt,
                            size_t iterations,
                            bool two_key) {
   auto sha1 = Botan::HashFunction::create_or_throw("SHA-1");
   Bytes key(two_key ? 16 : 24);
   Bytes iv(8);
   Botan::pkcs12_kdf(key, kdf_password_bytes, salt, iterations, 1, *sha1);
   Botan::pkcs12_kdf(iv, kdf_password_bytes, salt, iterations, 2, *sha1);
   if(two_key) {
      key.insert(key.end(), key.begin(), key.begin() + 8);
   }
   auto dec = Botan::Cipher_Mode::create_or_throw("TripleDES/CBC", Botan::Cipher_Dir::Decryption);
   dec->set_key(key);
   dec->start(iv);
   Botan::secure_vector<uint8_t> buf(ciphertext.begin(), ciphertext.end());
   dec->finish(buf);
   return Botan::unlock(buf);
}

Botan::AlgorithmIdentifier pbe_sha1_3des_alg_id(const Bytes& salt, const Botan::BigInt& iterations, bool two_key) {
   Bytes params;
   Botan::DER_Encoder(params).start_sequence().encode(salt, Botan::ASN1_Type::OctetString).encode(iterations).end_cons();
   const std::string oid_name = two_key ? "PBE-SHA1-2DES" : "PBE-SHA1-3DES";
   return Botan::AlgorithmIdentifier(Botan::OID::from_string(oid_name), params);
}

// DER encode an OCTET STRING (for use as AlgorithmIdentifier parameters)
Bytes der_octet_string(const Bytes& v) {
   Bytes out;
   Botan::DER_Encoder(out).encode(v, Botan::ASN1_Type::OctetString);
   return out;
}

Botan::AlgorithmIdentifier pbes2_pbkdf2_alg_id(const Botan::BigInt& iterations) {
   Bytes kdf_params;
   Botan::DER_Encoder(kdf_params)
      .start_sequence()
      .encode(Bytes(16, 0x11), Botan::ASN1_Type::OctetString)
      .encode(iterations)
      .encode(Botan::AlgorithmIdentifier("HMAC(SHA-256)", Botan::AlgorithmIdentifier::USE_NULL_PARAM))
      .end_cons();
   Bytes params;
   Botan::DER_Encoder(params)
      .start_sequence()
      .encode(Botan::AlgorithmIdentifier(Botan::OID::from_string("PKCS5.PBKDF2"), kdf_params))
      .encode(Botan::AlgorithmIdentifier(Botan::OID::from_string("AES-256/CBC"), der_octet_string(Bytes(16, 0x22))))
      .end_cons();
   return Botan::AlgorithmIdentifier(Botan::OID::from_string("PBE-PKCS5v20"), params);
}

Botan::AlgorithmIdentifier pbes2_scrypt_alg_id(size_t N, size_t r, size_t p) {
   Bytes kdf_params;
   Botan::DER_Encoder(kdf_params)
      .start_sequence()
      .encode(Bytes(16, 0x11), Botan::ASN1_Type::OctetString)
      .encode(N)
      .encode(r)
      .encode(p)
      .end_cons();
   Bytes params;
   Botan::DER_Encoder(params)
      .start_sequence()
      .encode(Botan::AlgorithmIdentifier(Botan::OID::from_string("Scrypt"), kdf_params))
      .encode(Botan::AlgorithmIdentifier(Botan::OID::from_string("AES-256/CBC"), der_octet_string(Bytes(16, 0x22))))
      .end_cons();
   return Botan::AlgorithmIdentifier(Botan::OID::from_string("PBE-PKCS5v20"), params);
}

// Walk an exported PFX (unencrypted certs, no MAC or MAC) and return the
// first PKCS8ShroudedKeyBag (algorithm identifier + ciphertext)
std::optional<std::pair<Botan::AlgorithmIdentifier, Bytes>> extract_first_shrouded_bag(const Bytes& pfx) {
   Botan::BER_Decoder outer(pfx);
   Botan::BER_Decoder pfx_seq = outer.start_sequence();
   size_t version = 0;
   pfx_seq.decode(version);
   Botan::BER_Decoder auth_safe_ci = pfx_seq.start_sequence();
   Botan::OID type;
   auth_safe_ci.decode(type);
   Bytes auth_safe;
   auth_safe_ci.start_context_specific(0).decode(auth_safe, Botan::ASN1_Type::OctetString);

   Botan::BER_Decoder as_dec(auth_safe);
   Botan::BER_Decoder as_seq = as_dec.start_sequence();
   while(as_seq.more_items()) {
      Botan::BER_Decoder ci = as_seq.start_sequence();
      Botan::OID ct;
      ci.decode(ct);
      if(ct != Botan::OID::from_string("PKCS7.Data")) {
         ci.discard_remaining();
         continue;
      }
      Bytes sc;
      ci.start_context_specific(0).decode(sc, Botan::ASN1_Type::OctetString);
      Botan::BER_Decoder sc_dec(sc);
      Botan::BER_Decoder bags = sc_dec.start_sequence();
      while(bags.more_items()) {
         Botan::BER_Decoder bag = bags.start_sequence();
         Botan::OID bag_type;
         bag.decode(bag_type);
         if(bag_type == Botan::OID::from_string("PKCS12.PKCS8ShroudedKeyBag")) {
            Botan::BER_Decoder val = bag.start_context_specific(0).start_sequence();
            Botan::AlgorithmIdentifier alg;
            Bytes ct_bytes;
            val.decode(alg);
            val.decode(ct_bytes, Botan::ASN1_Type::OctetString);
            return std::make_pair(alg, ct_bytes);
         }
         bag.discard_remaining();
      }
   }
   return std::nullopt;
}

// Re-encode a PFX without its MacData (simulating an attacker stripping the MAC)
Bytes strip_mac(const Bytes& pfx) {
   Botan::BER_Decoder outer(pfx);
   Botan::BER_Decoder pfx_seq = outer.start_sequence();
   size_t version = 0;
   pfx_seq.decode(version);
   const Botan::BER_Object auth_safe = pfx_seq.get_next_object();

   Bytes out;
   Botan::DER_Encoder enc(out);
   enc.start_sequence();
   enc.encode(version);
   enc.add_object(auth_safe.type_tag(), auth_safe.class_tag(), auth_safe.bits(), auth_safe.length());
   enc.end_cons();
   return out;
}

// Locate a byte pattern; returns position or nullopt
std::optional<size_t> find_bytes(const Bytes& haystack, const Bytes& needle) {
   const auto it = std::search(haystack.begin(), haystack.end(), needle.begin(), needle.end());
   if(it == haystack.end()) {
      return std::nullopt;
   }
   return static_cast<size_t>(std::distance(haystack.begin(), it));
}

// Outcome classification for hostile-input sweeps
enum class ParseOutcome : uint8_t {
   Ok,
   AuthTagError,
   DecodingError,
   OtherBotanException,
   NonBotanException,
};

struct SweepOutcome {
      ParseOutcome outcome;
      std::string type_name;
      std::optional<Bytes> fingerprint;
};

SweepOutcome try_parse(const Bytes& data, std::string_view password) {
   try {
      const Botan::PKCS12 p(data, password);
      return {ParseOutcome::Ok, "", bundle_fingerprint(p)};
   } catch(const Botan::Invalid_Authentication_Tag& e) {
      return {ParseOutcome::AuthTagError, typeid(e).name(), std::nullopt};
   } catch(const Botan::Decoding_Error& e) {
      return {ParseOutcome::DecodingError, typeid(e).name(), std::nullopt};
   } catch(const Botan::Exception& e) {
      return {ParseOutcome::OtherBotanException, typeid(e).name(), std::nullopt};
   } catch(const std::exception& e) {
      return {ParseOutcome::NonBotanException, typeid(e).name(), std::nullopt};
   }
}

class PKCS12_Audit_Tests final : public Test {
   public:
      std::vector<Test::Result> run() override {
         std::vector<Test::Result> results;

         results.push_back(test_state_empty_bundle());
         results.push_back(test_state_key_only_and_cert_only());
         results.push_back(test_state_key_cert_matching_order());
         results.push_back(test_state_parse_mutate_reexport());
         results.push_back(test_state_export_is_randomized_and_const());
         results.push_back(test_state_attribute_precedence());
         results.push_back(test_state_password_change());

         results.push_back(test_options_validation());
         results.push_back(test_options_iteration_boundaries());

         results.push_back(test_parameter_matrix());
         results.push_back(test_password_edge_cases());
         results.push_back(test_kdf_password_encoding_contract());
         results.push_back(test_legacy_pbe_independent_reimplementation());
         results.push_back(test_export_salt_uniqueness());

         results.push_back(test_mac_first_ordering());
         results.push_back(test_mac_data_variations());
         results.push_back(test_mac_stripping_and_substitution());
         results.push_back(test_unauthenticated_cbc_error_distinguishability());
         results.push_back(test_bitflip_sweep("modern", true));
         results.push_back(test_bitflip_sweep("legacy", false));
         results.push_back(test_truncation_sweep());

         results.push_back(test_crafted_attributes_and_ordering());
         results.push_back(test_crafted_nesting_boundary());
         results.push_back(test_crafted_encrypted_data_variants());
         results.push_back(test_crafted_shrouded_key_cost_limits());
         results.push_back(test_crafted_misc_structures());
         results.push_back(test_openssl_empty_password_convention());

         return results;
      }

   private:
      // ---------------------------------------------------------------
      // State transitions of the PKCS12 object
      // ---------------------------------------------------------------

      static Test::Result test_state_empty_bundle() {
         Test::Result result("PKCS12 audit: empty bundle state");
         auto rng = Test::new_rng("pkcs12_audit_empty");

         const Botan::PKCS12 empty;
         result.test_sz_eq("no keys", empty.private_keys().size(), 0);
         result.test_sz_eq("no certs", empty.certificates().size(), 0);
         result.test_is_false("no end entity", empty.end_entity_certificate().has_value());
         result.test_sz_eq("no ca certs", empty.ca_certificates().size(), 0);
         result.test_is_false("no friendly name", empty.friendly_name().has_value());
         result.test_is_false("no local key id", empty.local_key_id().has_value());
         result.test_sz_eq("no unknown bags", empty.unknown_bag_types().size(), 0);

         result.test_throws<Botan::Invalid_Argument>("export of empty bundle rejected", [&]() {
            (void)empty.export_to(Botan::PKCS12_Export_Options("pw"), *rng);
         });

         // Option validation happens only after the emptiness check:
         // an empty bundle with invalid options reports the emptiness first.
         result.test_throws<Botan::Invalid_Argument>("export of empty bundle with bad options rejected", [&]() {
            (void)empty.export_to(Botan::PKCS12_Export_Options("pw").with_iterations(0), *rng);
         });

         // A PFX with an empty AuthenticatedSafe parses to an empty bundle
         const auto pfx = der_pfx(der_authenticated_safe({}), "pw", MacSpec{});
         const Botan::PKCS12 parsed_empty(pfx, "pw");
         result.test_sz_eq("parsed empty: no keys", parsed_empty.private_keys().size(), 0);
         result.test_sz_eq("parsed empty: no certs", parsed_empty.certificates().size(), 0);
         result.test_throws<Botan::Invalid_Argument>("parsed empty bundle cannot be re-exported", [&]() {
            (void)parsed_empty.export_to(Botan::PKCS12_Export_Options("pw"), *rng);
         });

         // Empty SafeContents inside a Data ContentInfo also parses
         const auto pfx2 = simple_pfx({}, "pw", MacSpec{});
         const Botan::PKCS12 parsed_empty2(pfx2, "pw");
         result.test_sz_eq("parsed empty safe contents: no certs", parsed_empty2.certificates().size(), 0);

         return result;
      }

      static Test::Result test_state_key_only_and_cert_only() {
         Test::Result result("PKCS12 audit: key-only and cert-only bundles");
         auto rng = Test::new_rng("pkcs12_audit_keyonly");
         const auto creds = generate_credentials(*rng, "Key Only");
         const auto opts = Botan::PKCS12_Export_Options("pw").with_iterations(1);

         // Key only: contrary to the header documentation ("requires the
         // end-entity cert to be present when a key is exported") this is
         // accepted.
         Botan::PKCS12 key_only;
         key_only.add_key(creds.key);
         Bytes key_only_pfx;
         result.test_no_throw("key-only bundle exports", [&]() { key_only_pfx = key_only.export_to(opts, *rng); });
         if(!key_only_pfx.empty()) {
            const Botan::PKCS12 parsed(key_only_pfx, "pw");
            result.test_sz_eq("key-only: one key", parsed.private_keys().size(), 1);
            result.test_sz_eq("key-only: no certs", parsed.certificates().size(), 0);
            result.test_is_false("key-only: no end entity", parsed.end_entity_certificate().has_value());
            result.test_is_true("key-only: local key id derived", parsed.local_key_id().has_value());
            if(parsed.local_key_id()) {
               // The derived id must equal the one used when the matching
               // certificate is present (SHA-1 of the SPKI bit string)
               result.test_is_true("key-only: derived id equals cert SPKI SHA-1",
                                   *parsed.local_key_id() == creds.cert.subject_public_key_bitstring_sha1());
            }
            result.test_is_true("key-only: key matches",
                                parsed.private_keys().front()->private_key_bits() == creds.key->private_key_bits());
         }

         // Cert only
         Botan::PKCS12 cert_only;
         cert_only.add_certificate(creds.cert);
         const auto cert_only_pfx = cert_only.export_to(opts, *rng);
         const Botan::PKCS12 parsed_c(cert_only_pfx, "pw");
         result.test_sz_eq("cert-only: no keys", parsed_c.private_keys().size(), 0);
         result.test_sz_eq("cert-only: one cert", parsed_c.certificates().size(), 1);
         result.test_is_false("cert-only: no end entity", parsed_c.end_entity_certificate().has_value());
         result.test_sz_eq("cert-only: no ca certs", parsed_c.ca_certificates().size(), 0);
         result.test_is_false("cert-only: no local key id emitted", parsed_c.local_key_id().has_value());

         // Cert only with two certs: ca_certificates() returns "all but the first"
         Botan::PKCS12 two_certs;
         const auto other = generate_credentials(*rng, "Other");
         two_certs.add_certificate(creds.cert);
         two_certs.add_certificate(other.cert);
         const Botan::PKCS12 parsed_2(two_certs.export_to(opts, *rng), "pw");
         result.test_sz_eq("two certs: both stored", parsed_2.certificates().size(), 2);
         result.test_sz_eq("two certs, no key: one 'ca' cert", parsed_2.ca_certificates().size(), 1);

         // Cert-only bundle with cert encryption and a wrong password must fail
         const auto enc_opts = Botan::PKCS12_Export_Options("pw").with_iterations(1).with_cert_encryption_algo(
            "PBES2-SHA256-AES128");
         const auto enc_pfx = cert_only.export_to(enc_opts, *rng);
         result.test_throws<Botan::Invalid_Authentication_Tag>("cert-only encrypted, wrong pw",
                                                               [&]() { Botan::PKCS12 p(enc_pfx, "wrong"); });

         return result;
      }

      static Test::Result test_state_key_cert_matching_order() {
         Test::Result result("PKCS12 audit: key/cert matching depends on insertion order");
         auto rng = Test::new_rng("pkcs12_audit_order");
         const auto a = generate_credentials(*rng, "A");
         const auto b = generate_credentials(*rng, "B");
         const auto opts = Botan::PKCS12_Export_Options("pw").with_iterations(1);

         // Only the first key is matched against the certificates
         Botan::PKCS12 first_matches;
         first_matches.add_key(a.key);
         first_matches.add_key(b.key);  // no certificate for b
         first_matches.add_certificate(a.cert);
         Bytes pfx;
         result.test_no_throw("first key matches, second unmatched key tolerated",
                              [&]() { pfx = first_matches.export_to(opts, *rng); });
         if(!pfx.empty()) {
            const Botan::PKCS12 parsed(pfx, "pw");
            result.test_sz_eq("two keys surfaced", parsed.private_keys().size(), 2);
            result.test_is_true("end entity is A", parsed.end_entity_certificate().has_value() &&
                                                      parsed.end_entity_certificate()->BER_encode() == a.cert.BER_encode());
            result.test_is_true("first key is A",
                                parsed.private_keys().front()->private_key_bits() == a.key->private_key_bits());
         }

         Botan::PKCS12 first_unmatched;
         first_unmatched.add_key(b.key);
         first_unmatched.add_key(a.key);
         first_unmatched.add_certificate(a.cert);
         result.test_throws<Botan::Invalid_Argument>("first key unmatched rejected although second matches",
                                                     [&]() { (void)first_unmatched.export_to(opts, *rng); });

         // Two keys, two matching certs: each key is exported, but only the
         // first key/cert pair carries the localKeyId attribute.
         Botan::PKCS12 two_pairs;
         two_pairs.add_key(a.key);
         two_pairs.add_key(b.key);
         two_pairs.add_certificate(b.cert);
         two_pairs.add_certificate(a.cert);
         const Botan::PKCS12 parsed_pairs(two_pairs.export_to(opts, *rng), "pw");
         result.test_sz_eq("two pairs: two keys", parsed_pairs.private_keys().size(), 2);
         result.test_sz_eq("two pairs: two certs", parsed_pairs.certificates().size(), 2);
         result.test_is_true("two pairs: end entity A first",
                             !parsed_pairs.certificates().empty() &&
                                parsed_pairs.certificates().front().BER_encode() == a.cert.BER_encode());
         result.test_sz_eq("two pairs: B's cert reported as CA cert", parsed_pairs.ca_certificates().size(), 1);

         return result;
      }

      static Test::Result test_state_parse_mutate_reexport() {
         Test::Result result("PKCS12 audit: parse, mutate, re-export");
         auto rng = Test::new_rng("pkcs12_audit_reexport");
         const auto creds = generate_credentials(*rng, "EE");
         const auto ca = generate_credentials(*rng, "CA");

         Botan::PKCS12 original;
         original.add_key(creds.key);
         original.add_certificate(creds.cert);
         original.set_friendly_name("orig");
         const auto pfx1 =
            original.export_to(Botan::PKCS12_Export_Options::legacy_compat("pw").with_iterations(1).without_mac(), *rng);

         Botan::PKCS12 parsed(pfx1, "pw");
         result.test_str_eq("parsed friendly name", parsed.friendly_name().value_or(""), "orig");

         // Mutate the parsed object
         parsed.add_certificate(ca.cert);
         parsed.set_friendly_name("changed");
         parsed.set_local_key_id(Bytes{0x01, 0x02, 0x03});

         const auto pfx2 = parsed.export_to(Botan::PKCS12_Export_Options::modern("pw2").with_iterations(1), *rng);
         const Botan::PKCS12 reparsed(pfx2, "pw2");
         result.test_sz_eq("re-export: one key", reparsed.private_keys().size(), 1);
         result.test_sz_eq("re-export: two certs", reparsed.certificates().size(), 2);
         result.test_sz_eq("re-export: one ca cert", reparsed.ca_certificates().size(), 1);
         result.test_str_eq("re-export: friendly name", reparsed.friendly_name().value_or(""), "changed");
         result.test_is_true("re-export: custom local key id", reparsed.local_key_id() == Bytes{0x01, 0x02, 0x03});
         result.test_is_true("re-export: end entity", reparsed.end_entity_certificate().has_value() &&
                                                         reparsed.end_entity_certificate()->BER_encode() ==
                                                            creds.cert.BER_encode());
   #if BOTAN_VERSION_MAJOR > 3 || (BOTAN_VERSION_MAJOR == 3 && BOTAN_VERSION_MINOR >= 14)
         result.test_is_true("MAC-less input reported", parsed.mac_protected() == false);
         result.test_is_true("re-export is MAC protected", reparsed.mac_protected() == true);
   #endif
         result.test_throws<Botan::Invalid_Authentication_Tag>("old password rejected on re-export",
                                                               [&]() { Botan::PKCS12 p(pfx2, "pw"); });

         // Unknown bag types of a parsed file are dropped silently on re-export
         const auto unknown_pfx = Test::read_binary_data_file("pkcs12/unknown_bag_secret.pfx");
         const Botan::PKCS12 with_unknown(unknown_pfx, "");
         result.test_sz_eq("unknown bag surfaced", with_unknown.unknown_bag_types().size(), 1);
         const auto reexp = with_unknown.export_to(Botan::PKCS12_Export_Options("").with_iterations(1), *rng);
         const Botan::PKCS12 reexp_parsed(reexp, "");
         result.test_sz_eq("unknown bag dropped on re-export", reexp_parsed.unknown_bag_types().size(), 0);

         return result;
      }

      static Test::Result test_state_export_is_randomized_and_const() {
         Test::Result result("PKCS12 audit: repeated export uses fresh randomness");
         auto rng = Test::new_rng("pkcs12_audit_randomized");
         const auto creds = generate_credentials(*rng, "EE");
         Botan::PKCS12 bundle;
         bundle.add_key(creds.key);
         bundle.add_certificate(creds.cert);

         for(const auto& algo : {"PBES2-SHA256-AES256", "PBE-SHA1-3DES"}) {
            const auto opts = Botan::PKCS12_Export_Options("pw")
                                 .with_iterations(1)
                                 .with_key_encryption_algo(algo)
                                 .with_cert_encryption_algo(algo);
            const auto p1 = bundle.export_to(opts, *rng);
            const auto p2 = bundle.export_to(opts, *rng);
            result.test_is_true(std::string("exports differ (") + algo + ")", p1 != p2);
            result.test_sz_eq(std::string("exports same size (") + algo + ")", p1.size(), p2.size());
            const auto f1 = bundle_fingerprint(Botan::PKCS12(p1, "pw"));
            const auto f2 = bundle_fingerprint(Botan::PKCS12(p2, "pw"));
            result.test_is_true(std::string("exports parse identically (") + algo + ")", f1 == f2);

            const auto s1 = extract_first_shrouded_bag(p1);
            const auto s2 = extract_first_shrouded_bag(p2);
            if(result.test_is_true("shrouded bag found", s1.has_value() && s2.has_value())) {
               result.test_is_true(std::string("key encryption params differ (") + algo + ")",
                                   s1->first.parameters() != s2->first.parameters());
               result.test_is_true(std::string("key ciphertexts differ (") + algo + ")", s1->second != s2->second);
            }
         }
         // Bundle unchanged by exporting
         result.test_sz_eq("bundle still one key", bundle.private_keys().size(), 1);
         result.test_is_false("bundle has no friendly name", bundle.friendly_name().has_value());
         return result;
      }

      static Test::Result test_state_attribute_precedence() {
         Test::Result result("PKCS12 audit: friendly name / localKeyId precedence");
         auto rng = Test::new_rng("pkcs12_audit_attrs");
         const auto creds = generate_credentials(*rng, "EE");
         Botan::PKCS12 bundle;
         bundle.add_key(creds.key);
         bundle.add_certificate(creds.cert);

         auto parse_with = [&](const Botan::PKCS12_Export_Options& o) {
            return Botan::PKCS12(bundle.export_to(o, *rng), "pw");
         };

         // No name anywhere
         result.test_is_false("no name: nullopt",
                              parse_with(Botan::PKCS12_Export_Options("pw").with_iterations(1)).friendly_name().has_value());

         // Bundle-level name
         bundle.set_friendly_name("bundle");
         result.test_str_eq("bundle name used",
                            parse_with(Botan::PKCS12_Export_Options("pw").with_iterations(1)).friendly_name().value_or(""),
                            "bundle");

         // Option name overrides bundle name
         result.test_str_eq("option name wins",
                            parse_with(Botan::PKCS12_Export_Options("pw", "option").with_iterations(1))
                               .friendly_name()
                               .value_or(""),
                            "option");

         // An empty option name suppresses the attribute entirely and does
         // not fall back to the bundle-level name.
         result.test_is_false("empty option name suppresses name",
                              parse_with(Botan::PKCS12_Export_Options("pw", std::string("")).with_iterations(1))
                                 .friendly_name()
                                 .has_value());

         // Clearing restores the no-name state
         bundle.clear_friendly_name();
         result.test_is_false("cleared name: nullopt",
                              parse_with(Botan::PKCS12_Export_Options("pw").with_iterations(1)).friendly_name().has_value());

         // localKeyId: default derived, explicit, cleared, empty explicit
         const auto derived = parse_with(Botan::PKCS12_Export_Options("pw").with_iterations(1)).local_key_id();
         result.test_is_true("default local key id is SPKI SHA-1",
                             derived == creds.cert.subject_public_key_bitstring_sha1());
         bundle.set_local_key_id(Bytes{0xAB});
         result.test_is_true("explicit local key id",
                             parse_with(Botan::PKCS12_Export_Options("pw").with_iterations(1)).local_key_id() == Bytes{0xAB});
         bundle.set_local_key_id(Bytes{});
         // Empty explicit id: attribute is not written, so nothing is parsed back
         result.test_is_false(
            "empty explicit local key id suppresses attribute",
            parse_with(Botan::PKCS12_Export_Options("pw").with_iterations(1)).local_key_id().has_value());
         bundle.clear_local_key_id();
         result.test_is_true("cleared id falls back to derived",
                             parse_with(Botan::PKCS12_Export_Options("pw").with_iterations(1)).local_key_id() == derived);

         return result;
      }

      static Test::Result test_state_password_change() {
         Test::Result result("PKCS12 audit: password change via re-export");
         auto rng = Test::new_rng("pkcs12_audit_pwchange");
         const auto creds = generate_credentials(*rng, "EE");
         Botan::PKCS12 bundle;
         bundle.add_key(creds.key);
         bundle.add_certificate(creds.cert);

         const std::vector<std::string> passwords = {"first", "", "second", "first"};
         Bytes current = bundle.export_to(Botan::PKCS12_Export_Options(passwords[0]).with_iterations(1), *rng);
         for(size_t i = 1; i < passwords.size(); ++i) {
            const Botan::PKCS12 parsed(current, passwords[i - 1]);
            current = parsed.export_to(Botan::PKCS12_Export_Options(passwords[i]).with_iterations(1), *rng);
            result.test_no_throw(Botan::fmt("round {} parses with new password", i),
                                 [&]() { Botan::PKCS12 p(current, passwords[i]); });
            if(passwords[i] != passwords[i - 1]) {
               result.test_throws<Botan::Invalid_Authentication_Tag>(Botan::fmt("round {} rejects old password", i),
                                                                     [&]() { Botan::PKCS12 p(current, passwords[i - 1]); });
            }
         }
         const Botan::PKCS12 final_parsed(current, passwords.back());
         result.test_is_true("key survived all rounds",
                             final_parsed.private_keys().front()->private_key_bits() == creds.key->private_key_bits());
         return result;
      }

      // ---------------------------------------------------------------
      // Export option validation
      // ---------------------------------------------------------------

      static Test::Result test_options_validation() {
         Test::Result result("PKCS12 audit: export option validation");
         auto rng = Test::new_rng("pkcs12_audit_options");
         const auto creds = generate_credentials(*rng, "EE");
         Botan::PKCS12 bundle;
         bundle.add_key(creds.key);
         bundle.add_certificate(creds.cert);

         auto rejects = [&](const std::string& what, const Botan::PKCS12_Export_Options& o) {
            result.test_throws<Botan::Invalid_Argument>(what, [&]() { (void)bundle.export_to(o, *rng); });
         };
         auto accepts = [&](const std::string& what, const Botan::PKCS12_Export_Options& o) {
            result.test_no_throw(what, [&]() {
               const auto pfx = bundle.export_to(o, *rng);
               const Botan::PKCS12 p(pfx, o.password());
               if(p.private_keys().size() != 1) {
                  throw Botan::Internal_Error("round trip lost key");
               }
            });
         };

         const auto base = Botan::PKCS12_Export_Options("pw").with_iterations(1);

         rejects("empty key algo", Botan::PKCS12_Export_Options(base).with_key_encryption_algo(""));
         rejects("raw cipher name as key algo", Botan::PKCS12_Export_Options(base).with_key_encryption_algo("AES-256/CBC"));
         rejects("RC2 PBE not supported", Botan::PKCS12_Export_Options(base).with_key_encryption_algo("PBE-SHA1-RC2-40"));
         rejects("RC4 PBE not supported", Botan::PKCS12_Export_Options(base).with_key_encryption_algo("PBE-SHA1-RC4-128"));
         rejects("lower-case algo name rejected",
                 Botan::PKCS12_Export_Options(base).with_key_encryption_algo("pbes2-sha256-aes256"));
         rejects("algo with surrounding space rejected",
                 Botan::PKCS12_Export_Options(base).with_key_encryption_algo(" PBES2-SHA256-AES256"));
         rejects("scrypt PBES2 not offered", Botan::PKCS12_Export_Options(base).with_key_encryption_algo("PBES2-Scrypt-AES256"));
         rejects("unsupported cert algo", Botan::PKCS12_Export_Options(base).with_cert_encryption_algo("AES-128/GCM"));
         rejects("MD5 MAC rejected", Botan::PKCS12_Export_Options(base).with_mac_digest("MD5"));
         rejects("SHA-3 MAC rejected", Botan::PKCS12_Export_Options(base).with_mac_digest("SHA-3(256)"));
         rejects("empty MAC digest rejected", Botan::PKCS12_Export_Options(base).with_mac_digest(""));
         rejects("lower-case MAC digest rejected", Botan::PKCS12_Export_Options(base).with_mac_digest("sha-256"));

         // MAC digest is only validated when a MAC is produced
         accepts("bad MAC digest ignored when MAC disabled",
                 Botan::PKCS12_Export_Options(base).with_mac_digest("MD5").without_mac());
         accepts("cert algo set on key+cert bundle", Botan::PKCS12_Export_Options(base).with_cert_encryption_algo("PBE-SHA1-2DES"));

         // Validation of options is independent of bundle content: a
         // cert-only bundle still validates the key algorithm name.
         Botan::PKCS12 cert_only;
         cert_only.add_certificate(creds.cert);
         result.test_throws<Botan::Invalid_Argument>("key algo validated even without keys", [&]() {
            (void)cert_only.export_to(Botan::PKCS12_Export_Options(base).with_key_encryption_algo("bogus"), *rng);
         });

         return result;
      }

      static Test::Result test_options_iteration_boundaries() {
         Test::Result result("PKCS12 audit: iteration count boundaries");
         auto rng = Test::new_rng("pkcs12_audit_iter");
         const auto creds = generate_credentials(*rng, "EE");
         Botan::PKCS12 bundle;
         bundle.add_key(creds.key);
         bundle.add_certificate(creds.cert);

         result.test_throws<Botan::Invalid_Argument>("0 iterations rejected", [&]() {
            (void)bundle.export_to(Botan::PKCS12_Export_Options("pw").with_iterations(0), *rng);
         });

         // 100 000 000 + 1 must be rejected *before* any KDF work is done
         const auto start = std::chrono::steady_clock::now();
         result.test_throws<Botan::Invalid_Argument>("1e8+1 iterations rejected", [&]() {
            (void)bundle.export_to(Botan::PKCS12_Export_Options("pw").with_iterations(100'000'001), *rng);
         });
         const double ms = elapsed_ms(start);
         result.test_note(Botan::fmt("rejection of 1e8+1 iterations took {} ms", static_cast<size_t>(ms)));
         result.test_is_true("rejection was immediate", ms < 2000.0);

         // Minimum accepted count
         {
            const auto pfx = bundle.export_to(Botan::PKCS12_Export_Options("pw").with_iterations(1), *rng);
            const Botan::PKCS12 parsed(pfx, "pw");
            result.test_sz_eq("1 iteration round trip", parsed.private_keys().size(), 1);
            // With iterations == 1 the MacData omits the iteration field; make
            // sure it is really absent by looking for the DEFAULT-encoded form.
            // (The MacData ends the file; with the field absent the last
            // structure is the salt OCTET STRING.)
            result.test_is_true("file ends with MAC salt (iterations omitted)", pfx.size() > 34 &&
                                                                                    pfx[pfx.size() - 34] == 0x04 &&
                                                                                    pfx[pfx.size() - 33] == 0x20);
         }

         // The reference documentation claims the limit is 1 000 000. The
         // implementation accepts 1 000 001 (limit is 100 000 000).
         {
            const auto start2 = std::chrono::steady_clock::now();
            Bytes pfx;
            result.test_no_throw("1e6+1 iterations accepted (doc says rejected)", [&]() {
               pfx = bundle.export_to(
                  Botan::PKCS12_Export_Options("pw").with_iterations(1'000'001).with_key_encryption_algo("PBE-SHA1-3DES"),
                  *rng);
            });
            result.test_note(Botan::fmt("export with 1e6+1 iterations took {} ms", static_cast<size_t>(elapsed_ms(start2))));
            if(!pfx.empty()) {
               const Botan::PKCS12 parsed(pfx, "pw");
               result.test_sz_eq("1e6+1 round trip", parsed.private_keys().size(), 1);
            }
         }

         return result;
      }

      // ---------------------------------------------------------------
      // Parameter matrix
      // ---------------------------------------------------------------

      static Test::Result test_parameter_matrix() {
         Test::Result result("PKCS12 audit: algorithm x password matrix");
         auto rng = Test::new_rng("pkcs12_audit_matrix");
         const auto creds = generate_credentials(*rng, "EE");
         const auto ca = generate_credentials(*rng, "CA");
         Botan::PKCS12 bundle;
         bundle.add_key(creds.key);
         bundle.add_certificate(creds.cert);
         bundle.add_certificate(ca.cert);
         bundle.set_friendly_name("Zertifikat \xC3\xA4\xC3\xB6\xC3\xBC");  // UTF-8 umlauts

         const std::vector<std::string> key_algos = {
            "PBES2-SHA256-AES256", "PBES2-SHA256-AES128", "PBE-SHA1-3DES", "PBE-SHA1-2DES"};
         const std::vector<std::string> cert_algos = {"", "PBES2-SHA256-AES128", "PBE-SHA1-2DES"};
         const std::vector<std::string> mac_digests = {"SHA-1", "SHA-256", "SHA-512"};
         const std::vector<std::string> passwords = {
            "",
            "p",
            "p\xC3\xA4ssw\xC3\xB6rd",  // UTF-8 non-ASCII, BMP
            std::string(70, 'x'),      // longer than the SHA-1/SHA-256 block (64 bytes)
            std::string(130, 'y'),     // longer than the SHA-512 block (128 bytes)
            std::string("a\0b", 3),    // embedded NUL
         };

         size_t combos = 0;
         size_t failures = 0;
         for(const auto& ka : key_algos) {
            for(const auto& ca_algo : cert_algos) {
               for(const auto& md : mac_digests) {
                  for(const auto& pw : passwords) {
                     const std::string label = Botan::fmt("key={} cert={} mac={} pwlen={}", ka, ca_algo, md, pw.size());
                     ++combos;
                     try {
                        const auto opts = Botan::PKCS12_Export_Options(pw)
                                             .with_iterations(2)
                                             .with_key_encryption_algo(ka)
                                             .with_cert_encryption_algo(ca_algo)
                                             .with_mac_digest(md);
                        const auto pfx = bundle.export_to(opts, *rng);
                        const Botan::PKCS12 parsed(pfx, pw);
                        bool ok = parsed.private_keys().size() == 1 && parsed.certificates().size() == 2 &&
                                  parsed.end_entity_certificate().has_value() &&
                                  parsed.end_entity_certificate()->BER_encode() == creds.cert.BER_encode() &&
                                  parsed.ca_certificates().size() == 1 &&
                                  parsed.ca_certificates().front().BER_encode() == ca.cert.BER_encode() &&
                                  parsed.private_keys().front()->private_key_bits() == creds.key->private_key_bits() &&
                                  parsed.friendly_name() == bundle.friendly_name();
                        if(!ok) {
                           ++failures;
                           result.test_failure("round trip content mismatch: " + label);
                        }

                        // Wrong passwords must be rejected: a different
                        // password, a prefix, and a superstring.
                        for(const std::string& bad : {std::string("wrong"), pw.substr(0, pw.size() / 2), pw + "x"}) {
                           if(bad == pw) {
                              continue;
                           }
                           try {
                              const Botan::PKCS12 p(pfx, bad);
                              ++failures;
                              result.test_failure("wrong password accepted: " + label);
                           } catch(const Botan::Invalid_Authentication_Tag&) {
                              // expected
                           }
                        }
                     } catch(const std::exception& e) {
                        ++failures;
                        result.test_failure(label + ": " + e.what());
                     }
                  }
               }
            }
         }
         result.test_note(Botan::fmt("{} parameter combinations exercised", combos));
         result.test_sz_eq("no failures in matrix", failures, 0);
         return result;
      }

      static Test::Result test_password_edge_cases() {
         Test::Result result("PKCS12 audit: password edge cases");
         auto rng = Test::new_rng("pkcs12_audit_pwedge");
         const auto creds = generate_credentials(*rng, "EE");
         Botan::PKCS12 bundle;
         bundle.add_key(creds.key);
         bundle.add_certificate(creds.cert);

         const std::string emoji = "\xF0\x9F\x94\x91";  // U+1F511, outside the BMP
         const std::string invalid_utf8 = "\xFF\xFE";

         // Non-BMP characters cannot be encoded in UCS-2, which the PKCS#12
         // KDF (MAC and legacy PBE) requires. With the modern PBES2 key
         // encryption the MAC KDF still fails.
         result.test_throws<Botan::Decoding_Error>("non-BMP password rejected with MAC", [&]() {
            (void)bundle.export_to(Botan::PKCS12_Export_Options(emoji).with_iterations(1), *rng);
         });
         // ... but a MAC-less PBES2 file with a non-BMP password is produced,
         // since PBES2/PBKDF2 consumes the raw UTF-8 bytes.
         Bytes nomac;
         result.test_no_throw("non-BMP password accepted without MAC and with PBES2", [&]() {
            nomac = bundle.export_to(Botan::PKCS12_Export_Options(emoji).with_iterations(1).without_mac(), *rng);
         });
         if(!nomac.empty()) {
            result.test_no_throw("non-BMP password MAC-less file parses", [&]() { Botan::PKCS12 p(nomac, emoji); });
         }
         result.test_throws<Botan::Decoding_Error>("non-BMP password rejected with legacy PBE", [&]() {
            (void)bundle.export_to(
               Botan::PKCS12_Export_Options(emoji).with_iterations(1).without_mac().with_key_encryption_algo("PBE-SHA1-3DES"),
               *rng);
         });

         // Invalid UTF-8 in the password is rejected by the UCS-2 conversion
         result.test_throws<Botan::Decoding_Error>("invalid UTF-8 password rejected", [&]() {
            (void)bundle.export_to(Botan::PKCS12_Export_Options(invalid_utf8).with_iterations(1), *rng);
         });

         // Parsing with a non-BMP password against a MAC-protected file: the
         // exception is the encoding error, not an authentication failure.
         const auto pfx = bundle.export_to(Botan::PKCS12_Export_Options("pw").with_iterations(1), *rng);
         result.test_throws<Botan::Decoding_Error>("non-BMP password on parse is an encoding error",
                                                   [&]() { Botan::PKCS12 p(pfx, emoji); });

         // Embedded NUL is part of the password
         const std::string with_nul("a\0b", 3);
         const auto pfx_nul = bundle.export_to(Botan::PKCS12_Export_Options(with_nul).with_iterations(1), *rng);
         result.test_no_throw("NUL password round trip", [&]() { Botan::PKCS12 p(pfx_nul, with_nul); });
         result.test_throws<Botan::Invalid_Authentication_Tag>("NUL-truncated password rejected",
                                                               [&]() { Botan::PKCS12 p(pfx_nul, "a"); });

         // Very long password (4 KiB)
         const std::string long_pw(4096, 'L');
         const auto pfx_long =
            bundle.export_to(Botan::PKCS12_Export_Options(long_pw).with_iterations(1).with_key_encryption_algo("PBE-SHA1-3DES"),
                             *rng);
         result.test_no_throw("4 KiB password round trip", [&]() { Botan::PKCS12 p(pfx_long, long_pw); });
         result.test_throws<Botan::Invalid_Authentication_Tag>("4 KiB password, one char less rejected",
                                                               [&]() { Botan::PKCS12 p(pfx_long, long_pw.substr(1)); });

         return result;
      }

      static Test::Result test_kdf_password_encoding_contract() {
         Test::Result result("PKCS12 audit: KDF password encoding contract");
         auto sha1 = Botan::HashFunction::create_or_throw("SHA-1");
         const Bytes salt = {1, 2, 3, 4, 5, 6, 7, 8};

         auto via_family = [&](const std::string& pw, size_t out_len, size_t id) {
            auto fam = Botan::PasswordHashFamily::create_or_throw(Botan::fmt("PKCS12-KDF(SHA-1,{})", id));
            auto ph = fam->from_iterations(3);
            Bytes out(out_len);
            ph->derive_key(out.data(), out.size(), pw.data(), pw.size(), salt.data(), salt.size());
            return out;
         };
         auto via_raw = [&](const Bytes& pwd_bytes, size_t out_len, uint8_t id) {
            Bytes out(out_len);
            Botan::pkcs12_kdf(out, pwd_bytes, salt, 3, id, *sha1);
            return out;
         };

         result.test_is_true("empty password encodes as 00 00", via_family("", 24, 1) == via_raw({0, 0}, 24, 1));
         result.test_is_true("ascii password UCS-2 BE + terminator",
                             via_family("ab", 24, 1) == via_raw({0, 'a', 0, 'b', 0, 0}, 24, 1));
         result.test_is_true("umlaut encodes as U+00E4",
                             via_family("\xC3\xA4", 24, 2) == via_raw({0x00, 0xE4, 0, 0}, 24, 2));
         result.test_is_true("empty password differs from OpenSSL empty convention",
                             via_family("", 20, 3) != via_raw({}, 20, 3));
         // Output longer than one hash output exercises the I-update loop
         result.test_is_true("multi-block output consistent",
                             via_family("pw", 60, 1) == via_raw(rfc7292_password_bytes("pw"), 60, 1));
         // Output prefix property: a shorter request is a prefix of a longer one
         const auto long_out = via_family("pw", 60, 1);
         const auto short_out = via_family("pw", 20, 1);
         result.test_is_true("shorter output is a prefix", std::equal(short_out.begin(), short_out.end(), long_out.begin()));
         // The id byte separates key, IV and MAC derivation
         result.test_is_true("id=1 and id=2 differ", via_family("pw", 20, 1) != via_family("pw", 20, 2));
         result.test_is_true("id=2 and id=3 differ", via_family("pw", 20, 2) != via_family("pw", 20, 3));

         result.test_throws<Botan::Invalid_Argument>("id 0 rejected", [&]() { (void)via_raw({0, 0}, 20, 0); });
         result.test_throws<Botan::Invalid_Argument>("id 4 rejected", [&]() { (void)via_raw({0, 0}, 20, 4); });
         result.test_throws<Botan::Invalid_Argument>("0 iterations rejected", [&]() {
            Bytes out(20);
            Botan::pkcs12_kdf(out, Bytes{0, 0}, salt, 0, 1, *sha1);
         });
         return result;
      }

      static Test::Result test_legacy_pbe_independent_reimplementation() {
         Test::Result result("PKCS12 audit: legacy PBE cross-check with independent implementation");
         auto rng = Test::new_rng("pkcs12_audit_pbe_xcheck");
         const auto creds = generate_credentials(*rng, "EE");
         const auto pkcs8 = Botan::PKCS8::BER_encode(*creds.key);
         const Bytes pkcs8_bytes(pkcs8.begin(), pkcs8.end());

         for(const bool two_key : {false, true}) {
            const std::string algo = two_key ? "PBE-SHA1-2DES" : "PBE-SHA1-3DES";

            // Library-produced shrouded bag decrypted by the test's own
            // implementation of RFC 7292 Appendix B
            Botan::PKCS12 bundle;
            bundle.add_key(creds.key);
            bundle.add_certificate(creds.cert);
            const auto pfx = bundle.export_to(
               Botan::PKCS12_Export_Options("secret").with_iterations(7).with_key_encryption_algo(algo).without_mac(), *rng);
            const auto bag = extract_first_shrouded_bag(pfx);
            if(!result.test_is_true(algo + ": shrouded bag present", bag.has_value())) {
               continue;
            }
            result.test_is_true(algo + ": OID as expected", bag->first.oid() == Botan::OID::from_string(algo));
            Bytes salt;
            size_t iterations = 0;
            Botan::BER_Decoder(bag->first.parameters())
               .start_sequence()
               .decode(salt, Botan::ASN1_Type::OctetString)
               .decode(iterations)
               .end_cons();
            result.test_sz_eq(algo + ": salt length", salt.size(), 8);
            result.test_sz_eq(algo + ": iterations", iterations, 7);
            const auto decrypted =
               pbe_sha1_3des_decrypt(bag->second, rfc7292_password_bytes("secret"), salt, iterations, two_key);
            result.test_is_true(algo + ": independent decryption yields PKCS#8 key", decrypted == pkcs8_bytes);

            // Test-produced shrouded bag parsed by the library
            const Bytes my_salt = {9, 8, 7, 6, 5, 4, 3, 2};
            const auto enc = pbe_sha1_3des_encrypt(pkcs8_bytes, rfc7292_password_bytes("secret"), my_salt, 5, two_key);
            const auto crafted = simple_pfx({der_shrouded_key_bag(enc.alg, enc.ciphertext), der_cert_bag(creds.cert)},
                                            "secret",
                                            MacSpec{.hash = "SHA-1", .salt = Bytes(20, 1), .iterations = 5});
            const Botan::PKCS12 parsed(crafted, "secret");
            result.test_is_true(algo + ": library parses test-produced bag",
                                parsed.private_keys().size() == 1 &&
                                   parsed.private_keys().front()->private_key_bits() == creds.key->private_key_bits());
         }
         return result;
      }

      static Test::Result test_export_salt_uniqueness() {
         Test::Result result("PKCS12 audit: all salts in an export are distinct");
         auto rng = Test::new_rng("pkcs12_audit_salts");
         Botan::PKCS12 bundle;
         const auto a = generate_credentials(*rng, "A");
         const auto b = generate_credentials(*rng, "B");
         const auto c = generate_credentials(*rng, "C");
         bundle.add_key(a.key);
         bundle.add_key(b.key);
         bundle.add_key(c.key);
         bundle.add_certificate(a.cert);

         // Legacy PBE parameters are SEQUENCE { OCTET STRING(8) salt, INTEGER 2048 }
         const auto pfx = bundle.export_to(Botan::PKCS12_Export_Options::legacy_compat("pw")
                                              .with_cert_encryption_algo("PBE-SHA1-3DES")
                                              .with_iterations(2048),
                                           *rng);
         std::set<Bytes> salts;
         size_t found = 0;
         for(size_t i = 0; i + 14 <= pfx.size(); ++i) {
            if(pfx[i] == 0x30 && pfx[i + 1] == 0x0E && pfx[i + 2] == 0x04 && pfx[i + 3] == 0x08 && pfx[i + 12] == 0x02 &&
               pfx[i + 13] == 0x02 && pfx[i + 14] == 0x08 && pfx[i + 15] == 0x00) {
               ++found;
               salts.insert(Bytes(pfx.begin() + static_cast<std::ptrdiff_t>(i + 4),
                                  pfx.begin() + static_cast<std::ptrdiff_t>(i + 12)));
            }
         }
         // 3 shrouded keys + 1 EncryptedData
         result.test_sz_eq("four PBE parameter blocks found", found, 4);
         result.test_sz_eq("all PBE salts distinct", salts.size(), found);
         return result;
      }

      // ---------------------------------------------------------------
      // MAC handling
      // ---------------------------------------------------------------

      static Test::Result test_mac_first_ordering() {
         Test::Result result("PKCS12 audit: MAC is verified before any content is parsed");
         auto rng = Test::new_rng("pkcs12_audit_macfirst");
         const auto creds = generate_credentials(*rng, "EE");

         // A garbage key bag: with the wrong password, the failure must be the
         // MAC failure (Invalid_Authentication_Tag); with the correct password,
         // the structural error surfaces.
         const auto garbage_bag = der_key_bag_raw(Bytes{0x30, 0x03, 0x02, 0x01});
         const auto pfx = simple_pfx({garbage_bag, der_cert_bag(creds.cert)}, "pw", MacSpec{});
         result.test_throws<Botan::Invalid_Authentication_Tag>("wrong password: MAC error, not decoding error",
                                                               [&]() { Botan::PKCS12 p(pfx, "wrong"); });
         result.test_throws<Botan::Decoding_Error>("correct password: decoding error",
                                                   [&]() { Botan::PKCS12 p(pfx, "pw"); });

         // Expensive shrouded key bag (1e8 iterations, would take minutes):
         // with a wrong password the MAC check must stop processing first.
         const auto expensive = der_shrouded_key_bag(pbe_sha1_3des_alg_id(Bytes(8, 1), Botan::BigInt::from_u64(100'000'000), false), Bytes(16, 0));
         const auto pfx2 = simple_pfx({expensive}, "pw", MacSpec{});
         const auto start = std::chrono::steady_clock::now();
         result.test_throws<Botan::Invalid_Authentication_Tag>("wrong password never reaches expensive bag",
                                                               [&]() { Botan::PKCS12 p(pfx2, "wrong"); });
         result.test_is_true("rejection before KDF of the expensive bag", elapsed_ms(start) < 2000.0);
         return result;
      }

      static Test::Result test_mac_data_variations() {
         Test::Result result("PKCS12 audit: MacData variations");
         auto rng = Test::new_rng("pkcs12_audit_macdata");
         const auto creds = generate_credentials(*rng, "EE");
         const std::vector<Bytes> bags = {der_key_bag(*creds.key), der_cert_bag(creds.cert)};

         auto ok = [&](const std::string& what, const MacSpec& m, std::string_view pw = "pw") {
            result.test_no_throw(what, [&]() {
               const Botan::PKCS12 p(simple_pfx(bags, pw, m), pw);
               if(p.private_keys().size() != 1) {
                  throw Botan::Internal_Error("key missing");
               }
            });
         };
         auto decoding_error = [&](const std::string& what, const MacSpec& m) {
            result.test_throws<Botan::Decoding_Error>(what, [&]() { Botan::PKCS12 p(simple_pfx(bags, "pw", m), "pw"); });
         };
         auto auth_error = [&](const std::string& what, const MacSpec& m) {
            result.test_throws<Botan::Invalid_Authentication_Tag>(
               what, [&]() { Botan::PKCS12 p(simple_pfx(bags, "pw", m), "pw"); });
         };

         for(const auto& h : {"SHA-1", "SHA-224", "SHA-256", "SHA-384", "SHA-512", "SHA-512-256"}) {
            ok(Botan::fmt("MAC digest {} absent params", h), MacSpec{.hash = h});
            ok(Botan::fmt("MAC digest {} NULL params", h), MacSpec{.hash = h, .digest_null_param = true});
         }
         decoding_error("MD5 MAC digest rejected",
                        MacSpec{.hash = "SHA-1", .override_digest_oid = Botan::OID::from_string("MD5")});
         decoding_error("SHA-3 MAC digest rejected",
                        MacSpec{.hash = "SHA-256", .override_digest_oid = Botan::OID::from_string("SHA-3(256)")});

         ok("iterations field omitted (DEFAULT 1)", MacSpec{.iterations = 1, .omit_iterations = true});
         ok("iterations 2", MacSpec{.iterations = 2});
         ok("iterations 2048", MacSpec{.iterations = 2048});
         decoding_error("iterations 0", MacSpec{.iterations = 1, .override_iterations_integer = Botan::BigInt::zero()});
         decoding_error("iterations negative",
                        MacSpec{.iterations = 1, .override_iterations_integer = -Botan::BigInt::from_u64(1)});
         decoding_error("iterations 2^40",
                        MacSpec{.iterations = 1, .override_iterations_integer = Botan::BigInt::power_of_2(40)});
         {
            const auto start = std::chrono::steady_clock::now();
            decoding_error("iterations 1e8+1 rejected",
                           MacSpec{.iterations = 1, .override_iterations_integer = Botan::BigInt::from_u64(100'000'001)});
            result.test_is_true("1e8+1 rejected immediately", elapsed_ms(start) < 2000.0);
         }

         // Salt variations
         ok("empty MAC salt accepted", MacSpec{.salt = Bytes{}});
         ok("1-byte MAC salt accepted", MacSpec{.salt = Bytes{7}});
         ok("200-byte MAC salt accepted", MacSpec{.salt = Bytes(200, 3)});

         // MAC value variations
         auth_error("MAC value truncated by one byte",
                    MacSpec{.override_mac_value = Bytes(31, 0)});  // wrong length and wrong content
         auth_error("MAC value empty", MacSpec{.override_mac_value = Bytes{}});
         auth_error("MAC value all zero", MacSpec{.override_mac_value = Bytes(32, 0)});
         {
            // Correct MAC computed with SHA-1 but declared as SHA-256
            const auto auth_safe = der_authenticated_safe({der_content_info_data(der_safe_contents(bags))});
            const auto sha1_mac = compute_pkcs12_mac(auth_safe, "pw", "SHA-1", Bytes(32, 0x5A), 1);
            auth_error("MAC of other digest rejected", MacSpec{.hash = "SHA-256", .override_mac_value = sha1_mac});
         }
         // Empty password with a MAC
         ok("empty password with MAC", MacSpec{}, "");
         // Unicode password with SHA-512 MAC (block size 128)
         ok("unicode password, SHA-512 MAC", MacSpec{.hash = "SHA-512"}, "\xC3\xA4\xC3\xB6\xC3\xBC");

         return result;
      }

      static Test::Result test_mac_stripping_and_substitution() {
         Test::Result result("PKCS12 audit: MAC stripping enables certificate substitution");
         auto rng = Test::new_rng("pkcs12_audit_strip");
         const auto creds = generate_credentials(*rng, "EE");
         const auto ca = generate_credentials(*rng, "CA");
         Botan::PKCS12 bundle;
         bundle.add_key(creds.key);
         bundle.add_certificate(creds.cert);
         bundle.add_certificate(ca.cert);

         const auto protected_pfx = bundle.export_to(Botan::PKCS12_Export_Options("pw").with_iterations(1), *rng);
         const Botan::PKCS12 ref(protected_pfx, "pw");
         const auto ref_fp = bundle_fingerprint(ref);

         // 1. Stripping the MAC (no password needed) still parses
         const auto stripped = strip_mac(protected_pfx);
         result.test_sz_lt("stripped file is shorter", stripped.size(), protected_pfx.size());
         Botan::PKCS12 parsed_stripped(stripped, "pw");
         result.test_is_true("stripped file parses to identical content", bundle_fingerprint(parsed_stripped) == ref_fp);
   #if BOTAN_VERSION_MAJOR > 3 || (BOTAN_VERSION_MAJOR == 3 && BOTAN_VERSION_MINOR >= 14)
         result.test_is_true("stripping is detectable via mac_protected()", parsed_stripped.mac_protected() == false);
   #else
         result.test_note("Botan < 3.14: MAC stripping is not detectable through the API");
   #endif
         // Stripped file also parses with a *wrong* password? No: the key is
         // still encrypted, so a wrong password fails at the key bag.
         result.test_throws("stripped file with wrong password still fails (key encrypted)",
                            [&]() { Botan::PKCS12 p(stripped, "wrong"); });

         // 2. In the stripped file, the certificates are plaintext. Modify the
         //    CA certificate's signature (last byte) without the password:
         //    the parser accepts it, since certificate signatures are not
         //    checked on import.
         const auto ca_der = ca.cert.BER_encode();
         const auto pos = find_bytes(stripped, ca_der);
         if(result.test_is_true("CA certificate found in plaintext", pos.has_value())) {
            Bytes tampered = stripped;
            tampered[*pos + ca_der.size() - 1] ^= 0x01;
            result.test_no_throw("tampered CA cert accepted without MAC", [&]() {
               const Botan::PKCS12 p(tampered, "pw");
               const auto cas = p.ca_certificates();
               if(cas.size() != 1) {
                  throw Botan::Internal_Error("unexpected CA cert count");
               }
               if(cas.front().BER_encode() == ca_der) {
                  throw Botan::Internal_Error("modification not visible");
               }
            });

            // With the MAC in place the same modification is rejected
            const auto pos_p = find_bytes(protected_pfx, ca_der);
            if(result.test_is_true("CA certificate found in protected file", pos_p.has_value())) {
               Bytes tampered_p = protected_pfx;
               tampered_p[*pos_p + ca_der.size() - 1] ^= 0x01;
               result.test_throws<Botan::Invalid_Authentication_Tag>("tampering detected with MAC",
                                                                     [&]() { Botan::PKCS12 p(tampered_p, "pw"); });
            }
         }

         // 3. Substituting the whole CA certificate bag with another one
         //    (attacker inserts their own CA) also succeeds without the MAC.
         {
            const auto evil = generate_credentials(*rng, "Evil CA");
            Bytes substituted = stripped;
            const auto evil_der = evil.cert.BER_encode();
            // Same-length replacement keeps all enclosing lengths valid; certs
            // for the same key type/subject size are equal-length here only
            // by chance, so fall back to a full re-encode if not.
            if(evil_der.size() == ca_der.size() && pos.has_value()) {
               std::copy(evil_der.begin(), evil_der.end(), substituted.begin() + static_cast<std::ptrdiff_t>(*pos));
            } else {
               Botan::PKCS12 evil_bundle;
               evil_bundle.add_key(creds.key);
               evil_bundle.add_certificate(creds.cert);
               evil_bundle.add_certificate(evil.cert);
               substituted = strip_mac(evil_bundle.export_to(Botan::PKCS12_Export_Options("pw").with_iterations(1), *rng));
            }
            const Botan::PKCS12 p(substituted, "pw");
            result.test_is_true("substituted CA accepted", p.ca_certificates().size() == 1 &&
                                                              p.ca_certificates().front().BER_encode() == evil_der);
         }

         // 4. With encrypted certificates (PBES2), stripping the MAC and
         //    modifying ciphertext yields a decoding failure rather than
         //    silently altered content, but a *wrong* password is now only
         //    detected through the CBC padding / PKCS#8 parse.
         const auto enc_pfx = bundle.export_to(
            Botan::PKCS12_Export_Options("pw").with_iterations(1).with_cert_encryption_algo("PBES2-SHA256-AES256"), *rng);
         const auto enc_stripped = strip_mac(enc_pfx);
         result.test_no_throw("encrypted-certs stripped file parses", [&]() { Botan::PKCS12 p(enc_stripped, "pw"); });
         result.test_throws("encrypted-certs stripped file, wrong password fails",
                            [&]() { Botan::PKCS12 p(enc_stripped, "wrong"); });

         return result;
      }

      static Test::Result test_unauthenticated_cbc_error_distinguishability() {
         Test::Result result("PKCS12 audit: error distinguishability without MAC");
         auto rng = Test::new_rng("pkcs12_audit_oracle");
         const auto creds = generate_credentials(*rng, "EE");
         Botan::PKCS12 bundle;
         bundle.add_key(creds.key);
         bundle.add_certificate(creds.cert);

         for(const auto& algo : {"PBE-SHA1-3DES", "PBES2-SHA256-AES256"}) {
            const auto pfx = bundle.export_to(
               Botan::PKCS12_Export_Options("pw").with_iterations(1).with_key_encryption_algo(algo).without_mac(), *rng);
            const auto bag = extract_first_shrouded_bag(pfx);
            if(!result.test_is_true(std::string(algo) + ": shrouded bag found", bag.has_value())) {
               continue;
            }
            const auto ct = bag->second;
            const auto ct_pos = find_bytes(pfx, ct);
            if(!result.test_is_true(std::string(algo) + ": ciphertext located", ct_pos.has_value())) {
               continue;
            }
            std::map<std::string, size_t> messages;
            size_t same_key_successes = 0;
            size_t other_key_successes = 0;
            size_t other_key_with_ee_match = 0;
            size_t other_key_caught_by_check_key = 0;
            size_t other_key_signatures_created = 0;
            size_t other_key_sig_verifies_under_cert = 0;
            size_t other_key_sig_verifies_under_own_pub = 0;
            for(size_t i = 0; i < ct.size(); ++i) {
               Bytes mod = pfx;
               mod[*ct_pos + i] ^= 0x01;
               try {
                  const Botan::PKCS12 p(mod, "pw");
                  // No exception: the modified ciphertext decrypted to a
                  // loadable PKCS#8 structure. Either the modification hit
                  // bytes the key decoder ignores (same key), or the private
                  // scalar itself was silently altered (different key).
                  if(p.private_keys().size() == 1 &&
                     p.private_keys().front()->private_key_bits() == creds.key->private_key_bits()) {
                     ++same_key_successes;
                  } else {
                     ++other_key_successes;
                     if(p.end_entity_certificate().has_value()) {
                        ++other_key_with_ee_match;
                     }
                     if(p.private_keys().size() == 1 && !p.private_keys().front()->check_key(*rng, false)) {
                        ++other_key_caught_by_check_key;
                     }
                     // Use the altered key through the ordinary signing API
                     // and try to verify the result under the certificate's
                     // public key and under the key object's own public point.
                     if(p.private_keys().size() == 1) {
                        const auto& altered = *p.private_keys().front();
                        const Bytes msg = {'m', 's', 'g'};
                        try {
                           Botan::PK_Signer signer(altered, *rng, "SHA-256");
                           const auto sig = signer.sign_message(msg, *rng);
                           ++other_key_signatures_created;
                           Botan::PK_Verifier under_cert(*creds.cert.subject_public_key(), "SHA-256");
                           if(under_cert.verify_message(msg, sig)) {
                              ++other_key_sig_verifies_under_cert;
                           }
                           const auto own_pub = altered.public_key();
                           Botan::PK_Verifier under_own(*own_pub, "SHA-256");
                           if(under_own.verify_message(msg, sig)) {
                              ++other_key_sig_verifies_under_own_pub;
                           }
                        } catch(const Botan::Exception& e) {
                           result.test_note(std::string("signing with altered key threw: ") + e.what());
                        }
                     }
                  }
               } catch(const Botan::Exception& e) {
                  // Group by exception message prefix (strip variable detail)
                  std::string msg = e.what();
                  msg = msg.substr(0, msg.find(':') == std::string::npos ? msg.size() : msg.find(':'));
                  messages[msg]++;
               }
            }
            result.test_note(Botan::fmt("{}: {} distinct error classes over {} single-bit ciphertext modifications; "
                                        "{} modifications parsed to the unchanged key, {} to a silently altered key",
                                        algo,
                                        messages.size(),
                                        ct.size(),
                                        same_key_successes,
                                        other_key_successes));
            // The EC private key decoder takes the public point from the
            // PKCS#8 structure without checking it against the scalar, so an
            // altered scalar can still "match" the end-entity certificate.
            // check_key() is the only API-level detection for that case.
            result.test_note(Botan::fmt("{}: {} of the {} silently altered keys still match the end-entity certificate",
                                        algo,
                                        other_key_with_ee_match,
                                        other_key_successes));
            result.test_sz_eq(std::string(algo) + ": check_key() rejects every silently altered key",
                              other_key_caught_by_check_key,
                              other_key_successes);
            // Signing with the altered key succeeds through the normal API and
            // produces signatures that verify neither under the certificate
            // nor under the key object's own (unaltered) public point.
            result.test_note(Botan::fmt("{}: {} of the {} silently altered keys signed a message without error; "
                                        "{} of these signatures verify under the certificate, {} under the key's own public point",
                                        algo,
                                        other_key_signatures_created,
                                        other_key_successes,
                                        other_key_sig_verifies_under_cert,
                                        other_key_sig_verifies_under_own_pub));
            result.test_sz_eq(std::string(algo) + ": every altered key signs without error",
                              other_key_signatures_created,
                              other_key_successes);
            result.test_sz_eq(std::string(algo) + ": no altered-key signature verifies under the certificate",
                              other_key_sig_verifies_under_cert,
                              0);
            result.test_sz_eq(std::string(algo) + ": no altered-key signature verifies under the key's own public point",
                              other_key_sig_verifies_under_own_pub,
                              0);
            for(const auto& [m, n] : messages) {
               result.test_note(Botan::fmt("  {} x '{}'", n, m));
            }
            // The existence of more than one error class is the padding
            // oracle property inherent to unauthenticated CBC; record it.
            result.test_is_true(std::string(algo) + ": every modification produced an error", messages.size() >= 1);
         }
         return result;
      }

      static Test::Result test_bitflip_sweep(const std::string& variant, bool modern) {
         Test::Result result("PKCS12 audit: single-bit-flip sweep (" + variant + ")");
         auto rng = Test::new_rng("pkcs12_audit_bitflip_" + variant);
         const auto creds = generate_credentials(*rng, "EE");
         Botan::PKCS12 bundle;
         bundle.add_key(creds.key);
         bundle.add_certificate(creds.cert);
         bundle.set_friendly_name("flip");

         const auto opts = modern ? Botan::PKCS12_Export_Options::modern("pw").with_iterations(1)
                                  : Botan::PKCS12_Export_Options::legacy_compat("pw")
                                       .with_iterations(1)
                                       .with_cert_encryption_algo("PBE-SHA1-3DES");
         const auto pfx = bundle.export_to(opts, *rng);
         const auto ref_fp = bundle_fingerprint(Botan::PKCS12(pfx, "pw"));

         // Offset of the MacData structure (the last element of the PFX). The
         // MAC covers only the authSafe content, so flips inside MacData that
         // do not change its semantics may parse successfully.
         size_t mac_start = pfx.size();
         {
            Botan::BER_Decoder outer(pfx);
            Botan::BER_Decoder pfx_seq = outer.start_sequence();
            size_t version = 0;
            pfx_seq.decode(version);
            (void)pfx_seq.get_next_object();  // authSafe
            const Botan::BER_Object mac_data = pfx_seq.get_next_object();
            const size_t len = mac_data.length();
            const size_t hdr = (len < 128) ? 2 : (len < 256) ? 3 : 4;
            mac_start = pfx.size() - len - hdr;
         }

         std::map<ParseOutcome, size_t> counts;
         std::set<std::string> other_types;
         std::set<std::string> non_botan_types;
         size_t silent_modifications = 0;
         size_t benign_successes = 0;

         for(size_t i = 0; i < pfx.size(); ++i) {
            for(const uint8_t mask : {uint8_t(0x01), uint8_t(0x80)}) {
               Bytes mod = pfx;
               mod[i] ^= mask;
               const auto o = try_parse(mod, "pw");
               counts[o.outcome]++;
               if(o.outcome == ParseOutcome::Ok) {
                  if(o.fingerprint == ref_fp) {
                     ++benign_successes;
                     result.test_note(Botan::fmt("benign flip accepted at byte {} (mask {}), MacData starts at {}", i, static_cast<unsigned>(mask), mac_start));
                     result.test_is_true("benign flip lies within MacData (outside the MAC'ed content)", i >= mac_start);
                  } else {
                     ++silent_modifications;
                     result.test_failure(Botan::fmt("modification at byte {} mask {} silently accepted", i, mask));
                  }
               } else if(o.outcome == ParseOutcome::OtherBotanException) {
                  other_types.insert(o.type_name);
               } else if(o.outcome == ParseOutcome::NonBotanException) {
                  non_botan_types.insert(o.type_name);
               }
            }
         }
         result.test_note(Botan::fmt("{} bytes, {} flips: {} auth failures, {} decoding errors, {} other Botan "
                                     "exceptions, {} non-Botan exceptions, {} benign successes",
                                     pfx.size(),
                                     pfx.size() * 2,
                                     counts[ParseOutcome::AuthTagError],
                                     counts[ParseOutcome::DecodingError],
                                     counts[ParseOutcome::OtherBotanException],
                                     counts[ParseOutcome::NonBotanException],
                                     benign_successes));
         for(const auto& t : other_types) {
            result.test_note("other Botan exception type: " + t);
         }
         for(const auto& t : non_botan_types) {
            result.test_note("non-Botan exception type: " + t);
         }
         result.test_sz_eq("no silently accepted modification", silent_modifications, 0);
         result.test_sz_eq("no non-Botan exceptions", counts[ParseOutcome::NonBotanException], 0);
         return result;
      }

      static Test::Result test_truncation_sweep() {
         Test::Result result("PKCS12 audit: truncation sweep");
         auto rng = Test::new_rng("pkcs12_audit_trunc");
         const auto creds = generate_credentials(*rng, "EE");
         Botan::PKCS12 bundle;
         bundle.add_key(creds.key);
         bundle.add_certificate(creds.cert);

         for(const bool with_mac : {true, false}) {
            auto opts = Botan::PKCS12_Export_Options("pw").with_iterations(1);
            if(!with_mac) {
               opts.without_mac();
            }
            const auto pfx = bundle.export_to(opts, *rng);
            size_t non_botan = 0;
            size_t successes = 0;
            for(size_t len = 0; len < pfx.size(); ++len) {
               const Bytes trunc(pfx.begin(), pfx.begin() + static_cast<std::ptrdiff_t>(len));
               const auto o = try_parse(trunc, "pw");
               if(o.outcome == ParseOutcome::Ok) {
                  ++successes;
               } else if(o.outcome == ParseOutcome::NonBotanException) {
                  ++non_botan;
                  result.test_note("non-Botan exception at length " + std::to_string(len) + ": " + o.type_name);
               }
            }
            const std::string tag = with_mac ? "with MAC" : "without MAC";
            result.test_sz_eq(tag + ": no truncation parses", successes, 0);
            result.test_sz_eq(tag + ": no non-Botan exceptions", non_botan, 0);

            // Appended trailing data is rejected too
            Bytes extended = pfx;
            extended.push_back(0x00);
            result.test_throws<Botan::Decoding_Error>(tag + ": trailing byte rejected",
                                                      [&]() { Botan::PKCS12 p(extended, "pw"); });
         }
         return result;
      }

      // ---------------------------------------------------------------
      // Hand-crafted structures
      // ---------------------------------------------------------------

      static Test::Result test_crafted_attributes_and_ordering() {
         Test::Result result("PKCS12 audit: bag attributes and end-entity ordering");
         auto rng = Test::new_rng("pkcs12_audit_crafted_attrs");
         const auto a = generate_credentials(*rng, "A");
         const auto b = generate_credentials(*rng, "B");

         // localKeyId takes precedence over the SPKI match for *ordering*:
         // key has id 01, cert A (matching SPKI) has id 02, cert B has id 01.
         {
            const auto pfx = simple_pfx({der_key_bag(*a.key, {.local_key_id = Bytes{0x01}}),
                                         der_cert_bag(a.cert, {.friendly_name = "A", .local_key_id = Bytes{0x02}}),
                                         der_cert_bag(b.cert, {.friendly_name = "B", .local_key_id = Bytes{0x01}})},
                                        "pw",
                                        MacSpec{});
            const Botan::PKCS12 p(pfx, "pw");
            result.test_sz_eq("both certs", p.certificates().size(), 2);
            result.test_is_true("certificates().front() is the localKeyId match (B), not the SPKI match",
                                p.certificates().front().BER_encode() == b.cert.BER_encode());
            result.test_is_true("end_entity_certificate() is the SPKI match (A)",
                                p.end_entity_certificate().has_value() &&
                                   p.end_entity_certificate()->BER_encode() == a.cert.BER_encode());
            result.test_is_true("ca_certificates() is [B]", p.ca_certificates().size() == 1 &&
                                                               p.ca_certificates().front().BER_encode() ==
                                                                  b.cert.BER_encode());
            result.test_is_true("bundle local key id from key", p.local_key_id() == Bytes{0x01});
            // Friendly name: the key has none; the code takes it from the
            // cert it *ordered* first (B), which is not the end entity.
            result.test_str_eq("friendly name taken from localKeyId-matched cert", p.friendly_name().value_or(""), "B");
         }

         // Friendly name on the key wins over names on certs
         {
            const auto pfx = simple_pfx({der_key_bag(*a.key, {.friendly_name = "key-name"}),
                                         der_cert_bag(a.cert, {.friendly_name = "cert-name"})},
                                        "pw",
                                        MacSpec{});
            const Botan::PKCS12 p(pfx, "pw");
            result.test_str_eq("key name preferred", p.friendly_name().value_or(""), "key-name");
            result.test_is_true("no local key id when none in file", !p.local_key_id().has_value());
         }

         // Friendly name only on a CA certificate is still surfaced
         {
            const auto pfx =
               simple_pfx({der_key_bag(*a.key), der_cert_bag(a.cert), der_cert_bag(b.cert, {.friendly_name = "ca-name"})},
                          "pw",
                          MacSpec{});
            const Botan::PKCS12 p(pfx, "pw");
            result.test_str_eq("CA cert name surfaced", p.friendly_name().value_or(""), "ca-name");
         }

         // UTF8String friendly name (non-conforming producers) is accepted
         {
            const auto pfx = simple_pfx(
               {der_key_bag(*a.key, {.friendly_name = "utf8", .friendly_name_as_utf8string = true}), der_cert_bag(a.cert)},
               "pw",
               MacSpec{});
            const Botan::PKCS12 p(pfx, "pw");
            result.test_str_eq("UTF8String friendly name accepted", p.friendly_name().value_or(""), "utf8");
         }

         // Multiple values for one attribute: the first is taken
         {
            const auto pfx = simple_pfx(
               {der_key_bag(*a.key, {.friendly_name = "first", .duplicate_friendly_name_value = true}), der_cert_bag(a.cert)},
               "pw",
               MacSpec{});
            const Botan::PKCS12 p(pfx, "pw");
            result.test_str_eq("first attribute value taken", p.friendly_name().value_or(""), "first");
         }

         // Unknown attribute OIDs are ignored; an empty attribute SET is fine
         {
            const auto pfx = simple_pfx({der_key_bag(*a.key, {.friendly_name = "n", .add_unknown_attribute = true}),
                                         der_cert_bag(a.cert, {.emit_empty_set = true})},
                                        "pw",
                                        MacSpec{});
            result.test_no_throw("unknown attribute / empty set tolerated", [&]() {
               const Botan::PKCS12 p(pfx, "pw");
               if(p.friendly_name().value_or("") != "n") {
                  throw Botan::Internal_Error("friendly name lost");
               }
            });
         }

         // Multiple keys: attributes are taken from the first key only, and
         // the end entity is matched against the first key only.
         {
            const auto pfx = simple_pfx({der_key_bag(*b.key, {.friendly_name = "B-key"}),
                                         der_key_bag(*a.key, {.friendly_name = "A-key", .local_key_id = Bytes{0x0A}}),
                                         der_cert_bag(a.cert, {.local_key_id = Bytes{0x0A}})},
                                        "pw",
                                        MacSpec{});
            const Botan::PKCS12 p(pfx, "pw");
            result.test_sz_eq("two keys", p.private_keys().size(), 2);
            result.test_str_eq("first key's name", p.friendly_name().value_or(""), "B-key");
            result.test_is_false("first key's (absent) id", p.local_key_id().has_value());
            result.test_is_false("no end entity for first key (B)", p.end_entity_certificate().has_value());
            result.test_sz_eq("A's cert is reported as CA cert", p.ca_certificates().size(), 0);
            // (ca_certificates(): single cert, size < 2 -> empty)
         }

         // Duplicate certificate: both stored, only the first skipped in ca_certificates()
         {
            const auto pfx = simple_pfx({der_key_bag(*a.key), der_cert_bag(a.cert), der_cert_bag(a.cert)}, "pw", MacSpec{});
            const Botan::PKCS12 p(pfx, "pw");
            result.test_sz_eq("duplicate cert stored twice", p.certificates().size(), 2);
            result.test_sz_eq("duplicate cert once in ca_certificates", p.ca_certificates().size(), 1);
         }

         // Unknown certificate type inside a CertBag is dropped silently
         {
            const auto pfx = simple_pfx({der_key_bag(*a.key), der_cert_bag(a.cert, {}, true)}, "pw", MacSpec{});
            const Botan::PKCS12 p(pfx, "pw");
            result.test_sz_eq("SDSI cert bag dropped", p.certificates().size(), 0);
            result.test_sz_eq("SDSI cert bag not reported as unknown", p.unknown_bag_types().size(), 0);
         }

         // Unknown bag types are recorded, in order, including duplicates
         {
            Bytes unknown_bag;
            Botan::DER_Encoder(unknown_bag)
               .start_sequence()
               .encode(Botan::OID::from_string("PKCS12.SecretBag"))
               .start_context_specific(0)
               .encode(Bytes{1, 2, 3}, Botan::ASN1_Type::OctetString)
               .end_cons()
               .end_cons();
            const auto pfx = simple_pfx({unknown_bag, der_cert_bag(a.cert), unknown_bag}, "pw", MacSpec{});
            const Botan::PKCS12 p(pfx, "pw");
            result.test_sz_eq("two unknown bags recorded", p.unknown_bag_types().size(), 2);
            result.test_sz_eq("cert still parsed", p.certificates().size(), 1);
         }

         return result;
      }

      static Test::Result test_crafted_nesting_boundary() {
         Test::Result result("PKCS12 audit: SafeContentsBag nesting boundary");
         auto rng = Test::new_rng("pkcs12_audit_nesting");
         const auto a = generate_credentials(*rng, "A");

         auto nested = [&](size_t levels) {
            Bytes inner = der_safe_contents({der_key_bag(*a.key), der_cert_bag(a.cert)});
            for(size_t i = 0; i < levels; ++i) {
               inner = der_safe_contents({der_safe_contents_bag(inner, {.friendly_name = "level"})});
            }
            return der_pfx(der_authenticated_safe({der_content_info_data(inner)}), "pw", MacSpec{});
         };

         // Depth counter: top level is 0, each SafeContentsBag adds one, and
         // depth >= 10 is rejected. Nine nested bags -> depth 9 (accepted),
         // ten nested bags -> depth 10 (rejected).
         result.test_no_throw("9 nested SafeContentsBags accepted", [&]() {
            const Botan::PKCS12 p(nested(9), "pw");
            if(p.private_keys().size() != 1 || !p.end_entity_certificate()) {
               throw Botan::Internal_Error("content lost in nesting");
            }
         });
         result.test_throws<Botan::Decoding_Error>("10 nested SafeContentsBags rejected",
                                                   [&]() { Botan::PKCS12 p(nested(10), "pw"); });

         // Attributes on a SafeContentsBag are ignored (no cert/key pushed)
         {
            const Bytes inner = der_safe_contents({der_key_bag(*a.key), der_cert_bag(a.cert)});
            const auto pfx = der_pfx(
               der_authenticated_safe({der_content_info_data(
                  der_safe_contents({der_safe_contents_bag(inner, {.friendly_name = "outer", .local_key_id = Bytes{9}})}))}),
               "pw",
               MacSpec{});
            const Botan::PKCS12 p(pfx, "pw");
            result.test_is_false("SafeContentsBag attributes not applied to content", p.friendly_name().has_value());
         }

         // Breadth is not limited: 500 sibling SafeContentsBags each holding
         // one cert are fine (linear cost).
         {
            std::vector<Bytes> bags;
            for(size_t i = 0; i < 500; ++i) {
               bags.push_back(der_safe_contents_bag(der_safe_contents({der_cert_bag(a.cert)})));
            }
            const auto pfx = der_pfx(der_authenticated_safe({der_content_info_data(der_safe_contents(bags))}), "pw", MacSpec{});
            const auto start = std::chrono::steady_clock::now();
            const Botan::PKCS12 p(pfx, "pw");
            result.test_sz_eq("500 sibling bags parsed", p.certificates().size(), 500);
            result.test_note(Botan::fmt("500 sibling bags parsed in {} ms", static_cast<size_t>(elapsed_ms(start))));
         }
         return result;
      }

      static Test::Result test_crafted_encrypted_data_variants() {
         Test::Result result("PKCS12 audit: EncryptedData variants");
         auto rng = Test::new_rng("pkcs12_audit_encdata");
         const auto a = generate_credentials(*rng, "A");
         const auto safe_contents = der_safe_contents({der_cert_bag(a.cert)});
         const Bytes salt = {1, 2, 3, 4, 5, 6, 7, 8};

         auto make = [&](const Botan::AlgorithmIdentifier& alg, const Bytes& ct, size_t version = 0,
                         const Botan::OID& inner = Botan::OID::from_string("PKCS7.Data")) {
            return der_pfx(der_authenticated_safe({der_content_info_encrypted(alg, ct, version, inner)}), "pw", MacSpec{});
         };

         // Valid EncryptedData produced with the test's PBE implementation
         {
            const auto enc = pbe_sha1_3des_encrypt(safe_contents, rfc7292_password_bytes("pw"), salt, 3, false);
            const Botan::PKCS12 p(make(enc.alg, enc.ciphertext), "pw");
            result.test_sz_eq("3DES EncryptedData parsed", p.certificates().size(), 1);

            result.test_throws<Botan::Decoding_Error>("EncryptedData version 1 rejected",
                                                      [&]() { Botan::PKCS12 p2(make(enc.alg, enc.ciphertext, 1), "pw"); });
            result.test_throws<Botan::Decoding_Error>("EncryptedData inner type not Data rejected", [&]() {
               Botan::PKCS12 p2(make(enc.alg, enc.ciphertext, 0, Botan::OID::from_string("PKCS7.EncryptedData")), "pw");
            });
            // Ciphertext not a block multiple
            Bytes odd = enc.ciphertext;
            odd.pop_back();
            result.test_throws("ciphertext not block aligned rejected", [&]() { Botan::PKCS12 p2(make(enc.alg, odd), "pw"); });
            // Empty ciphertext
            result.test_throws("empty ciphertext rejected", [&]() { Botan::PKCS12 p2(make(enc.alg, Bytes{}), "pw"); });
         }

         // Unsupported PBE OIDs from RFC 7292 Appendix C
         for(const auto& [name, oid] : std::vector<std::pair<std::string, std::string>>{
                {"RC4-128", "1.2.840.113549.1.12.1.1"},
                {"RC4-40", "1.2.840.113549.1.12.1.2"},
                {"RC2-128", "1.2.840.113549.1.12.1.5"},
                {"RC2-40", "1.2.840.113549.1.12.1.6"},
                {"PBES1 MD5-DES", "1.2.840.113549.1.5.3"},
             }) {
            Bytes params;
            Botan::DER_Encoder(params).start_sequence().encode(salt, Botan::ASN1_Type::OctetString).encode(size_t(1)).end_cons();
            const Botan::AlgorithmIdentifier alg(Botan::OID(oid), params);
            result.test_throws<Botan::Decoding_Error>(name + " PBE rejected",
                                                      [&]() { Botan::PKCS12 p(make(alg, Bytes(16, 0)), "pw"); });
         }

         // PBES2 cost caps
         {
            const auto start = std::chrono::steady_clock::now();
            result.test_throws<Botan::Decoding_Error>("PBKDF2 1e8+1 iterations rejected", [&]() {
               Botan::PKCS12 p(make(pbes2_pbkdf2_alg_id(Botan::BigInt::from_u64(100'000'001)), Bytes(32, 0)), "pw");
            });
            result.test_is_true("PBKDF2 cap enforced before work", elapsed_ms(start) < 2000.0);
            result.test_throws<Botan::Decoding_Error>("PBKDF2 0 iterations rejected", [&]() {
               Botan::PKCS12 p(make(pbes2_pbkdf2_alg_id(Botan::BigInt::zero()), Bytes(32, 0)), "pw");
            });
            // Garbage ciphertext with acceptable parameters: decrypt fails
            result.test_throws("PBKDF2 garbage ciphertext rejected", [&]() {
               Botan::PKCS12 p(make(pbes2_pbkdf2_alg_id(Botan::BigInt::from_u64(1)), Bytes(32, 0)), "pw");
            });

            const auto start2 = std::chrono::steady_clock::now();
            result.test_throws<Botan::Decoding_Error>("scrypt N=2^23 rejected", [&]() {
               Botan::PKCS12 p(make(pbes2_scrypt_alg_id(size_t(1) << 23, 8, 1), Bytes(32, 0)), "pw");
            });
            result.test_throws<Botan::Decoding_Error>("scrypt N*r*p > 2^26 rejected", [&]() {
               Botan::PKCS12 p(make(pbes2_scrypt_alg_id(size_t(1) << 22, 17, 1), Bytes(32, 0)), "pw");
            });
            result.test_throws<Botan::Decoding_Error>("scrypt r=65 rejected", [&]() {
               Botan::PKCS12 p(make(pbes2_scrypt_alg_id(size_t(1) << 10, 65, 1), Bytes(32, 0)), "pw");
            });
            result.test_throws<Botan::Decoding_Error>("scrypt p=1024 rejected", [&]() {
               Botan::PKCS12 p(make(pbes2_scrypt_alg_id(size_t(1) << 10, 1, 1024), Bytes(32, 0)), "pw");
            });
            result.test_throws<Botan::Decoding_Error>("scrypt N not power of 2 rejected", [&]() {
               Botan::PKCS12 p(make(pbes2_scrypt_alg_id(1000, 8, 1), Bytes(32, 0)), "pw");
            });
            result.test_is_true("scrypt caps enforced before work", elapsed_ms(start2) < 2000.0);
            // Small acceptable scrypt parameters actually run (and then fail
            // on the garbage ciphertext)
            result.test_throws("scrypt small params run then fail on ciphertext", [&]() {
               Botan::PKCS12 p(make(pbes2_scrypt_alg_id(1024, 8, 1), Bytes(32, 0)), "pw");
            });
            // Largest accepted memory footprint: N=2^22, r=16, p=1 passes the
            // parameter checks and would allocate (N+1)*128*r = 8 GiB. This
            // is documented rather than executed here.
            result.test_note("scrypt N=2^22 r=16 p=1 passes the parameter validation (8 GiB allocation)");
         }
         return result;
      }

      static Test::Result test_crafted_shrouded_key_cost_limits() {
         Test::Result result("PKCS12 audit: shrouded key bag cost limits and malformed keys");
         auto rng = Test::new_rng("pkcs12_audit_shrouded");
         const auto a = generate_credentials(*rng, "A");
         const Bytes salt = {1, 2, 3, 4, 5, 6, 7, 8};

         auto make = [&](const Bytes& bag) { return simple_pfx({bag}, "pw", std::nullopt); };

         const auto start = std::chrono::steady_clock::now();
         result.test_throws<Botan::Decoding_Error>("PBE 1e8+1 iterations rejected", [&]() {
            Botan::PKCS12 p(make(der_shrouded_key_bag(pbe_sha1_3des_alg_id(salt, Botan::BigInt::from_u64(100'000'001), false), Bytes(16, 0))), "pw");
         });
         result.test_throws<Botan::Decoding_Error>("PBE 0 iterations rejected", [&]() {
            Botan::PKCS12 p(make(der_shrouded_key_bag(pbe_sha1_3des_alg_id(salt, Botan::BigInt::zero(), false), Bytes(16, 0))), "pw");
         });
         result.test_throws<Botan::Decoding_Error>("PBE negative iterations rejected", [&]() {
            Botan::PKCS12 p(make(der_shrouded_key_bag(pbe_sha1_3des_alg_id(salt, -Botan::BigInt::from_u64(5), false),
                                                      Bytes(16, 0))),
                            "pw");
         });
         result.test_throws<Botan::Decoding_Error>("PBE 2^33 iterations rejected", [&]() {
            Botan::PKCS12 p(make(der_shrouded_key_bag(pbe_sha1_3des_alg_id(salt, Botan::BigInt::power_of_2(33), false),
                                                      Bytes(16, 0))),
                            "pw");
         });
         result.test_is_true("iteration caps enforced before work", elapsed_ms(start) < 2000.0);

         // Each bag carries its own iteration count, and every bag that
         // decrypts correctly is processed: the KDF cost is additive over
         // the bags of a file. Compare one vs. three valid 200k-iteration bags.
         {
            const auto p8 = Botan::PKCS8::BER_encode(*a.key);
            const auto enc =
               pbe_sha1_3des_encrypt(Bytes(p8.begin(), p8.end()), rfc7292_password_bytes("pw"), salt, 200'000, false);
            const Bytes one_bag = der_shrouded_key_bag(enc.alg, enc.ciphertext);
            const auto t1 = std::chrono::steady_clock::now();
            const Botan::PKCS12 p1(make(one_bag), "pw");
            const double one = elapsed_ms(t1);
            const auto t3 = std::chrono::steady_clock::now();
            const Botan::PKCS12 p3(simple_pfx({one_bag, one_bag, one_bag}, "pw", std::nullopt), "pw");
            const double three = elapsed_ms(t3);
            result.test_sz_eq("one bag parsed", p1.private_keys().size(), 1);
            result.test_sz_eq("three bags parsed", p3.private_keys().size(), 3);
            result.test_note(
               Botan::fmt("one 200k-iteration bag: {} ms, three bags: {} ms", static_cast<size_t>(one), static_cast<size_t>(three)));
            result.test_is_true("cost grows with the number of bags", three > one);
         }

         // PKCS8 that is not a private key (an EncryptedPrivateKeyInfo) in a plain KeyBag
         {
            const auto enc_p8 = Botan::PKCS8::BER_encode_encrypted_pbkdf_iter(*a.key, *rng, "kp", 1);
            result.test_throws("encrypted PKCS#8 inside KeyBag rejected",
                               [&]() { Botan::PKCS12 p(make(der_key_bag_raw(enc_p8)), "pw"); });
         }
         // Public key (SPKI) in a KeyBag
         {
            const auto spki = a.key->subject_public_key();
            result.test_throws("SPKI inside KeyBag rejected", [&]() { Botan::PKCS12 p(make(der_key_bag_raw(spki)), "pw"); });
         }
         // Correct key but shrouded bag with mismatching salt in the alg id
         {
            const auto p8 = Botan::PKCS8::BER_encode(*a.key);
            const auto enc = pbe_sha1_3des_encrypt(Bytes(p8.begin(), p8.end()), rfc7292_password_bytes("pw"), salt, 3, false);
            const auto wrong_alg = pbe_sha1_3des_alg_id(Bytes{8, 7, 6, 5, 4, 3, 2, 1}, Botan::BigInt::from_u64(3), false);
            result.test_throws("wrong salt in alg id fails",
                               [&]() { Botan::PKCS12 p(make(der_shrouded_key_bag(wrong_alg, enc.ciphertext)), "pw"); });
            // and declared as 2DES although encrypted with 3DES
            const auto wrong_kind = pbe_sha1_3des_alg_id(salt, Botan::BigInt::from_u64(3), true);
            result.test_throws("3DES ciphertext declared as 2DES fails",
                               [&]() { Botan::PKCS12 p(make(der_shrouded_key_bag(wrong_kind, enc.ciphertext)), "pw"); });
         }
         return result;
      }

      static Test::Result test_crafted_misc_structures() {
         Test::Result result("PKCS12 audit: miscellaneous structure variants");
         auto rng = Test::new_rng("pkcs12_audit_misc");
         const auto a = generate_credentials(*rng, "A");
         const auto b = generate_credentials(*rng, "B");

         // Keys in one ContentInfo, certs in another (any order)
         {
            const auto pfx = der_pfx(der_authenticated_safe({der_content_info_data(der_safe_contents({der_cert_bag(b.cert)})),
                                                             der_content_info_data(der_safe_contents({der_key_bag(*a.key)})),
                                                             der_content_info_data(der_safe_contents({der_cert_bag(a.cert)}))}),
                                     "pw",
                                     MacSpec{});
            const Botan::PKCS12 p(pfx, "pw");
            result.test_sz_eq("three content infos: key", p.private_keys().size(), 1);
            result.test_sz_eq("three content infos: certs", p.certificates().size(), 2);
            result.test_is_true("end entity reordered first",
                                p.certificates().front().BER_encode() == a.cert.BER_encode());
         }

         // PFX versions other than 3
         for(const size_t v : {size_t(0), size_t(2), size_t(4)}) {
            result.test_throws<Botan::Decoding_Error>(Botan::fmt("PFX version {} rejected", v), [&]() {
               Botan::PKCS12 p(der_pfx(der_authenticated_safe({}), "pw", MacSpec{}, v), "pw");
            });
         }

         // authSafe of type other than Data (SignedData public-key integrity mode)
         {
            Bytes out;
            Botan::DER_Encoder enc(out);
            enc.start_sequence();
            enc.encode(size_t(3));
            enc.start_sequence();
            enc.encode(Botan::OID("1.2.840.113549.1.7.2"));
            enc.start_context_specific(0);
            enc.encode(Bytes{0x30, 0x00}, Botan::ASN1_Type::OctetString);
            enc.end_cons();
            enc.end_cons();
            enc.end_cons();
            result.test_throws<Botan::Decoding_Error>("SignedData authSafe rejected", [&]() { Botan::PKCS12 p(out, "pw"); });
         }

         // Unsupported AuthenticatedSafe content type (EnvelopedData)
         {
            Bytes ci;
            Botan::DER_Encoder(ci)
               .start_sequence()
               .encode(Botan::OID("1.2.840.113549.1.7.3"))
               .start_context_specific(0)
               .encode(Bytes{0x30, 0x00}, Botan::ASN1_Type::OctetString)
               .end_cons()
               .end_cons();
            result.test_throws<Botan::Decoding_Error>("EnvelopedData content rejected", [&]() {
               Botan::PKCS12 p(der_pfx(der_authenticated_safe({ci}), "pw", MacSpec{}), "pw");
            });
         }

         // Empty input, single byte, and a SEQUENCE with nothing in it
         result.test_throws<Botan::Decoding_Error>("empty input", [&]() { Botan::PKCS12 p(Bytes{}, "pw"); });
         result.test_throws<Botan::Decoding_Error>("single byte", [&]() { Botan::PKCS12 p(Bytes{0x30}, "pw"); });
         result.test_throws<Botan::Decoding_Error>("empty sequence", [&]() { Botan::PKCS12 p(Bytes{0x30, 0x00}, "pw"); });

         // Certificate with a key type the SPKI comparison may not support is
         // simulated by a certificate bag whose certificate is syntactically
         // valid but whose public key algorithm is unknown: parsing of the
         // certificate itself succeeds (X509_Certificate is lazy about keys).
         // We cannot easily produce one here; skip.

         // A trailing byte after the PFX
         {
            auto pfx = simple_pfx({der_cert_bag(a.cert)}, "pw", MacSpec{});
            pfx.push_back(0);
            result.test_throws<Botan::Decoding_Error>("trailing byte rejected", [&]() { Botan::PKCS12 p(pfx, "pw"); });
         }

         // Indefinite-length (BER) encodings: the constructed [0] content of
         // EncryptedData is explicitly supported; test a BER indefinite-length
         // outer SEQUENCE to see whether the decoder accepts it.
         {
            const auto der = simple_pfx({der_cert_bag(a.cert)}, "pw", std::nullopt);
            // 30 82 LL LL <content> -> 30 80 <content> 00 00
            if(der.size() > 4 && der[0] == 0x30 && der[1] == 0x82) {
               Bytes ber = {0x30, 0x80};
               ber.insert(ber.end(), der.begin() + 4, der.end());
               ber.push_back(0x00);
               ber.push_back(0x00);
               const auto o = try_parse(ber, "pw");
               result.test_note(std::string("BER indefinite-length outer SEQUENCE: ") +
                                (o.outcome == ParseOutcome::Ok ? "accepted" : "rejected"));
            }
         }
         return result;
      }

      static Test::Result test_openssl_empty_password_convention() {
         Test::Result result("PKCS12 audit: OpenSSL empty-password convention");
         auto rng = Test::new_rng("pkcs12_audit_ossl");
         const auto a = generate_credentials(*rng, "A");
         const auto p8 = Botan::PKCS8::BER_encode(*a.key);
         const Bytes p8_bytes(p8.begin(), p8.end());
         const Bytes salt = {1, 2, 3, 4, 5, 6, 7, 8};

         // OpenSSL convention: KDF input is the empty byte string (not 00 00)
         const auto ossl_enc = pbe_sha1_3des_encrypt(p8_bytes, Bytes{}, salt, 3, false);
         const auto rfc_enc = pbe_sha1_3des_encrypt(p8_bytes, rfc7292_password_bytes(""), salt, 3, false);
         result.test_is_true("conventions produce different ciphertexts", ossl_enc.ciphertext != rfc_enc.ciphertext);

         const std::vector<Bytes> ossl_bags = {der_shrouded_key_bag(ossl_enc.alg, ossl_enc.ciphertext), der_cert_bag(a.cert)};
         const std::vector<Bytes> rfc_bags = {der_shrouded_key_bag(rfc_enc.alg, rfc_enc.ciphertext), der_cert_bag(a.cert)};

         // MAC and bag both in OpenSSL convention: accepted via fallback
         result.test_no_throw("OpenSSL-convention MAC + bag parses with empty password", [&]() {
            const Botan::PKCS12 p(simple_pfx(ossl_bags, "", MacSpec{.openssl_empty_pwd = true}), "");
            if(p.private_keys().size() != 1) {
               throw Botan::Internal_Error("key missing");
            }
         });
         // RFC convention throughout: accepted directly
         result.test_no_throw("RFC-convention MAC + bag parses with empty password", [&]() {
            const Botan::PKCS12 p(simple_pfx(rfc_bags, "", MacSpec{}), "");
            if(p.private_keys().size() != 1) {
               throw Botan::Internal_Error("key missing");
            }
         });
         // Mixed: RFC MAC but OpenSSL bag -> the fallback is not attempted for the bag
         result.test_throws("RFC MAC with OpenSSL-convention bag fails",
                            [&]() { Botan::PKCS12 p(simple_pfx(ossl_bags, "", MacSpec{}), ""); });
         // Mixed the other way: OpenSSL MAC, RFC bag -> fallback convention is
         // propagated to the bag, which then fails
         result.test_throws("OpenSSL MAC with RFC-convention bag fails",
                            [&]() { Botan::PKCS12 p(simple_pfx(rfc_bags, "", MacSpec{.openssl_empty_pwd = true}), ""); });
         // No MAC: only the RFC convention is tried
         result.test_no_throw("MAC-less RFC-convention bag parses",
                              [&]() { Botan::PKCS12 p(simple_pfx(rfc_bags, "", std::nullopt), ""); });
         result.test_throws("MAC-less OpenSSL-convention bag fails (no fallback without MAC)",
                            [&]() { Botan::PKCS12 p(simple_pfx(ossl_bags, "", std::nullopt), ""); });
         // The fallback must only apply to the empty password
         result.test_throws<Botan::Invalid_Authentication_Tag>("non-empty password never uses fallback", [&]() {
            Botan::PKCS12 p(simple_pfx(rfc_bags, "x", MacSpec{.openssl_empty_pwd = true}), "x");
         });
         return result;
      }
};

BOTAN_REGISTER_TEST("pkcs12", "pkcs12_audit", PKCS12_Audit_Tests);

}  // namespace

}  // namespace Botan_Tests

#endif
