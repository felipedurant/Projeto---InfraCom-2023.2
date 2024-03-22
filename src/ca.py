import time
from socket import socket, AF_INET, SOCK_DGRAM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding as padding_asym

# Configurações iniciais
CA_PORT = 4242
BASE_PORT = 4200
BUFFER_SIZE = 4096

# Criação do socket UDP
sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(('localhost', CA_PORT))

# Geração da chave privada e pública da Autoridade Certificadora
priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
pub = priv.public_key()

# Dicionário para armazenar as chaves públicas dos PCs
pc_pem_pub_keys = {}

while True:
    msg, addr = sock.recvfrom(BUFFER_SIZE)

    if msg.decode() == "REGISTER":  # Aguarda por registros
        print(f"Registrando PC{addr[1] - BASE_PORT}...")
        pub_pem = pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        sock.sendto(pub_pem, addr)

        aes_key_encrypted, addr = sock.recvfrom(BUFFER_SIZE)
        aes_key = priv.decrypt(
            aes_key_encrypted,
            padding_asym.OAEP(
                mgf=padding_asym.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        pc_priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        pc_pub = pc_priv.public_key()

        pc_pem_priv = pc_priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        pc_pem_pub = pc_pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        pc_pem_pub_keys[addr[1] - BASE_PORT] = pc_pem_pub

        # Encriptar pc_priv com aes_key
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(pc_pem_priv) + padder.finalize()
        cipher_ecb = Cipher(algorithms.AES(aes_key), modes.ECB(), backend=default_backend())

        encryptor_ecb = cipher_ecb.encryptor()
        ct_ecb = encryptor_ecb.update(padded_data) + encryptor_ecb.finalize()

        sock.sendto(ct_ecb, addr)
        sock.sendto(b"REGISTERED", addr)
        print(f"PC{addr[1] - BASE_PORT} registrado.")
    elif msg.decode().startswith("GET_PUB"):
        pc_id = msg.decode().split()[1]
        pc_pem_pub = pc_pem_pub_keys[int(pc_id)]

        # Enviar qualquer coisa para escapar um loop da thread listen_for_messages no pc.py
        # Assim pc_pem_pub consegue ser recebido na linha 164 do pc.py
        sock.sendto(b'esc', addr)
        sock.sendto(pc_pem_pub, addr)
    else:
        print("Comando desconhecido:", msg.decode())
