from RSA_Util import *

rsa = RSAClass()

msg_to_send = "Teste123"


rsa.export_public_key_to_file("pubkey_client.pem")
input("Enter to continue...")
pubKeyServer = import_public_key_from_file("pubkey_server.pem")


signed = rsa.sign_msg(msg_to_send.encode())
print(signed)

unsigned = remove_signature_msg(signed, rsa.key.publickey())
print(unsigned)