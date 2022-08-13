# -*- coding: utf-8 -*-

from utils import generate_password_hash
import getopt
import sys


def show_help():
    print("command options:")
    print("-h show this help")
    print("-n <name> : set name of account")
    print("-p <password> : set password of account")
    print("-s <status> : set status of account "
          "(status string should be admin or user), "
          "default value is admin [this option not required]")
    print("-v show generated hash string at separate line")


def show_args_error():
    print("args -n and -p is required")


def show_hash_string(hash_str):
    hash_value = "".join(["hash: ", hash_str])
    print(hash_value)


def show_query(name, hash_str, status):
    account_insert_query = \
       '''INSERT INTO accounts (id, name, password, status)
          VALUES(default,'{0}','{1}',{2});''' \
        .format(name, hash_str, status)

    print(account_insert_query)


def generate_account():
    try:
        name = None
        password = None
        status = 2
        need_help = False
        need_show_hash_string = False
        opts, args = getopt.getopt(sys.argv[1:], "n:p:s:hv")
        if not opts:
            show_args_error()
            return
        for key, value in opts:
            if key == "-n":
                name = value
            if key == "-p":
                password = value
            if key == "-s":
                if value == "admin":
                    status = 2
                if value == "user":
                    status = 1
            if key == "-h":
                need_help = True
            if key == "-v":
                need_show_hash_string = True

        if need_help:
            show_help()
            return
        if name and password:
            hash_str = generate_password_hash(password)
            if need_show_hash_string:
                show_hash_string(hash_str)
            show_query(name, hash_str, status)
        else:
            show_args_error()
    except getopt.GetoptError as err:
        print(str(err))


generate_account()
