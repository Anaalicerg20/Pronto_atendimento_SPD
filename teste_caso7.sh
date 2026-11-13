echo "Ambulatório: 2 cadeiras, 1 médico, porto 9999"
python3 ambulatorio.py 2 1 9999 > amb.out 2>&1 &
sleep 1

echo "Médico (Consulta demorada: 10 segundos)"
python3 medico.py 9991 99.1 10 localhost 9999 > med1.out 2>&1 &
sleep 1

echo "Paciente 1 (Ocupa o médico)"
python3 paciente.py 1.1 dor localhost 9999 > pac1.out 2>&1 &
sleep 1

echo "Paciente 2 (Fica preso na fila de espera)"
python3 paciente.py 2.1 febre localhost 9999 > pac2.out 2>&1 &
sleep 2

echo "Fim do expediente"
python3 fim_de_expediente.py localhost 9999 > fim.out 2>&1