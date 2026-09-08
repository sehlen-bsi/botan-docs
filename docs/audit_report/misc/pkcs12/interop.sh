#!/bin/bash
# PKCS#12 interoperability matrix: Botan CLI <-> OpenSSL CLI
# Exercises parameter variations (ciphers, MAC digests, iteration counts,
# password shapes) in both directions and reports PASS/FAIL per case.
set -u
BOTAN=${BOTAN:-$PWD/botan}
OPENSSL=${OPENSSL:-openssl}
WORK=$(mktemp -d)
export LD_LIBRARY_PATH=$PWD
cd "$WORK" || exit 1

pass=0; fail=0; results=()
report() { if [ "$1" = 0 ]; then pass=$((pass+1)); results+=("PASS $2"); else fail=$((fail+1)); results+=("FAIL $2"); fi; }

# Key + self-signed cert (OpenSSL), plus a CA cert
$OPENSSL req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes -keyout key.pem -out cert.pem -subj "/CN=interop" -days 2 >/dev/null 2>&1
$OPENSSL req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes -keyout cakey.pem -out ca.pem -subj "/CN=interop CA" -days 2 >/dev/null 2>&1
KEY_FP=$($OPENSSL pkey -in key.pem -pubout -outform DER 2>/dev/null | sha256sum | cut -c1-16)

passwords=( "" "p" "pässwörd" "$(printf 'x%.0s' $(seq 1 70))" )
pwlabel() { case "$1" in "") echo empty;; "p") echo short;; "pässwörd") echo unicode;; *) echo long70;; esac; }

# ---------- Botan export -> OpenSSL parse ----------
for pw in "${passwords[@]}"; do
  for keyc in PBES2-SHA256-AES256 PBES2-SHA256-AES128 PBE-SHA1-3DES PBE-SHA1-2DES; do
    for certc in "" PBE-SHA1-3DES PBES2-SHA256-AES128; do
      for mac in SHA-1 SHA-256 SHA-512; do
        for iter in 1 2048; do
          label="botan->ossl pw=$(pwlabel "$pw") key=$keyc cert=${certc:-none} mac=$mac iter=$iter"
          out="b_$(echo "$label" | md5sum | cut -c1-8).p12"
          if ! $BOTAN pkcs12_export --output="$out" --pass="$pw" --key-cipher="$keyc" --cert-cipher="$certc" --mac-digest="$mac" --iterations="$iter" key.pem cert.pem ca.pem >/dev/null 2>err.txt; then
            report 1 "$label (botan export failed: $(head -c 200 err.txt))"; continue
          fi
          # OpenSSL: extract key and check it matches, count certs
          if ! $OPENSSL pkcs12 -in "$out" -passin "pass:$pw" -nodes -out parsed.pem >/dev/null 2>err.txt; then
            report 1 "$label (openssl parse failed: $(head -c 200 err.txt))"; continue
          fi
          fp=$($OPENSSL pkey -in parsed.pem -pubout -outform DER 2>/dev/null | sha256sum | cut -c1-16)
          ncert=$(grep -c "BEGIN CERTIFICATE" parsed.pem)
          if [ "$fp" = "$KEY_FP" ] && [ "$ncert" = 2 ]; then report 0 "$label"; else report 1 "$label (key fp $fp, $ncert certs)"; fi
          # wrong password must fail in OpenSSL
          if $OPENSSL pkcs12 -in "$out" -passin "pass:${pw}x" -nodes -out /dev/null >/dev/null 2>&1; then report 1 "$label (openssl accepted wrong password)"; fi
        done
      done
    done
  done
done

# Botan without MAC -> OpenSSL
for pw in "" "p"; do
  label="botan->ossl no-mac pw=$(pwlabel "$pw")"
  $BOTAN pkcs12_export --output=nomac.p12 --pass="$pw" --no-mac --iterations=1 key.pem cert.pem >/dev/null 2>err.txt || { report 1 "$label (export failed)"; continue; }
  if $OPENSSL pkcs12 -in nomac.p12 -passin "pass:$pw" -nodes -out parsed.pem >/dev/null 2>err.txt; then report 0 "$label"; else report 1 "$label ($(head -c 200 err.txt))"; fi
done

# ---------- OpenSSL export -> Botan parse ----------
ossl_variants=(
  "default|"
  "legacy|-legacy -keypbe PBE-SHA1-3DES -certpbe PBE-SHA1-RC2-40 -macalg sha1"
  "3des-3des-sha1|-keypbe PBE-SHA1-3DES -certpbe PBE-SHA1-3DES -macalg sha1"
  "2des-2des-sha1|-keypbe PBE-SHA1-2DES -certpbe PBE-SHA1-2DES -macalg sha1"
  "aes128-none-sha384|-keypbe AES-128-CBC -certpbe NONE -macalg sha384"
  "aes256-aes256-sha512|-keypbe AES-256-CBC -certpbe AES-256-CBC -macalg sha512"
  "aes256-3des-sha224|-keypbe AES-256-CBC -certpbe PBE-SHA1-3DES -macalg sha224"
  "iter1|-iter 1 -maciter"
  "nomaciter|-nomaciter"
  "nomac|-nomac"
  "aes-nomac-emptycertpbe|-nomac -certpbe NONE"
  "maciter100k|-macsaltlen 20 -iter 100000"
)
for pw in "${passwords[@]}"; do
  for v in "${ossl_variants[@]}"; do
    name=${v%%|*}; args=${v#*|}
    label="ossl->botan pw=$(pwlabel "$pw") $name"
    out="o_$(echo "$label" | md5sum | cut -c1-8).p12"
    # shellcheck disable=SC2086
    if ! $OPENSSL pkcs12 -export -in cert.pem -inkey key.pem -certfile ca.pem -name "friendly $name" -out "$out" -passout "pass:$pw" $args >/dev/null 2>err.txt; then
      report 1 "$label (openssl export failed: $(head -c 200 err.txt))"; continue
    fi
    if ! $BOTAN pkcs12_info --pass="$pw" --key-out=bk.pem --cert-out=bc.pem --chain-out=bchain.pem "$out" >/dev/null 2>err.txt; then
      report 1 "$label (botan parse failed: $(head -c 200 err.txt))"; continue
    fi
    $BOTAN pkcs12_info --pass="$pw" "$out" >info.txt 2>/dev/null
    fp=$($OPENSSL pkey -in bk.pem -pubout -outform DER 2>/dev/null | sha256sum | cut -c1-16)
    nchain=$(grep -c "BEGIN CERTIFICATE" bchain.pem 2>/dev/null || echo 0)
    if [ "$fp" = "$KEY_FP" ] && [ "$nchain" = 1 ] && grep -q "friendly $name" info.txt; then report 0 "$label"; else report 1 "$label (fp $fp chain $nchain name:$(grep -c 'friendly' info.txt))"; fi
    if $BOTAN pkcs12_info --pass="${pw}x" "$out" >/dev/null 2>&1; then report 1 "$label (botan accepted wrong password)"; fi
  done
done

printf '%s\n' "${results[@]}"
echo "----"
echo "PASS: $pass  FAIL: $fail"
echo "workdir: $WORK"
