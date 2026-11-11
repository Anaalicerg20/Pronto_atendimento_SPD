import sys
import grpc
import threading
from concurrent import futures
from mytimer import tstamp_msg, my_sleep

import ambulatorio_pb2
import ambulatorio_pb2_grpc
import consultorio_pb2
import consultorio_pb2_grpc

class ConsultorioServicer(consultorio_pb2_grpc.ConsultorioServicer):
    def __init__(self, id_medico, sem_chegada, sem_pronto, sem_fim):
        self.id_medico = id_medico
        self.sem_chegada = sem_chegada
        self.sem_pronto = sem_pronto
        self.sem_fim = sem_fim
        self.paciente_id = 0
        self.paciente_desc = ""

    def Consulta(self, request, context):
        tstamp_msg(f"CI({request.id_paciente:4.1f},{request.descricao})")

        self.paciente_id = request.id_paciente
        self.paciente_desc = request.descricao
        self.sem_chegada.release()

        self.sem_pronto.acquire()

        self.sem_fim.acquire()

        tstamp_msg(f"CR({request.id_paciente:4.1f},{self.id_medico:4.1f})")
        return consultorio_pb2.RespostaConsulta(id_medico=self.id_medico)

def run():
    if len(sys.argv) != 6:
        print("Uso: python3 medico.py <porta_cons> <id_medico> <tempo_cons> <ender_amb> <porta_amb>")
        return

    porta_cons = int(sys.argv[1])
    id_medico = float(sys.argv[2])
    tempo_cons = float(sys.argv[3])
    ender_amb = sys.argv[4]
    porta_amb = int(sys.argv[5])

    sem_chegada = threading.Semaphore(0)
    sem_pronto = threading.Semaphore(0)
    sem_fim = threading.Semaphore(0)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    servicer_local = ConsultorioServicer(id_medico, sem_chegada, sem_pronto, sem_fim)
    consultorio_pb2_grpc.add_ConsultorioServicer_to_server(servicer_local, server)
    server.add_insecure_port(f"[::]:{porta_cons}")
    server.start()

    canal_amb = grpc.insecure_channel(f"{ender_amb}:{porta_amb}")
    stub_amb = ambulatorio_pb2_grpc.AmbulatorioStub(canal_amb)

    req_reg = ambulatorio_pb2.RequisicaoRegistraMedico(id_medico=id_medico, porto=porta_cons)
    resp_reg = stub_amb.RegistraMedico(req_reg)

    tstamp_msg(f"MI({id_medico:4.1f}) x {tempo_cons:3.1f} @ {porta_cons} = {resp_reg.resultado}")

    if resp_reg.resultado == -1:
        sys.exit(0)

    while True:
        tstamp_msg("MCPI") #imediatamente antes de chamar o paciente
        
        req_proc = ambulatorio_pb2.RequisicaoProcuraPaciente(id_medico=id_medico)
        resp_proc = stub_amb.ProcuraPaciente(req_proc)
        
        if resp_proc.id_paciente == 0:#se o ambulatorio encerrou o expediente
            tstamp_msg("MT ")
            sys.exit(0)

        tstamp_msg(f"MCPR -> {resp_proc.id_paciente:4.1f}")
        
        if resp_proc.id_paciente < 1:
            sys.exit(0)

        sem_chegada.acquire()
        
        p_id = servicer_local.paciente_id
        p_desc = servicer_local.paciente_desc
        
        sem_pronto.release()

        tstamp_msg(f"MAI({p_id:4.1f},{p_desc})")
        my_sleep(tempo_cons)
        tstamp_msg("MAF")

        sem_fim.release()

if __name__ == "__main__":
    run()