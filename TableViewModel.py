# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QAbstractTableModel, Qt
import pandas as pd

class TableViewModel(QAbstractTableModel):
   def __init__(self, data = pd.DataFrame(), parent = None):
      QAbstractTableModel.__init__(self, parent)
      self._data = data

   def data(self, index, role):
      if role == Qt.ItemDataRole.DisplayRole:
         value = self._data.iloc[index.row(), index.column()]
         return str(value)

   def rowCount(self, index):
      return self._data.shape[0]

   def columnCount(self, index):
      return self._data.shape[1]

   def headerData(self, section, orientation, role):
      # section is the index of the column/row.
      if role == Qt.ItemDataRole.DisplayRole:
         if orientation == Qt.Orientation.Horizontal:
            return str(self._data.columns[section])

         if orientation == Qt.Orientation.Vertical:
            return str(self._data.index[section])
