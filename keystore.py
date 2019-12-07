import keyring
from AES_M import AESClass
import base64

def set_key(abs_path,mac,master_key,file_key):
    aes = AESClass(master_key)
    encripted_key = aes.encrypt(file_key)
    keyring.set_password(abs_path,mac,encripted_key)

def get_key(abs_path,mac,master_key):
    aes = AESClass(master_key)
    obtained = keyring.get_password(abs_path, mac)
    if not obtained: #if empty
        return obtained
    try:
        encripted_key, iv = obtained.split(" ")
        return aes.decrypt(encripted_key,iv)
    except UnicodeDecodeError:
        # wrong key
        return None

