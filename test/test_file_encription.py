'''
a differenca entre absolute paths e relative esta confusa no files client
'''
import pytest
import os
from config import CONFIG
from files_client import _generate_safe_password,_generate_safe_key,_check_if_mounted
from files_client import *

from keystore import NoKeyError
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

@pytest.fixture
def register_new_directory_fixture(setup_folder):
    path = os.path.abspath(setup_folder)
    mac = '00:21:213312'
    master_key = _generate_safe_password(32)
    register_new_directory(path,mac,master_key)
    
    yield path,mac,master_key

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
    with pytest.raises((ErrorDecrypt,NoKeyError)):
        decrypt_directory(path, mac, wrong_key)
    
    logging.getLogger().info(os.system(f'ls ./{setup_folder}'))

def test_decrypt_wrong_mac(setup_folder):
    path = os.path.abspath(setup_folder)
    mac = '0012'
    master_key = _generate_safe_password(32)

    with pytest.raises(NoKeyError): # not in keyring
        decrypt_directory(path, mac, master_key)

def test_remove_folder(register_new_directory_fixture):
    path,mac,master_key = register_new_directory_fixture
    enc_path = CONFIG().get_config()['directories'][path]['enc_path']

    resp = remove_folder(path,mac,master_key)
    
    assert resp == True
    assert os.path.isdir(path)
    assert len(os.listdir(path)) !=0
    assert not os.path.isdir(enc_path)

def test_remove_folder_no_access(register_new_directory_fixture):
    path,mac,master_key = register_new_directory_fixture
    enc_path = CONFIG().get_config()['directories'][path]['enc_path']
    lockdown()

    resp = remove_folder(path,mac,master_key)
    
    assert resp == False
    assert os.path.isdir(path)
    assert os.path.isdir(enc_path)


def test_if_is_mounted_True(register_new_directory_fixture):
    path,mac,master_key = register_new_directory_fixture
    enc_path = CONFIG().get_config()['directories'][path]['enc_path']

    assert _check_if_mounted(path,enc_path) == True

def test_if_is_mounted_False(register_new_directory_fixture):
    path,mac,master_key = register_new_directory_fixture
    enc_path = CONFIG().get_config()['directories'][path]['enc_path']
    lockdown()

    assert _check_if_mounted(path,enc_path) == False

#
#
#
#
