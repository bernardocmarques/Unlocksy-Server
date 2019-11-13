from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto import Random


def encrypt_msg(msg, encryption_key):
    cipher = PKCS1_OAEP.new(encryption_key)
    return cipher.encrypt(msg)


def remove_signature_msg(sign_msg, signature_key):
    cipher = PKCS1_v1_5.new(signature_key)
    return cipher.decrypt(sign_msg, None)


def import_public_key_from_file(filename):
    with open(filename, 'r') as file:
        key_data = file.read()
        return RSA.importKey(key_data)


class RSAClass:

    def __init__(self):
        random_generator = Random.new().read
        self.key = RSA.generate(2048, random_generator)

    def get_public_key(self):
        return self.key.publickey()

    def sign_msg(self, msg):
        cipher = PKCS1_v1_5.new(self.key)
        return cipher.encrypt(msg)

    def sing_and_encrypt(self, msg, encryption_key):
        return encrypt_msg(self.sign_msg(msg), encryption_key)

    def decrypt_msg(self, encrypted_msg):
        cipher = PKCS1_OAEP.new(self.key)
        return cipher.decrypt(encrypted_msg)

    def remove_signature_and_decrypt(self, msg, signature_key):
        return self.decrypt_msg(remove_signature_msg(msg, signature_key))

    def export_public_key_to_file(self, filename):
        with open(filename, "wb") as file:
            file.write(self.key.publickey().exportKey())
