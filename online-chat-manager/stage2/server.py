import socket
import struct
import json
import threading
import time

HOST = "127.0.0.1"
TCP_PORT = 65432
UDP_PORT = 65430
HEADER_SIZE = 32
MAX_MSG_SIZE = 4096
CLIENT_TIMEOUT = 10

class Room:
    def __init__(self, name, password=""):
        self.name = name
        self.password = password
        self.users = {}
    def add_user(self, user):
        self.users[user.username] = user

class User:
    def __init__(self, username, token, host):
        self.username = username
        self.token = token
        self.host = host
#udp open
def handle_messages(sock,payload,new_room):
    clients = {}
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            username_len, = struct.unpack('>B', data[:1])
            username = data[1:username_len+1].decode()
            token_len = data[username_len+1:username_len+2]
            token = data[username_len+2:username_len+2+token_len]
            message = data[username_len+2+token_len:].decode()
            clients[addr] = (username, time.time())
            print(f"Message from {addr}: {username} = {message}, token{token}")

            disconnected_clients = []
            for client in list(clients):
                last_active_time = clients[client][1]
                if time.time() - last_active_time > CLIENT_TIMEOUT:
                    print(f"Client {client} timed out and is being removed.")
                    disconnected_clients.append(client)
                    continue
                try:
                    if client != addr:
                        sock.sendto(data, client)
                except Exception as e:
                    print(f"Failed to send to {client}: {e}")
                    disconnected_clients.append(client)

            for client in disconnected_clients:
                del clients[client]
        except Exception as e:
            print(f"Error: {e}")

def start_udp_server(payload,server):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Server started at {HOST}:{UDP_PORT}")
    threading.Thread(target=handle_messages, args=(sock,payload), daemon=True).start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nServer is shutting down...")
    finally:
        sock.close()

class Server:
    def __init__(self):
        self.tcp_socket = tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((HOST, TCP_PORT))
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((HOST, UDP_PORT))
        self.rooms = {}

server = Server()
server.tcp_socket.listen()
#receive room info
while True:
    client_socket, addr = server.tcp_socket.accept()
    header = client_socket.recv(HEADER_SIZE)
    room_name_size, operation, state, operation_payload_size = struct.unpack('!B B B 29s', header)
    room_name = client_socket.recv(room_name_size)
    room_name = room_name.decode()
    operation_payload = client_socket.recv(
        int.from_bytes(operation_payload_size, 'big'))
    operation_payload = json.loads(operation_payload)
    print(room_name, operation, state, operation_payload)

    # create token and user
    token = room_name + "123"
    if operation == 1:
        user = User(operation_payload["username"], token, True)
        room = Room(room_name,operation_payload["password"])
        room.add_user(user)
        server.rooms[room_name] = room
    elif operation == 2:
        user = User(operation_payload["username"], token, False)
        room = server.rooms[room_name]
        if operation_payload["password"] == room.password:
            room.add_user(user)
    payload ={
        'status': "status",
        'message':"message",
        'token':token,
    }
    # return token and port for udp
    payload_data = json.dumps(payload).encode('utf-8')
    header = struct.pack('!B B B 29s', 0, operation, state, len(payload_data).to_bytes(29, 'big'))
    client_socket.send(header + payload_data)
    threading.Thread(target=start_udp_server, args=(payload,server,), daemon=True).start()

