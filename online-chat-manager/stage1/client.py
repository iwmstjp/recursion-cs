import socket
import threading
import struct

HEADER_SIZE = 32
MAX_ROOM_NAME_SIZE = 28
MAX_PAYLOAD_SIZE = 229

# Define operations
OPERATION_CREATE = 1
OPERATION_JOIN = 2
OPERATION_MESSAGE = 3

STATE_OK = 0
STATE_ERROR = 1

HOST = "127.0.0.1"
PORT = 65420
def receive_messages(sock):
    while True:
        try:
            data, _ = sock.recvfrom(4096)
            username_len, = struct.unpack('>B', data[:1])
            username = data[1:username_len+1].decode()
            message = data[username_len+1:].decode()
            print(f"{username}:{message}")
        except Exception as e:
            print(f"Error: {e}")
            break

def create_packet(room_name, operation, state, payload):
    if len(room_name) > MAX_ROOM_NAME_SIZE:
        raise ValueError("Room name exceeds maximum size")
    if len(payload) > MAX_PAYLOAD_SIZE:
        raise ValueError("Payload exceeds maximum size")

    room_name_size = len(room_name)
    operation_payload_size = len(payload)
    header = struct.pack(
        "!BBB29s", room_name_size, operation, state, bytes(payload[:29], 'utf-8')
    )
    body = room_name.encode('utf-8') + payload[:229].encode('utf-8')

    return header + body


def create_message(username, message):
    username_len = len(username).to_bytes(1, byteorder='big')
    data = username_len + username.encode() + message.encode()
    return data

def start_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    username = input("Enter your username: ")
    sock.sendto(create_message(username, f"{username} joined the chat"), (HOST, PORT))
    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    try:
        while True:
            message = input("You: ")
            message = create_message(username, message)
            if message.lower() == "exit":
                sock.sendto(message, (HOST, PORT))
                break
            sock.sendto(message, (HOST, PORT))
    finally:
        sock.close()

if __name__ == "__main__":
    start_client()
