echo "Ambulatório: 0 cadeiras, 1 médico, porto 9999"
python3 ambulatorio.py 0 1 9999 > amb.out 2>&1 &
sleep 1

echo "Médico"
python3 medico.py 9991 99.1 2 localhost 9999 > med1.out 2>&1 &
sleep 1

echo "Paciente (Deve ser atendido imediatamente)"
python3 paciente.py 1.1 dor_de_costas localhost 9999 > pac1.out 2>&1 &
sleep 4

echo "Fim do expediente"
python3 fim_de_expediente.py localhost 9999 > fim.out 2>&1