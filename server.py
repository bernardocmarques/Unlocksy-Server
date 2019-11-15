from bluetooth import *
from RSA import *

# rsa = RSAClass()
#
# rsa.export_public_key_to_file("pubkey_server.pem")
# input("Enter to continue...")
# pubKeyClient = import_public_key_from_file("pubkey_client.pem")

name = "BluetoothChat"
uuid = "fa87c0d0-afac-11de-8a39-0800200c9a66"

server_socket = BluetoothSocket(RFCOMM)

port = PORT_ANY

server_socket.bind(("", port))
print("Listening for connections on port: ", port)
print("Server Running. Press Ctrl+Z to close.")
server_socket.listen(1)
port = server_socket.getsockname()[1]

advertise_service(server_socket, name, uuid)
try:
    client_socket, address = server_socket.accept()
except KeyboardInterrupt:
    exit()

# noinspection PyUnboundLocalVariable
print("Connected to", address)

closed = False
while not closed:
    try:
        # noinspection PyUnboundLocalVariable
        data = client_socket.recv(2048)
        print(">>>", data.decode())
        client_socket.send(input(">>>").encode())


        # print(">>>", rsa.remove_signature_and_decrypt(data, pubKeyClient))
    except KeyboardInterrupt:
        closed = True

print("Closing Server")
client_socket.close()
server_socket.close()
