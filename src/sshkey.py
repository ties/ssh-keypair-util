import argparse
import os
import pwd

from ssh_keygen import ALLOWED_TYPES, ssh_key
from ssh_config import AugeasSSHConfig

import logging

log = logging.getLogger(__name__)
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def generate_key(args):
    # Split hostname and username
    user, host = args.login.split('@')
    host_clean = host.replace('.', '_')

    # Get home dir
    pwd_entry = pwd.getpwuid(os.getuid())
    ssh_dir = os.path.join(pwd_entry[5], '.ssh')
    
    key_file = os.path.join(ssh_dir, 'id_{}_{}'.format(args.type, host_clean))

    log.info("user: {}, file: {}".format(user, key_file))
    # Step 1: Generate the key
    ssh_key(key_file, args.type) 

    ash = AugeasSSHConfig(pwd_entry.pw_name)
    # ensure defaults
    if args.defaults:
        ash.set_defaults()

    ash.define_host(user, host, host, key_file)
    ash.save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Interact with your ssh config and keys")

    parser.add_argument("--verbose", action="store_true", default=False,
                        help="verbose output")
    parser.add_argument('--defaults', action='store_false', help='Set ssh defaults')
    parser.set_defaults(func=None)

    subs = parser.add_subparsers()

    genkey = subs.add_parser('genkey',
                                   help='Create keypair for login')

    possible_types = ', '.join(ALLOWED_TYPES)

    genkey.add_argument('login', help='user@hostname.fqdn.tld')
    genkey.add_argument('-t', '--type', default='ed25519',
                              help='key type ({})'.format(possible_types))

    genkey.set_defaults(func=generate_key)


    args = parser.parse_args()

    if args.func:
        args.func(args)
    else:
        print("You did not choose a mode")
