from PySide6.QtCore import Qt, QModelIndex, QAbstractItemModel
from PySide6.QtGui import QStandardItem
from lxml import etree
import re

class XmlItemModel(QAbstractItemModel):
    def __init__(self, xml_file):
        super().__init__()
        self.root_item = QStandardItem("Root")
        self.__setup_model(xml_file)

    def __setup_model(self, xml_file):
        with open(xml_file) as f:
            xml_doc = etree.parse(f)
        root_element = xml_doc.getroot()
        if root_element.tag != 'cc':
            raise ValueError(f"Invalid root element '{root_element.tag}'")
        for child_element in root_element:
            if child_element.tag == 'f-class':
                self.__create_model_from_element(self.root_item, child_element)
            elif child_element.tag == 'a-class':
                self.__create_model_from_element(self.root_item, child_element)
            elif child_element.tag == 'eal':
                self.__create_model_from_element(self.root_item, child_element)
            elif child_element.tag == 'cap':
                self.__create_model_from_element(self.root_item, child_element)

    def __create_model_from_element(self, parent_item, element):
        item_label = element.tag
        family_attrs = {}
        for key, value in element.attrib.items():
            if key not in ('name', 'id'):
                family_attrs[key] = value
            else:
                item_label += f" - {value}"
        if family_attrs:
            item_label += ' - ' + ' '.join([f"{key}={value}" for key, value in family_attrs.items()])
        item = QStandardItem(item_label)

        # Remove extra whitespaces for f-family and a-family elements
        if element.tag in ('f-family', 'a-family'):
            cleaned_text = re.sub(r'\s+', ' ', item.text())
            item.setText(cleaned_text)

        self.__add_child_elements(item, element)
        parent_item.appendRow(item)


    def __add_child_elements(self, parent_item, element):
        for child_element in element:
            if child_element.tag == 'f-class':
                self.__create_model_from_element(parent_item, child_element)
            elif child_element.tag == 'a-class':
                self.__create_model_from_element(parent_item, child_element)
            elif child_element.tag == 'f-family':
                self.__create_model_from_element(parent_item, child_element)
            elif child_element.tag == 'a-family':
                self.__create_model_from_element(parent_item, child_element)
            else:
                item_label = str(child_element.tag)
                if 'id' in child_element.attrib:
                    item_label += f" - {child_element.attrib['id']}"
                item = QStandardItem(item_label)
                attributes = child_element.attrib
                for key, value in attributes.items():
                    if key != 'id':
                        attr_item = QStandardItem(f"{key} = {value}")
                        item.appendRow(attr_item)
                self.__add_text_and_tail_to_item(item, child_element)
                self.__add_child_elements(item, child_element)
                parent_item.appendRow(item)

    def __add_text_and_tail_to_item(self, item, element):
        if element.text and element.text.strip():
            text = element.text.strip()
            if element.tag == 'f-element':
                text = self.__parse_fe_element_text(element)
            text = self.__remove_newlines_and_extra_whitespaces(text)
            data_item = QStandardItem(text)
            item.appendRow(data_item)
        elif element.tail and element.tail.strip():
            text = element.tail.strip()
            text = self.__remove_newlines_and_extra_whitespaces(text)
            data_item = QStandardItem(text)
            item.appendRow(data_item)

        # handle nested elements
        for child in element:
            if child.tag == 'fe-list':
                self.__parse_fe_list(item, child)

    def __parse_fe_list(self, item, element):
        """
        Parses the fe-list element and its children, and populates the item with the text of the list items.
        """
        for child in element:
            if child.tag == 'fe-item':
                text = child.text.strip() if child.text else ''
                for sub_child in child:
                    if sub_child.tag == 'fe-selection':
                        text += f' [selection: {self.__parse_fe_selection(sub_child)}]'
                    elif sub_child.tag == 'fe-assignment':
                        text += f' [assignment: {sub_child.find("fe-assignmentitem").text.strip()}]'
                text = self.__remove_newlines_and_extra_whitespaces(text)
                data_item = QStandardItem(text)
                item.appendRow(data_item)

    def __parse_fe_selection(self, element):
        """
        Parses the fe-selection element and its children, and returns the text of the selection items.
        """
        items_text = []
        for child in element:
            if child.tag == 'fe-selectionitem':
                items_text.append(child.text.strip())
            elif child.tag == 'fe-selectionnotes':
                self.__parse_fe_selection(child)
        return ', '.join(items_text)


    def __parse_fe_element_text(self, element):
        """
        Parses the text of an f-element element that may contain fe-assignment and/or fe-selection elements.
        """
        text = element.text.strip()
        for child in element:
            if child.tag == 'fe-assignment':
                text += f' [assignment: {child.find("fe-assignmentitem").text.strip()}] '
                if child.tail and child.tail.strip():
                    text += self.__remove_newlines_and_extra_whitespaces(child.tail.strip())
            elif child.tag == 'fe-selection':
                text += ' [selection: '
                selection_items = child.findall('fe-selectionitem')
                items_text = [item.text.strip() for item in selection_items if item.text and item.text.strip()]
                if items_text:
                    text += ', '.join(items_text)
                    if child.findall(".//fe-assignmentitem"):
                        assignments = child.findall(".//fe-assignmentitem")
                        assignment_text = [f"[assignment: {assign.text.strip()}]" for assign in assignments]
                        text += ', ' + ', '.join(assignment_text)
                    text += '] '
                    if child.tail and child.tail.strip():
                        text += self.__remove_newlines_and_extra_whitespaces(child.tail.strip())
            elif child.tail and child.tail.strip():
                text += ' ' + self.__remove_newlines_and_extra_whitespaces(child.tail.strip())
        return text

    def __remove_newlines_and_extra_whitespaces(self, text):
        """
        Removes newlines and extra whitespace characters from the given text.
        """
        return re.sub(r'\s+', ' ', text)

    def __parse_selection_items(self, element, items_text):
        """
        Recursively parses the fe-selection elements and their fe-selectionitem children, and populates the items_text
        list with the text of the selection items.
        """
        for child in element:
            if child.tag == 'fe-selectionitem':
                if child.text:
                    items_text.append(child.text.strip())
                self.__parse_selection_items(child, items_text)
            elif child.tag == 'fe-selectionnotes':
                self.__parse_selection_items(child, items_text)

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        parent_item = parent.internalPointer() if parent.isValid() else self.root_item
        child_item = parent_item.child(row, column)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        child_item = index.internalPointer()
        parent_item = child_item.parent()
        if parent_item == self.root_item:
            return QModelIndex()
        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()
        return parent_item.rowCount()

    def columnCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == Qt.DisplayRole:
            return item.text().strip()
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and section == 0 and orientation == Qt.Horizontal:
            return "Element"
        return None

    def itemFromIndex(self, index: QModelIndex):
        return index.internalPointer()