# This Python file uses the following encoding: utf-8
import os

from cryptography.fernet import Fernet


class Security:
    def __init__(self):
        self.key = b"yjEcdAh9FrBgmCVipBLiRXIRC0Uv4aGXcCmjh-nwu2o="

    def encrypt(self, text):
        try:
            fernet = Fernet(self.key)
            return fernet.encrypt(text.encode())
        except:
            raise

    def decrypt(self, text):
        try:
            fernet = Fernet(self.key)
            return fernet.decrypt(text).decode()
        except:
            raise
