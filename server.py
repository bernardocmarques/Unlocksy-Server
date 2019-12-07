import time
from datetime import datetime
import random

from bluetooth import *
from AES_Util import *
import threading
from BluetoothMessage import BluetoothMessage


class Lockdown(Exception):
    pass


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
        self.server_socket = self.client_socket = None
        self.isRunning = False
        self.isConnected = False
        self.device_address = ""
        self.device_name = ""
        self.challenge_answer = None
        self.isLockdown = False  # fixme queremos isto?

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

        self.isConnected = True
        threading.Thread(target=self.challenge).start()
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

    def lockdown(self):
        print("-----------------------LOCKDOWN-----------------------")
        self.client_socket.shutdown(2)
        self.isLockdown = True

    def request_challenge(self, challenge):
        self.send_cmd("RCA " + str(challenge))
        print("REQUEST Challenge " + self.device_address)

    def challenge(self):
        time.sleep(15)
        nr_try = 0
        while self.isConnected:
            self.challenge_answer = None
            challenge = random.randint(0, 10000000)
            self.request_challenge(challenge)
            time.sleep(15)
            if self.challenge_answer is None or not eval(self.challenge_answer) == challenge + 1:
                nr_try += 1
                print("wrong challenge answer (" + str(nr_try) + ")")
                if nr_try == 3:
                    self.lockdown()
                    break
            else:
                nr_try = 0

    def run_server(self):
        self.isRunning = True
        self.server_socket, self.client_socket = self.create_server()

        while self.isRunning:
            try:
                print("Waiting for commands...")
                data = self.client_socket.recv(2048).decode()
                if self.isLockdown:
                    self.isLockdown = False
                    raise Lockdown
                msg, iv = data.split(" ")
                cmd = self.aes.decrypt(msg, iv)
                self.execute_cmd(cmd)
            except (BluetoothError, Lockdown):
                self.isConnected = False
                print("Bluetooth connection lost")
                print("Closing connection & restarting...\n\n")
                self.client_socket.close()
                self.server_socket.close()

                self.device_address = ""
                self.device_name = ""

                self.server_socket, self.client_socket = self.create_server()
            except KeyboardInterrupt:
                self.isConnected = False
                self.isRunning = False

        print("Closing connection....")
        self.client_socket.close()
        self.server_socket.close()
        self.device_address = ""
        self.device_name = ""
        print("Connection closed.\n\n")

    def send_cmd(self, cmd):
        bluetooth_message = BluetoothMessage(cmd)
        self.client_socket.send(self.aes.encrypt(str(bluetooth_message)).encode())

    def send_ack(self, cmd):
        self.send_cmd("ACK " + cmd)

    def execute_cmd(self, cmd):
        cmd = self.validate_bluetooth_message(cmd)
        print(cmd)

        if cmd is None:
            print("Invalid command")
            return

        cmd_splited = cmd.split(" ")
        cmd = cmd_splited[0]
        args = cmd_splited[1:]

        if cmd == 'SGK':
            print("SGK - Send Generated Keychain-Key\n")
            key = args[0]
            print("key: " + key)
            self.send_ack(cmd)

        elif cmd == 'SK':
            print("SK - Send Keychain-Key\n")
            key = args[0]
            print("key: " + key)
            self.send_ack(cmd)

        elif cmd == 'SCA':
            print("SCA - Send Challenge Answer\n")
            self.challenge_answer = args[0]

        elif cmd == "ola":
            self.send_cmd("ola tudo bem")
            pass
        else:
            print("Unknown command")
            print(" ".join(cmd_splited))
