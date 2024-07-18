import subprocess
import webbrowser
import time

# Iniciar o servidor
subprocess.Popen(["python", "client/start_servers.py"])

# Esperar alguns segundos para garantir que o servidor esteja iniciado
time.sleep(2)

# Iniciar o cliente web
subprocess.Popen(["python", "client/web_client.py"])

# Esperar mais alguns segundos para garantir que o cliente web esteja iniciado
time.sleep(2)

# Abrir a aplicação web no navegador
webbrowser.open("http://127.0.0.1:5000")
