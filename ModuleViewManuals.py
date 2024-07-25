# This Python file uses the following encoding: utf-8
import ModuleWriteLogs, ModuleUsers
import pandas as pd
import Connects


class ViewManuals:
    def __init__(self, connects, users):
        self.connects = Connects.Connects(connects)
        self.users = ModuleUsers.Users(connects)
        self.users.assign(users)
        self.viewNo = int()
        self.viewName = str()
        self.createDate = str()
        self.lastupdate = str()
        self.userCreate = int()
        self.userLastUpdate = int()
        self.viewStatus = int()  # 1 new 2 update 3 delete
        self.releaseStatus = False  # 1 no 2 yes
        self.inDatabase = False  # 1 no 2 yes

        self.sqlList = []

        self.isUpdate = False

        self.writeLog = ModuleWriteLogs.WriteLogs(self.connects)

    def set_viewno(self, index):
        self.viewNo = index

    def set_view_name(self, viewName):
        self.viewName = viewName

    def set_release_status(self, index):
        if index == 2:
            self.releaseStatus = True
        else:
            self.releaseStatus = False

    def set_in_db(self, index):
        if index == 2:
            self.inDatabase = True
        else:
            self.inDatabase = False

    def set_update(self, status):
        self.isUpdate = status

    def get_release_status(self):
        if self.releaseStatus:
            return 2
        else:
            return 1

    def get_in_db(self):
        if self.inDatabase:
            return 2
        else:
            return 1

    def get_str_status(self):
        if self.viewStatus == 3:
            return "Delete"
        elif self.viewStatus == 2:
            return "Update"
        else:
            return "Create"

    def get_str_release(self):
        if self.releaseStatus:
            return "Release"
        else:
            return "Pending"

    def get_str_indb(self):
        if self.inDatabase:
            return "Yes"
        else:
            return "No"

    def set_sql_string(self, sql):
        lengthSQL = len(sql)
        self.sqlList = []
        if lengthSQL > 0:
            if lengthSQL > 4500:
                raise MemoryError(
                    "The number of characters exceeds the allowed limit (4500)"
                )
            else:
                position = 0
                while lengthSQL > 0:
                    if lengthSQL > 900:
                        self.sqlList.append(sql[position : position + 900])
                        position = position + 900
                        lengthSQL = lengthSQL - 900
                    else:
                        self.sqlList.append(sql[position : len(sql)])
                        lengthSQL = 0
            if len(self.sqlList) > 5:
                self.sqlList = []
                raise MemoryError(
                    "The number of characters exceeds the allowed limit (4500)"
                )

    def get_sql_string(self):
        return "".join(self.sqlList)

    def sql_run_test(self, sql):
        try:
            print(sql)
            sqlTest = """SELECT * FROM ({0}) t1 WHERE ROWNUM < 2""".format(sql)
            self.connects.get_data_operation(sqlTest)
        except:
            raise

    def sql_run(self, sql):
        try:
            data = pd.DataFrame()
            data = self.connects.get_data_operation(sql)
            return data
        except:
            raise

    def loadData(self, data):
        try:
            self.viewNo = int(data.iloc[0].viewno)
            self.viewName = data.iloc[0].viewname
            self.viewStatus = int(
                data.iloc[0].viewstatus
            )  # 1 new 2 update 3 delete
            self.set_release_status(data.iloc[0].viewrelease)
            self.set_in_db(data.iloc[0].indb)

            self.sqlList = [
                data.iloc[0].str1,
                data.iloc[0].str2,
                data.iloc[0].str3,
                data.iloc[0].str4,
                data.iloc[0].str5,
            ]
        except:
            raise

    def create(self):
        try:
            viewNo = self.connects.insert_view_manual(self.parameter_create())
            self.viewNo = viewNo
            self.writeLogs("View", "Create")
            return viewNo
        except:
            raise

    def parameter_create(self):
        listPara = [self.viewName, self.users.userno] + self.sqlList
        while len(listPara) < 7:
            listPara.append("")
        return listPara

    def update(self):
        try:
            self.connects.update_view_manual(self.parameter_update())
            self.writeLogs("View", "Update")
            self.isUpdate = True
            self.releaseStatus = False
            self.inDatabase = True
        except:
            raise

    def parameter_update(self):
        listPara = [self.viewNo, self.users.userno] + self.sqlList
        while len(listPara) < 7:
            listPara.append("")
        return listPara

    def delete(self):
        try:
            self.connects.delete_view_manual(self.parameter_delete())
            self.writeLogs("View", "Delete")
        except:
            raise

    def parameter_delete(self):
        listPara = [self.viewNo, self.users.userno]
        return listPara

    def release(self):
        try:
            if not self.releaseStatus:
                if self.viewStatus == 1:
                    self.connects.excute_query(self.db_create())
                    self.writeLogs("Release", "Create")
                elif self.viewStatus == 2:
                    if self.inDatabase:
                        self.connects.excute_query(self.db_update())
                        self.writeLogs("Release", "Update")
                    else:
                        self.connects.excute_query(self.db_create())
                        self.writeLogs("Release", "Create")
                elif self.viewStatus == 3:
                    if self.inDatabase:
                        self.connects.excute_query(self.db_delete())
                        self.writeLogs("Release", "Delete")
                self.update_release()
        except:
            raise

    def update_release(self):
        try:
            self.connects.update_release_view_manual(self.parameter_release())
        except:
            raise

    def parameter_release(self):
        listPara = [self.viewNo]
        return listPara

    def writeLogs(self, action, detail):
        self.writeLog.write_transaction(
            [self.users.userno, "V_Manual", int(self.viewNo), action, detail]
        )

    def db_create(self):
        try:
            sql = """CREATE VIEW REPORTUSER.{0} AS {1}""".format(
                self.viewName, self.get_sql_string()
            )
            return sql
        except:
            raise

    def db_update(self):
        try:
            sql = """CREATE OR REPLACE VIEW REPORTUSER.{0} AS {1}""".format(
                self.viewName, self.get_sql_string()
            )
            return sql
        except:
            raise

    def db_delete(self):
        try:
            sql = """DROP VIEW REPORTUSER.{0}""".format(self.viewName)
            return sql
        except:
            raise
