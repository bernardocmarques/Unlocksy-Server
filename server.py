from bluetooth import *
from AES_Util import *
import threading

# aes = AES_Util()


# def listen_socket():
#     listening = True
#     while listening:
#         try:
#             data = client_socket.recv(2048).decode()
#             msg, iv = data.split(" ")
#             cmd = aes.decrypt(msg, iv)
#             execute_cmd(cmd)
#         except BluetoothError:
#             listening = False
#         except KeyboardInterrupt:
#             listening = False
#     print("Stop listening\n")


# def execute_cmd(cmd):
#     print(cmd.lower())
#     cmd_splited = cmd.split(" ")
#     cmd = cmd_splited[0]
#     args = cmd_splited[1:]


# def create_server():
#     server_sock = BluetoothSocket(RFCOMM)
#
#     name = "BluetoothChat"
#     uuid = "fa87c0d0-afac-11de-8a39-0800200c9a66"
#     client_sock = address = None
#
#     port = PORT_ANY
#
#     server_sock.bind(("", port))
#     print("Listening for connections on port: ", port)
#     print("Server Running. Press Ctrl+Z to close.")
#     server_sock.listen(1)
#
#     advertise_service(server_sock, name, uuid)
#     try:
#         client_sock, address = server_sock.accept()
#     except KeyboardInterrupt:
#         exit()
#
#     print("Connected to", address)
#     key = client_sock.recv(2048).decode()
#     aes.set_key_base64(rsa.decrypt_msg(key))
#     return server_sock, client_sock, address


# def run_server(rsa):
#     server_socket, client_socket, _ = create_server()
#     server_closed = False
#
#     while not server_closed:
#         receiving_thread = threading.Thread(target=listen_socket)
#         receiving_thread.start()
#         try:
#             client_socket.send(aes.encrypt(input()).encode())
#         except BluetoothError:
#             client_socket.close()
#             server_socket.close()
#             print("Connection Closed\n\n")
#             server_socket, client_socket, _ = create_server()
#         except KeyboardInterrupt:
#             server_closed = True
#
#     print("Closing Server")
#     client_socket.close()
#     server_socket.close()


class BT_Server:

    def __init__(self, rsa):
        self.aes = AES_Util()
        self.rsa = rsa
        self.server_socket = self.client_socket = None

    def create_server(self):
        server_sock = BluetoothSocket(RFCOMM)

        name = "BluetoothChat"
        uuid = "fa87c0d0-afac-11de-8a39-0800200c9a66"
        client_sock = address = None

        port = PORT_ANY

        server_sock.bind(("", port))
        print("Listening for connections on port: ", port)
        print("Server Running. Press Ctrl+Z to close.")
        server_sock.listen(1)

        advertise_service(server_sock, name, uuid)
        try:
            client_sock, address = server_sock.accept()
        except KeyboardInterrupt:
            exit()

        print("Connected to", address)
        key = client_sock.recv(2048).decode()
        self.aes.set_key_base64(self.rsa.decrypt_msg(key))
        return server_sock, client_sock, address

    def run_server(self):
        server_socket, client_socket, _ = self.create_server()
        server_closed = False

        while not server_closed:
            try:
                data = client_socket.recv(2048).decode()
                msg, iv = data.split(" ")
                cmd = self.aes.decrypt(msg, iv)
                print(cmd)
                # execute_cmd(cmd)
            except BluetoothError:
                client_socket.close()
                server_socket.close()
                print("Connection Closed\n\n")
                server_socket, client_socket, _ = self.create_server()
            except KeyboardInterrupt:
                server_closed = True

        print("Closing Server")
        client_socket.close()
        server_socket.close()
