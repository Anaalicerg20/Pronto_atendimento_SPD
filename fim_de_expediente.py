import sys
import grpc


import ambulatorio_pb2
import ambulatorio_pb2_grpc

from mytimer import tstamp_msg

def run():

    if len(sys.argv) != 3:
        sys.exit(1)

    endereco = sys.argv[1]
    porta = sys.argv[2] 
    porta_int = int(porta)

    tstamp_msg(f"FE({endereco},{porta_int})")

    canal = grpc.insecure_channel(f"{endereco}:{porta}")#ativamento da linha telefônica
    stub = ambulatorio_pb2_grpc.AmbulatorioStub(canal)
    requisicao = ambulatorio_pb2.EmptyTermino()

    resposta = stub.Termino(requisicao) 
    tstamp_msg(f"FE -> {resposta.liberados}") #dispara evento de encerramneto global

if __name__ == "__main__":
    run()