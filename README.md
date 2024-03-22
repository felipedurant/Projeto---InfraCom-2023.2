# Projeto de Comunicação Segura com Autoridade Certificadora

Este projeto implementa um sistema de comunicação segura entre nós, utilizando uma Autoridade Certificadora (CA) para gerenciar as chaves públicas. O sistema garante que as mensagens entre nós sejam encriptadas e apenas o nó destinatário possa descriptografá-las, utilizando um esquema híbrido de criptografia que combina AES para a encriptação de dados e RSA para o intercâmbio seguro das chaves.

## Funcionamento do Sistema

- **Geração de Chaves**: Cada nó gera seu próprio par de chaves RSA (pública e privada) e uma chave AES para encriptação de dados. A chave pública RSA é registrada na CA.
- **Registro na CA**: Ao registrar-se, o nó envia sua chave pública RSA para a CA. A CA, então, armazena essa chave pública associada ao identificador do nó.
- **Comunicação Segura**: Quando um nó deseja comunicar-se com outro, solicita à CA a chave pública RSA do destinatário para encriptar a chave AES de sessão, garantindo que apenas o nó destinatário possa descriptografar a mensagem com sua chave privada RSA.

## Topologia de Rede

A topologia da rede é configurada em forma de anel, e o algoritmo de roteamento adotado segue o sentido horário para simplificar a implementação e manter o sistema stateless, evitando complexidade adicional no código dos nós.

1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 1 -> ...

Esta abordagem garante que a mensagem criptografada passe pelos nós intermediários sem ser compreendida, até alcançar o nó destinatário, onde é descriptografada e lida.

## Requisitos

- Python 3.11.6 ou superior
- Biblioteca Cryptography do Python

## Configuração

Para configurar o ambiente de desenvolvimento e instalar as dependências necessárias, siga os passos abaixo:

```bash
# Criação de um ambiente virtual
python3 -m venv venv

# Ativação do ambiente virtual
source ./venv/bin/activate

# Instalação da biblioteca Cryptography
pip install cryptography
```

## Estrutura do Projeto

O projeto é organizado nos seguintes componentes principais:

- `src/ca.py`: Implementação da Autoridade Certificadora, responsável por gerenciar as chaves públicas dos nós.
- `src/node.py`: Script do nó, capaz de enviar e receber mensagens criptografadas.
- `README.md`: Documentação do projeto.

## Executando o Projeto

### Iniciar a Autoridade Certificadora (CA)

```bash
python src/ca.py
```

### Registrar os Nós e Iniciar a Comunicação

Abra terminais separados para cada nó e inicie-os passando um identificador único como argumento:

```bash
python src/node.py 1
python src/node.py 2
...
python src/node.py 6
```

Os nós agora são capazes de se comunicar de forma segura através da CA, solicitando a chave pública do destinatário para encriptar as mensagens.
