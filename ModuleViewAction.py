# This Python file uses the following encoding: utf-8


class ViewAction:
    def __init__(self):
        self.viewNo = int()
        self.viewName = str()
        self.viewStatus = int()
        self.isRelease = False
        self.datasetNo = int()
        self.datasetName = str()
        self.datasetTable = str()
        self.isDataRelease = False
        self.isInDB = False

    def set_data(self, view):
        self.viewNo = int(view.viewno)
        self.viewName = str(view.viewname)
        self.viewStatus = int(view.viewstatus)
        self.set_release(view.releasestatus)
        self.datasetNo = int(view.datasetno)
        self.datasetName = view.datasetname
        self.datasetTable = view.datasettable
        self.set_indb(view.indb)

    def set_view(self, view):
        self.viewNo = view.viewNo
        self.viewName = view.viewName
        self.viewStatus = view.viewStatus
        self.isRelease = view.isRelease
        self.datasetNo = view.datasetNo
        self.datasetName = view.datasetName
        self.datasetTable = view.datasetTable
        self.isDataRelease = True
        self.isInDB = view.isInDB

    def set_release(self, index):
        if index == 1:
            self.isRelease = False
        else:
            self.isRelease = True

    def get_str_release(self):
        if self.isDataRelease:
            if self.isRelease:
                return "Release"
            else:
                return "Pending"
        else:
            return ""

    def get_str_status(self):
        if self.viewStatus == 1:
            return "Create"
        elif self.viewStatus == 2:
            return "Update"
        elif self.viewStatus == 3:
            return "Delete"
        else:
            return ""

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

    def get_status_btn_release(self):
        return self.isDataRelease and not self.isRelease
