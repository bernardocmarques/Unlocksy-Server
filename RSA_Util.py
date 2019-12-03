import base64

from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random


def import_public_key_from_file(filename):
    with open(filename, 'r') as file:
        key_data = file.read()
        return RSA.importKey(key_data)


class RSA_Util:

    def __init__(self, filename=None):
        if not filename:
            random_generator = Random.new().read
            self.key = RSA.generate(2048, random_generator)
            self.export_key_to_file("key")
        else:
            with open(filename, 'r') as file:
                key_data = file.read()
                self.key = RSA.importKey(key_data)

    def get_public_key(self):
        return self.key.publickey()

    def decrypt_msg(self, encrypted_msg_base64):
        encrypted_msg = base64.b64decode(encrypted_msg_base64)
        cipher = PKCS1_OAEP.new(self.key, hashAlgo=SHA256)
        try:
            msg = cipher.decrypt(encrypted_msg)
        except:
            return None
        return msg

    def get_public_key_base64(self, mode="DER"):
        return base64.b64encode(self.key.publickey().exportKey(mode)).decode()

    def export_public_key_to_file(self, filename):
        with open(filename, "wb") as file:
            file.write(self.key.publickey().exportKey())

    def export_key_to_file(self, filename):
        with open(filename, "wb") as file:
            file.write(self.key.exportKey())
