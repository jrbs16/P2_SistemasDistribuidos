import Pyro5.api
import threading
import time

@Pyro5.api.expose
class ClientCallback:
    def receive_message(self, message, sender):
        if message.startswith("[PRIVADO]"):
            print(f"\n{message}")
        else:
            print(f"\n[{sender}] {message}")

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
    username = input("Digite seu nome de usuário: ").strip()

    daemon = Pyro5.api.Daemon()
    callback = ClientCallback()
    callback_uri = daemon.register(callback)

    # inicia o daemon em thread antes de registrar no servidor
    threading.Thread(target=daemon.requestLoop, daemon=True).start()
    time.sleep(0.1)  # pequeno delay garante que daemon esteja pronto

    server = Pyro5.api.Proxy("PYRONAME:chat.server")

    # envia somente o URI
    ok = server.register(username, callback_uri)
    if not ok:
        print("Nome já está em uso. Execute novamente.")
        return

    print("Conectado ao servidor.")

    listen_input(server, username)


if __name__ == "__main__":
    main()
