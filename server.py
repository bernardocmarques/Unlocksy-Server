from bluetooth import *
from AES_M import *
import threading
import time

# rsa = RSAClass()
#
# rsa.export_public_key_to_file("pubkey_server.pem")
# input("Enter to continue...")
# pubKeyClient = import_public_key_from_file("pubkey_client.pem")

aes = AESClass()


def listen_socket():
    listening = True
    while listening:
        try:
            data = client_socket.recv(2048).decode()
            msg, iv = data.split(" ")
            cmd = aes.decrypt(msg, iv)
            execute_cmd(cmd)
        except BluetoothError:
            listening = False
        except KeyboardInterrupt:
            listening = False
    print("Stop listening\n")


def execute_cmd(cmd):
    print(cmd.lower())
    cmd_splited = cmd.split(" ")
    cmd = cmd_splited[0]
    args = cmd_splited[1:]

def create_server():
    server_socket = BluetoothSocket(RFCOMM)

    name = "BluetoothChat"
    uuid = "fa87c0d0-afac-11de-8a39-0800200c9a66"
    client_sock = address = None

    port = PORT_ANY

    server_socket.bind(("", port))
    print("Listening for connections on port: ", port)
    print("Server Running. Press Ctrl+Z to close.")
    server_socket.listen(1)

    advertise_service(server_socket, name, uuid)
    try:
        client_sock, address = server_socket.accept()
    except KeyboardInterrupt:
        exit()

    print("Connected to", address)
    key = client_sock.recv(2048).decode()
    aes.set_key_base64(key)
    print(key)
    return server_socket, client_sock, address


server_socket, client_socket, _ = create_server()
server_closed = False

while not server_closed:
    receiving_thread = threading.Thread(target=listen_socket)
    receiving_thread.start()
    try:
        client_socket.send(aes.encrypt(input()).encode())
    except BluetoothError:
        client_socket.close()
        server_socket.close()
        print("Connection Closed\n\n")
        server_socket, client_socket, _ = create_server()
    except KeyboardInterrupt:
        server_closed = True

print("Closing Server")
client_socket.close()
server_socket.close()
