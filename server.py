from bluetooth import *
from RSA import *

# rsa = RSAClass()
#
# rsa.export_public_key_to_file("pubkey_server.pem")
# input("Enter to continue...")
# pubKeyClient = import_public_key_from_file("pubkey_client.pem")
server_socket = BluetoothSocket(RFCOMM)

server_socket.bind(("", PORT_ANY))
print("Server Running. Press Ctrl+Z to close.")
server_socket.listen(1)
client_socket, address = server_socket.accept()


print("Connected to", address)

closed = False
while not closed:
    try:
        data = client_socket.recv(2048)
        print(">>>", data.decode())

        # print(">>>", rsa.remove_signature_and_decrypt(data, pubKeyClient))
    except KeyboardInterrupt:
        closed = True

print("saindo")
client_socket.close()
server_socket.close()