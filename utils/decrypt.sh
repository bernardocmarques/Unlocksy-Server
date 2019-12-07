#!/bin/bash

# remember to unlink from the kernel the signatures

sudo mount -t ecryptfs -o key=passphrase:passphrase_passwd_fd=0,no_sig_cache,verbose,ecryptfs_cipher=aes,ecryptfs_key_bytes=32,ecryptfs_enable_filename=y,ecryptfs_passthrough=n,ecryptfs_enable_filename_crypto=n,ecryptfs_unlink_sigs=y "$1" "$1"
