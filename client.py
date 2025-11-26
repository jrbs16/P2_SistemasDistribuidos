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
                target, content = msg[1:].split(" ", 1)
                ok = server.private_message(username, target, content)
                if not ok:
                    print("[ERRO] Usuário não encontrado.")
            except:
                print("Use: @usuario mensagem")
            continue
        server.broadcast(msg, username)

def main():
    # lê configuração
    config = configparser.ConfigParser()
    config.read("chat.conf")
    server_host = config.get("pyro", "host", fallback="localhost")
    ns_host = config.get("pyro", "ns_host", fallback="localhost")
    ns_port = config.getint("pyro", "ns_port", fallback=9090)

    username = input("Digite seu nome de usuário: ").strip()

    # pega o IP local da máquina cliente para o callback
    local_ip = socket.gethostbyname(socket.gethostname())
    daemon = Pyro5.api.Daemon(host=local_ip)
    callback = ClientCallback()
    callback_uri = daemon.register(callback)

    threading.Thread(target=daemon.requestLoop, daemon=True).start()
    time.sleep(0.1)

    ns = Pyro5.api.locate_ns(host=ns_host, port=ns_port)
    server = Pyro5.api.Proxy(f"PYRONAME:chat.server@{server_host}")

    ok = server.register(username, callback_uri)
    if not ok:
        print("Nome já está em uso. Execute novamente.")
        return

    print("Conectado ao servidor.")
    listen_input(server, username)

if __name__ == "__main__":
    main()
