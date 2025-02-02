import socket
import threading

import state
import strings

HOST = ''
PORT = 9975

tcp = None
conn = None
client = None

friend_username = ""

def server_loop():
    global conn
    global friend_username

    try:
        while True:
            # A abertura do servidor foi movida para a função init()

            # Muda o estado para esperando
            state.update("status", "waiting")

            # Espera pela conexão
            conn, _ = tcp.accept()

            # Muda o estado para conectado
            state.update("status", "connected")

            # Faz as apresentações
            
            # Pega o nome de usuário do cliente
            friend_username = conn.recv(1024).decode('utf-8').strip()

            # Verifica se os usernames são iguais
            # Se forem, corta a conexão
            if (friend_username == state.get_username()):
                conn.sendall(bytes(strings.same_usernames_not_allowed, 'utf-8'))
                state.add_message("command", strings.same_usernames_not_allowed)
                conn.sendall(bytes('bye', 'utf-8'))
                conn.close()
                conn = None
                state.update("status", "waiting")
                continue
            
            state.add_message("command", strings.connected_to % (str(friend_username)))

            # Envia seu nome pro cliente
            conn.sendall(bytes(state.get("username"), "utf-8"))

            messages_loop()

    except Exception as e:
        state.add_message("command", "[!] SVR: " + str(e))

def connect_to_server(host, port):
    global conn
    global friend_username

    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.connect((host, port))

    conn = tcp
        
    state.update("status", "connected")

    # Envia seu nome pro servidor
    conn.sendall(bytes(state.get("username"), "utf-8"))

    # Pega o nome de usuário do servidor
    friend_username = conn.recv(1024).decode('utf-8').strip()
    state.add_message("command", strings.connected_to % (str(friend_username)))

    messages_loop()

def messages_loop():
    global conn
    global friend_username

    while True:
        msg = conn.recv(1024)
        if msg.decode('utf-8').strip() == 'bye':
            conn.sendall(bytes('sul8r' , 'utf-8'))
            conn.close()
            conn = None
            state.add_message("command", strings.friend_disconnected % (friend_username))
            state.update("status", "offline")
            break
        if not msg:
            state.add_message("command", strings.friend_disconnected % (friend_username))
            state.update("status", "offline")
            break
        state.add_message(friend_username, msg)

def send_message(message):
    global conn

    if not conn:
        state.add_message("command", strings.please_connect_before_sending_messages)
        return

    # envia a mensagem para o contato
    conn.sendall(bytes(message, 'utf-8'))

    # Adiciona a mensagem à lista
    state.add_message(state.get_username(), message)
    
def init():
    global tcp

    # Abre o servidor
    try:
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp.bind((HOST, PORT))
        tcp.listen(1)

        y = threading.Thread(target = server_loop)
        y.name = "Communication-SERVER-THREAD"
        y.start()

        return HOST, PORT
    except Exception as e:
        state.add_message("command", "Error: " + str(e)[0:100]+'...')
        return -1, -1


def connect_to(host, port):
    y = threading.Thread(target = connect_to_server, args=(host, int(port) if port else 9975))
    y.name = "Communication-CLIENT-THREAD"
    y.start()

# Função para verificar se o usuário
# está apto a realizar uma conexão; isso é:
# Se ele já tem um usuário e já definiu uma chave
# para o HMAC
def is_able_to_connect(verbose = False):
    is_able = state.get_username() != '' and state.get("secret") != ''
    if not is_able and verbose:
        state.add_message("command", strings.please_set_user_and_secret)
    return is_able