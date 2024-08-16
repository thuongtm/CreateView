# This Python file uses the following encoding: utf-8


class Columns:
    def __init__(self, column=None):
        self.datasetNo = int()
        self.viewNo = int()
        self.lines = int()
        self.columnName = str()
        self.columnNameNew = str()
        self.typeColumn = str()
        self.isAgg = False
        self.numberUse = 0
        self.isColNew = False
        self.isSelected = False
        # 0 - column load from DB
        # 1 - column add from function
        # 2 - column merge None aggreate -> không cho merge tiếp
        # 3 - column merge True aggreate (1 or 2) --> không cho merge tiếp
        self.level = 0

        if not column == None:
            self.datasetNo = column.datasetNo
            self.lines = column.lines
            self.columnName = column.columnName
            self.columnNameNew = column.columnNameNew
            self.typeColumn = column.typeColumn
            self.isAgg = column.isAgg
            self.numberUse = column.numberUse
            self.isColNew = column.isColNew
            self.isSelected = column.isSelected
            self.level = column.level

    def set_line(self, index):
        self.lines = index

    def set_view_no(self, index):
        self.viewNo = index

    def set_column(self, column):
        try:
            self.datasetNo = int(column.datasetno)
            self.lines = int(column.lines)
            self.columnName = column.columnnames
            self.typeColumn = column.columntypes
        except:
            raise

    def increase_use(self):
        self.numberUse += 1

    def decrease_use(self):
        if self.numberUse > 0:
            self.numberUse -= 1

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Columns):
            return self.columnName == value.columnName
        else:
            return False

    def set_name_new(self, name):
        self.columnNameNew = name

    def set_selected(self, status):
        self.isSelected = status

    def sql_name(self):
        if self.columnName == self.columnNameNew or self.columnNameNew == "":
            return self.columnName
        else:
            return (
                " "
                + self.columnName
                + " as "
                + "{0}".format(self.columnNameNew)
            )

    def sql_name_as(self):
        if self.columnNameNew == "":
            return self.columnName
        else:
            return self.columnNameNew

    def sql_insert(self):
        listInsert = [
            self.viewNo,
            self.lines,
            self.columnName,
            self.columnNameNew,
            self.typeColumn,
        ]
        return listInsert
