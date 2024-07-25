# This Python file uses the following encoding: utf-8
import Sentences
import Connects
import ModuleWriteLogs, ModuleSecurity


class Users:
    def __init__(self, connects):
        self.connects = Connects.Connects(connects)
        self.userno = int()
        self.user = str()
        self.password = str()
        self.email = str()
        self.department = str()
        self.group = int()
        self.fullname = str()
        self.permission = "ANY"
        self.phone = str()
        self.sentence = Sentences.Sentences()
        self.isLogin = False
        self.writeLog = ModuleWriteLogs.WriteLogs(connects)
        self.sercurity = ModuleSecurity.Security()
        self.status = True  # 1 yes 2 no

        self.isUpdate = False

    def assign(self, user):
        self.connects = user.connects
        self.userno = user.userno
        self.user = user.user
        self.password = user.password
        self.email = user.email
        self.department = user.department
        self.group = user.group
        self.fullname = user.fullname
        self.permission = user.permission
        self.phone = user.phone
        self.isLogin = user.isLogin
        self.status = user.status  # 1 yes 2 no

        self.isUpdate = user.isUpdate

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

    def is_admin(self):
        return self.userno == 1 and self.user == "admin"

    def set_password(self, password):
        self.password = self.sercurity.decrypt(password)

    def set_user(self, user):
        try:
            self.userno = int(user.userno)
            self.user = user.users
            self.set_password(user.password)
            self.email = user.emails
            self.department = user.departments
            self.group = int(user.groups)
            self.fullname = user.fullname
            self.permission = user.permissions
            self.phone = user.phonenumber
            self.set_status(int(user.status))
        except:
            raise

    def set_islogin(self, status):
        self.isLogin = status

    def set_update(self, status):
        self.isUpdate = status

    def login_check(self, user, password):
        sql = self.sentence.sql_login_check(user)
        try:
            userAll = self.connects.get_data_operation(sql)
            if len(userAll) == 0:
                return "Login Faild. Not found username"
            else:
                ischeck = True
                for item in userAll.iloc:
                    passwordDB = self.sercurity.decrypt(item.password)
                    if password == passwordDB:
                        ischeck = False
                        self.set_user(item)
                        self.set_islogin(True)
                        self.writeLog.write_login(self.user, "In")
                        return "Login successfull."
                if ischeck:
                    return "Password incorrect."
        except:
            raise

    def change_password(self, passCur, passNew, passConfirm):
        isCheck = True
        if passCur != self.password and isCheck:
            isCheck = False
            raise ValueError("Password Current incorrect.")
        if isCheck and passNew != passConfirm:
            isCheck = False
            raise ValueError("New Password different Confirm Password.")

        if isCheck and passNew.find(" ") >= 0:
            isCheck = False
            raise ValueError("The new password contains space characters.")

        if isCheck and not passNew.isascii():
            isCheck = False
            raise ValueError("The new password contains Vietnamese characters.")
        if isCheck:
            try:
                passChange = self.sercurity.encrypt(passNew)
                self.connects.change_password([self.userno, passChange])
                self.password = passNew
                self.writeLog.write_transaction(
                    [
                        self.user.userno,
                        "User",
                        self.userno,
                        "Change Password",
                        "Change Password",
                    ]
                )
            except:
                raise

    def add(
        self,
        userName,
        password,
        passwordConfirm,
        email,
        fullName,
        phone,
        depts,
        per,
        status,
    ):
        isCheck = True

        if password != passwordConfirm:
            isCheck = False
            raise ValueError("The password different confirm password.")

        if isCheck and userName.strip() == "":
            isCheck = False
            raise ValueError("The user Name not null.")

        if isCheck and not userName.isascii():
            isCheck = False
            raise ValueError("The user Name contains Vietnamese characters.")

        if isCheck and depts.strip() == "":
            isCheck = False
            raise ValueError("Please select Departments.")

        if isCheck and password.find(" ") >= 0:
            isCheck = False
            raise ValueError("The new password contains space characters.")

        if isCheck and not password.isascii():
            isCheck = False
            raise ValueError("The new password contains Vietnamese characters.")

        if isCheck:
            passwordChange = self.sercurity.encrypt(password)
            statusText = 1
            if not status:
                statusText = 0
            try:
                userNo = self.connects.add_user(
                    [
                        userName,
                        passwordChange,
                        email,
                        fullName,
                        phone,
                        depts,
                        per,
                        statusText,
                    ]
                )
                self.writeLog.write_transaction(
                    [
                        1,
                        "User",
                        userNo,
                        "Create User",
                        "Add",
                    ]
                )
                return userNo
            except:
                raise

    def update(
        self,
        userName,
        password,
        passwordConfirm,
        email,
        fullName,
        phone,
        depts,
        per,
        status,
    ):
        isCheck = True

        if password != passwordConfirm:
            isCheck = False
            raise ValueError("The password different confirm password.")

        if isCheck and userName.strip() == "":
            isCheck = False
            raise ValueError("The user Name not null.")

        if isCheck and not userName.isascii():
            isCheck = False
            raise ValueError("The user Name contains Vietnamese characters.")
        if isCheck and depts.strip() == "":
            isCheck = False
            raise ValueError("Please select Departments.")

        if isCheck and password.find(" ") >= 0:
            isCheck = False
            raise ValueError("The new password contains space characters.")

        if isCheck and not password.isascii():
            isCheck = False
            raise ValueError("The new password contains Vietnamese characters.")

        if isCheck:
            passwordChange = self.sercurity.encrypt(password)
            statusText = 1
            if not status:
                statusText = 0
            try:
                self.connects.update_user(
                    [
                        userName,
                        passwordChange,
                        email,
                        fullName,
                        phone,
                        depts,
                        per,
                        statusText,
                    ]
                )
                self.writeLog.write_transaction(
                    [
                        1,
                        "User",
                        self.userno,
                        "Create User",
                        "Update",
                    ]
                )
            except:
                raise
