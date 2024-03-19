import socket
import threading
import sys

# Configurações iniciais
ID = sys.argv[1]
BASE_PORT = 4200
AC_ADDRESS = ('localhost', 4242)

# Criação do socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('localhost', BASE_PORT + int(ID)))

def listen_for_messages():
    while True:
        data, _ = sock.recvfrom(1024)
        msg = data.decode()
        if msg == "REGISTERED":
            is_registred = True
            print(f"PC{ID} up and registered. Type 'TO <ID> <message>' to send a message.")
        break

    while True:
        data, _ = sock.recvfrom(1024)

        msg = data.decode()
        splitted_msg = msg.split()

        if splitted_msg[0].upper() == "FROM":
            from_id = int(splitted_msg[1])
            to_id = int(splitted_msg[3])

            if to_id == int(ID):
                print(f"Received message: {' '.join(splitted_msg[4])} from PC{from_id}")
            else:
                sock.sendto(msg.encode(), AC_ADDRESS)
                print(f"Fowarded message: {' '.join(splitted_msg[4])} from PC{from_id} to PC{to_id}")

# Iniciando a thread para escutar mensagens
listener_thread = threading.Thread(target=listen_for_messages)
listener_thread.daemon = True
listener_thread.start()

def send_message(msg, address):
    sock.sendto(msg.encode(), address)

def register_with_ac():
    send_message(f"REGISTER", AC_ADDRESS)

# Registra-se na AC
register_with_ac()

# Loop para enviar mensagens
try:
    while True:
        msg = input()
        splitted_msg = msg.split()
        if splitted_msg[0].upper() == "TO":
            send_message(msg, AC_ADDRESS)
except KeyboardInterrupt:
    print("Shutting down.")
