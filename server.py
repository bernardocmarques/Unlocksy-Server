from datetime import datetime

from bluetooth import *
from AES_Util import *
import threading
from BluetoothMessage import BluetoothMessage


class BT_Server:
    nonces = []

    # noinspection PyBroadException
    def validate_bluetooth_message(self, string):
        try:
            string_splited = string.split(",")
            msg = string_splited[0]
            nonce = string_splited[1]
            t1 = eval(string_splited[2]) / 1000
            t2 = eval(string_splited[3]) / 1000
            bluetooth_message = BluetoothMessage(msg, nonce, t1, t2)
        except Exception as e:
            print("Exception:", e)
            return None

        if bluetooth_message.nonce in self.nonces:
            print("Repeated Nonce")
            return None
        else:
            self.nonces.append(bluetooth_message.nonce)
            now = datetime.now()
            return bluetooth_message.message if bluetooth_message.t1 < now < bluetooth_message.t2 else None

    def __init__(self, rsa):
        self.aes = AES_Util()
        self.rsa = rsa
        self.client_socket = None
        self.isRunning = False
        self.device_address = ""
        self.device_name = ""

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

        print("Connected to", address)

        self.device_address = address[0]
        threading.Thread(target=self.find_device_name).start()

        key_enc = client_sock.recv(2048).decode()
        key = self.rsa.decrypt_msg(key_enc)

        if key:
            self.aes.set_key_base64(key)
        else:
            print("Could not get key")
            print("Closing connection & restarting...\n\n")
            client_sock.close()
            server_sock.close()
            self.device_name = ""
            self.device_address = ""
            return self.create_server()

        return server_sock, client_sock

    def find_device_name(self):
        while self.device_name == "" and self.device_address != "":
            print("Finding connection...")
            nearby_devices = discover_devices(duration=4, lookup_names=True, )
            print("%d devices found" % len(nearby_devices))
            for addr, name in nearby_devices:
                print("Found %s  (%s)" % (name, addr))
                if addr == self.device_address:
                    print("Connected to %s  (%s)\n" % (name, addr))
                    self.device_name = name
                    break

    def run_server(self):
        self.isRunning = True
        server_socket, self.client_socket = self.create_server()

        while self.isRunning:
            try:
                print("Waiting for commands...")
                data = self.client_socket.recv(2048).decode()
                msg, iv = data.split(" ")
                cmd = self.aes.decrypt(msg, iv)
                self.execute_cmd(cmd)
            except BluetoothError:
                print("Bluetooth connection lost")
                print("Closing connection & restarting...\n\n")
                self.client_socket.close()
                server_socket.close()

                self.device_address = ""
                self.device_name = ""

                server_socket, self.client_socket = self.create_server()
            except KeyboardInterrupt:
                self.isRunning = False

        print("Closing connection....")
        self.client_socket.close()
        server_socket.close()
        self.device_address = ""
        self.device_name = ""
        print("Connection closed.\n\n")

    def send_cmd(self, cmd):
        bluetooth_message = BluetoothMessage(cmd)
        self.client_socket.send(self.aes.encrypt(str(bluetooth_message)).encode())

    def execute_cmd(self, cmd):
        cmd = self.validate_bluetooth_message(cmd)

        if cmd is None:
            print("Invalid command")
            return

        cmd_splited = cmd.split(" ")
        cmd = cmd_splited[0]
        args = cmd_splited[1:]

        if cmd == 'SGK':
            print("SGK - Send Generated Keychain-Key\n")

        elif cmd == 'SK':
            print("SK - Send Keychain-Key\n")

        elif cmd == 'SCA':
            print("SCA - Send Challenge Answer\n")

        elif cmd == "ola":
            self.send_cmd("ola tudo bem")
            pass
        else:
            print("Unknown command")
            print(" ".join(cmd_splited))
