# Pronto Atendimento Distribuído (gRPC + Threads)

Sistema simulador de pronto-atendimento médico distribuído desenvolvido em Python 3 utilizando gRPC para comunicação remota (RPC) e primitivas de sincronização (`threading.Lock`, `threading.Condition`).

---

## 1. Conceitos Fundamentais

### RPC (Remote Procedure Call)

Modelo de computação distribuída que permite a um programa invocar um procedimento/função em outro espaço de endereçamento (em outro processo ou máquina remota) com a mesma sintaxe de uma chamada de função local, abstraindo o transporte de rede.

### gRPC & Protocol Buffers (.proto)

- **Contrato Estrito:** O arquivo `.proto` define formalmente a interface do serviço (métodos RPC exportados) e a estrutura das mensagens de dados com tipagem estática.
- **Sem JSON:** A comunicação não trafega strings JSON nem requer parse textual; os dados são serializados diretamente em formato binário de alta densidade via Protobuf.
- **Geração de Stubs:** A compilação do `.proto` gera classes Python de apoio:
  - `*_pb2.py`: estruturas das mensagens e rotinas de serialização binária.
  - `*_pb2_grpc.py`: classes base para implementação dos servidores (`Servicer`) e procuradores de rede para os clientes (`Stub`).

---

## 2. Configuração do Ambiente

Requisitos: Python 3.8+ e ambiente Linux.

# Criar e ativar o ambiente virtual

python3 -m venv .venv
source .venv/bin/activate

# Instalar dependências necessárias

pip install grpcio grpcio-tools

# compilar arquivos .proto

make stubs

# limpar arquivos gerados automaticamente

make clean
