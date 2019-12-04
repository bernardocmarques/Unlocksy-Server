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
'''

import subprocess
import shlex
import os
import random
import string
import regex
import secrets
import shutil

from pathlib import Path


from config import CONFIG

CURRENT_SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))


def _add_directory(path):
    config = CONFIG().get_config()
    config['directories'].append()

    CONFIG().set_config(config)

def _randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def _try_rename_folder(path):
    i=0
    while True:
        dest_path=path+_randomString()

        try:
            os.rename(path,dest_path)
        except OSError as e:
            #not renamed
            i+=1
            if i>5:
                print(e)
                raise e
            else:
                #try again
                continue

        return dest_path

def _move_files_from_folder(source,dest):
    files = os.listdir(source)

    for f in files:
        shutil.move(f'{source}/{f}', dest)
    
    # if folder not empty then something went wrong
    os.rmdir(source)
    

def _mount_directory(directory,key,new=False):

    if new:
        p = subprocess.run(
            shlex.split('ecryptfs-add-passphrase --fnek'),
            stdout=subprocess.PIPE,
            input=f'{key}\n', encoding='ascii')
        print(p.returncode)
        # -> 0

        if p.returncode!=0:
            raise Exception('Error in saving fnek')

        print(p.stdout)
        fnek = regex.findall('\[(.*)\]',p.stdout)[0]
    else:
        config = CONFIG().get_config()
        fnek = config['directories'][directory]['FNEK'] #FIXME throws not exists


    p = subprocess.run(
        shlex.split(f'sudo {CURRENT_SCRIPT_PATH + "/utils/decrypt.sh"} {directory} {fnek}'),
        stdout=subprocess.PIPE,
        input=f'passphrase_passwd={key}\n', encoding='ascii')

    print(p.returncode)
    # -> 0

    if p.returncode!=0:
        raise Exception('Error in Decrypting - Probably wrong key - '+p.stdout)

    # se for novo registar no config
    if new:
        config = CONFIG().get_config()
        config['directories'][directory]={'FNEK':fnek}
        CONFIG().set_config(config) #update config


def _umount_directory(directory):
    #FIXME NEEDS WORK
    process = subprocess.Popen(
        shlex.split(f'sudo {CURRENT_SCRIPT_PATH + "/utils/encrypt.sh"} {directory}'),
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=0)

    process.communicate()

    if process.returncode !=0:
        #probs ja encriptado
        print(f'Error on umounting - exit code {process.returncode}')
        print(process.stdout)



def _generate_safe_password(size=32):
    # Sera q devia ser feito de outra maneira?
    stringSource  = string.ascii_letters + string.digits + string.punctuation 

    return ''.join(secrets.choice(stringSource) for i in range(size)) 


def register_new_directory(path):
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
    #work with absolute path
    path = os.path.abspath(path)

    key = _generate_safe_password()
    
    #FIXME pudia ser refatorizado
    if os.path.isdir(path):
        #blabbla backup
        dir_contents = os.listdir(path)
        if not len(dir_contents)==0:
            #has files, therefore backup
            renamed_folder = _try_rename_folder(path)
            
            os.mkdir(path)

            _mount_directory(path,key,new=True)

            # move from backup to destination
            _move_files_from_folder(renamed_folder,path)

        else:
            _mount_directory(path,key,new=True)
        

    elif not os.path.exists(path):
        os.mkdir(path)

        _mount_directory(path,key,new=True)

    return key

    
    


def decrypt_directory(path, key):
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

    if path in config['directories'].keys():
        _mount_directory(path,key)
    else:
        raise Exception('Directory is not in config')


def lockdown():
    '''
    encripts back everything from config
    :return:
    '''
    config = CONFIG().get_config()

    for directory in config['directories']:
        _umount_directory(directory)


def list_directories():
    config = CONFIG().get_config()
    return tuple(config['directories'].keys())


if __name__ == "__main__":
    folder='./testencrypt'
    os.mkdir(folder)
    

