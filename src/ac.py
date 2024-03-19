# ac.py

import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('localhost', 4242))

nodes = [(f'localhost', 4201 + i) for i in range(6)]  # Lista de endereços dos nós



def listen_for_requests():
    while True:
        data, addr = sock.recvfrom(1024)
        message = data.decode()
        print(f"AC Received message: {message} from {addr}")
        # Se for uma mensagem de broadcast, reenviar para todos os nós
        if message.startswith("BROADCAST"):
            for node in nodes:
                if node != addr:  # Não enviar de volta para o remetente
                    sock.sendto(data, node)

listen_for_requests()
