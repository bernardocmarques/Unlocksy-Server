'''
a differenca entre absolute paths e relative esta confusa no files client
'''
import pytest
import os
from config import CONFIG
from files_client import register_new_directory,lockdown,decrypt_directory,_generate_safe_key,list_directories,_generate_safe_password,ENCRYPT_PATH

import logging
import base64

folder = 'encrypt_testing_folder'

@pytest.fixture
def setup_folder():
    os.system(f'mkdir {folder}')
    os.system(f'echo "ola" > ./{folder}/ola')
    os.system(f'echo "1234567890\n\nalgo" > ./{folder}/coisas')
    yield folder
    # unmount
    lockdown()
    CONFIG().reset()
    os.system(f'rm -rf {folder}')
    os.system(f'rm -rf {ENCRYPT_PATH}')


def test_new_folder(setup_folder):
    path = os.path.abspath(setup_folder)
    mac = '00:21:213312'
    # wrong_mac='00012003:::3'
    master_key = _generate_safe_password(32)
    register_new_directory(path,mac,master_key)

    logging.getLogger().info(os.system(f'ls ./{setup_folder}'))


def test_decrypt_correct_key(setup_folder):
    path = os.path.abspath(setup_folder)
    mac = '00:21:213312'
    master_key = _generate_safe_password(32)
    register_new_directory(path, mac, master_key)

    lockdown()

    decrypt_directory(path,mac,master_key)

    logging.getLogger().info(os.system(f'ls ./{setup_folder}'))

    with open(f'./{setup_folder}/ola','rb') as f:
        content = f.read()

    assert content == b'ola\n'


def test_decrypt_wrong_key(setup_folder):
    path = os.path.abspath(setup_folder)
    mac = '00:21:213312'
    master_key = _generate_safe_password(32)
    wrong_key = _generate_safe_password(32)
    register_new_directory(path, mac, master_key)

    lockdown()

    try:
        decrypt_directory(path, mac, wrong_key)
    except Exception:
        # might give exception
        # if wrong key
        # we dumbly will ignore
        pass

    logging.getLogger().info(os.system(f'ls ./{setup_folder}'))

def test_decrypt_wrong_mac(setup_folder):
    path = os.path.abspath(setup_folder)
    mac = '0012'
    master_key = _generate_safe_password(32)

    with pytest.raises(Exception): # not in keyring
        decrypt_directory(path, mac, master_key)

#
#
#
#
