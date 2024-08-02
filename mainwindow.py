import sys, copy
import pandas as pd

from PySide6.QtWidgets import (
    QMessageBox,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QApplication,
    QMainWindow,
    QWidget,
    QDialog,
    QAbstractItemView,
    QDialogButtonBox,
    QFileDialog,
)

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_MainWindow import Ui_MainWindow
from ui_frmCreateView import Ui_frmCreateView
from ui_frmRelease import Ui_frmRelease
from ui_frmRun import Ui_frmRunView
from ui_dialogSearch import Ui_DialogSearch
from ui_frmLogin import Ui_frmLogin
from ui_frmViewData import Ui_frmViewData
from ui_frmChangePassword import Ui_ChangePassword
from ui_frmCreateUser import Ui_CreateUser
from ui_frmViewManual import Ui_CreateManual
from ui_frmResult import Ui_ShowResult

# import Module
import Connects, ModuleUsers, ModuleDataBasics, ModuleViews, ModuleColumns
import ModuleSorts, Sentences, ModuleFunctions, ModuleCalculations
import TableViewModel, ModuleViewAction, ModuleWriteLogs, ModuleViewManuals
import ModuleMores


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.loadfrm_main()

    def closeEvent(self, event):
        self.show_message(0, "Close Program", "Do you want Quit Program ?")
        if self.messageBoxButton == QMessageBox.StandardButton.Ok:
            if self.users.isLogin:
                self.writeLog.write_login(self.users.user, "Out")
            self.view_run_dataset_widgets = QWidget()
            self.view_run_dataset_widgets.close()
            event.accept()
        else:
            event.ignore()

    def loadfrm_main(self):
        # define trigger
        self.ui.actionCreate_View.triggered.connect(self.menu_view_create)
        self.ui.actionLogout.triggered.connect(self.menu_log_out)
        self.ui.actionRelease_View.triggered.connect(self.menu_view_release)
        self.ui.actionRun_View.triggered.connect(self.menu_view_run)
        self.ui.actionHome.triggered.connect(self.menu_view_home)
        self.ui.actionSearch.triggered.connect(self.menu_view_search)
        self.ui.actionChange_Password.triggered.connect(
            self.menu_change_password
        )
        self.ui.actionCreate_User.triggered.connect(self.menu_user_create)
        self.ui.actionCreate_View_Manual.triggered.connect(
            self.menu_view_create_manual
        )

        # define variable global
        try:
            self.connects = Connects.Connects()
            self.users = ModuleUsers.Users(self.connects)
            self.sentence = Sentences.Sentences()
            self.dataBasic = ModuleDataBasics.DataBasics(
                self.connects, self.users
            )
            self.writeLog = ModuleWriteLogs.WriteLogs(self.connects)
        except Exception as e:
            self.show_message(3, "Exception", str(e.__class__.__name__), str(e))

        # check login
        self.loadfrm_login()

    def enable_menu_by_index(self, index):
        self.ui.actionCreate_View.setEnabled(index != 1)
        self.ui.actionRun_View.setEnabled(index != 2)
        self.ui.actionRelease_View.setEnabled(index != 3)
        self.ui.actionChange_Password.setEnabled(index != 4)
        self.ui.actionCreate_User.setEnabled(
            self.users.is_admin() and index != 5
        )
        self.ui.actionCreate_View_Manual.setEnabled(index != 6)

    def show_message(self, type, title, content, moreinfo=None):
        messageBox = QMessageBox()
        if type == 1:  # successfull
            messageBox.setWindowTitle(title)
            messageBox.setText(content)
            messageBox.setIcon(QMessageBox.Icon.Information)
            messageBox.setStandardButtons(QMessageBox.StandardButton.Ok)
        elif type == 2:  # warning
            messageBox.setWindowTitle(title)
            messageBox.setText(content)
            messageBox.setIcon(QMessageBox.Icon.Warning)
            messageBox.setStandardButtons(QMessageBox.StandardButton.Ok)
        elif type == 3:  # --> Error
            messageBox.setWindowTitle(title)
            messageBox.setIcon(QMessageBox.Icon.Critical)
            messageBox.setStandardButtons(QMessageBox.StandardButton.Ok)
            messageBox.setDefaultButton(QMessageBox.StandardButton.Ok)
            messageBox.setInformativeText(content)
            messageBox.setDetailedText(moreinfo)
        else:
            messageBox.setWindowTitle(title)
            messageBox.setText(content)
            messageBox.setStandardButtons(
                QMessageBox.StandardButton.Ok
                | QMessageBox.StandardButton.Cancel
            )
        self.messageBoxButton = messageBox.exec()

    def show_status(self, type, content):
        if type == 3:
            self.ui.statusbar.showMessage(content, 5000)
            self.ui.statusbar.setStyleSheet("#statusbar{ color: #FF0000;}")
        elif type == 2:
            self.ui.statusbar.showMessage(content, 5000)
            self.ui.statusbar.setStyleSheet("#statusbar{ color: #0000FF;}")
        elif type == 1:
            self.ui.statusbar.showMessage(content, 5000)
            self.ui.statusbar.setStyleSheet("#statusbar{ color: #006600;}")

    # define enable visiable when login or not login
    def refresh_var_global(self):
        self.viewCurrent = ModuleViews.Views(self.connects, self.users)
        self.columnCur = ModuleColumns.Columns()
        self.sortCur = ModuleSorts.Sorts()
        self.functionCur = ModuleFunctions.Functions()
        self.calCur = ModuleCalculations.Calculations()
        self.viewAction = ModuleViewAction.ViewAction()

    ################# LOGIN ###############################3
    def visiable_login(self):
        self.ui.menubar.setVisible(self.users.isLogin)
        self.ui.toolBar.setVisible(self.users.isLogin)

    def loadfrm_login(self):
        self.visiable_login()
        if not self.users.isLogin:
            self.view_login_ui = Ui_frmLogin()
            self.view_login_widgets = QWidget()
            self.view_login_ui.setupUi(self.view_login_widgets)
            self.ui.scrollArea.setWidget(self.view_login_widgets)

            # define event
            self.view_login_ui.btnExit.clicked.connect(self.close)
            self.view_login_ui.btnLogin.clicked.connect(self.click_btn_login)
        else:
            self.menu_view_home()

    def click_btn_login(self):
        user = self.view_login_ui.leUserName.text()
        password = self.view_login_ui.lePassword.text()
        try:
            isCheck = True
            if user.strip() == "":
                isCheck = False
                self.show_status(2, "Please enter UserName")
            if isCheck and password.strip() == "":
                isCheck = False
                self.show_status(2, "Please enter Password")

            # login after user entered UserName and Password
            if isCheck:
                message = self.users.login_check(user, password)
                if not self.users.isLogin:
                    self.show_message(2, "Warning Login", message)
                else:
                    self.menu_view_home()
        except Exception as e:
            self.show_message(3, "Exception", "Error when login.", str(e.args))

    def menu_log_out(self):
        self.writeLog.write_login(self.users.user, "Out")
        self.users = ModuleUsers.Users(self.connects)
        self.loadfrm_login()

    def menu_view_home(self):
        self.visiable_login()
        self.ui.scrollArea.setWidget(QWidget())
        self.enable_menu_by_index(0)

    ########################    SEARCH #########################3
    def menu_view_search(self):
        self.view_search_ui = Ui_DialogSearch()
        self.view_search_widgets = QDialog()
        self.view_search_ui.setupUi(self.view_search_widgets)
        try:
            self.dataBasic.initdata_search()
            self.loaddata_view_search()
            self.view_search_ui.leSearch.textEdited.connect(
                self.change_search_text
            )
            self.view_search_ui.tbwSearch.itemClicked.connect(
                self.itemclick_tbw_search
            )
            self.view_search_ui.buttonBox.clicked.connect(
                self.click_search_button
            )
            self.view_search_ui.tbwSearch.itemDoubleClicked.connect(
                self.double_itemclick_search
            )
            self.view_search_widgets.exec()
        except Exception as e:
            self.show_message(
                3, "Load View Error", str(e.__class__.__name__), str(e)
            )

    def loaddata_view_search(self):
        self.view_search_ui.tbwSearch.clear()
        self.view_search_ui.tbwSearch.setColumnCount(2)
        hItem0 = QTableWidgetItem("View No")
        hItem1 = QTableWidgetItem("View Name")
        hItem0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        hItem1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view_search_ui.tbwSearch.setHorizontalHeaderItem(0, hItem0)
        self.view_search_ui.tbwSearch.setHorizontalHeaderItem(1, hItem1)
        if len(self.dataBasic.dataSearch) > 0:
            searchText = self.view_search_ui.leSearch.text()
            if self.view_search_ui.cbSeachID.isChecked():
                dataLoad = self.dataBasic.dataSearch[
                    self.dataBasic.dataSearch["viewno"]
                    .astype(str)
                    .str.contains(str(searchText), regex=True)
                ]
            else:
                dataLoad = self.dataBasic.dataSearch[
                    self.dataBasic.dataSearch["viewname"]
                    .astype(str)
                    .str.contains(str(searchText), regex=True)
                ]
            rows = len(dataLoad)
            if rows > 0:
                dataLoad = dataLoad.reset_index(drop=True)
                self.view_search_ui.tbwSearch.setRowCount(rows)
                for row in range(0, rows):
                    rItem0 = QTableWidgetItem(str(dataLoad.loc[row].iloc[0]))
                    rItem1 = QTableWidgetItem(str(dataLoad.loc[row].iloc[1]))
                    self.view_search_ui.tbwSearch.setItem(row, 0, rItem0)
                    self.view_search_ui.tbwSearch.setItem(row, 1, rItem1)
                self.view_search_ui.tbwSearch.setEditTriggers(
                    QAbstractItemView.NoEditTriggers
                )
                self.view_search_ui.tbwSearch.setSelectionBehavior(
                    QAbstractItemView.SelectRows
                )
                self.view_search_ui.tbwSearch.horizontalHeader().setSectionResizeMode(
                    0, QHeaderView.ResizeMode.ResizeToContents
                )
                self.view_search_ui.tbwSearch.horizontalHeader().setSectionResizeMode(
                    1, QHeaderView.ResizeMode.Stretch
                )

    def change_search_text(self):
        self.loaddata_view_search()

    def itemclick_tbw_search(self, item):
        try:
            row = self.view_search_ui.tbwSearch.row(item)
            self.viewUpdate = ModuleViews.Views(self.connects, self.users)
            self.viewUpdate.set_no(
                int(self.view_search_ui.tbwSearch.item(row, 0).text())
            )
            self.viewUpdate.set_view_name(
                self.view_search_ui.tbwSearch.item(row, 1).text()
            )
            self.view_search_ui.buttonBox.setEnabled(
                self.viewUpdate.viewNo != int()
            )
        except Exception as e:
            self.show_message(
                3, "Select View Error", str(e.__class__.__name__), str(e)
            )

    def click_search_button(self, button):
        if (
            self.view_search_ui.buttonBox.buttonRole(button)
            == QDialogButtonBox.ButtonRole.AcceptRole
        ):
            self.view_search_widgets.accept()
            self.loaddata_view_update()
        else:
            self.view_search_widgets.reject()

    def double_itemclick_search(self):
        self.view_search_widgets.accept()
        self.loaddata_view_update()

    def loaddata_view_update(self):
        try:
            self.menu_view_create()
            self.viewUpdate.loadData(self.dataBasic)
            self.viewCurrent = copy.deepcopy(self.viewUpdate)
            self.view_create_ui.cbbViewDataSet.setCurrentText(
                self.viewCurrent.dataset.datasetName
            )
            self.viewUpdate = ModuleViews.Views(self.connects, self.users)
        except Exception as e:
            self.show_message(
                3, "Load info View", str(e.__class__.__name__), str(e)
            )
            self.menu_view_home()

    ########################        CREATE QUERY ###################33
    def menu_view_create(self):
        self.refresh_var_global()
        self.view_create_ui = Ui_frmCreateView()
        self.view_create_widgets = QWidget()
        self.view_create_ui.setupUi(self.view_create_widgets)
        self.ui.scrollArea.setWidget(self.view_create_widgets)
        self.enable_menu_by_index(1)

        # defin variable
        try:
            self.dataBasic.initdata_create()
            self.viewCurrent = ModuleViews.Views(self.connects, self.users)
        except Exception as e:
            self.show_message(
                3, "Exception when Load Data", "Define variable", str(e.args)
            )
            self.menu_view_home()

        self.loaddata_name_dataset()  # --> load Name of Dataset to combobox

        # define event
        self.view_create_ui.btnTabSelectColumn.clicked.connect(
            self.click_btn_tab_select_column
        )
        self.view_create_ui.btnTabCreateColumn.clicked.connect(
            self.click_btn_tab_create_column
        )
        self.view_create_ui.btnTabFilter.clicked.connect(
            self.click_btn_tab_filter
        )
        self.view_create_ui.btnTabSort.clicked.connect(self.click_btn_tab_sort)
        self.view_create_ui.btnTabMore.clicked.connect(self.click_btn_tab_more)
        self.view_create_ui.btnTabColumnPlus.clicked.connect(
            self.click_btn_tab_column_plus
        )
        self.view_create_ui.btnTabSql.clicked.connect(self.click_btn_tab_sql)
        self.view_create_ui.cbbViewDataSet.currentIndexChanged.connect(
            self.change_cbb_dataset
        )
        # event select column
        self.view_create_ui.lvSelectColumnAll.itemClicked.connect(
            self.itemclick_lv_not_select
        )
        self.view_create_ui.lvSelectColumnChoose.itemClicked.connect(
            self.itemclick_lv_select
        )
        self.view_create_ui.lvSelectColumnAll.itemDoubleClicked.connect(
            self.double_itemclick_select
        )
        self.view_create_ui.lvSelectColumnChoose.itemDoubleClicked.connect(
            self.double_itemclick_select
        )
        self.view_create_ui.btnSelectAddAll.clicked.connect(
            self.click_select_all
        )
        self.view_create_ui.btnSelectAddOne.clicked.connect(
            self.click_select_one
        )
        self.view_create_ui.btnSelectRemoveAll.clicked.connect(
            self.click_remove_all
        )
        self.view_create_ui.btnSelectRemoveOne.clicked.connect(
            self.click_remove_one
        )
        self.view_create_ui.btnSelectSave.clicked.connect(
            self.click_select_save
        )

        # event sort
        self.view_create_ui.cbbSortColumn.currentIndexChanged.connect(
            self.changeindex_cbb_sort_column
        )
        self.view_create_ui.btnSortAdd.clicked.connect(self.click_btn_sort_add)
        self.view_create_ui.btnSortUpdate.clicked.connect(
            self.click_btn_sort_update
        )
        self.view_create_ui.tbwSort.itemDoubleClicked.connect(
            self.itemdoubleclick_sort
        )

        # event create new column
        self.view_create_ui.cbbCreateColumn.currentIndexChanged.connect(
            self.change_cbb_columnnew_column
        )
        self.view_create_ui.cbbCreateFunction.currentIndexChanged.connect(
            self.change_cbb_columnnew_function
        )
        self.view_create_ui.btnCreateAdd.clicked.connect(
            self.click_btn_columnnew_add
        )
        self.view_create_ui.btnCreateUpdate.clicked.connect(
            self.click_btn_columnnew_update
        )
        self.view_create_ui.tbwCreateColumn.itemDoubleClicked.connect(
            self.itemdoubleclick_columnnew
        )

        # event new column plus

        # event filter
        self.view_create_ui.cbbFilterColumn.currentIndexChanged.connect(
            self.change_cbb_filter_column
        )
        self.view_create_ui.cbbFilterCal.currentIndexChanged.connect(
            self.change_cbb_filter_calculation
        )
        self.view_create_ui.spbFilterRelLevel.valueChanged.connect(
            self.change_spin_filter_level
        )
        self.view_create_ui.btnFilterAdd.clicked.connect(
            self.click_btn_filter_add
        )
        self.view_create_ui.btnFilterUpdate.clicked.connect(
            self.click_btn_filter_update
        )
        self.view_create_ui.tbwFilter.itemDoubleClicked.connect(
            self.itemdoubleclick_filter
        )

        # event More
        self.view_create_ui.cbbMoreType.currentIndexChanged.connect(
            self.change_cbb_more_type
        )
        self.view_create_ui.cbbMoreView.currentIndexChanged.connect(
            self.change_cbb_more_view
        )
        self.view_create_ui.btnMoreAdd.clicked.connect(self.click_btn_more_add)
        self.view_create_ui.btnMoreUpdate.clicked.connect(
            self.click_btn_more_update
        )
        self.view_create_ui.tbwMore.itemDoubleClicked.connect(
            self.click_item_more_tbw
        )

        # header
        self.view_create_ui.cbViewDuplicate.checkStateChanged.connect(
            self.change_cb_distinct
        )
        self.view_create_ui.leViewTop.textEdited.connect(self.edit_le_top)
        self.view_create_ui.btnViewCreate.clicked.connect(
            self.click_btn_view_create
        )
        self.view_create_ui.btnViewDuplicate.clicked.connect(
            self.click_btn_view_duplicate
        )
        self.view_create_ui.btnViewDataSetRun.clicked.connect(
            self.click_btn_view_run
        )
        self.view_create_ui.btnViewDelete.clicked.connect(
            self.click_btn_view_delete
        )
        self.view_create_ui.btnViewNew.clicked.connect(self.click_btn_view_new)
        self.view_create_ui.btnViewUpdate.clicked.connect(
            self.click_btn_view_update
        )
        self.view_create_ui.leViewName.editingFinished.connect(
            self.edit_le_view_name
        )

    def loaddata_name_dataset(self):
        self.view_create_ui.cbbViewDataSet.clear()
        self.view_create_ui.cbbViewDataSet.addItems(
            self.dataBasic.get_all_dataset_name()
        )
        self.view_create_ui.cbbViewDataSet.setCurrentIndex(0)

    def change_cbb_dataset(self):
        datasetName = self.view_create_ui.cbbViewDataSet.currentText()
        if not datasetName == "":
            try:
                if not self.viewCurrent.isDataset:
                    dataset = self.dataBasic.get_dataset_with_name(datasetName)
                    dataset.set_column_list()
                    self.viewCurrent.set_dataset(dataset)
                    self.viewCurrent.set_view_no(self.dataBasic.idNew)
            except Exception as e:
                self.show_message(
                    3,
                    "Exception when select Dataset",
                    str(e.__class__.__name__),
                    str(e),
                )
                self.view_create_ui.cbbViewDataSet.setCurrentIndex(0)
        else:
            self.viewCurrent = ModuleViews.Views(self.connects, self.users)

        # define info after select dataset
        self.click_btn_tab_select_column()  # --> select tab select column
        self.loaddata_view_header()  # --> load data header: name, top, id, distint
        self.loaddata_column_cbb()  # --> load data of dataset to cbb, lv
        self.enable_select_dataset()  # --> enable or of when select dataset
        self.update_sql_sentence()  # --> update sql
        self.loaddata_tbw_sort()  # --> load data of table sort
        self.loaddata_tbw_columnnew()  # --> load data of table new column
        self.loaddata_tbw_filter()  # --> load data filter to table widgets

    def loaddata_view_header(self):
        try:
            self.view_create_ui.leViewId.setText(
                self.viewCurrent.get_str_view_no()
            )
            self.view_create_ui.leViewName.setText(self.viewCurrent.viewName)
            self.view_create_ui.leViewCreateDate.setText(
                self.viewCurrent.get_create_date()
            )
            self.view_create_ui.leViewTop.setText(
                self.viewCurrent.get_str_rowtop()
            )
            self.view_create_ui.cbViewDuplicate.setChecked(
                self.viewCurrent.duplicates
            )
        except Exception as e:
            self.show_message(
                3,
                "Exception when Load data View Header",
                str(e.__class__.__name__),
                str(e),
            )
            self.menu_view_home()

    def loaddata_column_cbb(self):
        self.view_create_ui.cbbCreateColumn.clear()
        self.view_create_ui.cbbFilterColumn.clear()
        self.view_create_ui.cbbSortColumn.clear()
        nameColumnList = self.viewCurrent.get_name_column_dataset()
        # add to select column
        self.loaddata_select_column()
        # add to cbb create column
        if len(nameColumnList) > 0:
            self.view_create_ui.cbbCreateColumn.addItem("")
        self.view_create_ui.cbbCreateColumn.addItems(nameColumnList)
        self.view_create_ui.cbbCreateColumn.setCurrentIndex(0)
        # add to cbb fileter
        if len(nameColumnList) > 0:
            self.view_create_ui.cbbFilterColumn.addItem("")
        self.view_create_ui.cbbFilterColumn.addItems(nameColumnList)
        self.view_create_ui.cbbFilterColumn.setCurrentIndex(0)
        # add to cbb sort
        if len(nameColumnList) > 0:
            self.view_create_ui.cbbSortColumn.addItem("")
        self.view_create_ui.cbbSortColumn.addItems(nameColumnList)
        self.view_create_ui.cbbSortColumn.setCurrentIndex(0)
        # load more view
        self.loaddata_more()

    def loaddata_select_column(self):
        self.view_create_ui.lvSelectColumnAll.clear()
        self.view_create_ui.lvSelectColumnChoose.clear()
        self.view_create_ui.lvSelectColumnAll.addItems(
            self.viewCurrent.get_name_column_not_select()
        )
        self.view_create_ui.lvSelectColumnChoose.addItems(
            self.viewCurrent.get_name_column_selected()
        )

    def enable_select_dataset(self):
        self.view_create_ui.btnViewDataSetRun.setEnabled(
            self.viewCurrent.isDataset
        )
        self.view_create_ui.cbbCreateColumn.setEnabled(
            self.viewCurrent.isDataset
        )
        self.view_create_ui.cbbFilterColumn.setEnabled(
            self.viewCurrent.isDataset
        )
        self.view_create_ui.cbbSortColumn.setEnabled(self.viewCurrent.isDataset)
        self.view_create_ui.btnViewDataSetRun.setEnabled(
            self.viewCurrent.isDataset
        )
        # enable button select all, remove all
        self.enable_btn_select_remove()
        self.enable_btn_view_main()

    def enable_btn_view_main(self):
        self.view_create_ui.btnViewCreate.setEnabled(
            self.viewCurrent.isDataset and not self.viewCurrent.isUpdate
        )
        self.view_create_ui.btnViewNew.setEnabled(self.viewCurrent.isDataset)
        self.view_create_ui.btnViewUpdate.setEnabled(self.viewCurrent.isUpdate)
        self.view_create_ui.btnViewDelete.setEnabled(self.viewCurrent.isUpdate)
        self.view_create_ui.btnViewDuplicate.setEnabled(
            self.viewCurrent.isUpdate
        )
        self.view_create_ui.leViewName.setEnabled(not self.viewCurrent.isUpdate)

    def enable_btn_select_remove(self, status=None):
        self.view_create_ui.btnSelectAddAll.setEnabled(
            len(self.viewCurrent.get_name_column_not_select()) > 0
        )
        self.view_create_ui.btnSelectRemoveAll.setEnabled(
            len(self.viewCurrent.get_name_column_selected()) > 0
        )
        if status != None:
            self.view_create_ui.btnSelectAddOne.setEnabled(
                status and self.viewCurrent.isDataset
            )
            self.view_create_ui.btnSelectRemoveOne.setEnabled(
                not status and self.viewCurrent.isDataset
            )
        else:
            self.view_create_ui.btnSelectAddOne.setEnabled(False)
            self.view_create_ui.btnSelectRemoveOne.setEnabled(False)

    def update_sql_sentence(self):
        self.view_create_ui.pleViewSql.setPlainText(
            self.viewCurrent.get_sql_sentence()
        )

    ############ SELECT COLUMN ###############
    def itemclick_lv_not_select(self, item):
        self.columnCur = self.viewCurrent.get_column_not_by_name(item.text())
        self.view_create_ui.lvSelectColumnChoose.clearSelection()
        self.enable_btn_select_remove(True)
        self.change_when_double_click(False)

    def itemclick_lv_select(self, item):
        self.columnCur = self.viewCurrent.get_column_selected_by_name(
            item.text()
        )
        self.columnCur.set_selected(True)
        self.view_create_ui.lvSelectColumnAll.clearSelection()
        self.enable_btn_select_remove(False)
        self.change_when_double_click(False)

    def double_itemclick_select(self, item):
        self.change_when_double_click(True)

    def click_select_all(self):
        self.viewCurrent.set_select_column_all()
        self.change_when_add_select_remove()
        self.loaddata_select_column()
        self.update_sql_sentence()

    def click_select_one(self):
        try:
            self.viewCurrent.set_select_column_one(self.columnCur)
            self.change_when_add_select_remove()
            self.loaddata_select_column()
            self.update_sql_sentence()
        except Exception as e:
            self.show_message(
                3,
                "Exception when Add Column",
                str(e.__class__.__name__),
                str(e),
            )

    def click_remove_all(self):
        self.viewCurrent.set_remove_column_all()
        self.change_when_add_select_remove()
        self.loaddata_select_column()
        self.update_sql_sentence()

    def click_remove_one(self):
        self.viewCurrent.set_remove_column_one(self.columnCur)
        self.change_when_add_select_remove()
        self.loaddata_select_column()
        self.update_sql_sentence()

    def click_select_save(self):
        name_new = self.view_create_ui.leSelectNameNew.text()
        isCheck = True
        if name_new != "":
            if name_new.find(" ") >= 0:
                isCheck = False
                self.show_message(
                    3,
                    "Check Name New",
                    "Name of column contain space character",
                )
            if isCheck and not name_new.replace("_", "").isascii():
                isCheck = False
                self.show_message(
                    3,
                    "Check Name New",
                    "Name of column contain special character",
                )
            if isCheck and not name_new.replace("_", "").isalnum():
                isCheck = False
                self.show_message(
                    3,
                    "Check Name New",
                    "Name of column contain special character",
                )
            if isCheck and self.viewCurrent.check_column_name_new(name_new):
                self.show_message(
                    3, "Check Name New", "Name of column is exist."
                )

        if isCheck:
            self.columnCur.set_name_new(name_new)
            if self.columnCur.isSelected:
                self.viewCurrent.update_column_selected(self.columnCur)
            self.change_when_double_click(False)
            self.update_sql_sentence()

    def change_when_double_click(self, status):
        if status:
            self.view_create_ui.leSelectNameCur.setText(
                self.columnCur.columnNameNew
            )
            self.view_create_ui.leSelectColumn.setText(
                self.columnCur.columnName
            )
            self.view_create_ui.leSelectNameNew.setText("")
            self.view_create_ui.btnSelectSave.setEnabled(
                self.columnCur.columnName != str()
            )
        else:
            self.view_create_ui.leSelectNameCur.setText("")
            self.view_create_ui.leSelectColumn.setText("")
            self.view_create_ui.leSelectNameNew.setText("")
            self.view_create_ui.btnSelectSave.setEnabled(False)

    def change_when_add_select_remove(self):
        self.view_create_ui.lvSelectColumnAll.clearSelection()
        self.view_create_ui.lvSelectColumnChoose.clearSelection()
        self.enable_btn_select_remove()
        self.columnCur = ModuleColumns.Columns()

    ##################      SORT    ##################
    def loaddata_tbw_sort(self):
        hearderTitle = self.sentence.header_table_sort()
        self.view_create_ui.tbwSort.clear()
        self.view_create_ui.tbwSort.setColumnCount(len(hearderTitle))
        self.view_create_ui.tbwSort.setRowCount(
            len(self.viewCurrent.sortSelect)
        )
        # add header
        hItem0 = QTableWidgetItem(hearderTitle[0])
        hItem1 = QTableWidgetItem(hearderTitle[1])
        hItem2 = QTableWidgetItem(hearderTitle[2])
        hItem0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        hItem1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        hItem2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view_create_ui.tbwSort.setHorizontalHeaderItem(0, hItem0)
        self.view_create_ui.tbwSort.setHorizontalHeaderItem(1, hItem1)
        self.view_create_ui.tbwSort.setHorizontalHeaderItem(2, hItem2)
        # add row
        if len(self.viewCurrent.sortSelect) > 0:
            row = 0
            for rowItem in self.viewCurrent.sortSelect:
                rItem0 = QPushButton("   Delete")
                rItem0.clicked.connect(self.click_btn_sort_delete)
                rItem0.setMinimumSize(QSize(80, 24))
                rItem0.setMaximumSize(QSize(80, 24))
                icon = QIcon()
                icon.addFile(
                    ":/images/images/minus.png",
                    QSize(),
                    QIcon.Normal,
                    QIcon.Off,
                )
                rItem0.setIcon(icon)
                rItem1 = QTableWidgetItem(rowItem.columns.columnName)
                rItem2 = QTableWidgetItem(rowItem.types)
                self.view_create_ui.tbwSort.setCellWidget(row, 0, rItem0)
                self.view_create_ui.tbwSort.setItem(row, 1, rItem1)
                self.view_create_ui.tbwSort.setItem(row, 2, rItem2)
                self.view_create_ui.tbwSort.cellWidget(
                    row, 0
                ).setContentsMargins(10, 3, 10, 3)
                row += 1
            self.view_create_ui.tbwSort.setColumnWidth(0, 100)
            self.view_create_ui.tbwSort.horizontalHeader().setSectionResizeMode(
                1, QHeaderView.ResizeMode.Stretch
            )
            self.view_create_ui.tbwSort.setColumnWidth(2, 150)

    def changeindex_cbb_sort_column(self):
        nameCol = self.view_create_ui.cbbSortColumn.currentText()
        self.sortCur = ModuleSorts.Sorts()
        if nameCol.strip() != "":
            col = self.viewCurrent.get_column_by_name(nameCol)
            self.sortCur.set_column(col)
        self.enable_sort_column()

    def click_btn_sort_add(self):
        self.sortCur.set_type(self.view_create_ui.cbSortAsc.isChecked())
        try:
            self.viewCurrent.add_sort(self.sortCur)
            self.view_create_ui.cbbSortColumn.setCurrentIndex(0)
            self.loaddata_tbw_sort()
            self.update_sql_sentence()
        except Exception as e:
            self.show_message(
                3, "Error Add Sort", str(e.__class__.__name__), str(e)
            )

    def click_btn_sort_update(self):
        self.sortCur.set_type(self.view_create_ui.cbSortAsc.isChecked())
        try:
            self.sortCur.set_update(False)
            self.viewCurrent.update_sort(self.sortCur)
            self.view_create_ui.cbbSortColumn.setCurrentIndex(0)
            self.loaddata_tbw_sort()
            self.update_sql_sentence()
        except Exception as e:
            self.show_message(
                3, "Error Update Sort", str(e.__class__.__name__), str(e)
            )

    def itemdoubleclick_sort(self, item):
        rowIndex = self.view_create_ui.tbwSort.row(item)
        colName = self.view_create_ui.tbwSort.item(rowIndex, 1).text()
        self.view_create_ui.cbbSortColumn.setCurrentText(colName)
        self.sortCur = self.viewCurrent.get_sort_by_column_name(colName)
        self.sortCur.set_update(True)
        self.enable_sort_column()

    def click_btn_sort_delete(self):
        try:
            btnDelete = self.sender()
            index = self.view_create_ui.tbwSort.indexAt(btnDelete.pos())
            if index.isValid():
                self.show_message(
                    0,
                    "Delete Sort",
                    "Do you want Delete Sort ?",
                )
                if self.messageBoxButton == QMessageBox.StandardButton.Ok:
                    colName = self.view_create_ui.tbwSort.item(
                        index.row(), 1
                    ).text()
                    self.viewCurrent.delete_sort_by_column_name(colName)
                    self.loaddata_tbw_sort()
                    self.update_sql_sentence()
                    if (
                        colName
                        == self.view_create_ui.cbbSortColumn.currentText().strip()
                    ):
                        self.view_create_ui.cbbSortColumn.setCurrentIndex(0)
        except Exception as e:
            self.show_message(
                3, "Delete Sort Error", str(e.__class__.__name__), str(e)
            )

    def enable_sort_column(self):
        self.view_create_ui.cbSortAsc.setEnabled(self.sortCur.isColumn)
        self.view_create_ui.cbSortDes.setEnabled(self.sortCur.isColumn)
        self.view_create_ui.btnSortAdd.setEnabled(
            self.sortCur.isColumn and not self.sortCur.isUpdate
        )
        self.view_create_ui.btnSortUpdate.setEnabled(
            self.sortCur.isColumn and self.sortCur.isUpdate
        )
        self.view_create_ui.cbSortAsc.setChecked(self.sortCur.get_bool_type())
        self.view_create_ui.cbSortDes.setChecked(
            not self.sortCur.get_bool_type()
        )

    ####################        NEW COLUMN ###############
    def loaddata_tbw_columnnew(self):
        hearderTitle = self.sentence.header_table_column_new()
        self.view_create_ui.tbwCreateColumn.clear()
        self.view_create_ui.tbwCreateColumn.setColumnCount(len(hearderTitle))
        self.view_create_ui.tbwCreateColumn.setRowCount(
            len(self.viewCurrent.columnNewList)
        )
        # add header
        for i in range(0, len(hearderTitle)):
            hItem = QTableWidgetItem(hearderTitle[i])
            hItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.view_create_ui.tbwCreateColumn.setHorizontalHeaderItem(
                i, hItem
            )
        # add row
        if len(self.viewCurrent.columnNewList) > 0:
            row = 0
            for rowItem in self.viewCurrent.columnNewList:
                rItem0 = QPushButton("   Delete")
                rItem0.clicked.connect(self.click_btn_column_new_delete)
                rItem0.setMinimumSize(QSize(80, 24))
                rItem0.setMaximumSize(QSize(80, 24))
                icon = QIcon()
                icon.addFile(
                    ":/images/images/minus.png",
                    QSize(),
                    QIcon.Normal,
                    QIcon.Off,
                )
                rItem0.setIcon(icon)
                rItem1 = QTableWidgetItem(rowItem.column.columnName)
                rItem2 = QTableWidgetItem(
                    rowItem.get_show_by_column_name(rowItem.column.columnName)
                )
                rItem3 = QTableWidgetItem(rowItem.valueBasic1)
                rItem4 = QTableWidgetItem(rowItem.valueBasic2)
                rItem5 = QTableWidgetItem(rowItem.get_str_isagg())
                rItem5.setFlags(
                    Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsUserCheckable
                )
                if rowItem.isAgg:
                    rItem5.setCheckState(Qt.CheckState.Checked)
                else:
                    rItem5.setCheckState(Qt.CheckState.Unchecked)
                self.view_create_ui.tbwCreateColumn.setCellWidget(
                    row, 0, rItem0
                )
                self.view_create_ui.tbwCreateColumn.setItem(row, 1, rItem1)
                self.view_create_ui.tbwCreateColumn.setItem(row, 2, rItem2)
                self.view_create_ui.tbwCreateColumn.setItem(row, 3, rItem3)
                self.view_create_ui.tbwCreateColumn.setItem(row, 4, rItem4)
                self.view_create_ui.tbwCreateColumn.setItem(row, 5, rItem5)
                self.view_create_ui.tbwCreateColumn.cellWidget(
                    row, 0
                ).setContentsMargins(10, 3, 10, 3)
                row += 1
            self.view_create_ui.tbwCreateColumn.setColumnWidth(0, 100)
            self.view_create_ui.tbwCreateColumn.horizontalHeader().setSectionResizeMode(
                1, QHeaderView.ResizeMode.ResizeToContents
            )
            self.view_create_ui.tbwCreateColumn.horizontalHeader().setSectionResizeMode(
                2, QHeaderView.ResizeMode.ResizeToContents
            )
            self.view_create_ui.tbwCreateColumn.horizontalHeader().setSectionResizeMode(
                3, QHeaderView.ResizeMode.ResizeToContents
            )
            self.view_create_ui.tbwCreateColumn.horizontalHeader().setSectionResizeMode(
                4, QHeaderView.ResizeMode.ResizeToContents
            )
            self.view_create_ui.tbwCreateColumn.horizontalHeader().setSectionResizeMode(
                5, QHeaderView.ResizeMode.ResizeToContents
            )

    def change_cbb_columnnew_column(self):
        colName = self.view_create_ui.cbbCreateColumn.currentText()
        self.functionCur = ModuleFunctions.Functions()
        if colName.strip() != "":
            col = self.viewCurrent.get_column_by_name(colName)
            self.functionCur.set_column(col)
        self.enable_columnnew_cbb_column()

    def enable_columnnew_cbb_column(self):
        self.view_create_ui.cbbCreateFunction.clear()
        if self.functionCur.isColumn:
            funNameList = self.dataBasic.get_show_function_with_column(
                self.functionCur
            )
            if len(funNameList) > 0:
                self.view_create_ui.cbbCreateFunction.addItems(funNameList)
                self.view_create_ui.cbbCreateFunction.setCurrentIndex(0)
            self.view_create_ui.cbbCreateFunction.setEnabled(
                len(funNameList) > 0
            )
        else:
            self.view_create_ui.cbbCreateFunction.setEnabled(
                self.functionCur.isColumn
            )

    def change_cbb_columnnew_function(self):
        nameFunShow = self.view_create_ui.cbbCreateFunction.currentText()
        if nameFunShow.strip() != "":
            fun = self.dataBasic.get_function_with_show_name(
                nameFunShow, self.functionCur.column.columnName
            )
            self.functionCur.set_funtion(fun)
        self.enable_columnnew_cbb_function()

    def enable_columnnew_cbb_function(self):
        self.view_create_ui.leCreateValue1.setText(self.functionCur.valueBasic1)
        self.view_create_ui.leCreateValue2.setText(self.functionCur.valueBasic2)
        # enable
        self.view_create_ui.leCreateValue1.setEnabled(
            self.functionCur.numbers >= 2
        )
        self.view_create_ui.leCreateValue2.setEnabled(
            self.functionCur.numbers == 3
        )
        self.view_create_ui.btnCreateAdd.setEnabled(
            self.functionCur.isFunction and not self.functionCur.isUpdate
        )
        self.view_create_ui.btnCreateUpdate.setEnabled(
            self.functionCur.isFunction and self.functionCur.isUpdate
        )

    def click_btn_columnnew_add(self):
        value1 = self.view_create_ui.leCreateValue1.text()
        value2 = self.view_create_ui.leCreateValue2.text()
        try:
            self.functionCur.set_value(value1, value2)
            self.viewCurrent.add_column_new(self.functionCur)
            self.view_create_ui.cbbCreateColumn.setCurrentIndex(0)
            self.loaddata_tbw_columnnew()
            self.loaddata_column_cbb()
        except Exception as e:
            self.show_message(
                3, "Error Add New Column", str(e.__class__.__name__), str(e)
            )

    def click_btn_columnnew_update(self):
        value1 = self.view_create_ui.leCreateValue1.text()
        value2 = self.view_create_ui.leCreateValue2.text()
        try:
            self.functionCur.set_value(value1, value2)
            self.viewCurrent.update_column_new(self.functionCur)
            self.view_create_ui.cbbCreateColumn.setCurrentIndex(0)
            self.loaddata_tbw_columnnew()
            self.loaddata_column_cbb()
        except Exception as e:
            self.show_message(
                3, "Error Update New Column", str(e.__class__.__name__), str(e)
            )

    def itemdoubleclick_columnnew(self, item):
        rowIndex = self.view_create_ui.tbwCreateColumn.row(item)
        colName = self.view_create_ui.tbwCreateColumn.item(rowIndex, 1).text()
        funNameShow = self.view_create_ui.tbwCreateColumn.item(
            rowIndex, 2
        ).text()
        self.view_create_ui.cbbCreateColumn.setCurrentText(colName)
        self.view_create_ui.cbbCreateFunction.setCurrentText(funNameShow)
        self.functionCur = self.viewCurrent.get_function_by_key(
            colName, funNameShow
        )
        self.functionCur.set_update(True)
        self.enable_columnnew_cbb_function()

    def click_btn_column_new_delete(self):
        try:
            btnDelete = self.sender()
            index = self.view_create_ui.tbwCreateColumn.indexAt(btnDelete.pos())
            if index.isValid():
                self.show_message(
                    0,
                    "Delete Column New",
                    "Do you want Column New ?",
                )
                if self.messageBoxButton == QMessageBox.StandardButton.Ok:
                    colName = self.view_create_ui.tbwCreateColumn.item(
                        index.row(), 1
                    ).text()
                    funShowName = self.view_create_ui.tbwCreateColumn.item(
                        index.row(), 2
                    ).text()
                    self.viewCurrent.delete_column_new(colName, funShowName)
                    self.loaddata_tbw_columnnew()
                    self.loaddata_column_cbb()
                    if (
                        colName
                        == self.view_create_ui.cbbCreateColumn.currentText().strip()
                        and funShowName
                        == self.view_create_ui.cbbCreateFunction.currentText().strip()
                    ):
                        self.view_create_ui.cbbCreateColumn.setCurrentIndex(0)
        except Exception as e:
            self.show_message(
                3, "Delete Colum New Error", str(e.__class__.__name__), str(e)
            )

    ##############  FILTER  ######################
    def loaddata_tbw_filter(self):
        hearderTitle = self.sentence.header_table_filter()
        self.view_create_ui.tbwFilter.clear()
        self.view_create_ui.tbwFilter.setColumnCount(len(hearderTitle))
        self.view_create_ui.tbwFilter.setRowCount(
            len(self.viewCurrent.get_calculation_list_all())
        )
        # add header
        for i in range(0, len(hearderTitle)):
            hItem = QTableWidgetItem(hearderTitle[i])
            hItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.view_create_ui.tbwFilter.setHorizontalHeaderItem(i, hItem)
        # add row
        if len(self.viewCurrent.get_calculation_list_all()) > 0:
            row = 0
            for rowItem in self.viewCurrent.get_calculation_list_all():
                rItem0 = QPushButton("   Delete")
                rItem0.clicked.connect(self.click_btn_filter_delete)
                rItem0.setMinimumSize(QSize(80, 24))
                rItem0.setMaximumSize(QSize(80, 24))
                icon = QIcon()
                icon.addFile(
                    ":/images/images/minus.png",
                    QSize(),
                    QIcon.Normal,
                    QIcon.Off,
                )
                rItem0.setIcon(icon)
                rItem1 = QTableWidgetItem(rowItem.columns.columnName)
                rItem2 = QTableWidgetItem(rowItem.get_sql())
                rItem3 = QTableWidgetItem(str(rowItem.valueBasic1))
                rItem4 = QTableWidgetItem(str(rowItem.valueBasic2))
                rItem5 = QTableWidgetItem(rowItem.relation)
                rItem6 = QTableWidgetItem(str(rowItem.level))
                rItem7 = QTableWidgetItem(rowItem.relationWith)
                rItem8 = QTableWidgetItem(rowItem.get_str_isagg())
                self.view_create_ui.tbwFilter.setCellWidget(row, 0, rItem0)
                self.view_create_ui.tbwFilter.setItem(row, 1, rItem1)
                self.view_create_ui.tbwFilter.setItem(row, 2, rItem2)
                self.view_create_ui.tbwFilter.setItem(row, 3, rItem3)
                self.view_create_ui.tbwFilter.setItem(row, 4, rItem4)
                self.view_create_ui.tbwFilter.setItem(row, 5, rItem5)
                self.view_create_ui.tbwFilter.setItem(row, 6, rItem6)
                self.view_create_ui.tbwFilter.setItem(row, 7, rItem7)
                self.view_create_ui.tbwFilter.setItem(row, 8, rItem8)
                self.view_create_ui.tbwFilter.cellWidget(
                    row, 0
                ).setContentsMargins(10, 3, 10, 3)
                row += 1
            self.view_create_ui.tbwFilter.setColumnWidth(0, 100)
            self.view_create_ui.tbwFilter.horizontalHeader().setSectionResizeMode(
                1, QHeaderView.ResizeMode.ResizeToContents
            )
            self.view_create_ui.tbwFilter.horizontalHeader().setSectionResizeMode(
                2, QHeaderView.ResizeMode.ResizeToContents
            )
            self.view_create_ui.tbwFilter.horizontalHeader().setSectionResizeMode(
                3, QHeaderView.ResizeMode.ResizeToContents
            )
            self.view_create_ui.tbwFilter.horizontalHeader().setSectionResizeMode(
                4, QHeaderView.ResizeMode.ResizeToContents
            )
            self.view_create_ui.tbwFilter.horizontalHeader().setSectionResizeMode(
                5, QHeaderView.ResizeMode.ResizeToContents
            )
            self.view_create_ui.tbwFilter.horizontalHeader().setSectionResizeMode(
                6, QHeaderView.ResizeMode.ResizeToContents
            )
            self.view_create_ui.tbwFilter.horizontalHeader().setSectionResizeMode(
                7, QHeaderView.ResizeMode.ResizeToContents
            )
            self.view_create_ui.tbwFilter.horizontalHeader().setSectionResizeMode(
                8, QHeaderView.ResizeMode.ResizeToContents
            )

    def change_cbb_filter_column(self):
        colName = self.view_create_ui.cbbFilterColumn.currentText()
        self.calCur = ModuleCalculations.Calculations()
        if colName.strip() != "":
            col = self.viewCurrent.get_column_by_name(colName)
            self.calCur.set_column(col)
        self.enable_filter_column()

    def enable_filter_column(self):
        self.view_create_ui.cbbFilterCal.clear()
        if self.calCur.isColumn:
            calNameList = self.dataBasic.get_show_calculation(
                self.calCur.columns.columnName
            )
            if len(calNameList) > 0:
                self.view_create_ui.cbbFilterCal.addItems(calNameList)
                self.view_create_ui.cbbFilterCal.setEnabled(
                    len(calNameList) > 0
                )
                self.view_create_ui.cbbFilterCal.setCurrentIndex(0)
        else:
            self.view_create_ui.cbbFilterCal.setEnabled(False)

    def change_cbb_filter_calculation(self):
        calShowName = self.view_create_ui.cbbFilterCal.currentText()
        if calShowName.strip() != "":
            cal = self.dataBasic.get_calculation_with_key(
                self.calCur.columns.columnName, calShowName
            )
            self.calCur.set_calculation(cal)
        self.enable_filter_cal()

    def enable_filter_cal(self):
        # value
        self.view_create_ui.leFilterValue1.setText(str(self.calCur.valueBasic1))
        self.view_create_ui.leFilterValue2.setText(str(self.calCur.valueBasic2))
        self.view_create_ui.cbbFilterRel.clear()
        self.view_create_ui.cbbFilterRel.addItems(["and", "or"])
        self.view_create_ui.cbbFilterRel.setCurrentText(self.calCur.relation)
        self.view_create_ui.spbFilterRelLevel.setMaximum(
            self.viewCurrent.get_level_max(self.calCur.isAgg)
        )
        self.view_create_ui.spbFilterRelLevel.setValue(self.calCur.level)
        self.change_filter_level()
        self.view_create_ui.cbbFilterRelaWith.setCurrentText(
            self.calCur.relationWith
        )
        # enable
        self.view_create_ui.leFilterValue1.setEnabled(self.calCur.numbers >= 2)
        self.view_create_ui.leFilterValue2.setEnabled(self.calCur.numbers == 3)
        self.view_create_ui.cbbFilterRel.setEnabled(self.calCur.isCal)
        self.view_create_ui.spbFilterRelLevel.setEnabled(self.calCur.isCal)
        self.view_create_ui.btnFilterAdd.setEnabled(
            self.calCur.isCal and not self.calCur.isUpdate
        )
        self.view_create_ui.btnFilterUpdate.setEnabled(
            self.calCur.isCal and self.calCur.isUpdate
        )

    def change_filter_level(self):
        self.view_create_ui.cbbFilterRelaWith.clear()
        if self.calCur.isCal:
            level = self.view_create_ui.spbFilterRelLevel.value()
            listWith = self.viewCurrent.get_name_calculation_by_level(
                level, self.calCur.isAgg, self.calCur.get_sql()
            )
            if len(listWith) > 0:
                self.view_create_ui.cbbFilterRelaWith.addItems(listWith)
                self.view_create_ui.cbbFilterRelaWith.setCurrentIndex(0)
            self.view_create_ui.cbbFilterRelaWith.setEnabled(len(listWith) > 0)
        else:
            self.view_create_ui.cbbFilterRelaWith.setEnabled(False)

    def change_spin_filter_level(self):
        self.change_filter_level()

    def click_btn_filter_add(self):
        value1 = self.view_create_ui.leFilterValue1.text()
        value2 = self.view_create_ui.leFilterValue2.text()
        relation = self.view_create_ui.cbbFilterRel.currentText()
        withCal = self.view_create_ui.cbbFilterRelaWith.currentText()
        level = self.view_create_ui.spbFilterRelLevel.value()
        try:
            self.calCur.set_value(value1, value2)
            self.calCur.set_level(level)
            self.calCur.set_relation(relation)
            self.calCur.set_with_cal(withCal)
            self.viewCurrent.add_calculation(self.calCur)
            self.view_create_ui.cbbFilterColumn.setCurrentIndex(0)
            self.loaddata_tbw_filter()
            self.update_sql_sentence()
        except Exception as e:
            self.show_message(
                3, "Add Filter Error", str(e.__class__.__name__), str(e)
            )

    def click_btn_filter_update(self):
        value1 = self.view_create_ui.leFilterValue1.text()
        value2 = self.view_create_ui.leFilterValue2.text()
        relation = self.view_create_ui.cbbFilterRel.currentText()
        withCal = self.view_create_ui.cbbFilterRelaWith.currentText()
        level = self.view_create_ui.spbFilterRelLevel.value()
        try:
            self.calCur.set_value(value1, value2)
            self.calCur.set_level(level)
            self.calCur.set_relation(relation)
            self.calCur.set_with_cal(withCal)
            self.viewCurrent.update_calculation(self.calCur)
            self.view_create_ui.cbbFilterColumn.setCurrentIndex(0)
            self.loaddata_tbw_filter()
            self.update_sql_sentence()
        except Exception as e:
            self.show_message(
                3, "Update Filter Error", str(e.__class__.__name__), str(e)
            )

    def itemdoubleclick_filter(self, item):
        rowIndex = self.view_create_ui.tbwFilter.row(item)
        colName = self.view_create_ui.tbwFilter.item(rowIndex, 1).text()
        calNameShow = self.view_create_ui.tbwFilter.item(rowIndex, 2).text()
        isAgg = self.view_create_ui.tbwFilter.item(rowIndex, 8).text()
        self.view_create_ui.cbbFilterColumn.setCurrentText(colName)
        calUpdate = self.viewCurrent.get_calculation_by_key(
            colName, calNameShow, isAgg
        )
        self.view_create_ui.cbbFilterCal.setCurrentText(
            calUpdate.get_name_show()
        )
        self.calCur = copy.deepcopy(calUpdate)
        self.calCur.set_update(True)
        self.enable_filter_cal()

    def click_btn_filter_delete(self):
        try:
            btnDelete = self.sender()
            index = self.view_create_ui.tbwFilter.indexAt(btnDelete.pos())
            if index.isValid():
                self.show_message(
                    0,
                    "Delete Filter",
                    "Do you want Filter ?",
                )
                if self.messageBoxButton == QMessageBox.StandardButton.Ok:
                    colName = self.view_create_ui.tbwFilter.item(
                        index.row(), 1
                    ).text()
                    calShowName = self.view_create_ui.tbwFilter.item(
                        index.row(), 2
                    ).text()
                    isAgg = self.view_create_ui.tbwFilter.item(index.row(), 8)
                    self.viewCurrent.delete_calculation(
                        colName, calShowName, isAgg
                    )
                    self.loaddata_tbw_filter()
                    self.update_sql_sentence()
                    if (
                        colName
                        == self.view_create_ui.cbbFilterColumn.currentText().strip()
                        and calShowName
                        == self.view_create_ui.cbbFilterCal.currentText().strip()
                    ):
                        self.view_create_ui.cbbFilterColumn.setCurrentIndex(0)
        except Exception as e:
            self.show_message(
                3, "Delete Colum New Error", str(e.__class__.__name__), str(e)
            )

    ###############     MORE    ##############
    def loaddata_more(self):
        self.view_create_ui.cbbMoreType.clear()
        self.view_create_ui.cbbMoreType.addItems(["", "Included", "Excluded"])
        self.view_create_ui.cbbMoreType.setCurrentIndex(0)
        self.view_create_ui.cbbMoreType.setEnabled(True)
        self.loaddata_tbw_more()

    def loaddata_tbw_more(self):
        hearderTitle = self.sentence.header_table_more()
        self.view_create_ui.tbwMore.clear()
        self.view_create_ui.tbwMore.setColumnCount(len(hearderTitle))
        listMore = copy.deepcopy(self.viewCurrent.moreSelected)
        self.view_create_ui.tbwMore.setRowCount(len(listMore))
        # add header
        for i in range(0, len(hearderTitle)):
            hItem = QTableWidgetItem(hearderTitle[i])
            hItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.view_create_ui.tbwMore.setHorizontalHeaderItem(i, hItem)
        # add row
        if len(listMore) > 0:
            row = 0
            for rowItem in listMore:
                rItem0 = QPushButton("   Delete")
                rItem0.clicked.connect(self.click_btn_more_delete)
                rItem0.setMinimumSize(QSize(80, 24))
                rItem0.setMaximumSize(QSize(80, 24))
                icon = QIcon()
                icon.addFile(
                    ":/images/images/minus.png",
                    QSize(),
                    QIcon.Normal,
                    QIcon.Off,
                )
                rItem0.setIcon(icon)
                rItem1 = QTableWidgetItem(rowItem.viewConnect)
                rItem2 = QTableWidgetItem(rowItem.typeMore)
                rItem3 = QTableWidgetItem(rowItem.columnConnect)
                self.view_create_ui.tbwMore.setCellWidget(row, 0, rItem0)
                self.view_create_ui.tbwMore.setItem(row, 1, rItem1)
                self.view_create_ui.tbwMore.setItem(row, 2, rItem2)
                self.view_create_ui.tbwMore.setItem(row, 3, rItem3)
                self.view_create_ui.tbwMore.cellWidget(
                    row, 0
                ).setContentsMargins(10, 3, 10, 3)
                row += 1
            self.view_create_ui.tbwMore.setColumnWidth(0, 100)
            self.view_create_ui.tbwMore.horizontalHeader().setSectionResizeMode(
                1, QHeaderView.ResizeMode.ResizeToContents
            )
            self.view_create_ui.tbwMore.horizontalHeader().setSectionResizeMode(
                2, QHeaderView.ResizeMode.ResizeToContents
            )
            self.view_create_ui.tbwMore.horizontalHeader().setSectionResizeMode(
                3, QHeaderView.ResizeMode.ResizeToContents
            )

    def change_cbb_more_type(self):
        typeMore = self.view_create_ui.cbbMoreType.currentText()
        self.moreViewCurrent = ModuleMores.Mores()
        if typeMore.strip() != "":
            self.loaddata_cbb_view()
            self.moreViewCurrent.set_type(typeMore)
        else:
            self.view_create_ui.cbbMoreView.clear()
        self.view_create_ui.cbbMoreView.setCurrentIndex(0)
        self.view_create_ui.cbbMoreView.setEnabled(
            typeMore.strip() != "" and not self.moreViewCurrent.isUpdate
        )
        self.view_create_ui.cbbMoreColumn.setVisible(
            self.moreViewCurrent.get_int_type() == 1
        )
        self.view_create_ui.label_13.setVisible(
            self.moreViewCurrent.get_int_type() == 1
        )

    def loaddata_cbb_view(self):
        listView = copy.deepcopy(self.dataBasic.moreView)
        listView2 = [
            x for x in listView if x not in self.viewCurrent.get_view_in_more()
        ]
        self.view_create_ui.cbbMoreView.clear()
        if len(listView2) > 0:
            self.view_create_ui.cbbMoreView.addItem("")
            self.view_create_ui.cbbMoreView.addItems(listView2)
            self.view_create_ui.cbbMoreView.setCurrentIndex(0)

    def change_cbb_more_view(self):
        nameView = self.view_create_ui.cbbMoreView.currentText()
        self.view_create_ui.cbbMoreColumn.clear()
        if nameView.strip() != "":
            if self.moreViewCurrent.get_int_type() == 1:
                self.loaddata_column_of_view()
        
        self.view_create_ui.btnMoreAdd.setEnabled(
            nameView.strip() != "" and not self.moreViewCurrent.isUpdate
        )
        self.view_create_ui.btnMoreUpdate.setEnabled(
            nameView.strip() != "" and self.moreViewCurrent.isUpdate
        )

    def loaddata_column_of_view(self):
        try:
            listColumn = self.viewCurrent.get_list_column_name_select()
            self.view_create_ui.cbbMoreColumn.clear()
            if len(listColumn) > 0:
                self.view_create_ui.cbbMoreColumn.addItem("")
                self.view_create_ui.cbbMoreColumn.addItems(listColumn)
            self.view_create_ui.cbbMoreColumn.setEnabled(len(listColumn) > 0)
        except Exception as e:
            self.show_message(
                3,
                "Load Column of View Error",
                str(e.__class__.__name__),
                str(e),
            )

    def click_btn_more_add(self):
        viewName = self.view_create_ui.cbbMoreView.currentText()
        columnName = self.view_create_ui.cbbMoreColumn.currentText()
        try:
            self.moreViewCurrent.set_view(viewName, columnName)
            self.viewCurrent.add_more(self.moreViewCurrent)
            self.loaddata_more()
            self.update_sql_sentence()
        except Exception as e:
            self.show_message(
                3,
                "Add More Error",
                str(e.__class__.__name__),
                str(e),
            )

    def click_btn_more_update(self):
        viewName = self.view_create_ui.cbbMoreView.currentText()
        columnName = self.view_create_ui.cbbMoreColumn.currentText()
        try:
            self.moreViewCurrent.set_view(viewName, columnName)
            self.viewCurrent.update_more(self.moreViewCurrent)
            self.loaddata_more()
            self.update_sql_sentence()
            self.show_message(1, "Update More", "Update More Successful !")
        except Exception as e:
            self.show_message(
                3,
                "Update More Error",
                str(e.__class__.__name__),
                str(e),
            )

    def click_btn_more_delete(self):
        try:
            btnDelete = self.sender()
            index = self.view_create_ui.tbwMore.indexAt(btnDelete.pos())
            if index.isValid():
                self.show_message(
                    0,
                    "Delete More",
                    "Do you want More ?",
                )
                if self.messageBoxButton == QMessageBox.StandardButton.Ok:
                    viewConnect = self.view_create_ui.tbwMore.item(
                        index.row(), 1
                    ).text()
                    typeConnect = self.view_create_ui.tbwMore.item(
                        index.row(), 2
                    ).text()
                    self.viewCurrent.delete_more(viewConnect, typeConnect)
                    self.moreViewCurrent = ModuleMores.Mores()
                    self.loaddata_more()
                    self.update_sql_sentence()
        except Exception as e:
            self.show_message(
                3, "Delete Colum New Error", str(e.__class__.__name__), str(e)
            )

    def click_item_more_tbw(self, item):
        try:
            rowIndex = self.view_create_ui.tbwMore.row(item)
            viewName = self.view_create_ui.tbwMore.item(rowIndex, 1).text()
            typeConnect = self.view_create_ui.tbwMore.item(rowIndex, 2).text()
            moreUpdate = self.viewCurrent.get_more_selected(
                viewName, typeConnect
            )
            self.view_create_ui.cbbMoreType.setCurrentText(typeConnect)
            self.view_create_ui.cbbMoreType.setEnabled(False)
            self.moreViewCurrent = moreUpdate
            self.moreViewCurrent.set_update(True)
            self.view_create_ui.cbbMoreView.addItem(viewName)
            self.view_create_ui.cbbMoreView.setCurrentText(viewName)
            self.view_create_ui.cbbMoreView.setEnabled(False)
            self.view_create_ui.cbbMoreColumn.setCurrentText(
                self.moreViewCurrent.columnConnect
            )
        except Exception as e:
            self.show_message(
                3,
                "Load Item More Error",
                str(e.__class__.__name__),
                str(e),
            )

    ####################    HEADER #########################
    def change_cb_distinct(self):
        if self.view_create_ui.cbViewDuplicate.isChecked():
            self.viewCurrent.set_distinct(True)
        else:
            self.viewCurrent.set_distinct(False)
        self.update_sql_sentence()

    def edit_le_top(self):
        top = self.view_create_ui.leViewTop.text()
        if top.strip() == "":
            self.viewCurrent.set_select_row(0)
        else:
            try:
                value = int(top)
                self.viewCurrent.set_select_row(value)
            except Exception as e:
                self.show_message(
                    3,
                    "Value Top is not type Number",
                    str(e.__class__.__name__),
                    str(e),
                )
        self.update_sql_sentence()

    def click_btn_view_create(self):
        viewName = self.view_create_ui.leViewName.text()
        if viewName.strip() == "":
            self.show_message(
                3,
                "Check Name View",
                "View Name is not blank." "",
            )
        else:
            if self.dataBasic.check_view_name(viewName):
                self.show_message(
                    3,
                    "Check Name View",
                    "View Name is exist." "",
                )
            else:
                self.viewCurrent.set_view_name(viewName)
                try:
                    self.viewCurrent.create()
                    self.show_message(
                        1,
                        "Create View",
                        "Create View successfull, View number: {0}".format(
                            self.viewCurrent.viewNo
                        ),
                    )
                    self.dataBasic.loaddata_view_name_all()
                    self.dataBasic.loaddata_more()
                    self.view_create_ui.cbbViewDataSet.setCurrentIndex(0)
                except Exception as e:
                    self.show_message(
                        3,
                        "Create View Error",
                        str(e.__class__.__name__),
                        str(e),
                    )

    def click_btn_view_duplicate(self):
        self.viewCurrent.set_is_update(False)
        self.dataBasic.loaddata_view_id()
        self.viewCurrent.set_view_no(self.dataBasic.idNew)
        self.view_create_ui.leViewName.setText(self.viewCurrent.viewName)
        self.view_create_ui.leViewId.setText(str(self.viewCurrent.viewNo))
        self.view_create_ui.leViewCreateDate.setText(
            self.viewCurrent.get_create_date()
        )
        self.enable_btn_view_main()

    def click_btn_view_run(self):
        self.view_run_dataset_ui = Ui_frmViewData()
        self.view_run_dataset_widgets = QWidget()
        self.view_run_dataset_ui.setupUi(self.view_run_dataset_widgets)
        try:
            dataView = self.dataBasic.loaddata_30line_dataset(
                self.viewCurrent.dataset.datasetTable
            )
            model = TableViewModel.TableViewModel(dataView)
            self.view_run_dataset_ui.tableView.setModel(model)
            self.view_run_dataset_ui.tableView.setSelectionBehavior(
                QAbstractItemView.SelectionBehavior.SelectRows
            )
            self.view_run_dataset_ui.tableView.resizeColumnsToContents()
            self.view_run_dataset_ui.tableView.resizeRowsToContents()
            self.view_run_dataset_ui.tableView.setSortingEnabled(True)
            self.view_run_dataset_widgets.show()

        except Exception as e:
            self.show_message(
                3,
                "View Data Error",
                str(e.__class__.__name__),
                str(e),
            )

    def click_btn_view_delete(self):
        try:
            self.show_message(
                0,
                "Delete View",
                "Do you want delete View {0} ?".format(
                    self.viewCurrent.viewName
                ),
            )
            if self.messageBoxButton == QMessageBox.StandardButton.Ok:
                self.viewCurrent.delete()
                self.dataBasic.loaddata_view_name_all()
                self.dataBasic.loaddata_more()
                self.view_create_ui.cbbViewDataSet.setCurrentIndex(0)
                self.show_message(
                    1,
                    "Delete View",
                    "Delete view successfull !",
                )

        except Exception as e:
            self.show_message(
                3,
                "Delete View Error",
                str(e.__class__.__name__),
                str(e),
            )

    def edit_le_view_name(self):
        name_new = self.view_create_ui.leViewName.text()
        isCheck = True
        if name_new.strip() != "":
            if name_new.find(" ") >= 0:
                isCheck = False
                self.show_message(
                    3,
                    "Check Name View",
                    "Name of column contain space character",
                )
            if isCheck and not name_new.replace("_", "").isascii():
                isCheck = False
                self.show_message(
                    3,
                    "Check Name View",
                    "Name of column contain special character (not in ASCII)",
                )
            if isCheck and not name_new.replace("_", "").isalnum():
                isCheck = False
                self.show_message(
                    3,
                    "Check Name View",
                    "Name of column contain special character (not in ALPHA)",
                )
            if isCheck and self.dataBasic.check_view_name(name_new):
                isCheck = False
                self.show_message(
                    3, "Check Name View", "Name of View is exist."
                )

            if not isCheck:
                self.view_create_ui.leViewName.setText("")

    def click_btn_view_new(self):
        self.viewCurrent = ModuleViews.Views(self.connects, self.users)
        self.view_create_ui.cbbViewDataSet.setCurrentIndex(0)

    def click_btn_view_update(self):
        try:
            self.viewCurrent.update()
            self.show_message(
                1,
                "Update View",
                "Update View successfull !",
            )
            self.dataBasic.loaddata_view_name_all()
            self.view_create_ui.cbbViewDataSet.setCurrentIndex(0)
        except Exception as e:
            self.show_message(
                3,
                "Update View Error",
                str(e.__class__.__name__),
                str(e),
            )

    def click_btn_tab_select_column(self):
        self.view_create_ui.stackedWidget.setCurrentIndex(0)
        self.change_tab_view_create(0)

    def click_btn_tab_create_column(self):
        self.view_create_ui.stackedWidget.setCurrentIndex(1)
        self.change_tab_view_create(1)

    def click_btn_tab_column_plus(self):
        self.view_create_ui.stackedWidget.setCurrentIndex(2)
        self.change_tab_view_create(2)

    def click_btn_tab_filter(self):
        self.view_create_ui.stackedWidget.setCurrentIndex(3)
        self.change_tab_view_create(3)

    def click_btn_tab_sort(self):
        self.view_create_ui.stackedWidget.setCurrentIndex(4)
        self.change_tab_view_create(4)

    def click_btn_tab_more(self):
        self.view_create_ui.stackedWidget.setCurrentIndex(5)
        self.change_tab_view_create(5)

    def click_btn_tab_sql(self):
        self.view_create_ui.stackedWidget.setCurrentIndex(6)
        self.change_tab_view_create(6)

    def change_tab_view_create(self, index):
        self.view_create_ui.btnTabSelectColumn.setEnabled(index != 0)
        self.view_create_ui.btnTabCreateColumn.setEnabled(index != 1)
        self.view_create_ui.btnTabColumnPlus.setEnabled(index != 2)
        self.view_create_ui.btnTabColumnPlus.setEnabled(False)
        self.view_create_ui.btnTabFilter.setEnabled(index != 3)
        self.view_create_ui.btnTabSort.setEnabled(index != 4)
        self.view_create_ui.btnTabMore.setEnabled(index != 5)
        self.view_create_ui.btnTabSql.setEnabled(index != 6)

    def menu_view_run(self):
        self.refresh_var_global()
        self.view_run_ui = Ui_frmRunView()
        self.view_run_widgets = QWidget()
        self.view_run_ui.setupUi(self.view_run_widgets)
        self.ui.scrollArea.setWidget(self.view_run_widgets)
        try:
            self.dataBasic.initdata_run()
            self.enable_menu_by_index(2)

            # load data to cbb
            self.loaddata_cbb_run()
            self.view_run_ui.cbbRunView.currentIndexChanged.connect(
                self.change_cbb_run
            )
            self.view_run_ui.btnRunRun.clicked.connect(self.click_btn_run)
            self.view_run_ui.btnRunExport.clicked.connect(self.click_btn_export)

            # disvisiable
            self.view_run_ui.leRunSearch.setVisible(False)
            self.view_run_ui.cbbRunMore.setVisible(False)
            self.view_run_ui.cbbRunWithCol.setVisible(False)
            self.view_run_ui.label_6.setVisible(False)
            self.view_run_ui.label_4.setVisible(False)
            self.view_run_ui.label_7.setVisible(False)
            self.view_run_ui.widget_4.setVisible(False)
        except Exception as e:
            self.show_message(
                3,
                "Load Data Run Error",
                str(e.__class__.__name__),
                str(e),
            )

    def loaddata_cbb_run(self):
        self.dataBasic.loaddata_view_run()
        self.view_run_ui.cbbRunView.clear()
        self.view_run_ui.cbbRunView.addItems(self.dataBasic.get_all_view_run())
        self.view_run_ui.cbbRunView.setCurrentIndex(0)
        self.view_run_ui.cbbRunView.setEnabled(
            len(self.dataBasic.get_all_view_run()) > 0
        )

    def change_cbb_run(self):
        self.viewRun = ModuleViewAction.ViewAction()
        nameView = self.view_run_ui.cbbRunView.currentText()
        if nameView.strip() != "":
            self.viewRun.set_view(self.dataBasic.get_view_run_by_name(nameView))

        self.enable_cbb_run()

    def enable_cbb_run(self):
        self.view_run_ui.leRunDataSet.setText(self.viewRun.datasetName)
        self.view_run_ui.leRunTotalCol.setText("")
        self.view_run_ui.leRunTotalRow.setText("")
        self.view_run_ui.btnRunExport.setEnabled(False)
        self.view_run_ui.btnRunRun.setEnabled(self.viewRun.isDataRelease)
        self.view_run_ui.tbwRun.setModel(None)
        self.view_run_ui.tbwRun.setEnabled(False)

    def click_btn_run(self):
        try:
            view = ModuleViews.Views(self.connects, self.users)
            self.dataBasic.run(
                view.run_sql(self.viewRun.viewNo, self.dataBasic)
            )
            dataRun = copy.deepcopy(self.dataBasic.dataRun)
            model = TableViewModel.TableViewModel(dataRun)
            self.view_run_ui.tbwRun.setModel(model)
            self.view_run_ui.tbwRun.setSelectionBehavior(
                QAbstractItemView.SelectionBehavior.SelectRows
            )
            self.view_run_ui.tbwRun.resizeColumnsToContents()
            self.view_run_ui.tbwRun.resizeRowsToContents()
            self.view_run_ui.tbwRun.setEnabled(True)
            self.view_run_ui.leRunTotalCol.setText(str(len(dataRun.columns)))
            self.view_run_ui.leRunTotalRow.setText(str(len(dataRun)))
            self.view_run_ui.btnRunExport.setEnabled(True)
        except Exception as e:
            self.show_message(
                3,
                "Run View Error",
                str(e.__class__.__name__),
                str(e),
            )

    def click_btn_export(self):
        try:
            if len(self.dataBasic.dataRun) > 0:
                file_filter = "Excel File (*.xlsx);; Data File (*.csv)"
                response = QFileDialog.getSaveFileName(
                    parent=self,
                    caption="Save to file",
                    filter=file_filter,
                    selectedFilter="Excel File (*.xlsx)",
                )
                if len(response[0]) > 0:
                    self.dataBasic.exportToFile(response)
                    self.show_message(
                        1,
                        "Export Data",
                        "Export Data Successfull. Link: {0}".format(
                            str(response[0])
                        ),
                    )
            else:
                self.show_message(
                    2,
                    "Export Data",
                    "Not Found Data",
                )
        except Exception as e:
            self.show_message(
                3,
                "Export Data Error",
                str(e.__class__.__name__),
                str(e),
            )

    def menu_view_release(self):
        self.refresh_var_global()
        self.view_release_ui = Ui_frmRelease()
        self.view_release_widgets = QWidget()
        self.view_release_ui.setupUi(self.view_release_widgets)
        self.ui.scrollArea.setWidget(self.view_release_widgets)
        try:
            self.dataBasic.initdate_release()
            self.enable_menu_by_index(3)

            # load data
            self.loaddata_cbb_release()
            # event
            self.view_release_ui.btnReleaseAdd.clicked.connect(
                self.click_btn_release
            )
            self.view_release_ui.cbbReleaseView.currentIndexChanged.connect(
                self.change_cbb_release
            )
        except Exception as e:
            self.show_message(
                3,
                "Load Data Release Error",
                str(e.__class__.__name__),
                str(e),
            )

    def loaddata_cbb_release(self):
        self.dataBasic.loaddata_view_release()
        self.view_release_ui.cbbReleaseView.clear()
        self.view_release_ui.cbbReleaseView.addItems(
            self.dataBasic.get_all_view_release()
        )
        self.view_release_ui.cbbReleaseView.setCurrentIndex(0)
        self.view_release_ui.cbbReleaseView.setEnabled(
            len(self.dataBasic.get_all_view_release()) > 0
        )

    def change_cbb_release(self):
        self.viewAction = ModuleViewAction.ViewAction()
        viewName = self.view_release_ui.cbbReleaseView.currentText()
        if viewName.strip() != "":
            self.viewAction.set_view(
                self.dataBasic.get_view_release_by_name(viewName)
            )
        self.enable_cbb_release()

    def enable_cbb_release(self):
        self.view_release_ui.leReleaseViewNo.setText(
            str(self.viewAction.viewNo)
        )
        self.view_release_ui.leReleaseViewStatus.setText(
            self.viewAction.get_str_status()
        )
        self.view_release_ui.leReleaseStatus.setText(
            self.viewAction.get_str_release()
        )
        self.view_release_ui.leReleaseInDB.setText(
            self.viewAction.get_str_indb()
        )
        self.view_release_ui.leReleaseViewNo.setEnabled(False)
        self.view_release_ui.leReleaseViewStatus.setEnabled(False)
        self.view_release_ui.leReleaseStatus.setEnabled(False)
        self.view_release_ui.leReleaseInDB.setEnabled(False)
        self.view_release_ui.btnReleaseAdd.setEnabled(
            self.viewAction.get_status_btn_release()
        )

    def click_btn_release(self):
        try:
            self.show_message(
                0,
                "Release View",
                "Do you want {0} View: {1} in database ?".format(
                    self.viewAction.get_str_status(), self.viewAction.viewName
                ),
            )
            if self.messageBoxButton == QMessageBox.StandardButton.Ok:
                viewRelease = ModuleViews.Views(self.connects, self.users)
                viewRelease.set_view_release(self.viewAction)
                viewRelease.release(self.dataBasic)
                self.dataBasic.loaddata_view_release()
                self.view_release_ui.cbbReleaseView.setCurrentIndex(0)
        except Exception as e:
            self.show_message(
                3,
                "Release View Error",
                str(e.__class__.__name__),
                str(e),
            )

    #################### CHANGE PASSWORD ###############
    def menu_change_password(self):
        self.refresh_var_global()
        self.system_change_password_ui = Ui_ChangePassword()
        self.system_change_password_widgets = QWidget()
        self.system_change_password_ui.setupUi(
            self.system_change_password_widgets
        )
        self.ui.scrollArea.setWidget(self.system_change_password_widgets)
        self.enable_menu_by_index(4)

        self.system_change_password_ui.btnChange.clicked.connect(
            self.click_btn_change_password
        )

    def click_btn_change_password(self):
        passwordCur = self.system_change_password_ui.lePasswordCur.text()
        passwordNew = self.system_change_password_ui.lePasswordNew.text()
        passwordConfirm = (
            self.system_change_password_ui.lePasswordConfirm.text()
        )
        try:
            self.users.change_password(
                passwordCur, passwordNew, passwordConfirm
            )
            self.show_message(
                1,
                "Change Password",
                "Change Password successfull.",
            )
            self.system_change_password_ui.lePasswordCur.setText("")
            self.system_change_password_ui.lePasswordNew.setText("")
            self.system_change_password_ui.lePasswordConfirm.setText("")
        except Exception as e:
            self.show_message(
                3,
                "Change Password Error",
                str(e.__class__.__name__),
                str(e),
            )

    ############### CREATE USER ###########################
    def menu_user_create(self):
        self.refresh_var_global()
        self.system_create_user_ui = Ui_CreateUser()
        self.system_create_user_widgets = QWidget()
        self.system_create_user_ui.setupUi(self.system_create_user_widgets)
        self.ui.scrollArea.setWidget(self.system_create_user_widgets)
        self.enable_menu_by_index(5)
        try:
            self.dataBasic.initdata_create_user()
            self.userNew = ModuleUsers.Users(self.connects)
            self.loaddata_user_create()
        except Exception as e:
            self.show_message(
                3,
                "Load data Dept Error",
                str(e.__class__.__name__),
                str(e),
            )

        # define event
        self.system_create_user_ui.btnAdd.clicked.connect(
            self.click_btn_user_add
        )
        self.system_create_user_ui.btnUpdate.clicked.connect(
            self.click_btn_user_update
        )
        self.system_create_user_ui.btnSearch.clicked.connect(
            self.click_btn_user_search
        )
        self.system_create_user_ui.btnNew.clicked.connect(
            self.click_btn_user_new
        )
        self.system_create_user_ui.btnChangePassword.clicked.connect(
            self.click_btn_user_change_password
        )

    def loaddata_user_create(self):
        self.system_create_user_ui.cbbDept.clear()
        self.system_create_user_ui.cbbDept.addItems(
            self.dataBasic.get_dept_name()
        )
        self.system_create_user_ui.leUserName.setText(self.userNew.user)
        self.system_create_user_ui.lePassword.setText(self.userNew.password)
        self.system_create_user_ui.lePasswordConfirm.setText(
            self.userNew.password
        )
        self.system_create_user_ui.leEmail.setText(self.userNew.email)
        self.system_create_user_ui.leFullName.setText(self.userNew.fullname)
        self.system_create_user_ui.lePhoneNumber.setText(self.userNew.phone)
        self.system_create_user_ui.cbbDept.setCurrentText(
            self.userNew.department
        )
        self.system_create_user_ui.cbbPermission.setCurrentText(
            self.userNew.permission
        )
        self.system_create_user_ui.cbActive.setChecked(self.userNew.status)

        self.system_create_user_ui.leUserName.setEnabled(
            not self.userNew.isUpdate
        )
        self.system_create_user_ui.btnAdd.setEnabled(not self.userNew.isUpdate)
        self.system_create_user_ui.btnUpdate.setEnabled(self.userNew.isUpdate)
        self.system_create_user_ui.btnSearch.setEnabled(
            not self.userNew.isUpdate
        )
        self.system_create_user_ui.btnNew.setEnabled(True)
        self.system_create_user_ui.lePassword.setEnabled(
            not self.userNew.isUpdate
        )
        self.system_create_user_ui.lePasswordConfirm.setEnabled(
            not self.userNew.isUpdate
        )
        self.system_create_user_ui.btnChangePassword.setEnabled(
            self.userNew.isUpdate
        )

    def click_btn_user_add(self):
        userName = self.system_create_user_ui.leUserName.text()
        password = self.system_create_user_ui.lePassword.text()
        passwordConfirm = self.system_create_user_ui.lePasswordConfirm.text()
        email = self.system_create_user_ui.leEmail.text()
        fullName = self.system_create_user_ui.leFullName.text()
        phone = self.system_create_user_ui.lePhoneNumber.text()
        depts = self.system_create_user_ui.cbbDept.currentText()
        per = self.system_create_user_ui.cbbPermission.currentText()
        status = self.system_create_user_ui.cbActive.isChecked()
        try:
            userNo = self.userNew.add(
                userName,
                password,
                passwordConfirm,
                email,
                fullName,
                phone,
                depts,
                per,
                status,
            )
            self.show_message(
                1,
                "Add User",
                "Add user successfull. UserNo: " + str(userNo),
            )
            self.click_btn_user_new()
        except Exception as e:
            self.show_message(
                3,
                "Add User Error",
                str(e.__class__.__name__),
                str(e),
            )

    def click_btn_user_update(self):
        userName = self.system_create_user_ui.leUserName.text()
        password = self.system_create_user_ui.lePassword.text()
        passwordConfirm = self.system_create_user_ui.lePasswordConfirm.text()
        email = self.system_create_user_ui.leEmail.text()
        fullName = self.system_create_user_ui.leFullName.text()
        phone = self.system_create_user_ui.lePhoneNumber.text()
        depts = self.system_create_user_ui.cbbDept.currentText()
        per = self.system_create_user_ui.cbbPermission.currentText()
        status = self.system_create_user_ui.cbActive.isChecked()
        try:
            self.userNew.update(
                userName,
                password,
                passwordConfirm,
                email,
                fullName,
                phone,
                depts,
                per,
                status,
            )
            self.show_message(
                1,
                "Update User",
                "Update user successfull",
            )
            self.click_btn_user_new()
        except Exception as e:
            self.show_message(
                3,
                "Update User Error",
                str(e.__class__.__name__),
                str(e),
            )

    def click_btn_user_search(self):
        userName = self.system_create_user_ui.leUserName.text()
        if userName.strip() != "":
            try:
                self.userNew = self.dataBasic.get_user_by_name(userName)
                self.userNew.set_update(True)
                self.loaddata_user_create()
            except Exception as e:
                self.show_message(
                    3,
                    "Search User Error",
                    str(e.__class__.__name__),
                    str(e),
                )

    def click_btn_user_change_password(self):
        self.system_create_user_ui.lePasswordConfirm.setEnabled(True)
        self.system_create_user_ui.lePassword.setEnabled(True)

    def click_btn_user_new(self):
        self.userNew = ModuleUsers.Users(self.connects)
        self.loaddata_user_create()

    ###################     CREATE VIEW MANUAL #######################
    def menu_view_create_manual(self):
        self.refresh_var_global()
        self.view_manual_ui = Ui_CreateManual()
        self.view_manual_widgets = QWidget()
        self.view_manual_ui.setupUi(self.view_manual_widgets)
        self.ui.scrollArea.setWidget(self.view_manual_widgets)
        self.enable_menu_by_index(6)
        try:
            self.viewManual = ModuleViewManuals.ViewManuals(
                self.connects, self.users
            )
            self.loaddata_create_manual()

            # define event
            self.view_manual_ui.btnTest.clicked.connect(
                self.click_btn_manual_test
            )
            self.view_manual_ui.btnCreate.clicked.connect(
                self.click_btn_manual_create
            )
            self.view_manual_ui.btnUpdate.clicked.connect(
                self.click_btn_manual_update
            )
            self.view_manual_ui.btnRun.clicked.connect(
                self.click_btn_manual_run
            )
            self.view_manual_ui.btnRelease.clicked.connect(
                self.click_btn_manual_release
            )
            self.view_manual_ui.btnDelete.clicked.connect(
                self.click_btn_manual_delete
            )
            self.view_manual_ui.btnNew.clicked.connect(
                self.click_btn_manual_new
            )
            self.view_manual_ui.btnSearch.clicked.connect(
                self.click_btn_manual_search
            )
            self.view_manual_ui.leViewName.editingFinished.connect(
                self.edit_le_manual_view_name
            )

        except Exception as e:
            self.show_message(
                3,
                "Load data Dept Error",
                str(e.__class__.__name__),
                str(e),
            )

    def loaddata_create_manual(self):
        self.view_manual_ui.pltSql.setPlainText(
            self.viewManual.get_sql_string()
        )
        self.view_manual_ui.leViewName.setText(self.viewManual.viewName)
        self.view_manual_ui.leStatusView.setText(
            self.viewManual.get_str_status()
        )
        self.view_manual_ui.leStatusRelease.setText(
            self.viewManual.get_str_release()
        )
        self.view_manual_ui.leStatusDatabase.setText(
            self.viewManual.get_str_indb()
        )

        self.view_manual_ui.btnTest.setEnabled(True)
        self.view_manual_ui.btnSearch.setEnabled(not self.viewManual.isUpdate)
        self.view_manual_ui.btnCreate.setEnabled(not self.viewManual.isUpdate)
        self.view_manual_ui.btnUpdate.setEnabled(self.viewManual.isUpdate)
        self.view_manual_ui.btnDelete.setEnabled(self.viewManual.isUpdate)
        self.view_manual_ui.btnRelease.setEnabled(
            not self.viewManual.releaseStatus and self.viewManual.isUpdate
        )
        self.view_manual_ui.btnRun.setEnabled(True)
        self.view_manual_ui.btnNew.setEnabled(True)
        self.view_manual_ui.leViewName.setEnabled(not self.viewManual.isUpdate)
        self.view_manual_ui.leStatusView.setEnabled(False)
        self.view_manual_ui.leStatusRelease.setEnabled(False)
        self.view_manual_ui.leStatusDatabase.setEnabled(False)

    def click_btn_manual_test(self):
        sqlManual = self.view_manual_ui.pltSql.toPlainText()
        if sqlManual.strip() != "":
            try:
                self.viewManual.sql_run_test(sqlManual)
                self.show_message(
                    1,
                    "Run Test SQL",
                    "Test SQL Successfull !",
                )
            except Exception as e:
                self.show_message(
                    3,
                    "Run Test SQL Error",
                    str(e.__class__.__name__),
                    str(e),
                )
        else:
            self.show_message(
                2,
                "SQL sentence",
                "Please input SQL",
            )

    def click_btn_manual_create(self):
        viewName = self.view_manual_ui.leViewName.text()
        sqlString = self.view_manual_ui.pltSql.toPlainText()
        if viewName.strip() != "" and sqlString.strip() != "":
            try:
                self.viewManual.set_view_name(viewName)
                self.viewManual.set_sql_string(sqlString)
                viewNo = self.viewManual.create()
                self.show_message(
                    1,
                    "Create View Manual",
                    "Create View Successfull. View Manual No: {0} ".format(
                        viewNo
                    ),
                )
                self.viewManual = ModuleViewManuals.ViewManuals(
                    self.connects, self.users
                )
                self.loaddata_create_manual()
            except Exception as e:
                self.show_message(
                    3,
                    "Create View Manual Error",
                    str(e.__class__.__name__),
                    str(e),
                )

    def click_btn_manual_update(self):
        sqlString = self.view_manual_ui.pltSql.toPlainText()
        if sqlString.strip() != "":
            try:
                self.viewManual.set_sql_string(sqlString)
                self.viewManual.update()
                self.show_message(
                    1, "Update View Manual", "Update View Manual Successfull !"
                )
                self.view_manual_ui.btnRelease.setEnabled(
                    not self.viewManual.releaseStatus
                    and self.viewManual.isUpdate
                )
            except Exception as e:
                self.show_message(
                    3,
                    "Update View Manual Error",
                    str(e.__class__.__name__),
                    str(e),
                )

    def click_btn_manual_run(self):
        sqlManual = self.view_manual_ui.pltSql.toPlainText()
        self.dataResult = pd.DataFrame()
        if sqlManual.strip() != "":
            try:
                self.dataResult = self.viewManual.sql_run(sqlManual)
                self.load_frm_result()
            except Exception as e:
                self.show_message(
                    3,
                    "Run SQL Error",
                    str(e.__class__.__name__),
                    str(e),
                )
        else:
            self.show_message(
                2,
                "SQL sentence",
                "Please input SQL",
            )

    def load_frm_result(self):
        self.run_result_ui = Ui_ShowResult()
        self.run_result_widgets = QDialog()
        self.run_result_ui.setupUi(self.run_result_widgets)
        try:
            self.loaddata_result()
            self.run_result_ui.btnExport.clicked.connect(
                self.click_btn_result_export
            )
            self.run_result_widgets.exec()
        except Exception as e:
            self.show_message(
                3, "Load Result Error", str(e.__class__.__name__), str(e)
            )

    def loaddata_result(self):
        model = TableViewModel.TableViewModel(self.dataResult)
        self.run_result_ui.tbwResult.setModel(model)
        self.run_result_ui.tbwResult.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.run_result_ui.tbwResult.resizeColumnsToContents()
        self.run_result_ui.tbwResult.resizeRowsToContents()
        self.run_result_ui.tbwResult.setSortingEnabled(True)
        self.run_result_ui.leColumn.setText(str(len(self.dataResult.columns)))
        self.run_result_ui.leRow.setText(str(len(self.dataResult)))

    def click_btn_result_export(self):
        try:
            if len(self.dataResult) > 0:
                file_filter = "Excel File (*.xlsx);; Data File (*.csv)"
                response = QFileDialog.getSaveFileName(
                    parent=self,
                    caption="Save to file",
                    filter=file_filter,
                    selectedFilter="Excel File (*.xlsx)",
                )
                if len(response[0]) > 0:
                    self.dataBasic.exportToFileData(self.dataResult, response)
                    self.show_message(
                        1,
                        "Export Data",
                        "Export Data Successfull. Link: {0}".format(
                            str(response[0])
                        ),
                    )
            else:
                self.show_message(
                    2,
                    "Export Data",
                    "Not Found Data",
                )
        except Exception as e:
            self.show_message(
                3,
                "Export Data Error",
                str(e.__class__.__name__),
                str(e),
            )

    def click_btn_manual_release(self):
        try:
            self.viewManual.release()
            self.viewManual = ModuleViewManuals.ViewManuals(
                self.connects, self.users
            )
            self.show_message(
                1, "Release View Manual", "Release View Manual Successfull !"
            )
            self.loaddata_create_manual()
        except Exception as e:
            self.show_message(
                3,
                "Release View Manual Error",
                str(e.__class__.__name__),
                str(e),
            )

    def click_btn_manual_delete(self):
        try:
            self.viewManual.delete()
            self.viewManual = ModuleViewManuals.ViewManuals(
                self.connects, self.users
            )
            self.show_message(
                1, "Delete View Manual", "Delete View Manual Successfull !"
            )
            self.loaddata_create_manual()
        except Exception as e:
            self.show_message(
                3,
                "Delete View Manual Error",
                str(e.__class__.__name__),
                str(e),
            )

    def click_btn_manual_new(self):
        self.viewManual = ModuleViewManuals.ViewManuals(
            self.connects, self.users
        )
        self.loaddata_create_manual()

    def click_btn_manual_search(self):
        nameNew = self.view_manual_ui.leViewName.text()
        if nameNew.strip() != "":
            try:
                dataView = self.dataBasic.get_view_manual_by_search(nameNew)
                self.load_search_manual(dataView)
            except Exception as e:
                self.show_message(
                    3,
                    "Search View Error",
                    str(e.__class__.__name__),
                    str(e),
                )

    def load_search_manual(self, data):
        self.search_view_manual_ui = Ui_DialogSearch()
        self.search_view_manual_widgets = QDialog()
        self.search_view_manual_ui.setupUi(self.search_view_manual_widgets)
        self.search_view_manual_ui.tbwSearch.itemClicked.connect(
            self.itemclick_tbw_search_manual
        )
        self.search_view_manual_ui.buttonBox.clicked.connect(
            self.click_search_manual_button
        )
        self.search_view_manual_ui.tbwSearch.itemDoubleClicked.connect(
            self.double_itemclick_search_manual
        )
        self.loaddate_search_manual(data)
        self.search_view_manual_widgets.exec()

    def loaddate_search_manual(self, data):
        self.search_view_manual_ui.tbwSearch.clear()
        if len(data) > 0:
            self.search_view_manual_ui.tbwSearch.setColumnCount(1)
            hItem0 = QTableWidgetItem("View Name")
            hItem0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.search_view_manual_ui.tbwSearch.setHorizontalHeaderItem(
                0, hItem0
            )
            rows = len(data)
            self.search_view_manual_ui.tbwSearch.setRowCount(rows)
            for row in range(0, rows):
                rItem0 = QTableWidgetItem(str(data.loc[row].iloc[0]))
                self.search_view_manual_ui.tbwSearch.setItem(row, 0, rItem0)
            self.search_view_manual_ui.tbwSearch.setEditTriggers(
                QAbstractItemView.NoEditTriggers
            )
            self.search_view_manual_ui.tbwSearch.setSelectionBehavior(
                QAbstractItemView.SelectRows
            )
            self.search_view_manual_ui.tbwSearch.horizontalHeader().setSectionResizeMode(
                0, QHeaderView.ResizeMode.ResizeToContents
            )
        self.search_view_manual_ui.cbSeachID.setVisible(False)
        self.search_view_manual_ui.cbSearchName.setVisible(False)
        self.search_view_manual_ui.leSearch.setVisible(False)
        self.search_view_manual_ui.label.setVisible(False)

    def itemclick_tbw_search_manual(self, item):
        try:
            row = self.search_view_manual_ui.tbwSearch.row(item)
            self.updateViewManual = ModuleViewManuals.ViewManuals(
                self.connects, self.users
            )
            self.updateViewManual.set_view_name(
                self.search_view_manual_ui.tbwSearch.item(row, 0).text()
            )
            self.search_view_manual_ui.buttonBox.setEnabled(
                self.updateViewManual.viewName != str()
            )
        except Exception as e:
            self.show_message(
                3, "Select View Error", str(e.__class__.__name__), str(e)
            )

    def click_search_manual_button(self, button):
        if (
            self.search_view_manual_ui.buttonBox.buttonRole(button)
            == QDialogButtonBox.ButtonRole.AcceptRole
        ):
            self.search_view_manual_widgets.accept()
            self.loaddata_view_manual_update()
        else:
            self.search_view_manual_widgets.reject()

    def double_itemclick_search_manual(self):
        self.search_view_manual_widgets.accept()
        self.loaddata_view_manual_update()

    def loaddata_view_manual_update(self):
        try:
            self.updateViewManual.loadData(
                self.dataBasic.loaddata_view_manual(
                    self.updateViewManual.viewName
                )
            )
            self.viewManual = copy.deepcopy(self.updateViewManual)
            self.viewManual.set_update(True)
            self.loaddata_create_manual()
            self.updateViewManual = ModuleViewManuals.ViewManuals(
                self.connects, self.users
            )
        except Exception as e:
            self.show_message(
                3,
                "Load info View Manual Error",
                str(e.__class__.__name__),
                str(e),
            )

    def edit_le_manual_view_name(self):
        nameNew = self.view_manual_ui.leViewName.text()
        isCheck = True
        if nameNew.strip() != "":
            if nameNew.find(" ") >= 0:
                isCheck = False
                self.show_message(
                    3,
                    "Check Name View",
                    "Name of column contain space character",
                )
            if isCheck and not nameNew.replace("_", "").isascii():
                isCheck = False
                self.show_message(
                    3,
                    "Check Name View",
                    "Name of column contain special character (not in ASCII)",
                )
                """
            if isCheck and not nameNew.replace("_", "").isalnum():
                isCheck = False
                self.show_message(
                    3,
                    "Check Name View",
                    "Name of column contain special character (not in ALPHA)",
                )"""
            if isCheck and self.dataBasic.check_view_name(nameNew):
                isCheck = False
                self.show_message(
                    3, "Check Name View", "Name of View is exist."
                )

            if not isCheck:
                self.view_manual_ui.leViewName.setText("")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
