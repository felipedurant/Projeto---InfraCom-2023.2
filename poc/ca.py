from socket import socket, AF_INET, SOCK_DGRAM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding


def criptografar_mensagem(mensagem, chave_publica_pem):
    chave_publica = serialization.load_pem_public_key(chave_publica_pem)
    mensagem_criptografada = chave_publica.encrypt(
        mensagem.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return mensagem_criptografada


# Geração da chave privada e pública, conforme você forneceu
chave_privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
chave_publica = chave_privada.public_key()

chave_publica_pem = chave_publica.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode('utf-8')


servidor = socket(AF_INET, SOCK_DGRAM)
servidor.bind(('localhost', 12345))

pem_public_keys = {}

print("Servidor esperando conexões...")

while True:
    cliente_pem_pub, endereco_cliente = servidor.recvfrom(4096)
    node_id = endereco_cliente[1] - 4200

    # pem_public_keys[node_id] = chave_privada.

    cliente_pub = serialization.load_pem_public_key(cliente_pem_pub)



    print(cliente_pub, type(cliente_pub))

    # mensagem_criptografada = criptografar_mensagem("hello", chave_publica_pem)
    # servidor.sendto(mensagem_criptografada, endereco_cliente)

    # print(f"NODE{node_id} registered with key {chave_publica_pem}.")
