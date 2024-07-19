# This Python file uses the following encoding: utf-8


class Sentences:
    def __init__(self):
        pass

    # sql check login of user and password
    def sql_login_check(self, user):
        sql = """select * from TUSERS where USERS = '{0}' and status = 1""".format(
            user
        )
        return sql

    # sql get all dataset in database
    def sql_get_dataset_all(self, permiss, groups):
        if permiss == "ALL":
            sql = """select * from TDataset"""
        else:
            sql = """select * from TDataset"""
            """
            sql = "select * from TDataset where Group = '{0}'".format(
                groups
            )"""

        return sql

    # get all column of dataset {no = index}
    def sql_get_column_of_dataset(self, index):
        sql = """SELECT * FROM TDatasetLine where DatasetNo = '{0}'""".format(
            index
        )
        return sql

    # get ID new of view
    def sql_get_view_new_id(self):
        sql = """SELECT nvl(max(viewno), 0) + 1 as idnew from TViews"""
        return sql

    # get ViewName by permission
    def sql_get_view_name_all(self, permiss, groups, userno):
        sql = "SELECT ViewNo, ViewName  FROM TViews"
        return sql

    def sql_get_view_search(self, permiss, groups, userno):
        sql = "SELECT ViewNo, ViewName  FROM TViews where viewstatus <> 3"
        return sql

    def sql_get_view_name_release(self, permiss, groups, userno):
        sql = "SELECT ViewNo, ViewName  FROM TViews where indb = 2 and viewstatus <> 3"
        return sql

    def header_table_sort(self):
        return ["Action", "Column Name", "Type"]

    def sql_get_function_all(self):
        sql = "SELECT * FROM TFunctions"
        return sql

    def header_table_column_new(self):
        return [
            "Action",
            "Column Name",
            "Function",
            "Value1",
            "Value2",
            "Is Aggregate",
        ]

    def sql_get_calculation_all(self):
        sql = "SELECT * from TCALCULATIONS"
        return sql

    def header_table_filter(self):
        return [
            "Action",
            "Column Name",
            "Calculation",
            "Value1",
            "Value2",
            "Relation",
            "Level",
            "With Calculation",
            "Is Aggregate",
        ]

    def type_str(self):
        return ["NVARCHAR2", "VARCHAR2", "TEXT"]

    def type_number(self):
        return ["NUMBER", "INT", "DECIMAL"]

    def type_date(self):
        return ["DATE", "TIMESTAMP"]

    def sql_get_30line_dataset(self, table):
        sql = "SELECT * from {0} where rownum <= 30".format(table)
        return sql

    def sql_load_view_by_no(self, viewNo):
        sql = """SELECT  *
                FROM    TViews
                where   VIEWNO = {0}""".format(
            viewNo
        )
        return sql

    def sql_load_columnnew(self, viewNo):
        sql = "SELECT  * from TVIEW2 where VIEWNO = {0} and STATUS = 1".format(
            viewNo
        )
        return sql

    def sql_load_column_select(self, viewNo):
        sql = "SELECT  * from TVIEW1 where VIEWNO = {0} and STATUS = 1".format(
            viewNo
        )
        return sql

    def sql_load_filter(self, viewNo):
        sql = "SELECT  * from TVIEW4 where VIEWNO = {0} and STATUS = 1".format(
            viewNo
        )
        return sql

    def sql_load_sort(self, viewNo):
        sql = "SELECT  * from TVIEW3 where VIEWNO = {0} and STATUS = 1".format(
            viewNo
        )
        return sql

    def sql_load_view_release(self, permiss, groups, userno):
        sql = """SELECT t1.viewno, t1.viewname, t1.viewstatus, t1.releasestatus, t1.datasetno, t2.datasetname, t2.datasettable, t1.indb FROM Tviews t1 inner join Tdataset t2 on t1.datasetno = t2.datasetno where t1.viewstatus <> 3 or t1.indb = 2"""
        return sql

    def sql_load_view_run(self, permiss, groups, userno):
        sql = """SELECT t1.viewno, t1.viewname, t1.viewstatus, t1.releasestatus, t1.datasetno, t2.datasetname, t2.datasettable, t1.indb FROM Tviews t1 inner join Tdataset t2 on t1.datasetno = t2.datasetno where t1.viewstatus <> 3"""
        return sql

    def sql_get_view_name_included(self):
        sql = """SELECT ViewName From tviews where INCLUDEDVIEW is null and indb = 2 and viewstatus <> 3"""
        return sql

    def header_included_table(self):
        listHeader = ["Action", "ViewName", "Column", "TypeConnect"]
        return listHeader
