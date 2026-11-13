echo "Ambulatório: 2 cadeiras, 1 médico, porto 9999"
python3 ambulatorio.py 2 1 9999 > amb.out 2>&1 &
sleep 1

echo "Médico 1 (Registro aceito)"
python3 medico.py 9991 99.1 2 localhost 9999 > med1.out 2>&1 &
sleep 1

echo "Médico 2 (Excede o limite, registro deve retornar -1)"
python3 medico.py 9992 99.2 2 localhost 9999 > med2.out 2>&1 &
sleep 2

echo "Fim do expediente"
python3 fim_de_expediente.py localhost 9999 > fim.out 2>&1