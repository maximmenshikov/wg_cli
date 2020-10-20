#!/usr/bin/env python3
"""
Unofficial Wireguard user manipulation library

(C) Maxim Menshikov 2020
"""

import argparse
import os
import sys
import glob
import pathlib
import shutil

from enum import Enum

"""
Supported CLI actions
"""


class WgCliAction(Enum):
    list = 'list'
    restore_backup = 'restore_backup'
    make_backup = 'make_backup'
    add_user = 'add_user'
    del_user = 'del_user'


"""
CLI user with all his/her data
"""


class WgCliUser:
    """
    Initialize user data
    """

    def __init__(self):
        self.name = ""
        self.full_name = ""
        self.ip = ""
        self.public_key = ""

    """
    Read user data from folder
    """

    def read_from_folder(self, path):
        with open(os.path.join(path, "name.txt"), "r") as file:
            self.name = file.read().strip()

        with open(os.path.join(path, "full_name.txt"), "r") as file:
            self.full_name = file.read().strip()

        with open(os.path.join(path, "public_key.txt"), "r") as file:
            self.public_key = file.read().strip()

        with open(os.path.join(path, "ip.txt"), "r") as file:
            self.ip = file.read().strip()

    """
    Write user data to folder
    """

    def write_to_folder(self, path):
        with open(os.path.join(path, "name.txt"), "w") as file:
            file.write(self.name)

        with open(os.path.join(path, "full_name.txt"), "w") as file:
            file.write(self.full_name)

        with open(os.path.join(path, "public_key.txt"), "w") as file:
            file.write(self.public_key)

        with open(os.path.join(path, "ip.txt"), "w") as file:
            file.write(self.ip)

    """
    Print user data in user-friendly manner
    """

    def print(self):
        print("User: " + self.name)
        print(" -- Full name: " + self.full_name)
        print(" -- IP:        " + self.ip)
        print(" -- Key:       " + self.public_key)
        print("")


"""
Main CLI class
"""


class WgCli:
    """
    Initialize CLI
    """

    def __init__(self):
        self.head_template = ""
        self.user_template = ""
        self.users = []
        self.syspath = None
        self.interface = None
        self.interface_path = None
        self.user_path = None
        self.user_bkp_path = None
        self.conf_path = None
        self.conf_bkp_path = None

    """
    Set Wireguard CLI parameters
    """

    def set_params(self, syspath, interface):
        self.syspath = syspath
        self.interface = interface
        self.interface_path = os.path.join(self.syspath, self.interface)
        self.user_path = os.path.join(self.interface_path, "users")
        self.user_bkp_path = os.path.join(self.interface_path, "users.bkp")
        self.conf_path = os.path.join(self.syspath, self.interface + ".conf")
        self.conf_bkp_path = os.path.join(self.syspath,
                                          self.interface + ".conf.bkp")

    def verify_params(self):
        if self.syspath is None or \
           self.interface is None or \
           self.interface_path is None or \
           self.conf_path is None or \
           self.conf_bkp_path is None or \
           self.user_path is None or \
           self.user_bkp_path is None:
            return False
        return True

    """
    Read all the data and templates
    """

    def read(self):
        if self.verify_params() == False:
            print("Parameters are not set")
            return

        print("Reading from " + self.interface_path)
        with open(os.path.join(self.interface_path,
                               "wg_head_template.txt"), "r") as file:
            self.head_template = file.read()

        with open(os.path.join(self.interface_path,
                               "wg_user_template.txt"), "r") as file:
            self.user_template = file.read()

        self.users = []
        user_dirs = sorted(glob.glob(os.path.join(self.user_path, "*")))
        for user_dir in user_dirs:
            user = WgCliUser()
            user.read_from_folder(user_dir)
            self.users.append(user)

    """
    Write all the data and templates
    """

    def write(self):
        if self.verify_params() == False:
            print("Parameters are not set")
            return

        pathlib.Path(self.user_path).mkdir(parents=True, exist_ok=True)

        for user in self.users:
            folder = os.path.join(self.user_path, user.name)
            pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
            user.write_to_folder(folder)

        with open(self.conf_path, "w") as file:
            file.write(self.head_template)
            file.write("\n")
            for user in self.users:
                tmp = self.user_template
                tmp = tmp.replace("<IP>", user.ip)
                tmp = tmp.replace("<PublicKey>", user.public_key)
                file.write(tmp)
                file.write("\n")

    """
    List all the users in the configuration
    """

    def list(self):
        if self.verify_params() == False:
            print("Parameters are not set")
            return
        for user in self.users:
            user.print()

    """
    Add user to the configuration
    """

    def add_user(self, user):
        self.users.append(user)

    """
    Delete user from the configuration
    """

    def del_user(self, username):
        removed_users = [a for a in self.users if a.name == username]
        new_users = [a for a in self.users if not a.name == username]
        self.users = new_users
        return removed_users

    """
    Make backup of user information
    """

    def make_user_backup(self):
        if self.verify_params() == False:
            print("Parameters are not set")
            return
        if os.path.exists(self.user_path):
            if os.path.exists(self.user_bkp_path):
                shutil.rmtree(self.user_bkp_path)
            shutil.copytree(self.user_path, self.user_bkp_path)

    """
    Restore backup of user information
    """

    def restore_user_backup(self):
        if os.path.exists(self.user_bkp_path):
            if os.path.exists(self.user_path):
                shutil.rmtree(self.user_path)
            os.rename(self.user_bkp_path, self.user_path)
        else:
            print("Nothing to restore in user configuration")

    """
    Make backup of configuration file
    """

    def make_conf_backup(self):
        if os.path.exists(self.conf_path):
            if os.path.exists(self.conf_bkp_path):
                os.remove(self.conf_bkp_path)
            shutil.copyfile(self.conf_path, self.conf_bkp_path)

    """
    Restore backup of configuration file
    """

    def restore_conf_backup(self):
        if os.path.exists(self.conf_bkp_path):
            if os.path.exists(self.conf_path):
                os.remove(self.conf_path)
            os.rename(self.conf_bkp_path, self.conf_path)
        else:
            print("Nothing to restore in Wireguard configuration")

    """
    Make backup of all Wireguard data for the interface
    """

    def make_backup(self):
        if self.verify_params() == False:
            print("Parameters are not set")
            return
        self.make_user_backup()
        self.make_conf_backup()

    """
    Restore backup of all Wireguard data for the interface
    """

    def restore_backup(self):
        if self.verify_params() == False:
            print("Parameters are not set")
            return
        self.restore_user_backup()
        self.restore_conf_backup()

    """
    Stop Wireguard services (in Ubuntu)
    """

    def stop(self):
        if self.verify_params() == False:
            print("Parameters are not set")
            return
        if os.system("service wg-quick@" + self.interface + " stop") == 0:
            return True
        return False

    """
    Start Wireguard services (in Ubuntu)
    """

    def start(self):
        if self.verify_params() == False:
            print("Parameters are not set")
            return
        if os.system("service wg-quick@" + self.interface + " start") == 0:
            return True
        return False
