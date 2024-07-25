# This Python file uses the following encoding: utf-8
import Connects
import os, subprocess


class WriteLogs:
    def __init__(self, connects):
        self.connects = Connects.Connects(connects)

    def write_login(self, user, typeLog):
        try:
            comUserLogin = os.getlogin()
            comHostName = subprocess.check_output("hostname").decode()
            listPar = [comHostName, comUserLogin, user, typeLog]
            self.connects.insert_log_login(listPar)
        except:
            pass

    def write_transaction(self, info):
        try:
            self.connects.insert_log_transaction(info)
        except:
            pass
