import socket
import struct
import json
HOST = "127.0.0.1"
TCP_PORT = 65432
UDP_PORT = 65420
HEADER_SIZE = 32

def create_message(username, message,token):
    username_len = len(username).to_bytes(1, byteorder='big')
    token_len = len(token).to_bytes(1, byteorder='big')
    message = json.dumps(message).encode('utf-8')
    data = username_len + username.encode() + token_len + token.encode()+ message
    return data


tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.connect((HOST, TCP_PORT))
username = input("user name:")
operation = int(input("Create a room: 1\nJoin the room: 2\n"))
room_name = input("Room name:")
password = input("Enter password:")
room_name_size = len(room_name)
payload = {
    "username": username,
    "ip": HOST,
    "port": UDP_PORT,
    "password": password
}
payload_data = json.dumps(payload).encode('utf-8')
header = struct.pack("!B B B 29s", room_name_size, operation, 0, len(payload_data).to_bytes(29, 'big'))
tcp_socket.send(header + room_name.encode('utf-8') + payload_data)
header = tcp_socket.recv(HEADER_SIZE)
room_name_size, operation, state, operation_payload_size = struct.unpack('!B B B 29s', header)
room_name = tcp_socket.recv(room_name_size)
room_name = room_name.decode()
operation_payload = tcp_socket.recv(
    int.from_bytes(operation_payload_size, 'big'))
operation_payload = json.loads(operation_payload)
print(room_name, operation, state, operation_payload)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
        while True:
            message={}
            message['message'] = input("You: ")
            message['room_name'] = room_name
            message = create_message(username, message, operation_payload["token"])
            if message.lower() == "exit":
                sock.sendto(message, (HOST, UDP_PORT))
                break
            sock.sendto(message, (HOST, UDP_PORT))
finally:
    sock.close()