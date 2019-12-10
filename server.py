import time
import subprocess
from datetime import datetime
import random

from bluetooth import *
from AES_Util import *
import threading
from BluetoothMessage import BluetoothMessage

import files_client


class Lockdown(Exception):
    pass


class DeviceNotConnected(Exception):
    pass


class BT_Server:
    nonces = []

    # noinspection PyBroadException
    def validate_bluetooth_message(self, string):
        try:
            string_splited = string.split(",")
            msg = string_splited[0]
            nonce = string_splited[1]
            t1 = int(string_splited[2]) / 1000
            t2 = int(string_splited[3]) / 1000
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

        self.server_name = "BluetoothChat"
        self.server_uuid = "fa87c0d0-afac-11de-8a39-0800200c9a66"

        self.server_socket = self.client_socket = None
        self.isRunning = False
        self.isConnected = False

        self.device_address = ""
        self.device_name = ""

        self.device_address_to_share = None
        self.device_name_to_share = None
        self.share_device_key = None

        self.challenge_answer = None
        self.isLockdown = False
        self.isNear = None
        self.master_key = None

    def create_server(self):
        server_sock = BluetoothSocket(RFCOMM)

        client_sock = address = None

        port = PORT_ANY

        server_sock.bind(("", port))
        print("Listening for connections on port: ", port)
        print("Server Running. Press Ctrl+C to close.\n")
        server_sock.listen(1)

        advertise_service(server_sock, self.server_name, self.server_uuid)
        try:
            client_sock, address = server_sock.accept()
            stop_advertising(server_sock)
        except KeyboardInterrupt:
            exit()

        self.device_address = address[0]
        self.device_name = lookup_name(self.device_address)
        self.isNear = True  # we're assuming the device is near when reading the QR code
        print("Connected to %s  (%s)\n" % (self.device_name, self.device_address))

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
        threading.Thread(target=self.check_if_near).start()
        threading.Thread(target=self.challenge).start()
        return server_sock, client_sock

    def check_if_near(self):
        nr_far = 0
        nr_near = 0
        while self.isConnected:
            cmd_output = subprocess.check_output("hcitool rssi " + self.device_address, shell=True).decode()
            rssi_eval = int(cmd_output.split(' ')[3])
            # print("RSSI value is: " + str(rssi_eval))

            if rssi_eval == 0:
                nr_near += 1
                if nr_near == 3 and not self.isNear:
                    self.isNear = True
                    print("=======================")
                    print("DEVICE IS NEAR")
                    print("=======================")
                nr_far = 0

            elif rssi_eval == -1:
                nr_far += 1
                if nr_far == 3 and self.isNear:
                    self.isNear = False
                    print("=======================")
                    print("DEVICE IS FAR")
                    print("=======================")
                nr_near = 0

            else:
                print("Something went wrong when checking proximity of device.")

            time.sleep(1)

    def lockdown(self):
        print("-----------------------LOCKDOWN-----------------------")
        self.client_socket.shutdown(2)
        self.isLockdown = True

        files_client.lockdown()

    def request_challenge(self, challenge):
        self.send_cmd("RCA " + str(challenge))
        print("RCA " + str(challenge))

    def challenge(self):
        time.sleep(15)
        nr_try = 0
        while self.isConnected:
            self.challenge_answer = None
            challenge = random.randint(0, 10000000)
            self.request_challenge(challenge)
            time.sleep(15)
            if self.challenge_answer is None or not int(self.challenge_answer) == challenge + 1:
                nr_try += 1
                print("wrong challenge answer (" + str(nr_try) + ")")
                if nr_try == 3:
                    self.lockdown()
                    break
            else:
                nr_try = 0

    def disconnect(self):
        self.lockdown()

    def unlock_folders(self):
        self.request_master_key()
        files_client.unlock_with_device(self.device_address, self.master_key)

    def update_keys(self):
        old_master_key = self.master_key

        # ask for new key
        self.request_generate_new_master_key()

        files_client.update_keys(self.device_address, old_master_key, self.master_key)

    def remove_device(self):
        files_client.remove_device(self.device_address, self.master_key)

    def run_server(self):
        self.isRunning = True
        self.server_socket, self.client_socket = self.create_server()

        # start thread to unlock folders
        threading.Thread(target=self.unlock_folders).start()
        # threading.Thread(target=self.accept_second_device).start()

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
                self.master_key = None

                files_client.lockdown()

                self.server_socket, self.client_socket = self.create_server()
                threading.Thread(target=self.unlock_folders).start()
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

    def add_device(self):
        self.send_cmd("RGK")

    def request_master_key(self):
        '''
        FIXME check if the variable should not stay in memory
        '''
        self.master_key = None
        self.send_cmd("RGK")

        while not self.master_key:
            time.sleep(0.25)

    def request_generate_new_master_key(self):
        '''
        FIXME check if the variable should not stay in memory
        '''
        self.master_key = None
        self.send_cmd("RNK")

        while not self.master_key:
            time.sleep(0.25)

    def add_folder(self, path):
        if not self.isConnected or not self.device_address:
            raise DeviceNotConnected()

        if not self.master_key:
            self.request_master_key()

        if not path:  # if empty stop
            return

        files_client.register_new_directory(path, self.device_address, self.master_key)

    def list_folders(self):
        return files_client.list_directories()

    def remove_folder(self, path):
        if not self.isConnected or not self.device_address:
            raise DeviceNotConnected()

        files_client.remove_folder(path, self.device_address, self.master_key)

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
            self.master_key = base64.b64decode(args[0])
            print(f"key: {self.master_key}")
            self.send_ack(cmd)

        elif cmd == 'SNK':
            print("SNK - Send New Generated Keychain-Key\n")
            self.master_key = base64.b64decode(args[0])
            print(f"key: {self.master_key}")
            self.send_ack(cmd)

        elif cmd == 'SCA':
            print("SCA - Send Challenge Answer\n")
            self.challenge_answer = args[0]

        elif cmd == "ola":
            print(" ".join(cmd_splited))
        else:
            print("Unknown command")
            print(" ".join(cmd_splited))

    def stop_waiting_for_share_connection(self):
        self.is_waiting_for_share = False
        pass  # fixme change if no timeout

    def wait_for_share_device_info(self):
        while not (self.device_address_to_share and self.device_address_to_share and self.share_device_key):
            if not self.is_waiting_for_share:
                break
            time.sleep(0.5)
        return self.device_address_to_share, self.device_address_to_share, self.share_device_key

    def create_server_sharing(self):
        if not self.isRunning:
            return

        self.is_waiting_for_share = True
        try:
            print("Waiting device to share")  # fixme find way to timeout
            advertise_service(self.server_socket, self.server_name, self.server_uuid)  # fixme if not connecting probs the error is where
            client_sock_second, address = self.server_socket.accept()
            stop_advertising(self.server_socket)
        except Exception as e:
            print("entra")
            # return self.create_server_sharing()

        if self.is_waiting_for_share:  # fixme change if no timeout
            self.device_address_to_share = address[0]
            self.device_name_to_share = lookup_name(self.device_address_to_share)

            key_enc = client_sock_second.recv(2048).decode()
            self.share_device_key = self.rsa.decrypt_msg(key_enc)

            if self.share_device_key:
                print("got this key boy -> " + self.share_device_key.decode())
            else:
                print("Could not get share device key")
                client_sock_second.close()
                self.device_address_to_share = None
                self.device_name_to_share = None
                return self.create_server_sharing()

            client_sock_second.close()
        else:  # fixme change if no timeout
            print("Stopped waiting for share device key")
            self.device_address_to_share = None
            self.device_name_to_share = None


