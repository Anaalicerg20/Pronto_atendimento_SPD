## Arquivo .proto

Mesma sintaxe de C;
Contrato formal entre servidor e cliente;
Define as estruturas das mensagens;
Define os métodos remotos que o servidor disponibiliza para os clientes chamarem;
Não é um executável: dois arquivos em python serao gerados ao compilar os .
proto;

## gRPC

Permite que uma máquina chame uma função ou método em outro programa(sehja em outra máquina ou no memso computador) como se tivesse executando uma função local

Nota: gRPC empacota os parâmetros, abre a conexão de rede, aciona o método no servidor remoto e devolve a resposta direto para a variável resultado

## RPC

Dois sistemas conversando via web
Cliente: monta uma requisição HTTP(GET, POST) formato JSON e envia para uma URL
Servidor: recebe texto, faz parse do JSON, calcula e devolve outro JSON
