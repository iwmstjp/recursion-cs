import socket
import threading
import struct
import time

HOST = "127.0.0.1" 
PORT = 65432
MAX_MSG_SIZE = 4096
CLIENT_TIMEOUT = 10
clients = {}

def handle_messages(sock):
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            username_len, = struct.unpack('>B', data[:1])
            username = data[1:username_len+1].decode()
            message = data[username_len+1:].decode()
            clients[addr] = (username, time.time())
            print(f"Message from {addr}: {username} = {message}")

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

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"Server started at {HOST}:{PORT}")
    threading.Thread(target=handle_messages, args=(sock,), daemon=True).start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nServer is shutting down...")
    finally:
        sock.close()

if __name__ == "__main__":
    start_server()
