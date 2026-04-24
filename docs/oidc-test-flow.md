# OIDC Test Token Flow (JWKS-backed)

This walkthrough generates a local JWKS, signs a JWT, and configures Prompt Manager to validate it.

## 1) Generate a test RSA keypair and JWKS

```bash
python - <<'PY'
import json
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64

def b64url_uint(val: int) -> str:
    b = val.to_bytes((val.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")

key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
pub = key.public_key().public_numbers()

jwks = {
    "keys": [{
        "kty": "RSA",
        "kid": "test-key",
        "use": "sig",
        "alg": "RS256",
        "n": b64url_uint(pub.n),
        "e": b64url_uint(pub.e),
    }]
}
print(json.dumps(jwks, indent=2))

pem = key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)
print(pem.decode("utf-8"))
PY
```

Save the JWKS output to `jwks.json` and the PEM private key to `private_key.pem`.

## 2) Serve JWKS locally

```bash
python -m http.server 9000
```

This serves `jwks.json` at `http://localhost:9000/jwks.json`.

## 3) Configure Prompt Manager

Set env vars:

```bash
OIDC_ENABLED=true
OIDC_ISSUER=http://localhost:9000
OIDC_AUDIENCE=promptguard
OIDC_JWKS_URL=http://localhost:9000/jwks.json
```

## 4) Mint a JWT for testing

```bash
python - <<'PY'
import jwt
from datetime import datetime, timedelta

with open("private_key.pem", "r") as f:
    key = f.read()

claims = {
    "sub": "user-123",
    "org_id": "org-abc",
    "iss": "http://localhost:9000",
    "aud": "promptguard",
    "exp": datetime.utcnow() + timedelta(minutes=10),
}

token = jwt.encode(claims, key, algorithm="RS256", headers={"kid": "test-key"})
print(token)
PY
```

## 5) Call the API

```bash
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/api/v1/prompts
```
