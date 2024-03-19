from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Gerar o par de chaves para o servidor
chave_privada_servidor = rsa.generate_private_key(public_exponent=65537, key_size=2048)
chave_publica_servidor = chave_privada_servidor.public_key()

# Gerar o par de chaves para o cliente
chave_privada_cliente = rsa.generate_private_key(public_exponent=65537, key_size=2048)
chave_publica_cliente = chave_privada_cliente.public_key()

# Serializar a chave pública do cliente para o formato PEM
chave_publica_cliente_pem = chave_publica_cliente.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)


from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

assinatura = chave_privada_servidor.sign(
    chave_publica_cliente_pem,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)


from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives import hashes as crypt_hashes

# Suponha que esta seja a mensagem a ser criptografada
mensagem = f"{assinatura}"
mensagem_bytes = mensagem.encode()

# Criptografar a mensagem usando a chave pública do cliente
mensagem_criptografada = chave_publica_cliente.encrypt(
    assinatura,
    asym_padding.OAEP(
        mgf=asym_padding.MGF1(algorithm=crypt_hashes.SHA256()),
        algorithm=crypt_hashes.SHA256(),
        label=None
    )
)

mensagem_descriptografada = chave_privada_cliente.decrypt(
    mensagem_criptografada,
    asym_padding.OAEP(
        mgf=asym_padding.MGF1(algorithm=crypt_hashes.SHA256()),
        algorithm=crypt_hashes.SHA256(),
        label=None
    )
)


# Verificar a assinatura usando a chave pública do servidor
try:
    chave_publica_servidor.verify(
        mensagem_descriptografada,
        chave_publica_cliente_pem,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("A assinatura é válida.")
except Exception as e:
    print("A assinatura é inválida.", e)
