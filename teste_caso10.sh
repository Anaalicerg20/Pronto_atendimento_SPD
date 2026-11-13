echo "=== Verificando Ambiente do Laboratório ==="
python3 --version
python3 -c "import grpc; print('gRPC version:', grpc.__version__)"
echo "==========================================="

echo "Ambulatório: 1 cadeira, 1 médico, porto 9999"
python3 ambulatorio.py 1 1 9999 > amb.out 2>&1 &
sleep 1

echo "Médico"
python3 medico.py 9991 99.1 2 localhost 9999 > med1.out 2>&1 &
sleep 1

echo "Paciente"
python3 paciente.py 1.1 dor_de_cabeca localhost 9999 > pac1.out 2>&1 &
sleep 4

echo "Fim do expediente"
python3 fim_de_expediente.py localhost 9999 > fim.out 2>&1