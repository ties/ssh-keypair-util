# -*- coding: utf-8 -*-
import argparse
import datetime
import os
import platform
import pwd
import sys

from .ssh_keygen import ALLOWED_TYPES, ssh_key
from .ssh_config import AugeasSSHConfig

import logging

log = logging.getLogger(__name__)


def global_config(args):
    # Get home dir
    pwd_entry = pwd.getpwuid(os.getuid())
    ssh_dir = os.path.join(pwd_entry[5], ".ssh")

    ash = AugeasSSHConfig(pwd_entry.pw_name)
    print("Setting SSH defaults in {}".format(ash.ssh_config))

    if args.multiplex:
        print("  [✔] With SSH multiplexing")
    ash.set_defaults(args.multiplex)

    ash.save()


def generate_key(args):
    # Split hostname and username
    user, host = args.login.split("@")
    host_clean = host.replace(".", "_")

    # Get home dir
    pwd_entry = pwd.getpwuid(os.getuid())
    ssh_dir = os.path.join(pwd_entry[5], ".ssh")

    key_file = os.path.join(ssh_dir, "id_{}_{}@{}".format(args.type, user, host_clean))
    pub_key_file = key_file + ".pub"

    log.info("user: {}, file: {}".format(user, key_file))

    today = datetime.datetime.today()
    comment = "{}@{} - {}-{}-{} - {}".format(
        user, host_clean, today.year, today.month, today.day, platform.node()
    )
    # Step 1: Generate the key
    ssh_key(key_file, args.type, args.rounds, comment)

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

    ash.define_host(
        user, host_alias, host, key_file, args.proxy_command, args.port, args.jump_host
    )
    ash.save()

    # Read the key file:

    with open(pub_key_file, "r") as f:
        print("SSH public key for {}/{}:".format(args.login, host_alias))
        print(f.read())


def main_func():
    parser = argparse.ArgumentParser(
        description="Interact with your ssh config and keys"
    )

    parser.add_argument(
        "--verbose", action="store_true", default=False, help="verbose output"
    )
    parser.add_argument(
        "--skip-defaults",
        dest="defaults",
        action="store_false",
        help="Set ssh defaults",
    )
    parser.add_argument(
        "--multiplex", action="store_true", help="Setup SSH multiplexing/ControlMaster"
    )
    parser.add_argument("--port", default=None, type=int, help="SSH port")

    subs = parser.add_subparsers()

    genkey = subs.add_parser("genkey", help="Create keypair for login")
    globalconfig = subs.add_parser("globalconfig", help="Set-up global SSH config")

    possible_types = ", ".join(ALLOWED_TYPES)

    genkey.add_argument("login", help="user@hostname.fqdn.tld")
    genkey.add_argument(
        "-t", "--type", default="ed25519", help="key type ({})".format(possible_types)
    )
    genkey.add_argument(
        "-a", "--rounds", default=100, help="Number of Key Derivation Function rounds"
    )
    genkey.add_argument("--alias", default=None, help="Alias for host name")
    genkey.add_argument(
        "--proxy_command",
        default=None,
        help="(user@)?host to connect to first (ProxyCommand)",
    )
    genkey.add_argument("--jump_host", default=None, help="jumphost to connect via")

    parser.set_defaults(func=None)
    genkey.set_defaults(func=generate_key)
    globalconfig.set_defaults(func=global_config)

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)

    if hasattr(args, "func") and args.func is not None:
        args.func(args)
    else:
        print("You did not choose a mode")
        parser.print_help(sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main_func()
