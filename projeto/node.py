import socket
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

def gerar_par_chaves():
    chave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    chave_publica = chave_privada.public_key()
    return chave_privada, chave_publica

def solicitar_chave_publica_ca(endereco_ca=('localhost', 12345)):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(b'solicitar_chave', endereco_ca)
        dados, _ = sock.recvfrom(4096)

        chave_publica_ca = serialization.load_pem_public_key(dados)
        return chave_publica_ca

# Função para criptografar mensagens usando a chave pública
def criptografar_mensagem_com_chave_publica(mensagem, chave_publica):
    mensagem_criptografada = chave_publica.encrypt(
        mensagem.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=SHA256()),
            algorithm=SHA256(),
            label=None
        )
    )
    return mensagem_criptografada

# Função para descriptografar mensagens usando a chave privada
def descriptografar_mensagem_com_chave_privada(mensagem_criptografada, chave_privada):
    mensagem_descriptografada = chave_privada.decrypt(
        mensagem_criptografada,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=SHA256()),
            algorithm=SHA256(),
            label=None
        )
    )
    return mensagem_descriptografada.decode()

if __name__ == '__main__':
    # Gera o par de chaves do nó cliente
    # chave_privada_no, chave_publica_no = gerar_par_chaves()

    # Solicita a chave pública da CA
    chave_publica_ca = solicitar_chave_publica_ca()
    print(chave_publica_ca)
    # print("Chave pública da CA recebida com sucesso.")

    # Aqui, o nó poderia, por exemplo, criptografar uma mensagem usando a chave pública da CA
    # e então enviá-la para outro nó, que usaria a chave privada correspondente para descriptografar a mensagem.
    # mensagem = "Olá, mundo segredo!"
    # mensagem_criptografada = criptografar_mensagem_com_chave_publica(mensagem, chave_publica_ca)
    # print("Mensagem criptografada:", mensagem_criptografada)

    # Para descriptografar, o nó de destino precisaria da chave privada correspondente, o que não é o caso aqui,
    # mas isso demonstra como a comunicação segura poderia ser estabelecida.
