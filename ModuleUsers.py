# This Python file uses the following encoding: utf-8
import Sentences
import Connect
import ModuleWriteLogs, ModuleSecurity


class Users:
    def __init__(self, connect):
        self.connect = Connect.Connect(connect)
        self.userno = int()
        self.user = str()
        self.password = str()
        self.email = str()
        self.department = str()
        self.group = str()
        self.fullname = str()
        self.permission = str()
        self.phone = str()
        self.sentence = Sentences.Sentences()
        self.isLogin = False
        self.writeLog = ModuleWriteLogs.WriteLogs(connect)
        self.sercurity = ModuleSecurity.Security()
        self.status = True

    def set_status(self, index):
        if index == 1:
            self.status = True
        else:
            self.status = False

    def get_status(self):
        if self.status:
            return 1
        else:
            return 0

    def set_user(self, user):
        try:
            self.userno = int(user.userno)
            self.user = user.users
            self.password = user.password
            self.email = user.emails
            self.department = user.departments
            self.group = user.groups
            self.fullname = user.fullname
            self.permission = user.permissions
            self.phone = user.phonenumber
            self.set_status(user.status)
        except:
            raise

    def set_islogin(self, status):
        self.isLogin = status

    def login_check(self, user, password):
        sql = self.sentence.sql_login_check(user)
        try:
            userAll = self.connect.get_data_operation(sql)
            if len(userAll) == 0:
                return "Login Faild. Not found username"
            else:
                ischeck = True
                for item in userAll.iloc:
                    passworđB = self.sercurity.decrypt(item.password)
                    if password == passworđB:
                        ischeck = False
                        self.set_user(item)
                        self.set_islogin(True)
                        self.writeLog.write_login(self.user, "In")
                        return "Login successfull."
                if ischeck:
                    return "Password incorrect."
        except:
            raise
