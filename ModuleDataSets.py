# This Python file uses the following encoding: utf-8
import Sentences, Connects, ModuleColumns


class DataSets:
    def __init__(self, connects):
        self.datasetNo = int()
        self.datasetName = str()
        self.datasetTable = str()
        self.datasetIP = str()
        self.ports = str()
        self.usernames = str()
        self.passwords = str()
        self.datasetDB = str()
        self.groups = str()
        self.depts = str()
        self.createDate = str()
        self.lastUpdate = str()
        self.userNo1 = int()
        self.columnList = []
        self.sentence = Sentences.Sentences()
        self.connects = Connects.Connects(connects)

    def set_no(self, index):
        self.datasetNo = index

    def get_connect_string(self):
        return f"oracle+oracledb://{self.usernames}:{self.passwords}@{self.datasetIP}:{self.ports}/?service_name={self.datasetDB}"

    def get_create_date(self):
        return self.createDate

    def get_last_update(self):
        return self.lastUpdate

    def set_dataset(self, dataset):
        try:
            self.datasetNo = int(dataset.datasetno)
            self.datasetName = dataset.datasetname
            self.datasetTable = dataset.datasettable
            self.datasetIP = dataset.datasetip
            self.ports = dataset.ports
            self.usernames = dataset.usenames
            self.passwords = dataset.password
            self.datasetDB = dataset.datasetdb
            self.groups = dataset.groups
            self.depts = dataset.depts
            self.createDate = dataset.createdate
            self.lastUpdate = dataset.lastupdate
            self.userNo1 = int(dataset.userno1)
        except:
            raise

    def set_column_list(self):
        sql = self.sentence.sql_get_column_of_dataset(self.datasetNo)
        try:
            dataColumn = self.connects.get_data_operation(sql)
            if dataColumn.empty:
                raise ValueError("Do not found Column of DataSet")
            else:
                for column in dataColumn.iloc:
                    col = ModuleColumns.Columns()
                    col.set_column(column=column)
                    self.columnList.append(col)
        except:
            raise

    def get_name_column(self):
        listName = []
        for item in self.columnList:
            listName.append(item.columnName)
        return sorted(listName)

    def add_column_new(self, function):
        col = ModuleColumns.Columns()
        col.datasetNo = self.datasetNo
        col.lines = 0
        col.columnName = function.get_column_name()
        col.columnNameNew = function.get_column_name_with_auto()
        col.typeColumn = function.funTypes
        col.isAgg = function.isAgg
        col.numberUse = 0
        col.isColNew = True
        col.isSelected = False
        self.columnList.append(col)

    def increase_use(self, column):
        for item in self.columnList:
            if item.columnName == column.columnName:
                item.increase_use()
                break

    def decrease_use(self, column):
        for item in self.columnList:
            if item.columnName == column.columnName:
                item.decrease_use()
                break
