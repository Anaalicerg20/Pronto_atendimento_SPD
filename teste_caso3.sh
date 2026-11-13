echo "Ambulatório: 1 cadeira, 1 médico, porto 9999"
python3 ambulatorio.py 1 1 9999 > amb.out 2>&1 &
sleep 1

echo "Médico (Tempo de consulta: 5 segundos)"
python3 medico.py 9991 99.1 5 localhost 9999 > med1.out 2>&1 &
sleep 1

echo "Paciente 1 (Ocupa o médico)"
python3 paciente.py 1.1 dor_de_cabeca localhost 9999 > pac1.out 2>&1 &
sleep 1

echo "Paciente 2 (Ocupa a única cadeira da fila de espera)"
python3 paciente.py 2.1 febre localhost 9999 > pac2.out 2>&1 &
sleep 1

echo "Paciente 3 (Acha a sala cheia e vai embora)"
python3 paciente.py 3.1 tosse localhost 9999 > pac3.out 2>&1 &
sleep 5

echo "Fim do expediente"
python3 fim_de_expediente.py localhost 9999 > fim.out 2>&1