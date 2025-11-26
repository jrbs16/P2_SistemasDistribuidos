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
python server.py

##### Iniciar clientes
python client.py 