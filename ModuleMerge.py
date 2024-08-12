# This Python file uses the following encoding: utf-8
import ModuleColumns


class Merge:
    def __init__(self):
        self.viewNo = int()
        self.lines = int()
        self.operNo = int()
        self.operName = str()
        self.operShow = str()
        self.numberPara = int()
        self.autoName = str()
        self.valueType = int()  # 1 - number, 2 - time, 3 - str

        self.column1 = ModuleColumns.Columns()
        self.column2 = ModuleColumns.Columns()
        self.isUse = 0
        self.isOper = False
        self.isColumn1 = False
        self.isColumn2 = False
        self.column1Name = str()
        self.column2Name = str()
        self.agg = False
        self.typeReturn = str()

    def set_agg(self, data):
        if data == "True":
            self.agg = True
        else:
            self.agg = False

    def set_view_no(self, index):
        self.viewNo = index

    def set_line(self, index):
        self.lines = index

    def set_data(self, data):
        try:
            self.operNo = int(data.operno)
            self.operName = data.opername
            self.operShow = data.opershow
            self.numberPara = int(data.numberpara)
            self.autoName = data.autoname
            self.valueType = int(data.valuetypes)
        except:
            raise

    def set_operation(self, oper):
        self.operNo = oper.operNo
        self.operName = oper.operName
        self.operShow = oper.operShow
        self.numberPara = oper.numberPara
        self.autoName = oper.autoName
        self.valueType = oper.valueType
        self.isOper = True

    def set_column1(self, column=ModuleColumns.Columns()):
        self.column1 = column
        if column.columnName == str():
            self.isColumn1 = False
        else:
            self.isColumn1 = True

    def set_column2(self, column=ModuleColumns.Columns()):
        self.column2 = column
        if column.columnName == str():
            self.isColumn2 = False
        else:
            self.isColumn2 = True

    def get_bool_add(self):
        return self.isColumn1 and self.isColumn2

    def get_key(self):
        return self.operName.replace(
            "{column1}", self.column1.columnName
        ).replace("{column2}", self.column2.columnName)

    def get_key_load(self):
        return self.operName.replace("{column1}", self.column1Name).replace(
            "{column2}", self.column2Name
        )

    def get_auto_key(self):
        return (
            self.autoName
            + "_"
            + self.column1.columnName.replace("(", "").replace(")", "")
            + "_"
            + self.column2.columnName.replace("(", "").replace(")", "")
        )

    def get_auto_key_load(self):
        return (
            self.autoName
            + "_"
            + self.column1Name.replace("(", "").replace(")", "")
            + "_"
            + self.column2Name.replace("(", "").replace(")", "")
        )

    def get_isagg(self):
        return self.column1.isAgg or self.column2.isAgg

    def get_type_return(self):
        if self.valueType == 1:
            return "NUMBER"
        else:
            return "NVARCHAR2"

    def sql_insert(self):
        return [
            self.viewNo,
            self.lines,
            self.operShow,
            self.column1.columnName,
            self.column2.columnName,
            str(self.get_isagg()),
            self.get_type_return(),
        ]

    def set_load_data(self, data, operList):
        try:
            self.viewNo = int(data.viewno)
            self.lines = int(data.lines)
            for item in operList:
                if data.operation == item.operShow:
                    self.set_operation(item)
                    break
            self.column1Name = data.column1
            self.column2Name = data.column2
            self.set_agg(data.isagg)
            self.typeReturn = data.typereturn
        except:
            raise

    def updateColumn(self, column1, column2):
        self.column1 = column1
        self.column2 = column2
