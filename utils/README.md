
Encrypting and decrypting directories requires root priveleges, so the idea is to create an encrypt and decrypt bash scripts that can be runned in root without asking for password

https://askubuntu.com/questions/155791/how-do-i-sudo-a-command-in-a-script-without-being-asked-for-a-password



em consequencia, o sistema tem de ser configurado para tal

sudo chown root:root $1
sudo chmod 700 $1

(para users poderem ler)

sudo chmod 744 $1

(sudo visudo)
(below %sudo   ALL=(ALL:ALL) ALL)
username  ALL=(ALL) NOPASSWD: $1