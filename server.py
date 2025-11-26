import Pyro5.api

@Pyro5.api.expose
class ChatServer:
    def __init__(self):
        self.clients = {}  # username -> callback_uri

    def register(self, username, callback_uri):
        if username in self.clients:
            return False
        self.clients[username] = callback_uri
        self.broadcast(f"{username} entrou no chat.", "SERVIDOR")
        print(f"[SERVER] Cliente registrado: {username}")
        return True

    def unregister(self, username):
        if username in self.clients:
            del self.clients[username]
            self.broadcast(f"{username} saiu do chat.", "SERVIDOR")
            print(f"[SERVER] Cliente removido: {username}")

    def broadcast(self, message, sender):
        desconectados = []
        for user, callback_uri in self.clients.items():
            try:
                callback = Pyro5.api.Proxy(callback_uri)
                callback._pyroTimeout = 1  # evita travar
                callback.receive_message(message, sender)
            except:
                desconectados.append(user)
        for user in desconectados:
            del self.clients[user]

    def private_message(self, sender, target, message):
        if target not in self.clients:
            return False
        try:
            callback = Pyro5.api.Proxy(self.clients[target])
            callback._pyroTimeout = 1
            # envia a mensagem com marcador [PRIVADO de sender]
            callback.receive_message(f"[PRIVADO de {sender}] {message}", sender)
            return True
        except:
            return False

def main():
    daemon = Pyro5.api.Daemon()
    ns = Pyro5.api.locate_ns()
    uri = daemon.register(ChatServer())
    ns.register("chat.server", uri)

    print("[SERVER] Registrado no NameServer como 'chat.server'")
    print("[SERVER] Servidor iniciado.")

    daemon.requestLoop()


if __name__ == "__main__":
    main()
