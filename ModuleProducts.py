# This Python file uses the following encoding: utf-8
import copy
from bs4 import BeautifulSoup
import Connects, ModuleSecurity, Sentences
import os, pathlib
from datetime import date
from datetime import datetime


class Products:
    def __init__(self, connects):
        self.version = str()
        self.licenses = str()
        self.info = str()
        self.existLicenses = False  # kiểm tra có file license hay không?
        self.isToActive = False  # kiểm tra lệnh btn active
        self.isLicenses = False  # kiểm tra license có hợp lệ (DB) hay không?
        self.isTrial = True  # kiểm tra còn hạn dùng thử hay không?
        self.timeTrial = int()  # thời gian dùng thử
        self.security = ModuleSecurity.Security()
        self.permission = (
            False  # kiểm tra có bị giới hạn quyền admin để chạy hay không?
        )
        self.sqlSentence = Sentences.Sentences()
        try:
            self.connects = Connects.Connects(connects)
            self.read_version()
            self.load_license()
            if self.isLicenses:
                self.set_is_trial(True)
            else:
                self.check_trial()
        except:
            raise

    def read_version(self):
        fileVer = str(os.getcwd()) + "\\Config\\Version.xml"
        fileLicenses = str(os.getcwd()) + "\\Config\\Licenses.src"
        try:
            with open(fileVer, "r") as ver:
                verRead = ver.read()
                bsData = BeautifulSoup(verRead, "xml")
                self.version = bsData.find("ver").getText()
                self.info = bsData.find("info").getText()
            if os.path.exists(fileLicenses):
                self.existLicenses = True
                with open(fileLicenses, "r") as lic:
                    licRead = lic.read()
                    self.licenses = str(licRead)
        except:
            self.licenses = str()
            self.existLicenses = False

    def get_license(self):
        if self.isLicenses:
            return self.licenses
        else:
            if self.isTrial:
                return "Trial {0} Day".format(self.timeTrial)
            else:
                return "Trial expired"

    def set_to_active(self, status):
        self.isToActive = status

    def set_is_trial(self, status):
        self.isTrial = status

    def set_time_trial(self, index):
        self.timeTrial = index

    def load_license(self):
        isCheck = False
        # kiểm tra thời hạn licence
        if self.licenses == "":
            isCheck = False
        else:
            try:
                isCheck = self.expired_license(self.licenses)
            except:
                isCheck = False
                raise
        if isCheck:
            # kiểm tra tồn tại trên DB
            sql = self.sqlSentence.sql_check_license()
            try:
                data = self.connects.get_data_operation(sql)
                if data.empty:
                    isCheck = False
                else:
                    for item in data.iloc:
                        keyDB = self.security.decrypt(item.keylicense, "Load")
                        if keyDB == self.licenses:
                            isCheck = True
                            break
                        else:
                            isCheck = False
            except:
                isCheck = False
                raise
        # kiểm tra số lượng sử dụng, <>1 False; =1 True --> update 1
        self.isLicenses = isCheck
        if not isCheck:
            self.set_to_active(False)

    def check_key(self, key, userno):
        isCheck = False
        # kiểm tra thời hạn licence
        if key == "":
            isCheck = False
        else:
            try:
                isCheck = self.expired_license(key)
            except:
                isCheck = False
                raise
        keySer = ""
        if isCheck:
            # kiểm tra tồn tại trên DB
            sql = self.sqlSentence.sql_get_license()
            try:
                data = self.connects.get_data_operation(sql)
                if data.empty:
                    isCheck = False
                else:
                    for item in data.iloc:
                        keyDB = self.security.decrypt(item.keylicense, "Load")
                        if keyDB == key:
                            keySer = item.keylicense
                            isCheck = True
                            break
            except:
                isCheck = False
                raise
        # kiểm tra số lượng sử dụng, <>1 False; =1 True --> update 1
        if not isCheck:
            self.set_to_active(False)
        else:
            fileLicenses = str(os.getcwd()) + "\\Config\\Licenses.src"
            try:
                # write license
                with open(fileLicenses, "w") as li:
                    li.write(key)
                    li.close()
                # update license
                host = os.getlogin()
                self.connects.update_license([keySer, host])
                self.connects.delete_license_use(["Trial", userno])
                self.connects.insert_license_use([key, userno])
            except:
                raise

    def expired_license(self, licen):
        # quy tắc license: X<Po_year>XX<expired>-XXXXX-XXXXX-XXXXX-XXXXX
        # exprired: Cha - 1, Num = 2
        try:
            listWord = licen.split("-")
            pYear = int(listWord[0][1:2])
            pYear = abs(abs(pYear - 5) - 4)
            pExpired = listWord[0][4:5]
            try:
                x = int(pExpired)
                pExpired2 = 2
            except:
                pExpired2 = 1
            posCharacter = copy.deepcopy(
                pYear
            )  # vị trí của từ trong license (1->4)
            if pYear == 0:  # 1 -> 4
                pdonvi = 3
                pchuc = 2
                ptram = 1
            elif pYear == 1:
                pdonvi = 1
                pchuc = 3
                ptram = 4
            elif pYear == 4:
                pdonvi = 3
                pchuc = 2
                ptram = 1
            else:
                pdonvi = 3
                pchuc = 2
                ptram = 4
            donvi = int(listWord[pdonvi][posCharacter])
            chuc = int(listWord[pchuc][posCharacter])
            tram = int(listWord[ptram][posCharacter])
            lYear = 2000 + tram * 100 + chuc * 10 + donvi + pExpired2
            if lYear <= date.today().year:
                return True
            else:
                return False
        except:
            raise ValueError("License Ex")

    def check_trial(self):
        user = os.getlogin()
        licenPath = os.path.join("C:\\", "Users", user, "crview.licen")
        try:
            if os.path.exists(licenPath):
                try:
                    with open(licenPath, "r") as li:
                        strDate = self.security.decrypt(li.read(), "Date")
                        firstDate = datetime.strptime(strDate, "%Y-%m-%d")
                        dateUse = (datetime.now() - firstDate).days
                        self.set_is_trial(not dateUse > 30)
                        self.set_time_trial(30 - dateUse)
                except IOError:
                    self.permission = True
                    raise IOError("Run program with Administrator read")
            else:
                if self.connects.numberUse > 0:
                    raise KeyError("License File Not Found")
                else:
                    try:
                        pathlib.Path.touch(licenPath, mode=0o777, exist_ok=True)
                        with open(licenPath, "w") as li:
                            strDate = self.security.encrypt(
                                str(date.today()), "ToDate"
                            )
                            li.write(strDate)
                            li.close()
                            self.connects.write_config("1")
                            self.set_is_trial(True)
                            self.set_time_trial(30)
                    except IOError:
                        self.permission = True
                        raise IOError("Run program with Administrator create")
        except:
            raise
