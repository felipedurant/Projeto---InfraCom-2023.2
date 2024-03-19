import os
import sys
import threading

from socket import socket, AF_INET, SOCK_DGRAM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding as padding_asym
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Configurações iniciais
ID = sys.argv[1]
BASE_PORT = 4200
BUFFER_SIZE = 4096

# Criação do socket UDP
sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(('localhost', BASE_PORT + int(ID)))

# Geração uma chave AES para o PC
aes_key = os.urandom(32)

# Iniciar regristro na Autoridade Certificadora
ca = ('localhost', 4242)
sock.sendto(b'REGISTER', ca)

ca_pem_pub, _ = sock.recvfrom(BUFFER_SIZE)
ca_pub = serialization.load_pem_public_key(ca_pem_pub)

aes_key_encrypted = ca_pub.encrypt(
    aes_key,
    padding_asym.OAEP(
        mgf=padding_asym.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
sock.sendto(aes_key_encrypted, ca)

# Aguarda chave privada do PC
pc_pem_priv_encrypted, _ = sock.recvfrom(BUFFER_SIZE)

# Aguardar confirmação de registro
msg, _ = sock.recvfrom(BUFFER_SIZE)
if msg.decode() == "REGISTERED":
    print(f"PC{ID} up and registered. Type 'TO <ID> <message>' to send a message.")

# Descriptografar pc_priv com aes_key
cipher_ecb = Cipher(algorithms.AES(aes_key), modes.ECB(), backend=default_backend())

decryptor_ecb = cipher_ecb.decryptor()
pt_ecb = decryptor_ecb.update(pc_pem_priv_encrypted) + decryptor_ecb.finalize()

unpadder_ecb = padding.PKCS7(128).unpadder()
decrypted_data_ecb = unpadder_ecb.update(pt_ecb) + unpadder_ecb.finalize()


# Pede a chave publica de um PC para a Autoridade Certificadora
def get_pub_key(pc_id):
    sock.sendto(b'GET_PUB', ca)
    sock.sendto(pc_id.encode(), ca)
    pc_pem_pub, _ = sock.recvfrom(BUFFER_SIZE)
    return pc_pem_pub


# Determina o próximo salto para um PC
def determine_next_hop(to_id, curr_id):
    graph = {1: [6, 2],  2: [1, 3],  3: [2, 4],
             4: [3, 5],  5: [4, 6],  6: [5, 1]}

    if curr_id == to_id:
        return 42

    return graph[curr_id][1]


def listen_for_messages():
    while True:
        data, _ = sock.recvfrom(BUFFER_SIZE)

        if data.decode().startswith("FROM"):
            from_id, _, to_id = data.decode().split(maxsplit=3)[1:]
            message, _ = sock.recvfrom(BUFFER_SIZE)

            if int(to_id) == int(ID):
                pc_priv = serialization.load_pem_private_key(decrypted_data_ecb, password=None)
                message_decrypted = pc_priv.decrypt(
                    message,
                    padding_asym.OAEP(
                        mgf=padding_asym.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ).decode()
                print(f"Message received from PC{from_id}: {message_decrypted}")
            else:
                next_hop = determine_next_hop(int(to_id), int(ID))
                sock.sendto(f"FROM {from_id} TO {to_id}".encode(), ('localhost', BASE_PORT + next_hop))
                sock.sendto(message, ('localhost', BASE_PORT + next_hop))
                print(f"Message forwarded from PC{from_id} to PC{next_hop}: {message}")


if __name__ == "__main__":
    thread_listen = threading.Thread(target=listen_for_messages)
    thread_listen.start()

    while True:
        msg = input()
        if msg.startswith("TO"):
            to_id, message = msg.split(maxsplit=2)[1:]

            sock.sendto(f'GET_PUB {to_id}'.encode(), ca)
            to_id_pem_pub_key, _ = sock.recvfrom(BUFFER_SIZE)

            to_id_pub_key = serialization.load_pem_public_key(to_id_pem_pub_key)
            message_encrypted = to_id_pub_key.encrypt(
                message.encode(),
                padding_asym.OAEP(
                    mgf=padding_asym.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            next_hop = determine_next_hop(int(to_id), int(ID))

            if next_hop == 42:
                sock.sendto(f"FROM {ID} TO {to_id}".encode(), ('localhost', BASE_PORT + int(to_id)))
                sock.sendto(message_encrypted, ('localhost', BASE_PORT + int(to_id)))
            else:
                sock.sendto(f"FROM {ID} TO {to_id}".encode(), ('localhost', BASE_PORT + next_hop))
                sock.sendto(message_encrypted, ('localhost', BASE_PORT + next_hop))
