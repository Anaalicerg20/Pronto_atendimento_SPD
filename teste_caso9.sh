echo "Ambulatório: 2 cadeiras, 1 médico, porto 9999"
python3 ambulatorio.py 2 1 9999 > amb.out 2>&1 &
PID_AMB=$!   # Salva o ID do processo do Ambulatório
sleep 1

echo "Médico (Servidor Consultório)"
python3 medico.py 9991 99.1 2 localhost 9999 > med1.out 2>&1 &
PID_MED=$!   # Salva o ID do processo do Médico
sleep 2

echo "Fim do expediente"
python3 fim_de_expediente.py localhost 9999 > fim.out 2>&1

echo "Aguardando o encerramento completo dos processos..."
wait $PID_MED
echo "Processo do Médico encerrado!"

wait $PID_AMB
echo "Processo do Ambulatório encerrado! Teste concluído."