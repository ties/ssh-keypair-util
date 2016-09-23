import subprocess
import os
import sys
import logging

log = logging.getLogger(__name__)

ALLOWED_TYPES = set(['ecdsa', 'ed25519', 'rsa'])  # No rsa1/dsa


def ssh_key(file_name, key_type, rounds, comment):
    assert key_type in ALLOWED_TYPES

    abs_keypath = os.path.abspath(file_name)
    if os.path.isfile(abs_keypath):
        log.info("Not overwriting '{}'".format(abs_keypath))
        return

    args = [
        '-f', os.path.abspath(file_name),
        '-t', key_type,
        # '-N', "''",
        '-a', str(rounds),
        '-C', comment,
        '-o'  # new format/use better Key Derivation Function
    ]

    if key_type == 'rsa':
        log.info("Forcing RSA 4096 bit length")
        args.extend(['-b', '4096'])

    subprocess.call(['/usr/bin/ssh-keygen'] + args, stdin=sys.stdin)


def read_key(file_name):
    with open(file_name, 'r'):
        return file_name.read()
