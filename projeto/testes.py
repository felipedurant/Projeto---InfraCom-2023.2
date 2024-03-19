from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

chave_privada = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

chave_publica = chave_privada.public_key()

print(chave_privada)
print(chave_publica)

chave_publica_pem = chave_publica.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

chave_privada_pem = chave_privada.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

print(chave_privada_pem.decode())
print(chave_publica_pem.decode())

print(serialization.load_pem_private_key(chave_privada_pem, password=None))
print(serialization.load_pem_public_key(chave_publica_pem))

