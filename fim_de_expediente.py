import sys
import grpc


import ambulatorio_pb2
import ambulatorio_pb2_grpc

from mytimer import tstamp_msg

def run():

    if len(sys.argv) != 3:
        print("Uso: python3 fim_de_expediente.py <endereco> <porta>")
        return

    endereco = sys.argv[1]
    porta = sys.argv[2]

 
    porta_int = int(porta)

    tstamp_msg(f"FE({endereco}, {porta_int})")

    canal = grpc.insecure_channel(f"{endereco}:{porta}")#ativamento da linha telefônica

    stub = ambulatorio_pb2_grpc.AmbulatorioStub(canal)

    requisicao = ambulatorio_pb2.EmptyTermino()

    resposta = stub.Termino(requisicao)
    tstamp_msg(f"FE -> {resposta.liberados}")

if _name_ == "_main_":
    run()