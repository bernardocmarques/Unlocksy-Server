#!/bin/bash

# echo "Positional Parameters"
# echo '$0 = ' $0
# echo '$1 = ' $1
# echo '$2 = ' $2
# echo '$3 = ' $3

sudo mount -t ecryptfs -o key=passphrase:passphrase_passwd_fd=0,no_sig_cache,verbose,ecryptfs_cipher=aes,ecryptfs_key_bytes=32,ecryptfs_enable_filename=y,ecryptfs_passthrough=n,ecryptfs_enable_filename_crypto=y,ecryptfs_fnek_sig="$2" "$1" "$1"
