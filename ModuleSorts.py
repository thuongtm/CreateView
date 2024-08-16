# This Python file uses the following encoding: utf-8
import ModuleColumns


class Sorts:
    def __init__(self):
        self.viewno = int()
        self.columns = ModuleColumns.Columns()
        self.isAgg = False
        self.types = "ASC"
        self.isUpdate = False
        self.isColumn = False
        self.lines = int()

    def set_line(self, index):
        self.lines = index

    def set_view_no(self, index):
        self.viewno = index

    def set_column(self, column):
        self.columns = column
        self.isAgg = column.isAgg
        self.isColumn = True

    def set_type(self, status):
        if status:  # --> ASC
            self.types = "ASC"
        else:
            self.types = "DESC"

    def set_type_str(self, typ):
        self.types = typ

    def get_bool_type(self):
        return self.types == "ASC"

    def set_update(self, status):
        self.isUpdate = status

    def sql_name(self):
        return self.columns.columnName + " " + self.types

    def sql_insert(self):
        listSort = [
            self.viewno,
            self.lines,
            self.columns.columnName,
            self.types,
        ]
        return listSort
