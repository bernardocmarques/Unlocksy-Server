import Crypto.Random
from Crypto.Cipher import AES
import math


class AESClass:

    def __init__(self):
        self.key = Crypto.Random.get_random_bytes(16)

    def encrypt(self, data):
        iv = Crypto.Random.get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return cipher.encrypt(_pad(data, AES.block_size)), iv

    def decrypt(self, data_enc):
        decipher = AES.new(key, AES.MODE_CBC, IV)
        return _unpad(decipher.decrypt(data_enc)).decode()


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