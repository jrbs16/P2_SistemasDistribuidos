import Pyro5.api
import configparser

@Pyro5.api.expose #Diz que os métodos da classe podem ser acessados remotamente
class ChatServer:
    def __init__(self):
        self.clients = {}  # username -> callback URI

    def register(self, username, callback_uri):
        if username in self.clients: #Verifica se o username ja não está no dicionário
            return False
        self.clients[username] = callback_uri #Registra o cliente. Salva o URI indexando com o nome.
        self.broadcast(f"{username} entrou no chat.", "SERVIDOR") #Envia uma mensagem ao chat avisando que o cliente entro
        print(f"[SERVER] Cliente registrado: {username}") #Log para o servidor
        return True

    def unregister(self, username):
        if username in self.clients: #Busca o username na lista de cliente
            del self.clients[username] #Remove ele do dicionário
            self.broadcast(f"{username} saiu do chat.", "SERVIDOR") #Faz um broadcast avisando que o usuário saiu do chat
            print(f"[SERVER] Cliente removido: {username}") #Log para o servidor

    def broadcast(self, message, sender):
        desconectados = [] #Salva uma lista para armazenar os clientes que foram desconectados
        for user, callback_uri in self.clients.items(): #Para cada par, user-URI.
            try:
                callback = Pyro5.api.Proxy(callback_uri) #Cria um proxy para chamar o cliente
                # Pega o URI do cliente, e cria um objeto para "ligar" ao método do cliente.
                callback._pyroTimeout = 1  #Timeout de 1 seg para evitar problemas
                callback.receive_message(message, sender) #Envia a mensagem para a função no servidor
            except:
                desconectados.append(user) #Se falhar, marca o cliente como desconectado
        for user in desconectados:
            del self.clients[user] #Limpa a lista dos desconectados

    def private_message(self, sender, target, message):
        if target not in self.clients: #Procura o target no dicionário. Se não encontrar retorna false.
            return False
        try:
            callback = Pyro5.api.Proxy(self.clients[target]) #Cria um proy com o uri do cliente. Cria um objeto para chamar
            #métodos remotos;
            callback._pyroTimeout = 1
            callback.receive_message(f"[PRIVADO de {sender}] {message}", sender) #Chama o receive message, com um marcador de quem mandou.
            return True #Indica que mandou corretamente
        except:
            return False #Caso de algum problema com a rede, retorna false.

def main():
    # Lê o arquivo de configuração 
    config = configparser.ConfigParser()
    config.read("chat.conf")
    host = config.get("pyro", "host", fallback="localhost")
    port = config.getint("pyro", "port", fallback=0)
    ns_host = config.get("pyro", "ns_host", fallback="localhost")
    ns_port = config.getint("pyro", "ns_port", fallback=9090)

    daemon = Pyro5.api.Daemon(host=host, port=port) #Cria o servidor Pyro
    ns = Pyro5.api.locate_ns(host=ns_host, port=ns_port) #Conecta ao NameServer

    uri = daemon.register(ChatServer()) #Aqui é registra uma instância do ChatServer no daemon Pyro. É devolvido um
    #URI
    ns.register("chat.server", uri) #Registra o servidor no nameserver

    print(f"[SERVER] Registrado no NameServer como 'chat.server' em {host}")
    print("[SERVER] Servidor iniciado.")

    daemon.requestLoop() #Faz o servidor entrar em loop infinito, escutando chamadas remotas dos clientes.

if __name__ == "__main__":
    main()
