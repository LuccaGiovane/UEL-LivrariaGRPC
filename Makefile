# Makefile para iniciar o projeto

.PHONY: run

run:
	@echo "Iniciando os servidores..."
	python3 client/start_servers.py &
	@echo "Iniciando o cliente web..."
	python3 client/web_client.py
