# node.py

import socket
import threading
import sys

# Configurações iniciais
ID = sys.argv[1]
BASE_PORT = 4200
ac_address = ('localhost', 4242)

# Topologia dos vizinhos
neighbors = {
    '1': [('localhost', BASE_PORT + 6), ('localhost', BASE_PORT + 2)],
    '2': [('localhost', BASE_PORT + 1), ('localhost', BASE_PORT + 3)],
    '3': [('localhost', BASE_PORT + 2), ('localhost', BASE_PORT + 4)],
    '4': [('localhost', BASE_PORT + 3), ('localhost', BASE_PORT + 5)],
    '5': [('localhost', BASE_PORT + 4), ('localhost', BASE_PORT + 6)],
    '6': [('localhost', BASE_PORT + 5), ('localhost', BASE_PORT + 1)],
}

# Criação do socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('localhost', BASE_PORT + int(ID)))

# Simulação simples de criptografia e descriptografia usando cifra de César
def encrypt(message, shift=3):
    encrypted = ''.join(chr((ord(char) + shift - 65) % 26 + 65)
                        for char in message.upper() if char.isalpha())
    return encrypted

def decrypt(message, shift=3):
    decrypted = ''.join(chr((ord(char) - shift - 65) % 26 + 65)
                        for char in message.upper() if char.isalpha())
    return decrypted

def send_message(msg, address):
    # Mensagem é criptografada antes do envio
    encrypted_msg = encrypt(msg)
    sock.sendto(encrypted_msg.encode(), address)

def listen_for_messages():
    while True:
        data, addr = sock.recvfrom(1024)
        decrypted_msg = decrypt(data.decode())
        print(f"Received message: {decrypted_msg} from {addr}")

# Iniciando a thread para escutar mensagens
listener_thread = threading.Thread(target=listen_for_messages)
listener_thread.daemon = True
listener_thread.start()

def send_to_neighbors(message):
    for neighbor in neighbors[ID]:
        send_message(message, neighbor)

def broadcast_message(message):
    # Enviar para AC que irá redistribuir
    send_message(f"BROADCAST FROM PC{ID}: {message}", ac_address)

print(f"PC{ID} up and running. Type messages to send, 'BROADCAST' to broadcast, 'EXIT' to exit.")

# Loop para enviar mensagens
try:
    while True:
        msg = input()
        if msg.upper() == "BROADCAST":
            broadcast_message(f"Hello from PC{ID}")
        elif msg.upper() == "EXIT":
            break
        else:
            break
except KeyboardInterrupt:
    print("Shutting down.")
