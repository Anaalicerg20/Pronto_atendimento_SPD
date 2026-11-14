import sys
import grpc
from mytimer import tstamp_msg


import ambulatorio_pb2
import ambulatorio_pb2_grpc
import consultorio_pb2
import consultorio_pb2_grpc

def run():
    if len(sys.argv) != 5:
        sys.exit(1)

    id_paciente = float(sys.argv[1])
    problema = sys.argv[2]
    endereco_amb = sys.argv[3]
    porta_amb = sys.argv[4]

    tstamp_msg(f"PI({id_paciente:4.1f},{problema})")

    porta_int = int(porta_amb)

    canal_amb = grpc.insecure_channel(f"{endereco_amb}:{porta_int}")
    stub_amb = ambulatorio_pb2_grpc.AmbulatorioStub(canal_amb) #primeiro: consumidor do serviço central ambulatório
    
    req_busca = ambulatorio_pb2.RequisicaoProcuraMedico(id_paciente=id_paciente)
    resposta_busca = stub_amb.ProcuraMedico(req_busca)

    tstamp_msg(f"PPMR({resposta_busca.ender}:{resposta_busca.porto})")

    if resposta_busca.porto == 0: #trata sala de espera lotada e fim de expedinete com paciente aguardando 
        sys.exit(0)
    
    canal_cons = grpc.insecure_channel(f"{resposta_busca.ender}:{resposta_busca.porto}")
    stub_cons = consultorio_pb2_grpc.ConsultorioStub(canal_cons)
    
    req_consulta = consultorio_pb2.RequisicaoConsulta(id_paciente=id_paciente, descricao=problema)
    resposta_consulta = stub_cons.Consulta(req_consulta) #novo canal direto com servidor local médico 
    
    tstamp_msg(f"PT -> {resposta_consulta.id_medico:4.1f}")

if __name__ == "__main__":
    run()