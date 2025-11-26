### Instalação das dependências ###
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install Pyro5

#### Habilitar virtual env no powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

##### Iniciar o nameserver
pyro5-ns

##### Iniciar o servidor
python server.py SERVER_IP

##### Iniciar clientes
python client.py SERVER_IP

Se não for passado argumentos para o server.py e pro client.py -> localhost é assumido como default