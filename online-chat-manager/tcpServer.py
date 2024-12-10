import socket
import struct
import json

HOST = "127.0.0.1"
PORT = 65432
HEADER_SIZE = 32

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind((HOST, PORT))
tcp_socket.listen()
client_socket, addr = tcp_socket.accept()
header = client_socket.recv(HEADER_SIZE)
room_name_size, operation, state, operation_payload_size = struct.unpack('!B B B 29s', header)
room_name = client_socket.recv(room_name_size)
room_name = room_name.decode()
operation_payload = client_socket.recv(
    int.from_bytes(operation_payload_size, 'big'))
operation_payload = json.loads(operation_payload)
print(room_name, operation, state, operation_payload)
if operation == 1:
    token = room_name + "123"
payload = {}
if token:
    payload['token'] = token
payload_data = json.dumps(payload).encode('utf-8')
header = struct.pack('!B B B 29s', 0, operation, state, len(payload_data).to_bytes(29, 'big'))
client_socket.send(header + payload_data)