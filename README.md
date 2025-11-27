### Instalação das dependências ###
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install Pyro5

#### Habilitar virtual env no powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

##### Iniciar o nameserver
pyro5-ns -n IP_SERVIDOR

##### Iniciar o servidor
python server.py 

##### Iniciar clientes
python client.py 

## Utilizando uma máquina como servidor. 
## Na máquina do servidor, alterar o chat.conf com:
host = IP_SERVIDOR
# Porta do daemon (opcional, padrão 0 = aleatória)
port = 0
# Host do NameServer
ns_host = IP_SERVIDOR
# Porta do NameServer
ns_port = 9090

## Na máquina que utilizará o client.
# Host do daemon (IP do servidor)
host = IP_SERVIDOR
# Porta do daemon (opcional, padrão 0 = aleatória)
port = 0
# Host do NameServer
ns_host = localhost
# Porta do NameServer
ns_port = 9090