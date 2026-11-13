echo "Ambulatório: 2 cadeiras, 2 médicos, porto 9999"
python3 ambulatorio.py 2 2 9999 > amb.out 2>&1 &
sleep 1

echo "Médico 1"
python3 medico.py 9991 99.1 2 localhost 9999 > med1.out 2>&1 &
sleep 1

echo "Médico 2"
python3 medico.py 9992 99.2 3 localhost 9999 > med2.out 2>&1 &
sleep 2

echo "Fim do expediente"
python3 fim_de_expediente.py localhost 9999 > fim.out 2>&1