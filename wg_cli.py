#!/usr/bin/env python3
"""
Unofficial Wireguard CLI
This executable provides means to add/delete users in Wireguard configuration.

(C) Maxim Menshikov 2020
"""

import argparse
import os
import sys
import shutil
from wg_lib import (WgCliAction, WgCliUser, WgCli)


def prepare_parser():
    """
    Parse common benchmark arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("action",
                        help="Action to do",
                        type=WgCliAction,
                        choices=list(WgCliAction),
                        default=WgCliAction.list)
    parser.add_argument("-n", "--name",
                        help="User name")
    parser.add_argument("-f", "--fullname",
                        help="Full user name")
    parser.add_argument("-i", "--ip",
                        help="User's IP")
    parser.add_argument("-k", "--key",
                        help="User's public key")
    parser.add_argument("-S", "--syspath",
                        help="System path to Wireguard",
                        default="/etc/wireguard")
    parser.add_argument("-W", "--wg-interface",
                        help="Wireguard interface",
                        default="wg0")
    parser.add_argument('--reload', dest='reload', action='store_true')
    parser.add_argument('--no-reload', dest='reload', action='store_false')
    parser.set_defaults(reload=True)
    return parser


if os.geteuid() != 0:
    print("Please run the script under root (sudo)")
    sys.exit(1)

parser = prepare_parser()
args = parser.parse_args()

# Filter out completely wrong arguments
if args.action == WgCliAction.add_user and \
    (args.name is None or
     args.fullname is None or
     args.ip is None or
     args.key is None):
    parser.error("add_user action requires name, full name, ip and key")
    sys.exit(1)

if args.action == WgCliAction.del_user and \
    (args.name is None or
     args.fullname is not None or
     args.ip is not None or
     args.key is not None):
    parser.error("del_user action requires only name")
    sys.exit(1)

# Perform actions
cli = WgCli()
print("System path:         " + args.syspath)
print("Wireguard interface: " + args.wg_interface)
cli.set_params(args.syspath, args.wg_interface)
cli.read()

# Short actions (list, restore_backup, make_backup)
if args.action == WgCliAction.list:
    cli.list()
    sys.exit(0)
elif args.action == WgCliAction.restore_backup:
    cli.restore_user_backup()
    sys.exit(0)
elif args.action == WgCliAction.make_backup:
    cli.make_user_backup()
    sys.exit(0)

# Longer actions with required Wireguard restart
if args.action == WgCliAction.add_user:
    print("Add user:")
    user = WgCliUser()
    user.name = args.name
    user.full_name = args.fullname
    user.ip = args.ip
    user.public_key = args.key
    user.print()
    cli.add_user(user)
elif args.action == WgCliAction.del_user:
    print("Delete user:")
    removed_users = cli.del_user(args.name)
    for user in removed_users:
        user.print()

cli.make_backup()
print("Backup taken")
cli.stop()
cli.write()
print("Configuration written")
success = not args.reload

if args.reload:
    print("Injecting configuration to Wireguard...")
    if cli.start() == True:
        success = True
        print(" -- OK")
else:
    print("Reloading disabled")

if success:
    print("OK")
else:
    cli.restore_backup()
    print("Failed, backup restored")
    cli.stop()
    cli.start()
