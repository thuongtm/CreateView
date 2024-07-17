# This Python file uses the following encoding: utf-8
import Connect
import os, subprocess, datetime


class WriteLogs:
    def __init__(self, connect=None):
        self.connect = Connect.Connect(connect)
        pass

    def write_login(self, user, typeLog):
        try:
            comUserLogin = os.getlogin()
            comHostName = subprocess.check_output("hostname").decode()
            listPar = [comHostName, comUserLogin, user, typeLog]
            self.connect.insert_log_login(listPar)
        except:
            pass

    def write_transaction(self, info):
        try:
            self.connect.insert_log_transaction(info)
        except:
            pass
