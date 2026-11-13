echo "Ambulatório: 5 cadeiras, 2 médicos, porto 9999"
python3 ambulatorio.py 5 2 9999 > amb.out 2>&1 &
sleep 1

echo "Médico 1 (Rápido: 3 segundos)"
python3 medico.py 9991 99.1 3 localhost 9999 > med1.out 2>&1 &
sleep 1

echo "Médico 2 (Lento: 4 segundos)"
python3 medico.py 9992 99.2 4 localhost 9999 > med2.out 2>&1 &
sleep 1

echo "Paciente 1 (Deverá ser pareado com Médico 1)"
python3 paciente.py 1.1 dor localhost 9999 > pac1.out 2>&1 &
sleep 1

echo "Paciente 2 (Deverá ser pareado com Médico 2)"
python3 paciente.py 2.1 febre localhost 9999 > pac2.out 2>&1 &
sleep 1

echo "Paciente 3 (Fila de espera - Aguardará Médico 1)"
python3 paciente.py 3.1 tosse localhost 9999 > pac3.out 2>&1 &
sleep 1

echo "Paciente 4 (Fila de espera - Aguardará Médico 2)"
python3 paciente.py 4.1 asma localhost 9999 > pac4.out 2>&1 &

# Aguarda tempo suficiente para as duas consultas da fila terminarem
sleep 10

echo "Fim do expediente"
python3 fim_de_expediente.py localhost 9999 > fim.out 2>&1