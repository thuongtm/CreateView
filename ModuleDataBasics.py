# This Python file uses the following encoding: utf-8
import Sentences, Connects, ModuleDataSets, ModuleFunctions, ModuleCalculations
import ModuleViewAction, ModuleUsers
import copy
import pandas as pd


class DataBasics:
    def __init__(self, connects, user):
        self.datasetList = []
        self.sentence = Sentences.Sentences()
        self.connects = Connects.Connects(connects)
        self.functionList = []
        self.calculationList = []
        self.dataSearch = pd.DataFrame()
        self.user = ModuleUsers.Users(connects)
        self.user.assign(user)
        self.idNew = int()
        self.actionViewList = []
        self.runViewList = []
        self.dataRun = pd.DataFrame()
        self.includedViewName = []
        self.viewNameAll = []
        self.depts = []

    def initdata_create(self):
        self.loaddata_dataset_all()
        self.loaddata_function()
        self.loaddata_calculation()
        self.loaddata_view_id()
        self.loaddata_view_name_included()
        self.loaddata_view_name_all()

    def initdata_search(self):
        self.loaddata_search()

    def initdate_release(self):
        self.loaddata_dataset_all()
        self.loaddata_function()
        self.loaddata_calculation()
        self.loaddata_view_release()

    def initdata_run(self):
        self.loaddata_dataset_all()
        self.loaddata_function()
        self.loaddata_calculation()
        self.loaddata_view_run()

    def initdata_create_user(self):
        self.get_list_dept()

    def loaddata_dataset_all(self):
        self.datasetList = []
        sql = self.sentence.sql_get_dataset_all(
            self.user.permission, self.user.group
        )
        try:
            data = self.connects.get_data_operation(sql)
            data = data.replace({pd.NA: None})
            data = data.replace({pd.NaT: None})
            data = data.fillna("")
            if data.empty:
                raise ValueError("Do not found DataSet in Database.")
            else:
                for item in data.iloc:
                    dataset = ModuleDataSets.DataSets(self.connects)
                    dataset.set_dataset(item)
                    self.datasetList.append(dataset)
        except:
            raise

    def get_all_dataset_name(self):
        list_name = [""]
        for item in self.datasetList:
            list_name.append(item.datasetName)
        return list_name

    def get_dataset_with_name(self, name):
        for item in self.datasetList:
            if item.datasetName == name:
                return copy.deepcopy(item)

    def loaddata_view_id(self):
        sql = self.sentence.sql_get_view_new_id()
        try:
            data = self.connects.get_data_operation(sql)
            if data.empty:
                raise ValueError("Error when get ID new of View")
            else:
                self.idNew = int(data.iloc[0].idnew)
        except:
            raise

    def loaddata_function(self):
        self.functionList = []
        sql = self.sentence.sql_get_function_all()
        try:
            data = self.connects.get_data_operation(sql)
            data = data.replace({pd.NA: None})
            data = data.replace({pd.NaT: None})
            data = data.fillna("")
            if data.empty:
                raise ValueError("Error when get Function info")
            else:
                for item in data.iloc:
                    function = ModuleFunctions.Functions()
                    function.setbasic_function(item)
                    self.functionList.append(function)
        except:
            raise

    def loaddata_calculation(self):
        self.calculationList = []
        sql = self.sentence.sql_get_calculation_all()
        try:
            data = self.connects.get_data_operation(sql)
            data = data.replace({pd.NA: None})
            data = data.replace({pd.NaT: None})
            data = data.fillna("")
            if data.empty:
                raise ValueError("Error when get Calculation info")
            else:
                for item in data.iloc:
                    calculation = ModuleCalculations.Calculations()
                    calculation.setbasic_calculation(item)
                    self.calculationList.append(calculation)
        except:
            raise

    def loaddata_search(self):
        sql = self.sentence.sql_get_view_name_all(
            self.user.permission, self.user.group, self.user.userno
        )
        try:
            self.dataSearch = pd.DataFrame()
            data = self.connects.get_data_operation(sql)
            if not data.empty:
                self.dataSearch = data
        except:
            raise

    def loaddata_view_name_all(self):
        sql = self.sentence.sql_get_view_name_all(
            self.user.permission, self.user.group, self.user.userno
        )
        try:
            self.viewNameAll = []
            data = self.connects.get_data_operation(sql)
            if not data.empty:
                for item in data.iloc:
                    self.viewNameAll.append(item.viewname)
        except:
            raise

    def loaddata_view_name_included(self):
        sql = self.sentence.sql_get_view_name_included()
        try:
            self.includedViewName = []
            data = self.connects.get_data_operation(sql)
            if not data.empty:
                for item in data.iloc:
                    self.includedViewName.append(item.viewname)
        except:
            raise

    def get_show_function_with_column(self, function):
        listName = []
        for item in self.functionList:
            if (
                function.column.typeColumn in item.columnTypes
                or "VAR" in item.columnTypes
            ):
                listName.append(
                    item.get_show_by_column_name(function.column.columnName)
                )
        if len(listName) > 0:
            return [""] + listName
        else:
            return listName

    def get_function_with_show_name(self, funShowName, colName):
        for item in self.functionList:
            if item.get_show_by_column_name(colName) == funShowName:
                return copy.deepcopy(item)

    def get_function_with_no(self, funcNo):
        for item in self.functionList:
            if item.funNo == funcNo:
                return copy.deepcopy(item)

    def get_show_calculation(self, colName):
        listName = []
        for item in self.calculationList:
            listName.append(item.get_name_show_with_column(colName))
        if len(listName) > 0:
            return [""] + listName
        else:
            return listName

    def get_calculation_with_key(self, colName, calShow):
        for item in self.calculationList:
            if item.get_name_show_with_column(colName) == calShow:
                return copy.deepcopy(item)

    def get_calculation_with_no(self, calNo):
        for item in self.calculationList:
            if item.calNo == calNo:
                return copy.deepcopy(item)

    def check_view_name(self, viewName):
        if viewName in self.viewNameAll:
            return True
        else:
            return False

    def loaddata_30line_dataset(self, table):
        sql = self.sentence.sql_get_30line_dataset(table)
        try:
            data = self.connects.get_data_operation(sql)
            data = data.replace({pd.NA: None})
            data = data.replace({pd.NaT: None})
            data = data.fillna("")
            if data.empty:
                raise ValueError(
                    "Do not find data with table {0}".format(table)
                )
            else:
                return data
        except:
            raise

    def get_dataset_by_no(self, datasetNo):
        for item in self.datasetList:
            if item.datasetNo == datasetNo:
                return copy.deepcopy(item)

    def loaddata_view_release(self):
        self.actionViewList = []
        sql = self.sentence.sql_load_view_release(
            self.user.permission, self.user.group, self.user.userno
        )
        try:
            data = self.connects.get_data_operation(sql)
            for item in data.iloc:
                vAction = ModuleViewAction.ViewAction()
                vAction.set_data(item)
                self.actionViewList.append(vAction)
        except:
            raise

    def get_all_view_release(self):
        listName = []
        for item in self.actionViewList:
            listName.append(item.viewName)
        if len(listName) > 0:
            return [""] + listName
        else:
            return listName

    def get_view_release_by_name(self, vName):
        for item in self.actionViewList:
            if item.viewName == vName:
                return copy.deepcopy(item)

    def loaddata_view_run(self):
        self.runViewList = []
        sql = self.sentence.sql_load_view_run(
            self.user.permission, self.user.group, self.user.userno
        )
        try:
            data = self.connects.get_data_operation(sql)
            for item in data.iloc:
                vAction = ModuleViewAction.ViewAction()
                vAction.set_data(item)
                self.runViewList.append(vAction)
        except:
            raise

    def get_all_view_run(self):
        listName = []
        for item in self.runViewList:
            listName.append(item.viewName)
        if len(listName) > 0:
            return [""] + listName
        else:
            return listName

    def get_view_run_by_name(self, vName):
        for item in self.runViewList:
            if item.viewName == vName:
                return copy.deepcopy(item)

    def run(self, sql):
        try:
            data = self.connects.get_data_operation(sql)
            data = data.replace({pd.NA: None})
            data = data.replace({pd.NaT: None})
            data = data.fillna("")
            self.dataRun = data
        except:
            raise

    def exportToFile(self, res=tuple()):
        try:
            linkfile = str(res[0])
            if len(self.dataRun) > 0:
                data_export = copy.deepcopy(self.dataRun)
                for col in data_export.columns:
                    data_export[col] = data_export[col].astype(str)
                if str(linkfile[::-1][:5]) == "xslx.":
                    data_export.to_excel(
                        linkfile,
                        index=False,
                        sheet_name="DataExport",
                        engine="xlsxwriter",
                    )
                else:
                    data_export.to_csv(
                        linkfile, index=False, encoding="utf-8", sep="\t"
                    )
        except:
            raise

    def exportToFileData(self, data, res=tuple()):
        try:
            linkfile = str(res[0])
            if len(data) > 0:
                data_export = copy.deepcopy(data)
                for col in data_export.columns:
                    data_export[col] = data_export[col].astype(str)
                if str(linkfile[::-1][:5]) == "xslx.":
                    data_export.to_excel(
                        linkfile,
                        index=False,
                        sheet_name="DataExport",
                        engine="xlsxwriter",
                    )
                else:
                    data_export.to_csv(
                        linkfile, index=False, encoding="utf-8", sep="\t"
                    )
        except:
            raise

    def get_list_dept(self):
        sql = self.sentence.sql_get_dept()
        try:
            data = self.connects.get_data_operation(sql)
            data = data.replace({pd.NA: None})
            data = data.replace({pd.NaT: None})
            data = data.fillna("")
            if data.empty:
                raise ValueError("Do not find dept")
            else:
                self.depts = []
                for item in data.iloc:
                    self.depts.append(item.to_list())
        except:
            raise

    def get_dept_name(self):
        listName = []
        for item in self.depts:
            listName.append(item[1])
        if len(listName) > 0:
            return [""] + listName
        else:
            return listName

    def get_user_by_name(self, userName):
        sql = self.sentence.sql_user_search(userName)
        try:
            data = self.connects.get_data_operation(sql)
            data = data.replace({pd.NA: None})
            data = data.replace({pd.NaT: None})
            data = data.fillna("")
            if data.empty:
                raise ValueError("Do not found user".format(userName))
            else:
                user = ModuleUsers.Users(self.connects)
                user.set_user(data.iloc[0])
                return user
        except:
            raise

    def get_view_manual_by_search(self, viewName):
        sql = self.sentence.sql_get_view_manual_all_name(viewName)
        try:
            data = self.connects.get_data_operation(sql)
            if data.empty:
                raise ValueError(
                    "Not found view with name {0}".format(viewName)
                )
            else:
                return data
        except:
            raise

    def loaddata_view_manual(self, viewName):
        sql = self.sentence.sql_get_view_manual_by_name(viewName)
        try:
            data = self.connects.get_data_operation(sql)
            if data.empty:
                raise ValueError(
                    "Not found view with name {0}".format(viewName)
                )
            elif len(data) != 1:
                raise ValueError("View duplicate. Please check view name.")
            else:
                data = data.replace({pd.NA: None})
                data = data.replace({pd.NaT: None})
                data = data.fillna("")
                return data
        except:
            raise
