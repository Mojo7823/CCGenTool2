from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QInputDialog, QMenu
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem, QGuiApplication
from ui.xml_parser_ui import Ui_xml_parser_window
from xml_parser_model import XmlItemModel
from xml_parser_insertdb import insert_to_db_combined
from xml_parser_insertealdb import inserteal_to_db_combined
import sys


class xml_parser_mainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_xml_parser_window()
        self.ui.setupUi(self)

        # ask user for location of db.xml file
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("XML files (*.xml)")
        file_dialog.setWindowTitle("Select db.xml file")
        if file_dialog.exec():
            xml_file = file_dialog.selectedFiles()[0]
        else:
            QMessageBox.critical(self, "Error", "Could not find db.xml file.")


        self.xml_model = XmlItemModel(xml_file)
        self.ui.treeView.setModel(self.xml_model)
        self.list_model = QStandardItemModel()
        self.ui.treeView.clicked.connect(self.on_treeView_clicked)

        self.ui.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.treeView.customContextMenuRequested.connect(self.on_context_menu_requested)
        self.ui.path_input_button.clicked.connect(self.on_path_input_button_clicked)
        self.ui.insertsfr_button.clicked.connect(self.on_insert_button_clicked)
        self.ui.inserteal_button.clicked.connect(self.on_inserteal_button_clicked)

    def on_insert_button_clicked(self):
        insert_to_db_combined('resources/cc_db.sqlite', self.xml_model)

    def on_inserteal_button_clicked(self):
        inserteal_to_db_combined('resources/cc_db.sqlite', self.xml_model)
        

    def on_treeView_clicked(self, index: QModelIndex):
        item = self.xml_model.itemFromIndex(index)
        data = item.data(Qt.DisplayRole)
        self.list_model.clear()
        list_item = QStandardItem(data)
        self.list_model.appendRow(list_item)
        self.ui.listView.setModel(self.list_model)
        
    def on_path_input_button_clicked(self):
        path, ok = QInputDialog.getText(self, 'Enter Path', 'Enter a path:')
        if ok:
            # Traverse the tree until we find the desired node
            item = self.xml_model.root_item
            for part in path.split('>'):
                for row in range(item.rowCount()):
                    child = item.child(row)
                    if child.data(Qt.DisplayRole) == part:
                        item = child
                        break
                else:
                    print(f"No item found for path: {path}")
                    return

            # Print all the available items in the node
            print("Path:", path)
            self.print_all_items(item)

    def print_all_items(self, item):
        if not item.hasChildren():
            print("Data:", item.data(Qt.DisplayRole))
        else:
            for row in range(item.rowCount()):
                child = item.child(row)
                if not child.hasChildren():  # Only print items with no children
                    self.print_all_items(child)

    def get_path(self, item):
        """
        Returns the path of the given item as a string.
        """
        path = []
        while item is not None:
            path.append(item.data(Qt.DisplayRole))
            item = item.parent()
        path.reverse()
        if len(path) > 1 and path[0] == "Root":
            path.pop(0)
        return ">".join(path)

    def on_context_menu_requested(self, pos):
        index = self.ui.treeView.indexAt(pos)
        item = self.xml_model.itemFromIndex(index)

        if item is not None:
            # create context menu
            menu = QMenu(self.ui.treeView)
            copy_path_action = menu.addAction("Copy Path")
            copy_data_action = menu.addAction("Copy Data")

            # execute context menu and handle selected action
            action = menu.exec(self.ui.treeView.mapToGlobal(pos))
            if action == copy_path_action:
                path = self.get_path(item)
                clipboard = QGuiApplication.clipboard()
                clipboard.setText(path)
            elif action == copy_data_action:
                if item.hasChildren():
                    QMessageBox.warning(self, "Error", "Cannot copy data from non-leaf node.")
                else:
                    clipboard = QGuiApplication.clipboard()
                    clipboard.setText(item.data(Qt.DisplayRole))