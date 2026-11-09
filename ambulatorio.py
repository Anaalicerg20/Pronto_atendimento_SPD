from concurrent import futures
import grpc
import ambulatorio_pb2
import ambulatorio_pb2_grpc
from collections import deque

import sys
import os
import socket

from mytimer import tstamp_msg, my_sleep
from threading import Thread, Lock, Condition, Semaphore

def split_peer(addr_str: str):
    if addr_str.startswith(("ipv4:", "ipv6:")):
        addr_str = addr_str.split(":", 1)[1]

    address, separator, port = addr_str.rpartition(":")
    if address.startswith("[") and address.endswith("]"):
        address = address[1:-1]

    return address, int(port)
class AmbulatorioServicer(ambulatorio_pb2_grpc.AmbulatorioServicer):
    
    def __init__(self, num_medicos, num_cadeiras):

        self.fila_medicos = deque(maxlen=num_medicos) #fila médicos livres: guarda prontuários iniciados pelos médicos
        self.fila_espera = deque(maxlen=num_cadeiras) #fila pacientes em espera: guarda prontuários iniciados pelos pacientes

        self.diretorio_medicos = {} #associa o médico à porta do seu consultório

        self.chamadas_ativas = 0 #controle RPC 

        self.lock = Lock() #mutex
        self.cond_chamadas_ativas = Condition(self.lock) #variável de condição

    def ProcuraMedico(self, request, context, ):

        with self.lock:
            self.chamadas_ativas += 1

            id_paciente = request.id_paciente 
            tstamp_msg ("APMI(%4.1f)" % (id_paciente))

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
        
            else:
                #medicos ocupados: cria o prontuario com id do paciente
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
            
    def RegistraMedico(self, request, context):

        with self.lock:
            self.chamadas_ativas += 1

            id_medico = request.id_medico
            consultorio = request.porto
            ip_medico , _ = split_peer(context.peer())

            if len(self.fila_medicos) == 0:
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
        id_med = request.id_medico
        
        # ... (Sua lógica para tirar um paciente da fila de cadeiras) ...
        
        return ambulatorio_pb2.RespostaChamaPaciente(id_paciente=123.4)

    def Termino(self, request, context):
        # ... (Sua lógica para limpar as filas e calcular os liberados) ...
        
        return ambulatorio_pb2.RespostaTermino(liberados=-3)


def serve():
    num_cadeiras = int(sys.argv[1]) 
    num_medicos = int(sys.argv[2]) 
    porta = int(sys.argv[3])

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    ambulatorio_pb2_grpc.add_AmbulatorioServicer_to_server(AmbulatorioServicer(num_medicos, num_cadeiras), server )
    
    server.add_insecure_port(f'[::]:{porta}')
    server.start()
    tstamp_msg("AI(%d,%d)@%d" % (num_cadeiras, num_medicos, porta))
    server.wait_for_termination()

if __name__ == '__main__':
    serve()