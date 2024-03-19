import time
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('localhost', 4242))

nodes = [(f'localhost', 4201 + i) for i in range(6)]  # Lista de endereços dos nós
pc_keys = {}  # Chaves dos PCs

BASE_PORT = 4200
still_accepts_registration = True

def find_clockwise_path(start, end):
    graph = {1: [6, 2],  2: [1, 3],  3: [2, 4],
             4: [3, 5],  5: [4, 6],  6: [5, 1]}

    if start == end:
        return [start]

    clockwise_path = [start]

    while True:
        node = clockwise_path[-1]
        if node == end:
            break
        else:
            clockwise_path.append(graph[node][1])

    return clockwise_path

def find_anticlockwise_path(start, end):
    graph = {
        1: [6, 2],
        2: [1, 3],
        3: [2, 4],
        4: [3, 5],
        5: [4, 6],
        6: [5, 1],
    }

    if start == end:
        return [start]

    anticlockwise_path = [start]

    while True:
        node = anticlockwise_path[-1]

        if node == end:
            break
        else:
            anticlockwise_path.append(graph[node][0])

    return anticlockwise_path

def determine_next_hop(from_id, to_id, curr_id):
    if curr_id == to_id:
        return 42

    clockwise_path = find_clockwise_path(from_id, to_id)
    anticlockwise_path = find_anticlockwise_path(from_id, to_id)

    if len(clockwise_path) < len(anticlockwise_path):
        idx = clockwise_path.index(curr_id)
        return clockwise_path[idx + 1]
    elif len(clockwise_path) > len(anticlockwise_path):
        idx = anticlockwise_path.index(curr_id)
        return anticlockwise_path[idx + 1]
    else:
        idx = clockwise_path.index(curr_id)
        return clockwise_path[idx + 1]

def register_pc(pc_id):
    # Usa o timestamp atual como chave (shift) para simulação
    timestamp = int(time.time())
    pc_keys[pc_id] = timestamp
    # Envia confirmação de registro para o PC
    msg = "REGISTERED"
    sock.sendto(msg.encode(), ('localhost' ,BASE_PORT + pc_id))
    print(f"PC{pc_id} registered with key {timestamp}.")

def send_message(from_pc, to_pc, curr_pc, message, startswith):
    if startswith == "TO":
        next_hop = determine_next_hop(from_pc, to_pc, curr_pc)
        print(f"Next hop: {next_hop}")

        if next_hop == 42:
            sock.sendto(f"FROM {from_pc} TO {to_pc} {1}".encode(), ('localhost' ,BASE_PORT + to_pc))
        else:
            sock.sendto(f"FROM {from_pc} TO {to_pc} {0}".encode(), ('localhost' ,BASE_PORT + next_hop))

    if startswith == "FROM":
        next_hop = determine_next_hop(from_pc, to_pc, curr_pc)
        print(f"Next hop: {next_hop}")

        if next_hop == 42:
            sock.sendto(f"FROM {from_pc} TO {to_pc} {1}".encode(), ('localhost' , BASE_PORT + to_pc))
        else:
            sock.sendto(f"FROM {from_pc} TO {to_pc} {0}".encode(), ('localhost' ,BASE_PORT + next_hop))

def listen_for_requests():
    while True:
        data, addr = sock.recvfrom(1024)

        msg = data.decode()
        splitted_msg = msg.split()

        pc_id = addr[1] - BASE_PORT

        if splitted_msg[0].upper() == "FROM":
            send_message(int(splitted_msg[1]), int(splitted_msg[3]), pc_id, splitted_msg[4], startswith="FROM")

        if splitted_msg[0].upper() == "TO":
            send_message(pc_id, int(splitted_msg[1]), pc_id, splitted_msg[2], startswith="TO")

        if splitted_msg[0].upper() == "REGISTER":
            register_pc(pc_id)

listen_for_requests()
