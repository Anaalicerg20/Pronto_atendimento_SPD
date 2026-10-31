all: stubs

stubs:
	python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ambulatorio.proto
	python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. consultorio.proto

clean:
	rm -f *_pb2.py *_pb2_grpc.py
	rm -rf __pycache__