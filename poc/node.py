import sys
from socket import socket, AF_INET, SOCK_DGRAM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding


# Geração da chave privada e pública, conforme você forneceu
chave_privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
chave_publica = chave_privada.public_key()

chave_publica_pem = chave_publica.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode('utf-8')

ID = sys.argv[1]
BASE_PORT = 4200

cliente = socket(AF_INET, SOCK_DGRAM)
cliente.bind(('localhost', BASE_PORT + int(ID)))

# Enviar a chave pública para o servidor
servidor_endereco = ('localhost', 12345)
cliente.sendto(chave_publica_pem.encode(), servidor_endereco)

# Aguardar pela resposta criptografada do servidor
mensagem_criptografada, _ = cliente.recvfrom(4096)

# Descriptografar a mensagem
mensagem_descriptografada = chave_privada.decrypt(
    mensagem_criptografada,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

print("Mensagem recebida do servidor:", mensagem_descriptografada.decode())
