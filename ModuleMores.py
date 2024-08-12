# This Python file uses the following encoding: utf-8


class Mores:
    def __init__(self):
        self.viewNo = int()
        self.lines = int()
        self.typeMore = str()
        self.viewConnect = str()
        self.columnConnect = str()

        self.isUpdate = False

    def update(self, more):
        self.viewNo = more.viewNo
        self.lines = more.lines
        self.typeMore = more.typeMore
        self.viewConnect = more.viewConnect
        self.columnConnect = more.columnConnect

    def set_type(self, typ):
        self.typeMore = typ

    def get_int_type(self):
        if self.typeMore == "Excluded":
            return 1
        elif self.typeMore == "Included":
            return 2
        else:
            return 0

    def set_view_no(self, viewNo):
        self.viewNo = viewNo

    def set_line(self, lines):
        self.lines = lines

    def set_update(self, status):
        self.isUpdate = status

    def set_view(self, viewName, ColumnName):
        if self.get_int_type() == 1 and ColumnName.strip() == "":
            raise ValueError("Column is null. Please select column")
        else:
            self.viewConnect = viewName
            self.columnConnect = ColumnName

    def get_sql(self):
        if self.get_int_type() == 1:
            return "{0} not in (Select {1} From {2})".format(
                self.columnConnect, self.columnConnect, self.viewConnect
            )
        elif self.get_int_type() == 2:
            return "UNION Select * from {0}".format(self.viewConnect)
        else:
            return ""

    def sql_insert(self):
        return [
            self.viewNo,
            self.lines,
            self.viewConnect,
            self.typeMore,
            self.columnConnect,
        ]
