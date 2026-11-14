from concurrent import futures
import grpc
import ambulatorio_pb2
import ambulatorio_pb2_grpc
from collections import deque

import sys

from mytimer import tstamp_msg, mysleep
from threading import Thread, Lock, Condition, Event

def split_peer(addr_str: str):
    if addr_str.startswith(("ipv4:", "ipv6:")):
        addr_str = addr_str.split(":", 1)[1]

    address, separator, port = addr_str.rpartition(":")
    if address.startswith("[") and address.endswith("]"):
        address = address[1:-1]

    return address, int(port)
class AmbulatorioServicer(ambulatorio_pb2_grpc.AmbulatorioServicer):
    
    def __init__(self, num_medicos, num_cadeiras, stop_event):

        self.fila_medicos = deque(maxlen=num_medicos) #fila médicos livres: guarda prontuários iniciados pelos médicos
        self.fila_espera = deque(maxlen=num_cadeiras) #fila pacientes em espera: guarda prontuários iniciados pelos pacientes

        self.diretorio_medicos = {} #associa o médico à porta do seu consultório

        self.chamadas_ativas = 0 #controle RPC 

        self.lock = Lock() #Lock compartilhado entre filas, diretório, contador (chamadas_ativas) : simplifica a seção crítica
        self.cond_chamadas_ativas = Condition(self.lock) #variável de condição atrelado ao self.lock

        self.max_medicos = num_medicos
        self.stop_event = stop_event

    def ProcuraMedico(self, request, context):

        with self.lock:
            self.chamadas_ativas += 1

            id_paciente = request.id_paciente 
            tstamp_msg ("APMI(%4.1f)" % (id_paciente))

            #prontuário: objeto de sincronização, quem chega primeiro preenche o prontário e dorme, quem chega depois preenche a seção flatante e acorda o primeiro 
            if len(self.fila_medicos) > 0 : #há medicos livres 
                prontuario = self.fila_medicos.popleft() #retira o prontuário
                prontuario ["id_paciente"] = id_paciente #anota  id do pacinete no prontuário
                
                #pega id, ender e consultório
                id_medico_atendente = prontuario["id_medico"]
                endereco_medico = self.diretorio_medicos[id_medico_atendente]["ender"]
                consultorio_medico = self.diretorio_medicos[id_medico_atendente]["porto"]

                prontuario["condicao"].notify() 

                tstamp_msg ("APMR(%4.1f) -> M(%4.1f) @ %s:%d" % (id_paciente, id_medico_atendente, endereco_medico, consultorio_medico))
                
                self.chamadas_ativas -= 1
                if self.chamadas_ativas == 0:
                    self.cond_chamadas_ativas.notify()

                return ambulatorio_pb2.RespostaProcuraMedico(
                    id_medico=id_medico_atendente,      
                    ender=endereco_medico, 
                    porto=consultorio_medico
                )
        
            elif len(self.fila_espera) != self.fila_espera.maxlen:
                #medicos ocupados mas existe cadeira: cria o prontuario com id do paciente 
                prontuario = {
                "id_paciente": id_paciente,
                "id_medico": None,
                "condicao": Condition(self.lock)
                }

                self.fila_espera.append(prontuario) #add prontuario na fila
                tstamp_msg ("APME(%4.1f)" % (id_paciente))

                while prontuario["id_medico"] is None:
                    prontuario["condicao"].wait() #espera até um médico ficar livre e pegar esse prontuário

                #Médico está livre(prontuario["condicao"] foi notificado): 
                id_medico_atendente = prontuario["id_medico"]

                # Verifica se acordou por causa do fim de expediente
                if id_medico_atendente == 0:
                    endereco_medico = ""
                    consultorio_medico = 0
                else:
                    endereco_medico = self.diretorio_medicos[id_medico_atendente]["ender"]
                    consultorio_medico = self.diretorio_medicos[id_medico_atendente]["porto"]

                tstamp_msg("APMR(%4.1f) -> M(%4.1f) @ %s:%d" % (id_paciente, id_medico_atendente, endereco_medico, consultorio_medico))
                
                self.chamadas_ativas -= 1
                if self.chamadas_ativas == 0:
                    self.cond_chamadas_ativas.notify()
                    
                return ambulatorio_pb2.RespostaProcuraMedico(
                    id_medico=id_medico_atendente,
                    ender=endereco_medico,
                    porto=consultorio_medico
                )
            if len(self.fila_espera) == self.fila_espera.maxlen: #sem cadeiras: cliente vai embora
                            tstamp_msg ("APMR(%4.1f) -> M(%4.1f) @ %s:%d" % (id_paciente, 0, "", 0))
                            
                            self.chamadas_ativas -= 1
                            if self.chamadas_ativas == 0:
                                self.cond_chamadas_ativas.notify()
                            
                            return ambulatorio_pb2.RespostaProcuraMedico(
                                id_medico= 0,    
                                ender="", 
                                porto= 0
                            )
            
    def RegistraMedico(self, request, context):

        with self.lock:
            self.chamadas_ativas += 1

            id_medico = request.id_medico
            consultorio = request.porto
            ip_medico , _ = split_peer(context.peer())

            if len(self.diretorio_medicos) == self.max_medicos:
                tstamp_msg ("ARM(%4.1f) @ %s:%d = %d" % (id_medico, ip_medico, consultorio, -1))
                self.chamadas_ativas -= 1
                if self.chamadas_ativas == 0:
                    self.cond_chamadas_ativas.notify()
                return ambulatorio_pb2.RespostaRegistraMedico(status=-1)

            self.diretorio_medicos[id_medico] = {
                "ender": ip_medico,
                "porto": consultorio
            }
            tstamp_msg ("ARM(%4.1f) @ %s:%d = %d" % (id_medico, ip_medico, consultorio, 0))

            self.chamadas_ativas -= 1
            if self.chamadas_ativas == 0:
               self.cond_chamadas_ativas.notify()

        return ambulatorio_pb2.RespostaRegistraMedico(status=0)

    def ChamaPaciente(self, request, context):
        with self.lock:
            self.chamadas_ativas += 1
            id_medico = request.id_medico
            tstamp_msg ("ACPI(%4.1f)" % (id_medico))


            if len(self.fila_espera) > 0: #tem pacinetes esperando 
                prontuario = self.fila_espera.popleft()
                prontuario["id_medico"] = id_medico #escreve o id do medico que atenderá no prontuário 
                id_paciente_atendido = prontuario["id_paciente"] #lê o id do paciente 

                prontuario["condicao"].notify() #notifica que o médico "chegou"

            else:
                prontuario = {
                    "id_paciente": None,
                    "id_medico": id_medico,
                    "condicao": Condition(self.lock)
                }

                self.fila_medicos.append(prontuario) #add prontuario na fila
                tstamp_msg ("ACPE(%4.1f)" % (id_medico))
                
                while prontuario["id_paciente"] is None:
                    prontuario["condicao"].wait() #espera até um pacinete chegar

                id_paciente_atendido = prontuario["id_paciente"]
        #dorme fora do lock para não bloquear todo o ambulatório enquanto simula tempo de descanso
        if id_paciente_atendido != 0:
            mysleep(0.1)

        with self.lock:
            tstamp_msg ("ACPR(%4.1f) -> P(%4.1f)" % (id_medico, id_paciente_atendido))
            self.chamadas_ativas -= 1

            if self.chamadas_ativas == 0:
                self.cond_chamadas_ativas.notify()

        return ambulatorio_pb2.RespostaChamaPaciente(id_paciente=id_paciente_atendido)
    
    def executar_desligamento(self):
        mysleep(1)
        self.stop_event.set()

    def Termino(self, request, context):
        with self.lock:
            tstamp_msg ("ATEI")

            count_medicos = 0
            count_pacientes = 0

            while len(self.fila_medicos) > 0:
                count_medicos += 1 
                prontuario = self.fila_medicos.popleft()
                prontuario["id_paciente"] = 0.0
                prontuario["condicao"].notify()

            while len(self.fila_espera) > 0:
                count_pacientes += 1
                prontuario = self.fila_espera.popleft()
                prontuario["id_medico"] = 0.0
                prontuario["condicao"].notify()

            if count_pacientes > 0:
                liberados = -count_pacientes
            else:
                liberados = count_medicos
            #garante que nenhuma thread RPC ativa seja abortada no meio da execção antes do servidr fechar
            while self.chamadas_ativas > 0:
                self.cond_chamadas_ativas.wait()

            Thread(target=self.executar_desligamento).start() #retorna a resposta pela rede antes q a thread principal execute "server.stop(0)"
            tstamp_msg("ATER -> %d" % liberados)

            return ambulatorio_pb2.RespostaTermino(liberados=liberados)

def serve():
    if len(sys.argv) != 4:
        sys.exit(1)
    num_cadeiras = int(sys.argv[1]) 
    num_medicos = int(sys.argv[2]) 
    porta = int(sys.argv[3])

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    stop_event = Event()

    ambulatorio_pb2_grpc.add_AmbulatorioServicer_to_server(AmbulatorioServicer(num_medicos, num_cadeiras, stop_event), server )
    
    server.add_insecure_port(f'[::]:{porta}')
    server.start()
    tstamp_msg("AI(%d,%d)@%d" % (num_cadeiras, num_medicos, porta))

    stop_event.wait()
    server.stop(0)

if __name__ == '__main__':
    serve()