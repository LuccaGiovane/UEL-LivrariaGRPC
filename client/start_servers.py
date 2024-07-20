import subprocess
import os

def start_server(script_name):
    """Inicia um servidor executando um script Python especificado."""

    return subprocess.Popen(['python', script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if __name__ == "__main__":
    # Caminhos para os scripts dos servidores
    servers = ['auth_server.py', 'catalog_server.py', 'orders_server.py']

    # Iniciar cada servidor
    processes = []
    for server in servers:
        script_path = os.path.join(os.path.dirname(__file__), server)
        process = start_server(script_path)
        processes.append(process)
        print(f"{server} iniciado com PID {process.pid}")

    # Manter o script principal rodando enquanto os servidores estão ativos
    try:
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        print("Interrompido pelo usuário. Finalizando servidores...")
        for process in processes:
            process.terminate()
            process.wait()
        print("Servidores finalizados.")
