# This Python file uses the following encoding: utf-8
import os

from cryptography.fernet import Fernet


class Security:
    def __init__(self):
        self.key = b"yjEcdAh9FrBgmCVipBLiRXIRC0Uv4aGXcCmjh-nwu2o="
        self.key2 = b"gAAAAABmrOlvCQJyb7vdSm3MXBZcWY8FHcvW5QasUouhwSW7kdONGeClQn7Fh5JOdUhFAlTOi1HLY2-f_cIhCxtdNhdx40QeUg=="

    def encrypt(self, text, key=None):
        try:
            if key == None:
                fernet = Fernet(self.key)
            else:
                fernet = Fernet(self.get_key())
            return fernet.encrypt(text.encode()).decode()
        except:
            raise

    def decrypt(self, text, key=None):
        try:
            if key == None:
                fernet = Fernet(self.key)
            else:
                fernet = Fernet(self.get_key())
            return fernet.decrypt(text).decode()
        except:
            raise

    def get_key(self):
        sKey = self.key + self.key2
        return sKey
