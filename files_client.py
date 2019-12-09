'''
Things to do
1. Register a new secure directory
2.decrypt an directory
3. check if wrong key was given
4. Store and List available directories

on new directory -> if not empty moves to temp, creates encrypted filesystem, encrypts files

we need a place on the computer to use as cold storage for the program..


better way for backup was to save it in temp 


neste momento depois de montar, nao e propriamente verificado se a password
e a correta, visto q ele so verifica se a chave ja foi usada ou n, portanto chaves
repetidas nao sao avisadas como serem as incorretas

encrypting filename means shit (any key decripts filenames)


if decrypt with wrong password right fnek sig error
wrong password and wrong fnek sig (right on password), doesnt show shit

we cannot add key to kernel, fica la e desbloqueia com chave errada

File names longer than 143 characters cannot be encrypted (with the FNEK option)



File key must be a password, aka a string not bytes

'''

import subprocess
import shlex
import os
import random
import string
import secrets
import shutil
import Crypto.Random


from config import CONFIG
import keystore

CURRENT_SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

ENCRYPT_PATH = f'{CURRENT_SCRIPT_PATH}/encrypted'


def _randomString(stringLength=10):
    """Generate a random string of fixed length 
    UNSAFE FOR PASSWORDS
    """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def _try_rename_folder(path):
    dest_path = _generate_unique_name(os.path.dirname(path), create_folder=False)
    os.rename(path, dest_path)
    return dest_path

def _try_copy_files_to_temp_location(path):
    '''
    moves some file to a temporary location
    '''
    dest_path = _generate_unique_name(os.path.dirname(path), create_folder=True)

    files = os.listdir(path)
    for f in files:
        shutil.move(f'{path}/{f}', dest_path)


    return dest_path

def _generate_unique_name(path, create_folder=True):
    while True:
        random_name = _randomString(24)
        encrypted_path = f'{path}/{random_name}'
        if not os.path.exists(encrypted_path):

            if create_folder:
                os.mkdir(encrypted_path)

            return encrypted_path


def _move_files_from_folder(source, dest):
    files = os.listdir(source)

    for f in files:
        shutil.move(f'{source}/{f}', dest)

    # if folder not empty then something went wrong
    # os.rmdir(source)
    shutil.rmtree(source)


