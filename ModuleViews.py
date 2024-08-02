# This Python file uses the following encoding: utf-8
import Sentences, ModuleDataSets, ModuleCalculations, ModuleSorts
import ModuleFunctions, ModuleWriteLogs, Connects, ModuleUsers
import copy
import pandas as pd
import ModuleMores


class Views:
    def __init__(self, connects, users):
        self.connects = Connects.Connects(connects)
        self.user = ModuleUsers.Users(connects)
        self.user.assign(users)
        self.viewNo = int()
        self.viewName = str()
        self.rowSelects = int()
        self.duplicates = False
        self.createDate = str()
        self.lastUpdate = str()
        self.user1 = int()
        self.user2 = int()
        self.viewStatus = int()
        self.includedType = str()
        self.includedView = str()
        self.dataset = ModuleDataSets.DataSets(connects)
        self.columnSelected = []
        self.sortSelect = []
        self.columnNewList = []
        self.whereSelected = []
        self.havingSelected = []
        self.moreSelected = []
        self.sentence = Sentences.Sentences()
        self.isUpdate = False
        self.whereLevel = 0
        self.havingLevel = 0
        self.isDataset = False  # check view existed dataset
        self.isRelease = False  # status release
        self.isDataRelease = False
        self.isInDB = False  # check release
        self.writeLog = ModuleWriteLogs.WriteLogs(
            self.connects
        )  # writelog transaction

    def get_str_view_no(self):
        if self.viewNo == 0:
            return ""
        else:
            return str(self.viewNo)

    def set_view(self, view):
        try:
            self.rowSelects = int(view.rowselects)
            self.set_duplicate(view.duplicates)
            self.createDate = view.createdate
            self.lastUpdate = view.lastupdate
            self.user1 = int(view.user1)
            self.viewStatus = int(view.viewstatus)
            self.includedType = view.includedtype
            self.includedView = view.includedview
            self.set_release(view.releasestatus)
            self.set_indb(view.indb)
        except:
            raise

    def set_indb(self, index):
        if index == 1:
            self.isInDB = False
        else:
            self.isInDB = True

    def get_str_indb(self):
        if self.isInDB:
            return "Yes"
        else:
            return "No"

    def set_release(self, index):
        if index == 1:
            self.isRelease = False
        else:
            self.isRelease = True

    def get_str_release(self):
        if self.isRelease:
            return "Release"
        else:
            return "Pending"

    def set_is_update(self, status):
        self.isUpdate = status
        if not status:
            self.viewName = str()
            self.createDate = str()

    def get_create_date(self):
        return copy.deepcopy(str(self.createDate))

    def get_str_rowtop(self):
        if self.rowSelects == 0:
            return ""
        else:
            return str(self.rowSelects)

    def get_duplicate(self):
        if self.duplicates:
            return "True"
        else:
            return "False"

    def set_duplicate(self, status):
        if status == "True":
            self.duplicates = True
        else:
            self.duplicates = False

    def set_view_no(self, number):
        self.viewNo = number

    def set_dataset(self, dataset):
        self.dataset = dataset
        if self.dataset.datasetNo != None:
            self.isDataset = True
        else:
            self.isDataset = False

    def get_name_column_dataset(self):
        return self.dataset.get_name_column()

    def get_column_not_select(self):
        listNew = []
        isCheck = False
        for item in self.dataset.columnList:
            for items in self.columnSelected:
                if item.columnName == items.columnName:
                    isCheck = True
                    break
            if not isCheck:
                listNew.append(copy.deepcopy(item))
            else:
                isCheck = False
        return listNew

    def get_name_column_selected(self):
        nameList = []
        for item in self.columnSelected:
            nameList.append(item.columnName)
        return nameList

    # get sql sentence of view -> plainText
    def get_sql_sentence(self):
        sql = ""
        if len(self.sql_select()) > 0:
            sql = "SELECT {0}".format(self.sql_select())
        if len(self.dataset.datasetTable) > 0:
            sql = "{0} FROM {1}".format(sql, self.dataset.datasetTable)
        if len(self.sql_where()) > 0:
            sql = "{0} WHERE {1}".format(sql, self.sql_where())
        if len(self.sql_groupby()) > 0:
            sql = "{0} GROUP BY {1}".format(sql, self.sql_groupby())
        if len(self.sql_having()) > 0:
            sql = "{0} HAVING {1}".format(sql, self.sql_having())
        if len(self.sql_sort()) > 0:
            sql = "{0} ORDER BY {1}".format(sql, self.sql_sort())
        if len(self.sql_more()) > 0:
            sql = "{0} {1}".format(sql, self.sql_more())
        return sql

    def get_name_column_not_select(self):
        return sorted(
            list(
                set(self.get_name_column_selected())
                ^ set(self.dataset.get_name_column())
            )
        )

    def get_column_not_by_name(self, name):
        for item in self.get_column_not_select():
            if item.columnName == name:
                return copy.deepcopy(item)

    def get_column_selected_by_name(self, name):
        for item in self.columnSelected:
            if item.columnName == name:
                return copy.deepcopy(item)

    def set_select_column_all(self):
        for item in self.dataset.columnList:
            if item.columnName not in self.get_name_column_selected():
                self.columnSelected.append(copy.deepcopy(item))
                self.dataset.increase_use(item)

    def set_select_column_one(self, column):
        for item in self.columnSelected:
            if item.columnName == column.columnName:
                raise ValueError(
                    "Column : {0} is selected. Do not add.".format(
                        column.columnName
                    )
                )
        self.columnSelected.append(copy.deepcopy(column))
        self.dataset.increase_use(column)

    def set_remove_column_all(self):
        for item in self.columnSelected:
            self.dataset.decrease_use(item)
        self.columnSelected = []

    def set_remove_column_one(self, column):
        for item in self.columnSelected:
            if item.columnName == column.columnName:
                self.columnSelected.remove(column)
                self.dataset.decrease_use(column)
                break

    def check_column_name_new(self, name):
        # check namecolum in dataset
        for item in self.dataset.columnList:
            if str.upper(item.columnName) == str.upper(name):
                return True
        # check name new in selected
        for item in self.columnSelected:
            if str.upper(item.columnNameNew) == str.upper(name):
                return True
        return False

    def get_column_by_name(self, name):
        for item in self.dataset.columnList:
            if item.columnName == name:
                return copy.deepcopy(item)

    def update_column_selected(self, column):
        for item in self.columnSelected:
            if item.columnName == column.columnName:
                item.columnNameNew = column.columnNameNew
                break

    def add_sort(self, sort):
        for item in self.sortSelect:
            if item.columns.columnName == sort.columns.columnName:
                raise ValueError("Column is exist in list Sort")
        self.sortSelect.append(sort)
        self.dataset.increase_use(sort.columns)

    def delete_sort_by_column_name(self, colName):
        for item in self.sortSelect:
            if item.columns.columnName == colName:
                self.sortSelect.remove(item)
                self.dataset.decrease_use(item.columns)
                break

    def get_sort_by_column_name(self, colName):
        for item in self.sortSelect:
            if item.columns.columnName == colName:
                return copy.deepcopy(item)

    def update_sort(self, sort):
        for item in self.sortSelect:
            if item.columns.columnName == sort.columns.columnName:
                item.types = sort.types
                return

    def add_column_new(self, function):
        isCheck = True
        for item in self.columnNewList:
            if (
                function.column.columnName == item.column.columnName
                and function.funNo == item.funNo
            ):
                isCheck = False
        if isCheck:
            self.columnNewList.append(function)
            self.dataset.add_column_new(function)
            self.dataset.increase_use(function.column)
        else:
            raise ValueError(
                "Column: {0} and Function No: {1} is exist.".format(
                    function.column.columnName, function.funNo
                )
            )

    def get_function_by_key(self, colName, funShow):
        for item in self.columnNewList:
            if (
                item.column.columnName == colName
                and item.get_show_by_column_name(colName) == funShow
            ):
                return copy.deepcopy(item)

    def update_column_new(self, function):
        if self.check_use_function(function):
            for item in self.columnNewList:
                if item.get_column_name() == function.funKeyOld:
                    item.value1 = function.value1
                    item.value2 = function.value2
                    break
            for item in self.dataset.columnList:
                if item.columnName == function.funKeyOld:
                    item.columnName = function.get_column_name()
                    item.columnNameNew = function.get_column_name_with_auto()
                    break
        else:
            raise ValueError(
                "Column: {0} and Function No: {1} being used.".format(
                    function.column.columnName, function.funNames
                )
            )

    def check_use_function(self, function):
        isCheck = True
        for item in self.dataset.columnList:
            if item.columnName == function.funKeyOld and item.numberUse > 0:
                isCheck = False
                break
        return isCheck

    def delete_column_new(self, colName, funShow):
        function = self.get_function_by_key(colName, funShow)
        function.funKeyOld = function.get_column_name()
        if self.check_use_function(function):
            for item in self.dataset.columnList:
                if item.columnName == function.funKeyOld:
                    self.dataset.columnList.remove(item)
                    break
            for item in self.dataset.columnList:
                if item.columnName == function.column.columnName:
                    self.dataset.decrease_use(item)
                    break
            for item in self.columnNewList:
                if item.get_column_name() == function.funKeyOld:
                    self.columnNewList.remove(item)
                    break
        else:
            raise ValueError(
                "Column: {0} being used.".format(function.funKeyOld)
            )

    def get_calculation_list_all(self):
        return self.whereSelected + self.havingSelected

    def get_name_calculation_by_level(self, level, status, calcur):
        listName = []
        if status:
            for item in self.havingSelected:
                if item.level == level or item.level == (level - 1):
                    listName.append(item.get_sql())
        else:
            for item in self.whereSelected:
                if item.level == level or item.level == (level - 1):
                    listName.append(item.get_sql())
        if len(listName) > 0:
            if calcur in listName:
                listName.remove(calcur)
            return [""] + listName
        else:
            return listName

    def get_level_max(self, status):
        if status:
            return self.havingLevel + 1
        else:
            return self.whereLevel + 1

    def add_calculation(self, cal):
        if self.check_use_calculation(cal):
            raise ValueError("Column {0} with Calculation {1} is used.")
        else:
            if cal.columns.isAgg:
                self.havingSelected.append(cal)
                if cal.level > self.havingLevel:
                    self.havingLevel = cal.level
            else:
                self.whereSelected.append(cal)
                if cal.level > self.whereLevel:
                    self.whereLevel = cal.level
            self.dataset.increase_use(cal.columns)

    def check_use_calculation(self, cal):
        isCheck = False
        if cal.columns.isAgg:
            for item in self.havingSelected:
                if item.get_sql() == cal.get_sql():
                    isCheck = True
                    break
        else:
            for item in self.whereSelected:
                if item.get_sql() == cal.get_sql():
                    isCheck = True
                    break
        return isCheck

    def get_calculation_by_key(self, colName, calShow, isAgg):
        if isAgg == "True":
            for item in self.havingSelected:
                if item.get_key_cal() == calShow:
                    return copy.deepcopy(item)
        else:
            for item in self.whereSelected:
                if item.get_key_cal() == calShow:
                    return copy.deepcopy(item)

    def update_calculation(self, cal):
        if cal.isAgg:
            for i in range(0, len(self.havingSelected)):
                if self.havingSelected[i].get_key_cal() == cal.get_key_cal():
                    self.havingSelected[i] = cal
                    if cal.level > self.havingLevel:
                        self.havingLevel = cal.level
                    break
        else:
            for i in range(0, len(self.whereSelected)):
                if self.whereSelected[i].get_key_cal() == cal.get_key_cal():
                    self.whereSelected[i] = cal
                    if cal.level > self.whereLevel:
                        self.whereLevel = cal.level
                    break

    def delete_calculation(self, colName, calShow, isAgg):
        try:
            if self.check_relation_calculation(colName, calShow, isAgg):
                raise ValueError("You cannot delete Filter that are in use.")
            else:
                if isAgg == "True":
                    for item in self.havingSelected:
                        if (
                            item.get_key_cal() == calShow
                            and item.columns.columnName == colName
                        ):
                            self.havingSelected.remove(item)
                            max = 0
                            for item in self.havingSelected:
                                if item.level > max:
                                    max = item.level
                            self.havingLevel = max
                            self.dataset.decrease_use(item.columns)
                            break
                else:
                    for item in self.whereSelected:
                        if (
                            item.get_key_cal() == calShow
                            and item.columns.columnName == colName
                        ):
                            self.whereSelected.remove(item)
                            max = 0
                            for item in self.whereSelected:
                                if item.level > max:
                                    max = item.level
                            self.whereLevel = max
                            self.dataset.decrease_use(item.columns)
                            break

        except:
            raise

    def check_relation_calculation(self, colName, calShow, isAgg):
        isCheck = False
        cal = self.get_calculation_by_key(colName, calShow, isAgg)
        if isAgg == "True":
            for item in self.havingSelected:
                if item.relationWith == cal.get_sql():
                    isCheck = True
                    break
        else:
            for item in self.whereSelected:
                if item.relationWith == cal.get_sql():
                    isCheck = True
                    break
        return isCheck

    def set_distinct(self, status):
        self.duplicates = status

    def set_select_row(self, value):
        self.rowSelects = value

    def set_included(self, inType, inView):
        self.includedType = inType
        self.includedView = inView

    def sql_select(self):
        listColumn = []
        for item in self.columnSelected:
            listColumn.append(item.sql_name())
        sql = ", ".join(listColumn)
        if self.duplicates:
            sql = "DISTINCT " + sql
        return sql

    def sql_sort(self):
        listSort = []
        for item in self.sortSelect:
            listSort.append(item.sql_name())
        return ", ".join(listSort)

    def sql_groupby(self):
        isGroup = False
        if len(self.havingSelected) > 0:
            isGroup = True
        if not isGroup:
            for item in self.columnSelected:
                if item.isAgg:
                    isGroup = True
                    break
        if not isGroup:
            for item in self.sortSelect:
                if item.isAgg:
                    isGroup = True
                    break
        if isGroup:
            listGroup = []
            for item in self.columnSelected:
                if not item.isAgg:
                    listGroup.append(item.columnName)
            for item in self.sortSelect:
                if not item.isAgg:
                    listGroup.append(item.columns.columnName)
            return ", ".join(listGroup)
        else:
            return ""

    def sql_where(self):
        whereSentence = ""
        listItem = []
        max_level = self.whereLevel
        for item in self.whereSelected:
            listItem.append(item.in_item_sql())
        while max_level > 0:
            for index in range(0, len(listItem)):
                if (
                    listItem[index][0] == max_level
                    and self.get_level_of_relation_with(
                        listItem[index][2], listItem
                    )
                    == max_level - 1
                ):
                    itemNew = listItem[index]
                    listItemChild = []
                    for index2 in range(0, len(listItem)):
                        if (
                            listItem[index2][2] == itemNew[3]
                            and listItem[index2][0] == itemNew[0]
                        ):
                            listItemChild.append(listItem[index2])
                    nameNew = "({0}".format(itemNew[3])
                    for item in listItemChild:
                        nameNew = "{0} {1} {2}".format(
                            nameNew, item[1], item[3]
                        )
                    nameNew = "{0})".format(nameNew)
                    listItem.append(
                        [max_level - 1, itemNew[1], itemNew[2], nameNew]
                    )
            max_level -= 1
        for index3 in range(0, len(listItem)):
            if listItem[index3][0] == 0:
                if len(whereSentence) == 0:
                    whereSentence = "{0}".format(listItem[index3][3])
                else:
                    whereSentence = "{0} {1} {2}".format(
                        whereSentence, listItem[index3][1], listItem[index3][3]
                    )
        if self.rowSelects > 0:
            if len(whereSentence) > 0:
                whereSentence = "{0} and {1}".format(
                    whereSentence, "ROWNUM <= {0}".format(self.rowSelects)
                )
            else:
                whereSentence = "{0}".format(
                    "ROWNUM <= {0}".format(self.rowSelects)
                )
        for item in self.moreSelected:
            if item.get_int_type() == 1:
                if len(whereSentence) > 0:
                    whereSentence = "{0} and {1}".format(
                        whereSentence, item.get_sql()
                    )
                else:
                    whereSentence = "{0}".format(item.get_sql())
        return whereSentence

    def sql_more(self):
        moreSentence = ""
        for item in self.moreSelected:
            if item.get_int_type() == 2:
                if len(moreSentence) > 0:
                    moreSentence = "{0} {1}".format(
                        moreSentence, item.get_sql()
                    )
                else:
                    moreSentence = "{0}{1}".format(moreSentence, item.get_sql())
        return moreSentence

    def get_level_of_relation_with(self, nameItem, listItem):
        level = 0
        for item in listItem:
            if item[3] == nameItem:
                level = item[0]
                break
        return level

    def sql_having(self):
        havingSentence = ""
        listItem = []
        max_level = self.havingLevel
        for item in self.havingSelected:
            listItem.append(item.in_item_sql())
        while max_level > 0:
            for index in range(0, len(listItem)):
                if (
                    listItem[index][0] == max_level
                    and self.get_level_of_relation_with(
                        listItem[index][2], listItem
                    )
                    == max_level - 1
                ):
                    itemNew = listItem[index]
                    listItemChild = []
                    for index2 in range(0, len(listItem)):
                        if (
                            listItem[index2][2] == itemNew[3]
                            and listItem[index2][0] == itemNew[0]
                        ):
                            listItemChild.append(listItem[index2])
                    nameNew = "({0}".format(itemNew[3])
                    for item in listItemChild:
                        nameNew = "{0} {1} {2}".format(
                            nameNew, item[1], item[3]
                        )
                    nameNew = "{0})".format(nameNew)
                    listItem.append(
                        [max_level - 1, itemNew[1], itemNew[2], nameNew]
                    )
            max_level -= 1
        for index3 in range(0, len(listItem)):
            if listItem[index3][0] == 0:
                if len(havingSentence) == 0:
                    havingSentence = "{0}".format(listItem[index3][3])
                else:
                    havingSentence = "{0} {1} {2}".format(
                        havingSentence, listItem[index3][1], listItem[index3][3]
                    )
        return havingSentence

    def set_no(self, index):
        self.viewNo = index

    def set_view_name(self, name):
        self.viewName = name

    def create(self):
        # insert header
        isCheck = False
        try:
            self.viewNo = self.connects.insert_header_view(
                self.sql_insert_header()
            )
            isCheck = True
        except:
            raise
        # insert line
        if isCheck:
            try:
                # insert column
                for i in range(0, len(self.columnSelected)):
                    col = self.columnSelected[i]
                    col.set_line(i)
                    col.set_view_no(self.viewNo)
                    self.connects.insert_view_line_column(col.sql_insert())

                # insert column new
                for i in range(0, len(self.columnNewList)):
                    newCol = self.columnNewList[i]
                    newCol.set_line(i)
                    newCol.set_view_no(self.viewNo)
                    self.connects.insert_view_line_column_new(
                        newCol.sql_insert()
                    )
                # insert sort
                for i in range(0, len(self.sortSelect)):
                    sort = self.sortSelect[i]
                    sort.set_line(i)
                    sort.set_view_no(self.viewNo)
                    self.connects.insert_view_line_sort(sort.sql_insert())
                # insert filter
                for i in range(0, len(self.whereSelected)):
                    where = self.whereSelected[i]
                    where.set_line(i)
                    where.set_view_no(self.viewNo)
                    self.connects.insert_view_line_filter(where.sql_insert())
                # having
                for i in range(0, len(self.havingSelected)):
                    having = self.havingSelected[i]
                    having.set_line(i)
                    having.set_view_no(self.viewNo)
                    self.connects.insert_view_line_filter(having.sql_insert())
                # more
                for i in range(0, len(self.moreSelected)):
                    more = self.moreSelected[i]
                    more.set_line(i)
                    more.set_view_no(self.viewNo)
                    self.connects.insert_view_line_more(more.sql_insert())
                self.writeLog.write_transaction(
                    [
                        self.user.userno,
                        "View",
                        self.viewNo,
                        "CreateView",
                        "Create",
                    ]
                )
            except:
                raise

    def sql_insert_header(self):
        listHeader = [
            self.viewName,
            self.rowSelects,
            self.get_duplicate(),
            self.user.userno,
            self.includedType,
            self.includedView,
            self.dataset.datasetNo,
        ]
        return listHeader

    def sql_update_header(self):
        listHeader = [
            self.viewNo,
            self.viewName,
            self.rowSelects,
            self.get_duplicate(),
            self.user.userno,
            self.includedType,
            self.includedView,
            self.dataset.datasetNo,
        ]
        return listHeader

    def sql_delete_header(self):
        listHeader = [
            self.viewNo,
        ]
        return listHeader

    def loadData(self, dataBasic):
        sql = self.sentence.sql_load_view_by_no(self.viewNo)
        try:
            dataView = self.connects.get_data_operation(sql)
            dataView = dataView.replace({pd.NA: None})
            dataView = dataView.replace({pd.NaT: None})
            dataView = dataView.fillna("")
            if dataView.empty:
                raise ValueError(
                    "Load data Error with View No {0}".format(self.viewNo)
                )
            else:
                self.set_view(dataView.iloc[0])
                dataset = dataBasic.get_dataset_by_no(
                    dataView.iloc[0].datasetno
                )
                dataset.set_column_list()
                self.set_dataset(dataset)
                self.loaddata_columnnew(dataBasic)
                self.loaddata_filter(dataBasic)
                self.loaddata_select_column()
                self.loaddata_sort()
                self.loaddata_more()
                self.set_is_update(True)
        except:
            raise
        pass

    def loaddata_columnnew(self, dataBasic):
        sql = self.sentence.sql_load_columnnew(self.viewNo)
        try:
            dataColumn = self.connects.get_data_operation(sql)
            if not dataColumn.empty:
                dataColumn = dataColumn.replace({pd.NA: None})
                dataColumn = dataColumn.replace({pd.NaT: None})
                dataColumn = dataColumn.fillna("")
                for item in dataColumn.iloc:
                    func = ModuleFunctions.Functions()
                    func.set_view_no(int(item.viewno))
                    func.set_funtion(
                        dataBasic.get_function_with_no(item.funcno)
                    )
                    func.set_line(item.lines)
                    func.set_column(self.get_column_by_name(item.columname))
                    func.set_value(value1=item.value1, value2=item.value2)
                    self.add_column_new(func)
        except:
            raise

    def loaddata_filter(self, dataBasic):
        sql = self.sentence.sql_load_filter(self.viewNo)
        try:
            dataFilter = self.connects.get_data_operation(sql)
            dataFilter = dataFilter.replace({pd.NA: None})
            dataFilter = dataFilter.replace({pd.NaT: None})
            dataFilter = dataFilter.fillna("")
            for item in dataFilter.iloc:
                cal = ModuleCalculations.Calculations()
                cal.set_view_no(item.viewno)
                cal.set_line(item.lines)
                cal.set_calculation(
                    dataBasic.get_calculation_with_no(item.calno)
                )
                cal.set_column(self.get_column_by_name(item.columnname))
                cal.set_level(item.levels)
                cal.set_relation(item.relation)
                cal.set_with_cal(item.relationwith)
                cal.set_value(item.value1, item.value2)
                self.add_calculation(cal)
        except:
            raise

    def loaddata_select_column(self):
        sql = self.sentence.sql_load_column_select(self.viewNo)
        try:
            dataColumn = self.connects.get_data_operation(sql)
            dataColumn = dataColumn.replace({pd.NA: None})
            dataColumn = dataColumn.replace({pd.NaT: None})
            dataColumn = dataColumn.fillna("")
            for item in dataColumn.iloc:
                col = self.get_column_by_name(item.columnname)
                col.set_view_no(item.viewno)
                col.set_line(item.lines)
                col.set_name_new(item.columnnamenew)
                self.set_select_column_one(col)
        except:
            raise

    def loaddata_sort(self):
        sql = self.sentence.sql_load_sort(self.viewNo)
        try:
            dataSort = self.connects.get_data_operation(sql)
            dataSort = dataSort.replace({pd.NA: None})
            dataSort = dataSort.replace({pd.NaT: None})
            dataSort = dataSort.fillna("")
            for item in dataSort.iloc:
                sort = ModuleSorts.Sorts()
                sort.set_view_no(item.viewno)
                sort.set_line(item.lines)
                sort.set_column(self.get_column_by_name(item.columnname))
                sort.set_type(item.types)
                self.add_sort(sort)
        except:
            raise

    def loaddata_more(self):
        sql = self.sentence.sql_load_more(self.viewNo)
        try:
            dataMore = self.connects.get_data_operation(sql)
            dataMore = dataMore.replace({pd.NA: None})
            dataMore = dataMore.replace({pd.NaT: None})
            dataMore = dataMore.fillna("")
            for item in dataMore.iloc:
                more = ModuleMores.Mores()
                more.set_view_no(item.viewno)
                more.set_line(item.lines)
                more.set_type(item.typesconnect)
                more.set_view(item.viewconnect, item.columnname)
                self.moreSelected.append(more)
        except:
            raise

    def update(self):
        try:
            # update column select
            for i in range(0, len(self.columnSelected)):
                col = self.columnSelected[i]
                col.set_line(i)
                col.set_view_no(self.viewNo)
                self.connects.update_view_line_column(col.sql_insert())

            # new col
            for i in range(0, len(self.columnNewList)):
                newCol = self.columnNewList[i]
                newCol.set_line(i)
                newCol.set_view_no(self.viewNo)
                self.connects.update_view_line_column_new(newCol.sql_insert())

            # insert sort
            for i in range(0, len(self.sortSelect)):
                sort = self.sortSelect[i]
                sort.set_line(i)
                sort.set_view_no(self.viewNo)
                self.connects.update_view_line_sort(sort.sql_insert())
            # insert filter
            for i in range(0, len(self.whereSelected)):
                where = self.whereSelected[i]
                where.set_line(i)
                where.set_view_no(self.viewNo)
                self.connects.update_view_line_filter(where.sql_insert())

            # having
            for i in range(0, len(self.havingSelected)):
                having = self.havingSelected[i]
                having.set_line(i)
                having.set_view_no(self.viewNo)
                self.connects.update_view_line_filter(having.sql_insert())
            # more
            for i in range(0, len(self.moreSelected)):
                more = self.moreSelected[i]
                more.set_line(i)
                more.set_view_no(self.viewNo)
                self.connects.update_view_line_more(more.sql_insert())
            # header
            self.connects.update_header_view(self.sql_update_header())
            self.writeLog.write_transaction(
                [self.user.userno, "View", self.viewNo, "CreateView", "Update"]
            )

        except:
            raise

    def delete(self):
        try:
            self.connects.delete_header_view(self.sql_delete_header())
            self.writeLog.write_transaction(
                [self.user.userno, "View", self.viewNo, "CreateView", "Delete"]
            )
        except:
            raise

    def set_view_release(self, vAction):
        self.viewNo = vAction.viewNo
        self.viewName = vAction.viewName
        self.viewStatus = vAction.viewStatus
        self.isRelease = vAction.isRelease
        self.isDataRelease = True

    def release(self, dataBasic):
        try:
            self.loadData(dataBasic)
            if not self.isRelease:
                if self.viewStatus == 1:
                    self.connects.excute_query(self.db_create_view())
                    self.writeLog.write_transaction(
                        [
                            self.user.userno,
                            "View",
                            self.viewNo,
                            "Release",
                            "Create",
                        ]
                    )
                elif self.viewStatus == 2:
                    if self.isInDB:
                        self.connects.excute_query(self.db_update_view())
                        self.writeLog.write_transaction(
                            [
                                self.user.userno,
                                "View",
                                self.viewNo,
                                "Release",
                                "Update",
                            ]
                        )
                    else:
                        self.connects.excute_query(self.db_create_view())
                        self.writeLog.write_transaction(
                            [
                                self.user.userno,
                                "View",
                                self.viewNo,
                                "Release",
                                "Create",
                            ]
                        )
                elif self.viewStatus == 3:
                    if self.isInDB:
                        self.connects.excute_query(self.db_delete_view())
                        self.writeLog.write_transaction(
                            [
                                self.user.userno,
                                "View",
                                self.viewNo,
                                "Release",
                                "Delete",
                            ]
                        )
            self.update_status_release()
        except:
            raise

    def db_create_view(self):
        try:
            sql = """CREATE VIEW REPORTUSER.{0} AS {1}""".format(
                self.viewName, self.get_sql_sentence()
            )
            return sql
        except:
            raise

    def db_update_view(self):
        try:
            sql = """CREATE OR REPLACE VIEW REPORTUSER.{0} AS {1}""".format(
                self.viewName, self.get_sql_sentence()
            )
            return sql
        except:
            raise

    def db_delete_view(self):
        try:
            sql = """DROP VIEW REPORTUSER.{0}""".format(self.viewName)
            return sql
        except:
            raise

    def update_status_release(self):
        try:
            self.connects.update_view_release_status([self.viewNo])
        except:
            raise

    def run_sql(self, vNo, dataBasic):
        try:
            self.viewNo = vNo
            self.loadData(dataBasic)
            return self.get_sql_sentence()
        except:
            raise

    def get_list_column_name_select(self):
        listColumn = []
        for item in self.columnSelected:
            listColumn.append(item.columnName)
        return listColumn

    def get_view_in_more(self):
        listName = []
        for item in self.moreSelected:
            listName.append(item.viewConnect)
        return listName

    def add_more(self, moreObject):
        for item in self.moreSelected:
            if item.viewConnect == moreObject.viewConnect:
                raise ValueError("View exist in More")
        self.moreSelected.append(moreObject)

    def get_more_selected(self, viewName, typeConnect):
        isCheck = False
        for item in self.moreSelected:
            if item.typeMore == typeConnect and item.viewConnect == viewName:
                isCheck = True
                return copy.deepcopy(item)
        if not isCheck:
            raise AttributeError("Not fount more")

    def update_more(self, moreObject):
        isCheck = False
        for i in range(0, len(self.moreSelected)):
            if (
                self.moreSelected[i].typeMore == moreObject.typeMore
                and self.moreSelected[i].viewConnect == moreObject.viewConnect
            ):
                isCheck = True
                self.moreSelected[i] = moreObject
                return
        if not isCheck:
            raise AttributeError("Not fount more")

    def delete_more(self, viewName, typeConnect):
        isCheck = False
        for item in self.moreSelected:
            if item.viewConnect == viewName and item.typeMore == typeConnect:
                self.moreSelected.remove(item)
                isCheck = True
                return
        if not isCheck:
            raise AttributeError("Not fount more")
