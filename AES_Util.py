import base64

import Crypto.Random
from Crypto.Cipher import AES
import math


class AES_Util:

    def __init__(self, key=None):
        if key:
            self.key = key
        else:
            self.key = Crypto.Random.get_random_bytes(32)

    def encrypt(self, data):
        iv = Crypto.Random.get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted_data = base64.b64encode(cipher.encrypt(_pad(data, AES.block_size))).decode()

        encrypted_data += " " + base64.b64encode(iv).decode()

        return encrypted_data

    def decrypt(self, data_enc_base64, iv_base64):
        iv = base64.b64decode(iv_base64)
        data_enc = base64.b64decode(data_enc_base64)
        decipher = AES.new(self.key, AES.MODE_CBC, iv)
        return _unpad(decipher.decrypt(data_enc)).decode()

    def set_key_base64(self, key_base64):
        self.key = base64.b64decode(key_base64)


def _pad(text, block_size):
    """
    Performs padding on the given plaintext to ensure that it is a multiple
    of the given block_size value in the parameter. Uses the PKCS7 standard
    for performing padding.
    """
    no_of_blocks = math.ceil(len(text) / float(block_size))
    pad_value = int(no_of_blocks * block_size - len(text))

    if pad_value == 0:
        return text + chr(block_size) * block_size
    else:
        return text + chr(pad_value) * pad_value


def _unpad(s):
    return s[:-ord(s[len(s) - 1:])]
