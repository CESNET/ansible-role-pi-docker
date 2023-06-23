import subprocess
import sys
import urllib.request
import base64
import json

try:
    from cryptojwt.jws.jws import factory
    from cryptojwt.jwk.x509 import import_public_key_from_pem_data
    from cryptojwt.jwk.rsa import RSAKey
    from OpenSSL import crypto
except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "cryptojwt", "pyOpenSSL"]
    )
    from cryptojwt.jws.jws import factory
    from cryptojwt.jwk.x509 import import_public_key_from_pem_data
    from cryptojwt.jwk.rsa import RSAKey
    from OpenSSL import crypto


ca_cert_file = open("/etc/ssl/certs/GlobalSign_Root_CA_-_R3.pem", "r")
ca_cert_data = ca_cert_file.read()

jwt = urllib.request.urlopen("https://mds.fidoalliance.org").read().decode("utf-8")

jwt_keys = json.loads(base64.b64decode(jwt.split(".")[0] + "========"))["x5c"]


def cert_data_to_pem(pem_data):
    PREFIX = "-----BEGIN CERTIFICATE-----"
    POSTFIX = "-----END CERTIFICATE-----"
    if not pem_data.startswith(PREFIX):
        pem_data = "{}\n{}\n{}".format(PREFIX, pem_data, POSTFIX)
    return pem_data


def get_valid_subcertificate(trusted_certificates_data, certificates_data):
    store = crypto.X509Store()
    for ca_certificate_data in trusted_certificates_data:
        ca_certificate = crypto.load_certificate(
            crypto.FILETYPE_PEM, cert_data_to_pem(ca_certificate_data)
        )
        store.add_cert(ca_certificate)

    for certificate_data in certificates_data:
        certificate = crypto.load_certificate(
            crypto.FILETYPE_PEM, cert_data_to_pem(certificate_data)
        )
        store_ctx = crypto.X509StoreContext(store, certificate)
        try:
            result = store_ctx.verify_certificate()
        except crypto.X509StoreContextError:
            result = "unknown error"
        if result is None:  # means no error
            return certificate_data


intermediate_cert_data = get_valid_subcertificate([ca_cert_data], jwt_keys)

if intermediate_cert_data is None:
    print("No valid intermediate certificate found")
    exit()

jwt_key = get_valid_subcertificate([ca_cert_data, intermediate_cert_data], jwt_keys)

if jwt_key is None:
    print("No valid key found")
    exit()

verifier = factory(jwt, alg="RS256")
content = verifier.verify_compact(
    jwt,
    [RSAKey(pub_key=import_public_key_from_pem_data(jwt_key))],
)

all_attestation_root_certs = set()
for entry in content["entries"]:
    statuses = [report["status"] for report in entry["statusReports"]]
    if "FIDO_CERTIFIED" in statuses:
        all_attestation_root_certs.update(
            entry["metadataStatement"]["attestationRootCertificates"]
        )

print(
    "Found {} certified attestation root certs".format(len(all_attestation_root_certs))
)

i = 0
for cert in all_attestation_root_certs:
    with open("webauthn_attestation_certs/cert{}.pem".format(i), "w") as f:
        f.write(cert_data_to_pem(cert))
    i += 1
