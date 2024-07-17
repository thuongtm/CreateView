# This Python file uses the following encoding: utf-8
import ModuleColumns
from datetime import datetime


class Functions:
    def __init__(self):
        self.funNo = int()
        self.lines = int()
        self.viewNo = int()
        self.funNames = str()
        self.funShows = str()
        self.numbers = int()
        self.isAgg = False
        self.funTypes = str()
        self.columnTypes = []
        self.valueTypes = []
        self.autoName = str()

        self.column = ModuleColumns.Columns()
        self.value1 = str()
        self.value2 = str()
        self.isUpdate = False
        self.isColumn = False
        self.isFunction = False
        self.funKeyOld = str()
        self.numberUse = 0
        self.valueBasic1 = str()
        self.valueBasic2 = str()

    def sql_insert(self):
        listParameter = [
            self.viewNo,
            self.lines,
            self.funNo,
            self.funNames,
            self.column.columnName,
            self.value1,
            self.value2,
        ]
        return listParameter

    def set_view_no(self, index):
        self.viewNo = index

    def set_column(self, column):
        self.column = column
        self.isColumn = True
        if not self.isAgg:
            self.isAgg = column.isAgg

    def set_line(self, index):
        self.lines = index

    def set_update(self, status):
        self.isUpdate = status
        if self.isUpdate:
            self.funKeyOld = self.get_column_name()
        else:
            self.funKeyOld = str()

    def set_isagg(self, status):
        if str.upper(status) == "TRUE":
            self.isAgg = True
        else:
            self.isAgg = False

    def get_str_isagg(self):
        if self.isAgg:
            return "True"
        else:
            return "False"

    def set_column_type(self, funtype):
        if funtype.find(","):
            self.columnTypes = funtype.split(",")
        else:
            self.columnTypes.append(funtype)

    def set_value_type(self, valuetype):
        if valuetype.find(","):
            self.valueTypes = valuetype.split(",")
        else:
            self.valueTypes.append(valuetype)

    def setbasic_function(self, function):
        try:
            self.funNo = int(function.funno)
            self.funNames = str(function.funnames)
            self.funShows = str(function.funshows)
            self.numbers = int(function.numberpara)
            self.set_isagg(function.isaggregates)
            self.funTypes = str(function.funtypes)
            self.set_column_type(str(function.columntypes))
            self.autoName = str(function.autonames)
            self.set_value_type(function.valuetypes)
        except:
            raise

    def get_show_by_column_name(self, columnName):
        return self.funShows.replace("{column}", columnName)

    def set_funtion(self, function):
        self.funNo = function.funNo
        self.funNames = function.funNames
        self.funShows = function.funShows
        self.numbers = function.numbers
        self.isAgg = function.isAgg
        self.funTypes = function.funTypes
        self.columnTypes = function.columnTypes
        self.autoName = function.autoName
        self.valueTypes = function.valueTypes
        self.isFunction = True
        self.set_update(False)

    def set_value(self, value1, value2):
        try:
            if self.numbers >= 2:
                if self.check_value(value1):
                    self.value1 = value1
                    self.valueBasic1 = value1
                else:
                    raise ValueError("{0} Incorrect data type.".format(value1))
            if self.numbers == 3:
                if self.check_value(value2):
                    self.value2 = value2
                    self.valueBasic2 = value2
                else:
                    raise ValueError("{0} Incorrect data type.".format(value2))
        except:
            raise

    def check_value(self, value):
        if "VAR" in self.valueTypes:
            return True
        else:
            isCheck = False
            if "NUMBER" in self.valueTypes:
                try:
                    x = int(value)
                    isCheck = True
                except:
                    raise
            elif "NVARCHAR2" in self.valueTypes:
                try:
                    x = str(value)
                    isCheck = True
                except:
                    raise
            elif "DATE" in self.valueTypes:
                try:
                    a = datetime.strptime(value, "%d/%m/%Y")
                    isCheck = True
                except:
                    raise
        return isCheck

    def get_column_name(self):
        name = self.funNames.replace("{column}", self.column.columnName)
        if self.numbers >= 2:
            name = name.replace(
                "{value1}", self.get_value_with_type(self.value1)
            )
        if self.numbers == 3:
            name = name.replace(
                "{value2}", self.get_value_with_type(self.value2)
            )
        return name

    def get_value_with_type(self, value):
        if "NUMBER" in self.columnTypes:
            if value != "":
                return int(value)
            else:
                return "''"
        elif "DATE" in self.columnTypes:
            if value != "":
                return "Todate('{0}','dd/mm/yyyy')".format(value)
            else:
                return "''"
        else:
            return "'{0}'".format(value)

    def get_column_name_with_auto(self):
        return "{0}_{1}".format(self.autoName, self.column.columnName)

    def increase_use(self):
        self.numberUse += 1

    def decrease_use(self):
        if self.numberUse > 0:
            self.numberUse -= 1
        else:
            self.numberUse = 0
