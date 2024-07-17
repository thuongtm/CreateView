# This Python file uses the following encoding: utf-8
import ModuleColumns, Sentences
from datetime import datetime


class Calculations:
    def __init__(self):
        self.calNo = int()
        self.calNames = str()
        self.calShow = str()
        self.numbers = int()
        self.isMany = False
        self.valueTypes = []
        self.viewNo = int()
        self.lines = int()

        self.columns = ModuleColumns.Columns()
        self.isColumn = False
        self.isUpdate = False
        self.value1 = str()
        self.value2 = str()
        self.isAgg = False  # --> classify Where or having
        self.level = int()
        self.relation = str()
        self.relationWith = str()
        self.isCal = False
        self.calKeyOld = str()
        self.sentence = Sentences.Sentences()
        self.valueBasic1 = str()
        self.valueBasic2 = str()

    def set_line(self, index):
        self.lines = index

    def set_view_no(self, index):
        self.viewNo = index

    def sql_insert(self):
        listFilter = [
            int(self.viewNo),
            int(self.lines),
            self.get_str_isagg(),
            self.calNo,
            self.calNames,
            self.columns.columnName,
            str(self.valueBasic1),
            str(self.valueBasic2),
            int(self.level),
            self.relation,
            self.relationWith,
        ]
        return listFilter

    def setbasic_calculation(self, cal):
        try:
            self.calNo = int(cal.calno)
            self.calNames = str(cal.calnames)
            self.calShow = str(cal.calshows)
            self.numbers = int(cal.numbervalues)
            self.set_ismany(cal.ismany)
            self.set_value_type(cal.valuetypes)
        except:
            raise

    def get_str_isagg(self):
        if self.isAgg:
            return "True"
        else:
            return "False"

    def get_key_cal(self):
        return self.calNames.replace("{column}", self.columns.columnName)

    def set_ismany(self, status):
        if status == "True":
            self.isMany = True
        else:
            self.isMany = False

    def get_str_ismany(self):
        if self.isMany:
            return "True"
        else:
            return "False"

    def set_value_type(self, value):
        if value.find(","):
            self.valueTypes = value.split(",")
        else:
            self.valueTypes.append(value)

    def get_name_show_with_column(self, colName):
        return self.calShow.replace("{column}", colName)

    def set_column(self, column):
        self.columns = column
        self.isColumn = True
        self.isAgg = self.columns.isAgg

    def set_calculation(self, cal):
        self.calNo = cal.calNo
        self.calNames = cal.calNames
        self.calShow = cal.calShow
        self.numbers = cal.numbers
        self.isMany = cal.isMany
        self.valueTypes = cal.valueTypes
        self.isCal = True

    def set_value(self, value1, value2):
        try:
            if not self.isMany:
                if self.numbers >= 2:
                    if self.check_value(value1):
                        self.value1 = self.get_value_with_type(value1)
                        self.valueBasic1 = value1
                if self.numbers == 3:
                    if self.check_value(value2):
                        self.value2 = self.get_value_with_type(value2)
                        self.valueBasic2 = value2
            else:
                listValue = []
                if value1.find(","):
                    for item in value1.split(","):
                        if self.check_value(item):
                            listValue.append(self.get_value_with_type(item))
                else:
                    listValue.append(self.get_value_with_type(value1))
                self.value1 = ",".join(listValue)
                self.valueBasic1 = value1
        except:
            raise

    def set_relation(self, rel):
        self.relation = rel

    def set_with_cal(self, calName):
        self.relationWith = calName

    def check_value(self, value):
        isCheck = False
        if self.columns.typeColumn.upper() in self.sentence.type_number():
            try:
                x = int(value)
                isCheck = True
            except:
                raise
        elif self.columns.typeColumn.upper() in self.sentence.type_str():
            try:
                x = str(value)
                isCheck = True
            except:
                raise
        elif self.columns.typeColumn.upper() in self.sentence.type_date():
            try:
                x = datetime.strptime(value, "%d/%m/%Y")
                isCheck = True
            except:
                raise
        return isCheck

    def get_value_with_type(self, value):
        if self.columns.typeColumn in self.sentence.type_number():
            if value != "":
                return int(value)
            else:
                return "''"
        elif self.columns.typeColumn in self.sentence.type_date():
            if value != "":
                return "To_date('{0}','dd/mm/yyyy')".format(value)
            else:
                return "''"
        else:
            return "'{0}'".format(value)

    def set_level(self, level):
        self.level = level

    def set_update(self, status):
        self.isUpdate = status
        if self.isUpdate:
            self.calKeyOld = self.get_key_cal()
        else:
            self.calKeyOld = str()

    def in_item_sql(self):
        return [
            self.level,
            self.relation,
            self.relationWith,
            self.get_sql(),
        ]

    def get_sql(self):
        if self.columns.typeColumn in self.sentence.type_date():
            sql = self.calNames.replace(
                "{column}", "Trunc(" + self.columns.columnName + ")"
            )
        else:
            sql = self.calNames.replace("{column}", self.columns.columnName)
        if self.numbers >= 2:
            sql = sql.replace("{value1}", str(self.value1))
        if self.numbers == 3:
            sql = sql.replace("{value2}", str(self.value2))
        return sql
