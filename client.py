import Pyro5.api
import threading
import configparser
import time
import socket

@Pyro5.api.expose
class ClientCallback:
    def receive_message(self, message, sender):
        print(f"\n{message}" if message.startswith("[PRIVADO]") else f"\n[{sender}] {message}")

def listen_input(server, username):
    while True:
        msg = input()
        if msg.lower() == "/sair":
            server.unregister(username)
            print("Você saiu do chat.")
            break
        if msg.startswith("@"):
            try:
                target, content = msg[1:].split(" ", 1) #Pega a string a partir do indice 1, o @ é o indice 0,
                #depois separa pelo primeiro espaço encontrado, e no máximo 1 divisão é feita.
                ok = server.private_message(username, target, content) #Invoca a função remota de enviar uma mensagem privada
                if not ok:
                    print("[ERRO] Usuário não encontrado.")
            except:
                print("Use: @usuario mensagem")
            continue
        server.broadcast(msg, username) #Se não tiver @, envia para todos no broadcast.

def main():
    # Lendo a configuração do arquivo chat.conf
    config = configparser.ConfigParser()
    config.read("chat.conf")
    server_host = config.get("pyro", "host", fallback="localhost") #Endereço do servidor Pyro
    ns_host = config.get("pyro", "ns_host", fallback="localhost") #Endereço do nameserver
    ns_port = config.getint("pyro", "ns_port", fallback=9090) #Porta do nameserver

    username = input("Digite seu nome de usuário: ").strip()

    # pega o IP local da máquina cliente para o callback
    local_ip = socket.gethostbyname(socket.gethostname()) #Retorna o IP do cliente
    daemon = Pyro5.api.Daemon(host=local_ip) #Cria um daemon Pyro. Um servidor RPC local.
    callback = ClientCallback() #Instanciando a classe do callback. É o objeto local que receberá mensagens
    callback_uri = daemon.register(callback) #Registra o objeto callback no daemon Pyro e retorna o URI (identificador).

    threading.Thread(target=daemon.requestLoop, daemon=True).start() #Thread onde o pyro fica escutando as requests do servidor.
    #É nessa thread que o servidor chama a receive_message, utilizando o objeto callback como referência.
    time.sleep(0.1)

    ns = Pyro5.api.locate_ns(host=ns_host, port=ns_port) #Localiza o nameserver.
    server = Pyro5.api.Proxy(f"PYRONAME:chat.server@{server_host}") #Obtém o objeto remoto do servidor via nameserver

    ok = server.register(username, callback_uri) #Registra o cliente no servidor
    if not ok: #Se o nome ja estiver registrado
        print("Nome já está em uso. Execute novamente.")
        return

    print("Conectado ao servidor.")
    listen_input(server, username)

if __name__ == "__main__":
    main()