def _mount_directory(directory, enc_directory, key):
    if not os.path.isdir(directory):
        os.mkdir(directory)

    shell_env = os.environ.copy()
    shell_env["CRYFS_FRONTEND"] = "noninteractive"

    p = subprocess.run(shlex.split(
        f'cryfs {enc_directory} {directory}'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        input=f'{key}\n',
        encoding='ascii',
        env=shell_env)
    #
    # print(p.returncode)
    # # -> 0
    #
    if p.returncode != 0:
        raise ErrorDecrypt(f'exit code {p.returncode} Error in Decrypting - {p.stdout} - {p.stderr}')

    # se for novo registar no config


def _umount_directory(directory):
    # FIXME NEEDS WORK
    process = subprocess.Popen(shlex.split(
        f' fusermount -u {directory}'),
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=0)

    process.communicate()

    if process.returncode != 0:
        # probs ja encriptado
        print(f'Error on umounting - exit code {process.returncode}')
        print(process.stdout)


def _generate_safe_password(size=32):
    # Ascii password
    stringSource = string.ascii_letters + string.digits + string.punctuation

    return ''.join(secrets.choice(stringSource) for i in range(size))


def _generate_safe_key(size=32):
    return Crypto.Random.get_random_bytes(size)


def register_new_directory(path, mac, master_key):
    '''


    assuming to generate key and send it

    check if empty
    move temp
    encrypt

    sudo mount -t ecryptfs directory directory

    where comes password?

    :param path:
    :return: key
    '''

    if not os.path.isdir(ENCRYPT_PATH):
        os.mkdir(ENCRYPT_PATH)

    # work with absolute path
    path = os.path.abspath(path)

    if path in CONFIG().get_config()['directories']:
        raise Exception('Already EXISTS')

    # file key must be a string
    key = _generate_safe_password(24)
    encrypted_path = _generate_unique_name(ENCRYPT_PATH)

    # FIXME pudia ser refatorizado
    if os.path.isdir(path):
        # blabbla backup
        dir_contents = os.listdir(path)
        if not len(dir_contents) == 0:
            # has files, therefore backup
            renamed_folder = _try_rename_folder(path)

            _mount_directory(path, encrypted_path, key)

            # move from backup to destination
            _move_files_from_folder(renamed_folder, path)

        else:
            _mount_directory(path, encrypted_path, key)

    elif not os.path.exists(path):

        _mount_directory(path, encrypted_path, key)

    config = CONFIG().get_config()
    config['directories'][path] = {'enc_path': encrypted_path}
    CONFIG().set_config(config)  # update config

    keystore.set_key(path, mac, master_key, key)


def decrypt_directory(path, mac, master_key):
    '''
    check if exists in config
    check if key worked well
    :param path:
    :param key:
    :return:
    '''

    # debug path should be alread absolute here
    # path = os.path.abspath(path)

    config = CONFIG().get_config()

    file_key = keystore.get_key(path, mac, master_key)

    if path in config['directories'].keys():
        _mount_directory(path, config['directories'][path]['enc_path'], file_key)
    else:
        raise Exception('Directory is not in config')


def unlock_with_device(mac,master_key):
    '''
    needs testing
    '''
    print('UNLOCK FILES')
    config = CONFIG().get_config()

    for path in config['directories'].keys():
        # will try to decrypt
        try:
            decrypt_directory(path,mac,master_key)
        except keystore.NoKeyError:
            # phone doesnt have key, try next key
            continue

def lockdown():
    '''
    encripts back everything from config
    :return:
    '''
    print('ENCRYPT FILES')
    config = CONFIG().get_config()

    for directory in config['directories'].keys():
        _umount_directory(directory)

def remove_folder(path):
    '''
    DOES NOT REMOVE FOLDER, BUT REMOVES ENCRYPTION FROM FOLDER
    FIXME Not TESTED
    '''
    config = CONFIG().get_config()

    if path in config['directories'].keys():
        encrypted_path = config['directories'][path]['enc_path']
    else:
        return False
    
    if _check_if_already_mounted(path,encrypted_path): #if already mounted then is has permission
        
        # blabbla backup
        dir_contents = os.listdir(path)
        if not len(dir_contents) == 0:
            # has files, therefore puts original files in path 
            temp_location = _try_copy_files_to_temp_location(path)

            # dismount path
            _umount_directory(path) 
            #removes encrypted folder and path
            shutil.rmtree(encrypted_path)
            shutil.rmtree(path)

            # move from backup to destination
            os.rename(temp_location, path)


        else:
            #if empty remove all
            _umount_directory(path)

            shutil.rmtree(encrypted_path)
            shutil.rmtree(path)

        return True
    else:
        return False





def update_keys(mac, old_master_key, new_master_key):
    config = CONFIG().get_config()

    for path in config['directories'].keys():
        # will try to decrypt
        try:
            file_key = keystore.get_key(path,mac,old_master_key)

            #update
            keystore.set_key(path,mac, new_master_key,file_key)

        except keystore.NoKeyError:
            # phone doesnt have key, try next key
            continue




def _check_if_already_mounted(directory,enc_directory):
    p = subprocess.run(shlex.split('mount'),stdout=subprocess.PIPE)

    mount_devices = p.stdout.decode()
    search_mountpoint = f'cryfs@{enc_directory} on {directory}'
    return search_mountpoint in mount_devices 

    

def list_directories():
    config = CONFIG().get_config()
    return tuple(config['directories'].keys())


class ErrorDecrypt(Exception):
    pass