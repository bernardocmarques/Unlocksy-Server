from bluetooth import *
from AES_Util import *


class BT_Server:

    def __init__(self, rsa):
        self.aes = AES_Util()
        self.rsa = rsa
        self.server_socket = self.client_socket = None
        self.isRunning = False
        self.deviceName = ''

    def create_server(self):
        server_sock = BluetoothSocket(RFCOMM)

        name = "BluetoothChat"
        uuid = "fa87c0d0-afac-11de-8a39-0800200c9a66"
        client_sock = address = None

        port = PORT_ANY

        server_sock.bind(("", port))
        print("Listening for connections on port: ", port)
        print("Server Running. Press Ctrl+C to close.\n")
        server_sock.listen(1)

        advertise_service(server_sock, name, uuid)
        try:
            client_sock, address = server_sock.accept()
        except KeyboardInterrupt:
            exit()


        print("Finding connection...")
        nearby_devices = discover_devices(lookup_names=True)
        print("%d devices found" % len(nearby_devices))

        for addr, name in nearby_devices:
            print("Found %s  (%s)" % (name, addr))
            if addr == address[0]:
                print("Connected to %s  (%s)\n" % (name, addr))
                self.deviceName = name
                break

        if self.deviceName == '':
            print("Connection not found.\nRestarting...\n")
            client_sock.close()
            server_sock.close()
            return self.create_server()

        key_enc = client_sock.recv(2048).decode()
        key = self.rsa.decrypt_msg(key_enc)

        if key:
            self.aes.set_key_base64(key)
        else:
            print("Could not get key")
            print("Closing connection....")
            client_sock.close()
            server_sock.close()
            print("Connection closed.\n\n")
            return self.create_server()

        self.server_socket = server_sock
        self.client_socket = client_sock

    def run_server(self):
        self.isRunning = True
        server_socket = self.server_socket
        client_socket = self.client_socket

        while self.isRunning:
            try:
                print("Waiting for commands...")
                data = client_socket.recv(2048).decode()
                msg, iv = data.split(" ")
                cmd = self.aes.decrypt(msg, iv)
                self.execute_cmd(cmd)
            except BluetoothError:
                client_socket.close()
                print("Closing connection....")
                server_socket.close()
                print("Connection closed.\n\n")
                self.create_server()
            except KeyboardInterrupt:
                self.isRunning = False

        print("Closing connection....")
        client_socket.close()
        server_socket.close()
        print("Connection closed.\n\n")

    def execute_cmd(self, cmd):
        cmd_splited = cmd.split(" ")
        cmd = cmd_splited[0]
        args = cmd_splited[1:]

        if cmd == 'SGK':
            print("SGK - Send Generated Keychain-Key\n")
            key = args[0]

        elif cmd == 'SK':
            print("SK - Send Keychain-Key\n")

        elif cmd == 'SCA':
            print("SCA - Send Challenge Answer\n")

        else:
            print("Unknown command\n")