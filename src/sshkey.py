import argparse
import datetime
import os
import pwd

from ssh_keygen import ALLOWED_TYPES, ssh_key
from ssh_config import AugeasSSHConfig

import logging

log = logging.getLogger(__name__)


def generate_key(args):
    # Split hostname and username
    user, host = args.login.split('@')
    host_clean = host.replace('.', '_')

    # Get home dir
    pwd_entry = pwd.getpwuid(os.getuid())
    ssh_dir = os.path.join(pwd_entry[5], '.ssh')

    key_file = os.path.join(ssh_dir, 'id_{}_{}@{}'.format(args.type, user,
                                                          host_clean))
    pub_key_file = key_file + ".pub"

    log.info("user: {}, file: {}".format(user, key_file))

    today = datetime.datetime.today()
    comment = "{}@{} - {}-{}-{}".format(user, host_clean, today.year,
                                        today.month, today.day)
    # Step 1: Generate the key
    ssh_key(key_file, args.type, comment)

    assert os.path.isfile(key_file) and os.path.isfile(pub_key_file)

    ash = AugeasSSHConfig(pwd_entry.pw_name)
    print("Added new key to '{}'".format(ash.ssh_config))

    # ensure defaults
    if args.defaults:
        print("Set SSH defaults (no X forwarding, no agent forwarding)")
        if args.multiplex:
            print("With SSH multiplexing")
        ash.set_defaults(args.multiplex)

    if args.alias:
        host_alias = args.alias
    else:
        host_alias = host

    ash.define_host(user, host_alias, host, key_file, args.proxy_command,
                    args.port)
    ash.save()

    # Read the key file:

    with open(pub_key_file, 'r') as f:
        print("SSH public key for {}/{}:".format(args.login, host_alias))
        print(f.read())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Interact with your ssh config and keys")

    parser.add_argument("--verbose", action="store_true", default=False,
                        help="verbose output")
    parser.add_argument('--defaults', action='store_false',
                        help='Set ssh defaults')
    parser.add_argument('--multiplex', action='store_false',
                        help='Setup SSH multiplexing/ControlMaster')
    parser.add_argument('--port', default=22, help='SSH port')

    subs = parser.add_subparsers()

    genkey = subs.add_parser('genkey',
                             help='Create keypair for login')

    possible_types = ', '.join(ALLOWED_TYPES)

    genkey.add_argument('login', help='user@hostname.fqdn.tld')
    genkey.add_argument('-t', '--type', default='ed25519',
                              help='key type ({})'.format(possible_types))
    genkey.add_argument('--alias', default=None, help='Alias for host name')
    genkey.add_argument('--proxy_command', default=None,
                        help='(user@)?host to connect to first (ProxyCommand)')

    genkey.set_defaults(func=generate_key)


    args = parser.parse_args()

    if args.func:
        args.func(args)
    else:
        print("You did not choose a mode")
