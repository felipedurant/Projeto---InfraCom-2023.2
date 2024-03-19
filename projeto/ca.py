import socket
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def gerar_par_chaves():
    chave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    chave_publica = chave_privada.public_key()
    return chave_privada, chave_publica

def iniciar_ca(endereco_ip='localhost', porta=12345):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((endereco_ip, porta))
        print(f"CA rodando em {endereco_ip}:{porta}")

        while True:
            dados, endereco_cliente = sock.recvfrom(4096)
            mensagem = dados.decode()
            if mensagem == 'solicitar_chave':
                chave_privada, chave_publica = gerar_par_chaves()

                chave_publica_serializada = chave_publica.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode('utf-8')

                sock.sendto(chave_publica_serializada.encode(), endereco_cliente)

if __name__ == '__main__':
    iniciar_ca()
