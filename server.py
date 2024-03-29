import time
import subprocess
from datetime import datetime
import random
import easygui

from bluetooth import *
from AES_Util import *
import threading
from BluetoothMessage import BluetoothMessage

import files_client
import keystore


# ##############################################################
# ######################## Exceptions ##########################
# ##############################################################

class Lockdown(Exception):
    pass


class StopWaitingForShare(Exception):
    pass


class DeviceNotConnected(Exception):
    pass


# ##############################################################
# ####################### Server Class #########################
# ##############################################################

class BT_Server:

    def __init__(self, rsa):
        self.aes = AES_Util()
        self.rsa = rsa
        self.nonces = []

        self.server_name = "Unlocksy"
        self.server_uuid = "fa87c0d0-afac-11de-8a39-0800200c9a66"

        self.server_socket = self.client_socket = None
        self.isRunning = False
        self.isConnected = False
        self.isProximityActivated = False

        self.device_address = None
        self.device_name = None

        self.device_address_to_share = None
        self.device_name_to_share = None
        self.share_device_key = None

        self.challenge_answer = None
        self.isLockdown = False
        self.isNear = None
        self.master_key = None

    # ##############################################################
    # #################### Server Main Functions ###################
    # ##############################################################

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
            self.device_name = None
            self.device_address = None
            return self.create_server()

        self.isConnected = True
        threading.Thread(target=self.check_if_near).start()
        threading.Thread(target=self.challenge).start()
        return server_sock, client_sock

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

                self.device_address = None
                self.device_name = None
                self.master_key = None

                files_client.lockdown()

                self.server_socket, self.client_socket = self.create_server()
                # threading.Thread(target=self.unlock_folders).start()
            except KeyboardInterrupt:
                self.isConnected = False
                self.isRunning = False

        print("Closing connection....")
        self.client_socket.close()
        self.server_socket.close()
        self.device_address = None
        self.device_name = None
        print("Connection closed.\n\n")

    # ##############################################################
    # ############### Server Communication Functions ###############
    # ##############################################################

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

        else:
            print("Unknown command")
            print(" ".join(cmd_splited))

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

    def send_cmd(self, cmd):
        bluetooth_message = BluetoothMessage(cmd)
        self.client_socket.send(self.aes.encrypt(str(bluetooth_message)).encode())

    def send_ack(self, cmd):
        self.send_cmd("ACK " + cmd)

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

    def request_challenge(self, challenge):
        self.send_cmd("RCA " + str(challenge))
        print("RCA " + str(challenge))

    def request_master_key(self):
        self.master_key = None
        self.send_cmd("RGK")

        while not self.master_key:
            time.sleep(0.25)

    def request_generate_new_master_key(self):
        self.master_key = None
        self.send_cmd("RNK")

        while not self.master_key:
            time.sleep(0.25)

    # ##############################################################
    # ################## Server Control Functions ##################
    # ##############################################################

    def disconnect(self):
        self.lockdown()

    def lockdown(self):
        print("-----------------------LOCKDOWN-----------------------")
        self.client_socket.shutdown(2)
        self.isLockdown = True

        files_client.lockdown()

    def near_lockdown_countdown(self):
        sec = 15

        while True:
            s = "" if sec == 1 else "s"
            if not self.isNear and sec > 0:
                print(f"{sec} second{s} to lockdown!")
                time.sleep(1)
                sec -= 1
            elif not self.isNear:
                self.lockdown()
                break
            else:
                print("Lockdown canceled!")
                break

    def check_if_near(self):
        nr_far = nr_near = 0

        while self.isConnected:
            if self.isProximityActivated:
                cmd_output = subprocess.check_output("hcitool rssi " + self.device_address, shell=True).decode()
                rssi_eval = int(cmd_output.split(' ')[3])

                if rssi_eval == 0:
                    nr_near += 1
                    if nr_near == 10 and not self.isNear:
                        self.isNear = True
                        print("==========================")
                        print("     DEVICE IS NEAR")
                        print("==========================")
                    nr_far = 0

                elif rssi_eval == -1:
                    nr_far += 1
                    if nr_far == 10 and self.isNear:
                        self.isNear = False
                        print("==========================")
                        print("      DEVICE IS FAR")
                        print("==========================")
                        threading.Thread(target=self.near_lockdown_countdown).start()
                    nr_near = 0

                else:
                    print("Something went wrong when checking proximity of device.")

                time.sleep(0.25)

            else:
                # retry every 2s
                time.sleep(2)
                self.check_if_near()

    def add_folder(self, path):
        if not self.isConnected or not self.device_address:
            raise DeviceNotConnected()

        if not self.master_key:
            self.request_master_key()

        if not path:  # if empty stop
            return

        files_client.register_new_directory(path, self.device_address, self.master_key)

    def remove_folder(self, path):
        if not self.isConnected or not self.device_address:
            raise DeviceNotConnected()

        if not self.master_key:
            self.request_master_key()

        return files_client.remove_folder(path, self.device_address, self.master_key)

    def unlock_folders(self):
        print('UNLOCK ALL FOLDERS')
        if not self.master_key:
            self.request_master_key()
        files_client.unlock_with_device(self.device_address, self.master_key)

    def toggle_encryption(self, path, is_encrypted):
        print("encrypted" if is_encrypted else "decrypted")
        if is_encrypted:
            print("trying to decrypt")
            if not self.master_key:
                self.request_master_key()
            files_client.decrypt_directory(path, self.device_address, self.master_key)
        else:
            print("trying to encrypt")
            files_client._try_umount_directory(path)

    def list_folders(self):
        if not self.master_key:
            self.request_master_key()
        return files_client.list_directories_device(self.device_address, self.master_key)

    def share_folder(self, path):
        if not self.master_key:
            self.request_master_key()
        if self.device_address_to_share is None or self.share_device_key is None:
            print("Error: Can't get information to share folder")
            return
        print(path, self.device_address, self.master_key, self.device_address_to_share, self.share_device_key,
              sep="\n->")
        keystore.share_keys(path, self.device_address, self.master_key, self.device_address_to_share,
                            self.share_device_key)

    def update_keys(self):
        old_master_key = self.master_key

        # ask for new key
        self.request_generate_new_master_key()

        files_client.update_keys(self.device_address, old_master_key, self.master_key)

    def add_device(self):
        self.send_cmd("RGK")

    def remove_device(self):

        msg = "Which phone mac address do you want to revoke?\nPlease pick a mac address:"
        title = "Choose mac address to revoke acess"
        mac_devices = files_client.list_mac_devices()
        choice = easygui.choicebox(msg, title, mac_devices)
        if choice:
            files_client.remove_device(self.device_address, self.master_key, choice)

    # ##############################################################
    # ################### Share Server Functions ###################
    # ##############################################################

    def wait_for_share_device_info(self):
        while not (self.device_address_to_share and self.device_address_to_share and self.share_device_key):
            if not self.is_waiting_for_share:
                break
            time.sleep(0.5)
        return self.device_address_to_share, self.device_address_to_share, self.share_device_key

    def create_server_sharing(self):
        if not self.isRunning:
            print("Main server not running!")
            return

        self.device_address_to_share = None
        self.device_name_to_share = None

        self.is_waiting_for_share = True
        try:
            print("Waiting device to share")
            advertise_service(self.server_socket, self.server_name,
                              self.server_uuid)
            client_sock_second, address = self.server_socket.accept()
            stop_advertising(self.server_socket)
        except StopWaitingForShare:
            print("Stopped waiting for share device key")
            return
        except Exception:
            print("Error second device")
            return

        if self.is_waiting_for_share:
            self.device_address_to_share = address[0]
            self.device_name_to_share = lookup_name(self.device_address_to_share)

            key_enc = client_sock_second.recv(2048).decode()
            self.share_device_key = base64.b64decode(self.rsa.decrypt_msg(key_enc).decode())

            if self.share_device_key:
                print(f"Share key -> {self.share_device_key}")
            else:
                print("Could not get share device key")
                client_sock_second.close()
                self.device_address_to_share = None
                self.device_name_to_share = None
                return self.create_server_sharing()

            client_sock_second.close()
