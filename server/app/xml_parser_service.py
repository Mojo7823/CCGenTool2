"""
XML Parser Service for Common Criteria XML files.
Adapted from the original Qt-based xml_parser_model.py to work with web backend.
Now includes multi-table database insertion based on component families.
"""
from typing import Dict, List, Any, Optional, Type
from lxml import etree
import re
from sqlalchemy.orm import Session
from .models import (
    Component, ComponentFamilyBase, ElementListDb,
    FauDb, FcoDb, FcsDb, FdpDb, FiaDb, FmtDb, FprDb, FptDb, FruDb, FtaDb, FtpDb,
    AcoDb, AdvDb, AgdDb, AlcDb, ApeDb, AseDb, AteDb, AvaDb
)


class XmlNode:
    """Represents a node in the XML tree structure."""
    
    def __init__(self, label: str, data: Optional[str] = None):
        self.label = label
        self.data = data
        self.children: List['XmlNode'] = []
        self.attributes: Dict[str, str] = {}
    
    def add_child(self, child: 'XmlNode') -> None:
        """Add a child node."""
        self.children.append(child)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary for JSON serialization."""
        result = {
            'label': self.label,
            'data': self.data,
            'attributes': self.attributes,
            'children': [child.to_dict() for child in self.children]
        }
        return result


class XmlParserService:
    """Service for parsing Common Criteria XML files."""
    
    def __init__(self):
        self.root_node: Optional[XmlNode] = None
        # Define table mappings based on class IDs from the XML
        self.functional_table_mappings = {
            "fau": FauDb,  # Security audit
            "fco": FcoDb,  # Communication
            "fcs": FcsDb,  # Cryptographic support
            "fdp": FdpDb,  # User data protection
            "fia": FiaDb,  # Identification and authentication
            "fmt": FmtDb,  # Security management
            "fpr": FprDb,  # Privacy
            "fpt": FptDb,  # Protection of the TSF
            "fru": FruDb,  # Resource utilisation
            "fta": FtaDb,  # TOE access
            "ftp": FtpDb,  # Trusted path/channels
        }
        
        self.assurance_table_mappings = {
            "aco": AcoDb,  # Composition
            "adv": AdvDb,  # Development
            "agd": AgdDb,  # Guidance documents
            "alc": AlcDb,  # Life-cycle support
            "ape": ApeDb,  # Protection Profile evaluation
            "ase": AseDb,  # Security Target evaluation
            "ate": AteDb,  # Tests
            "ava": AvaDb,  # Vulnerability assessment
        }
    
    def parse_xml_file(self, xml_content: str) -> Dict[str, Any]:
        """
        Parse XML content and return structured data.
        
        Args:
            xml_content: String content of the XML file
            
        Returns:
            Dictionary containing the parsed XML structure
        """
        try:
            xml_doc = etree.fromstring(xml_content.encode('utf-8'))
        except etree.XMLSyntaxError as e:
            raise ValueError(f"Invalid XML content: {str(e)}")
        
        if xml_doc.tag != 'cc':
            raise ValueError(f"Invalid root element '{xml_doc.tag}'. Expected 'cc'.")
        
        self.root_node = XmlNode("Root")
        self.xml_doc = xml_doc  # Store for component extraction
        
        for child_element in xml_doc:
            if child_element.tag in ['f-class', 'a-class', 'eal', 'cap']:
                self._create_node_from_element(self.root_node, child_element)
        
        return {
            'success': True,
            'data': self.root_node.to_dict() if self.root_node else None,
            'components': self._extract_components_directly()
        }
    
    def import_to_database(self, xml_content: str, db: Session) -> Dict[str, Any]:
        """
        Parse XML and import components to appropriate database tables.
        
        Args:
            xml_content: String content of the XML file
            db: Database session
            
        Returns:
            Dictionary containing import results
        """
        # Parse the XML first
        parse_result = self.parse_xml_file(xml_content)
        
        if not parse_result['success'] or not parse_result['components']:
            return {
                'success': False,
                'message': "No components found in XML file",
                'components_imported': 0,
                'components_failed': 0,
                'element_lists_imported': 0,
                'tables_used': []
            }
        
        components_imported = 0
        components_failed = 0
        element_lists_imported = 0
        errors = []
        tables_used = set()
        
        # Process components and insert into appropriate tables
        for component_data in parse_result['components']:
            try:
                success = self._insert_component_to_table(component_data, db)
                if success:
                    components_imported += 1
                    # Track which table was used
                    class_id = component_data.get('class_id', '')
                    table_name = self._get_table_name_for_class_id(class_id)
                    if table_name:
                        tables_used.add(table_name)
                else:
                    components_failed += 1
            except Exception as e:
                components_failed += 1
                errors.append(f"Failed to import component: {str(e)}")
        
        # Extract and import element lists
        try:
            element_lists = self._extract_element_lists()
            for element_list_data in element_lists:
                try:
                    success = self._insert_element_list_to_db(element_list_data, db)
                    if success:
                        element_lists_imported += 1
                        tables_used.add("element_list_db")
                except Exception as e:
                    errors.append(f"Failed to import element list: {str(e)}")
        except Exception as e:
            errors.append(f"Failed to extract element lists: {str(e)}")
        
        try:
            db.commit()
            return {
                'success': True,
                'message': f"Successfully imported {components_imported} components and {element_lists_imported} element lists",
                'components_imported': components_imported,
                'components_failed': components_failed,
                'element_lists_imported': element_lists_imported,
                'errors': errors if errors else None,
                'tables_used': list(tables_used)
            }
        except Exception as e:
            db.rollback()
            raise Exception(f"Database error: {str(e)}")
    
    def _insert_component_to_table(self, component_data: Dict[str, str], db: Session) -> bool:
        """Insert component data into the appropriate table based on class."""
        class_name = component_data.get('class_name', '')
        class_id = component_data.get('class_id', '')
        
        if not class_name:
            return False
        
        # Determine which table to use based on class_id
        table_class = self._get_table_class_for_class_id(class_id)
        
        if not table_class:
            # Fall back to general components table
            component = Component(
                class_name=component_data.get('class_name', ''),
                family=component_data.get('family'),
                component=component_data.get('component'),
                component_name=component_data.get('component_name'),
                element=component_data.get('element'),
                element_item=component_data.get('element_item')
            )
            db.add(component)
            return True
        
        # Insert into specific family table
        component = table_class(
            class_field=component_data.get('class_name', ''),
            family=component_data.get('family'),
            component=component_data.get('component'),
            component_name=component_data.get('component_name'),
            element=component_data.get('element'),
            element_item=component_data.get('element_item')
        )
        db.add(component)
        return True
    
    def _get_table_class_for_class_id(self, class_id: str) -> Optional[Type]:
        """Get the appropriate table class for a given class ID."""
        if not class_id:
            return None
            
        # Check functional tables
        if class_id in self.functional_table_mappings:
            return self.functional_table_mappings[class_id]
        
        # Check assurance tables
        if class_id in self.assurance_table_mappings:
            return self.assurance_table_mappings[class_id]
        
        return None
    
    def _get_table_name_for_class_id(self, class_id: str) -> Optional[str]:
        """Get the table name for a given class ID."""
        table_class = self._get_table_class_for_class_id(class_id)
        if table_class:
            return table_class.__tablename__
        return "components"
    
    def _create_node_from_element(self, parent_node: XmlNode, element) -> None:
        """Create a node from an XML element."""
        item_label = element.tag
        family_attrs = {}
        
        # Process attributes
        for key, value in element.attrib.items():
            if key not in ('name', 'id'):
                family_attrs[key] = value
            else:
                item_label += f" - {value}"
        
        if family_attrs:
            item_label += ' - ' + ' '.join([f"{key}={value}" for key, value in family_attrs.items()])
        
        node = XmlNode(item_label)
        node.attributes = dict(element.attrib)
        
        # Remove extra whitespaces for f-family and a-family elements
        if element.tag in ('f-family', 'a-family'):
            node.label = re.sub(r'\s+', ' ', node.label)
        
        self._add_child_elements(node, element)
        parent_node.add_child(node)
    
    def _add_child_elements(self, parent_node: XmlNode, element) -> None:
        """Add child elements to a parent node."""
        for child_element in element:
            if child_element.tag in ['f-class', 'a-class', 'f-family', 'a-family']:
                self._create_node_from_element(parent_node, child_element)
            else:
                item_label = str(child_element.tag)
                if 'id' in child_element.attrib:
                    item_label += f" - {child_element.attrib['id']}"
                
                node = XmlNode(item_label)
                node.attributes = dict(child_element.attrib)
                
                # Add attributes as child nodes
                for key, value in child_element.attrib.items():
                    if key != 'id':
                        attr_node = XmlNode(f"{key} = {value}")
                        node.add_child(attr_node)
                
                self._add_text_and_tail_to_node(node, child_element)
                self._add_child_elements(node, child_element)
                parent_node.add_child(node)
    
    def _add_text_and_tail_to_node(self, node: XmlNode, element) -> None:
        """Add text content from element to node."""
        if element.text and element.text.strip():
            text = element.text.strip()
            if element.tag == 'f-element':
                text = self._parse_fe_element_text(element)
            text = self._remove_newlines_and_extra_whitespaces(text)
            data_node = XmlNode(text)
            node.add_child(data_node)
        elif element.tail and element.tail.strip():
            text = element.tail.strip()
            text = self._remove_newlines_and_extra_whitespaces(text)
            data_node = XmlNode(text)
            node.add_child(data_node)
        
        # Handle nested elements
        for child in element:
            if child.tag == 'fe-list':
                self._parse_fe_list(node, child)
    
    def _parse_fe_list(self, node: XmlNode, element) -> None:
        """Parse fe-list element and its children."""
        for child in element:
            if child.tag == 'fe-item':
                text = child.text.strip() if child.text else ''
                for sub_child in child:
                    if sub_child.tag == 'fe-selection':
                        text += f' [selection: {self._parse_fe_selection(sub_child)}]'
                    elif sub_child.tag == 'fe-assignment':
                        fe_item = sub_child.find("fe-assignmentitem")
                        if fe_item is not None and fe_item.text:
                            text += f' [assignment: {fe_item.text.strip()}]'
                    # Add tail text processing - this was missing!
                    if sub_child.tail and sub_child.tail.strip():
                        text += ' ' + self._remove_newlines_and_extra_whitespaces(sub_child.tail.strip())
                text = self._remove_newlines_and_extra_whitespaces(text)
                data_node = XmlNode(text)
                node.add_child(data_node)
    
    def _parse_fe_selection(self, element) -> str:
        """Parse fe-selection element and return selection items text."""
        items_text = []
        for child in element:
            if child.tag == 'fe-selectionitem':
                if child.text:
                    items_text.append(child.text.strip())
            elif child.tag == 'fe-selectionnotes':
                items_text.append(self._parse_fe_selection(child))
        return ', '.join(filter(None, items_text))
    
    def _parse_fe_element_text(self, element) -> str:
        """Parse text of an f-element that may contain assignment/assignmentitem and/or selection elements."""
        text = element.text.strip() if element.text else ''
        
        for child in element:
            if child.tag == 'assignment':
                # Handle assignment elements (modern XML format)
                assign_item = child.find("assignmentitem")
                if assign_item is not None and assign_item.text:
                    text += f' [assignment: {assign_item.text.strip()}]'
                if child.tail and child.tail.strip():
                    text += ' ' + self._remove_newlines_and_extra_whitespaces(child.tail.strip())
            elif child.tag == 'fe-assignment':
                # Handle fe-assignment elements (legacy format)
                fe_item = child.find("fe-assignmentitem")
                if fe_item is not None and fe_item.text:
                    text += f' [assignment: {fe_item.text.strip()}]'
                if child.tail and child.tail.strip():
                    text += ' ' + self._remove_newlines_and_extra_whitespaces(child.tail.strip())
            elif child.tag == 'fe-selection':
                text += ' [selection: '
                selection_items = child.findall('fe-selectionitem')
                items_text = [item.text.strip() for item in selection_items if item.text and item.text.strip()]
                if items_text:
                    text += ', '.join(items_text)
                    assignments = child.findall(".//fe-assignmentitem")
                    if assignments:
                        assignment_text = [f"[assignment: {assign.text.strip()}]" for assign in assignments if assign.text]
                        if assignment_text:
                            text += ', ' + ', '.join(assignment_text)
                    text += ']'
                if child.tail and child.tail.strip():
                    text += ' ' + self._remove_newlines_and_extra_whitespaces(child.tail.strip())
            elif child.tail and child.tail.strip():
                text += ' ' + self._remove_newlines_and_extra_whitespaces(child.tail.strip())
        
        return text
    
    def _remove_newlines_and_extra_whitespaces(self, text: str) -> str:
        """Remove newlines and extra whitespace characters."""
        return re.sub(r'\s+', ' ', text.strip())
    
    def _extract_components_directly(self) -> List[Dict[str, str]]:
        """Extract component data directly from the XML document."""
        components = []
        
        if not hasattr(self, 'xml_doc'):
            return components
        
        # Find all f-element tags and assurance evidence elements in the XML
        element_query = './/f-element | .//a-element | .//ae-developer | .//ae-content | .//ae-evaluator'
        for element in self.xml_doc.xpath(element_query):
            component_data = self._extract_component_from_element(element)
            if self._is_valid_component(component_data):
                components.append(component_data)
        
        return components
    
    def _extract_component_from_element(self, element) -> Dict[str, str]:
        """Extract component information from an f-element or a-element."""
        component_data = {
            'class_name': '',
            'class_id': '',
            'family': '',
            'component': '',
            'component_name': '',
            'element': '',
            'element_item': ''
        }
        
        # Get element ID
        element_id = element.get('id', '')
        component_data['element'] = element_id
        
        # Extract class_id from element_id (e.g., "fpr" from "fpr_ano.2.1")
        if '_' in element_id:
            component_data['class_id'] = element_id.split('_')[0]
        
        # Find parent hierarchy
        component_elem = element.getparent()  # f-component
        family_elem = component_elem.getparent() if component_elem is not None else None  # f-family
        class_elem = family_elem.getparent() if family_elem is not None else None  # f-class
        
        # Extract class information
        if class_elem is not None:
            class_name = class_elem.get('name', '')
            class_id = class_elem.get('id', '')
            if class_name and class_id:
                component_data['class_name'] = f"{class_id} - {class_name}"
                if not component_data['class_id']:
                    component_data['class_id'] = class_id
        
        # Extract family information
        if family_elem is not None:
            family_name = family_elem.get('name', '')
            family_id = family_elem.get('id', '')
            if family_name and family_id:
                component_data['family'] = f"{family_id} - {family_name}"
        
        # Extract component information
        if component_elem is not None:
            component_id = component_elem.get('id', '')
            component_name = component_elem.get('name', '')
            component_data['component'] = component_id
            component_data['component_name'] = component_name
        
        # Extract element_item using the corrected parsing method
        element_text = self._parse_element_text_content(element)
        component_data['element_item'] = element_text
        
        return component_data
    
    def _parse_element_text_content(self, element) -> str:
        """Parse the complete text content of an element including assignments."""

        # Assurance evidence elements (ae-*) should only capture their direct requirement text.
        if element.tag.startswith('ae-'):
            assurance_text = self._extract_assurance_text(element)
            if assurance_text:
                return assurance_text

        parts: List[str] = []

        if element.text and element.text.strip():
            parts.append(self._remove_newlines_and_extra_whitespaces(element.text))

        for child in element:
            if child.tag == 'assignment':
                assign_item = child.find("assignmentitem")
                if assign_item is not None and assign_item.text:
                    parts.append(f"[assignment: {self._remove_newlines_and_extra_whitespaces(assign_item.text)}]")
                if child.tail and child.tail.strip():
                    parts.append(self._remove_newlines_and_extra_whitespaces(child.tail))
                continue
            if child.tag == 'fe-assignment':
                fe_item = child.find("fe-assignmentitem")
                if fe_item is not None and fe_item.text:
                    parts.append(f"[assignment: {self._remove_newlines_and_extra_whitespaces(fe_item.text)}]")
                if child.tail and child.tail.strip():
                    parts.append(self._remove_newlines_and_extra_whitespaces(child.tail))
                continue
            if child.tag == 'fe-selection':
                selection_items = child.findall('fe-selectionitem')
                items_text = [item.text.strip() for item in selection_items if item.text and item.text.strip()]
                if items_text:
                    parts.append(f"[selection: {', '.join(items_text)}]")
                if child.tail and child.tail.strip():
                    parts.append(self._remove_newlines_and_extra_whitespaces(child.tail))
                continue

            nested_text = self._parse_element_text_content(child)
            if nested_text:
                parts.append(nested_text)

            if child.tail and child.tail.strip():
                parts.append(self._remove_newlines_and_extra_whitespaces(child.tail))

        combined = ' '.join(part for part in parts if part)
        return self._remove_newlines_and_extra_whitespaces(combined)

    def _extract_assurance_text(self, element) -> str:
        """Collect only the primary requirement text for assurance evidence elements."""
        parts: List[str] = []

        if element.text and element.text.strip():
            parts.append(self._remove_newlines_and_extra_whitespaces(element.text))

        for child in element:
            # Skip detailed evaluator work units such as m-workunit and similar blocks
            if self._is_assurance_detail_element(child.tag):
                if child.tail and child.tail.strip():
                    parts.append(self._remove_newlines_and_extra_whitespaces(child.tail))
                continue

            inline_text = self._extract_assurance_text(child)
            if inline_text:
                parts.append(inline_text)

            if child.tail and child.tail.strip():
                parts.append(self._remove_newlines_and_extra_whitespaces(child.tail))

        if not parts:
            return ""

        combined = ' '.join(part for part in parts if part)
        return self._remove_newlines_and_extra_whitespaces(combined)

    @staticmethod
    def _is_assurance_detail_element(tag: str) -> bool:
        """Identify tags that contain evaluator work units or detailed guidance."""
        if not tag:
            return False

        if tag.startswith('m-'):
            return True

        return tag == 'ae-dc-element'

    def _is_valid_component(self, component_data: Dict[str, str]) -> bool:
        """Check if component data has sufficient information to be valid."""
        return bool(component_data.get('element') and component_data.get('element_item'))
    
    def _extract_element_lists(self) -> List[Dict[str, Any]]:
        """Extract element list data from the XML document for populating element_list_db."""
        element_lists = []
        
        if not hasattr(self, 'xml_doc'):
            return element_lists
        
        # Find all f-element tags that contain fe-list elements
        for f_element in self.xml_doc.xpath('.//f-element[fe-list]'):
            element_id = f_element.get('id', '')
            
            if not element_id:
                continue
            
            # Extract hierarchy for this element
            hierarchy_path = self._get_element_hierarchy_path(f_element)
            
            # Get the main element text (before fe-list)
            main_text = f_element.text.strip() if f_element.text else ''
            
            # Find the fe-list within this f-element
            fe_list = f_element.find('fe-list')
            if fe_list is not None:
                order = 1
                for fe_item in fe_list.findall('fe-item'):
                    item_text = self._parse_fe_item_text(fe_item)
                    if item_text.strip():  # Only add non-empty items
                        element_index = f"{element_id}_{order}"
                        
                        # Format with letter prefix (a, b, c, etc.)
                        letter = chr(ord('a') + order - 1)
                        formatted_item = f"{letter}. {item_text.strip()}"
                        
                        element_list_data = {
                            'element': element_id,
                            'element_index': element_index,
                            'item_list': hierarchy_path,
                            'item_text': formatted_item,
                            'main_text': main_text
                        }
                        element_lists.append(element_list_data)
                        order += 1
        
        return element_lists
    
    def _get_element_hierarchy_path(self, f_element) -> str:
        """Get the hierarchy path for an f-element."""
        # Find parent hierarchy
        component_elem = f_element.getparent()  # f-component
        family_elem = component_elem.getparent() if component_elem is not None else None  # f-family
        class_elem = family_elem.getparent() if family_elem is not None else None  # f-class
        
        path_parts = []
        
        # Build hierarchy path similar to the old parser format
        if class_elem is not None:
            class_name = class_elem.get('name', '')
            class_id = class_elem.get('id', '')
            if class_name and class_id:
                path_parts.append(f"f-class - {class_name} - {class_id}")
        
        if family_elem is not None:
            family_name = family_elem.get('name', '')
            family_id = family_elem.get('id', '')
            if family_name and family_id:
                path_parts.append(f"f-family - {family_name} - {family_id}")
        
        if component_elem is not None:
            component_id = component_elem.get('id', '')
            component_name = component_elem.get('name', '')
            if component_id:
                path_parts.append(f"f-component - {component_id}")
        
        element_id = f_element.get('id', '')
        if element_id:
            path_parts.append(f"f-element - {element_id}")
        
        return '>'.join(path_parts)
    
    def _parse_fe_item_text(self, fe_item) -> str:
        """Parse the text content of a fe-item element."""
        text = fe_item.text.strip() if fe_item.text else ''
        
        # Process child elements within fe-item
        for child in fe_item:
            if child.tag == 'fe-selection':
                text += f' [selection: {self._parse_fe_selection(child)}]'
            elif child.tag == 'fe-assignment':
                fe_assignment_item = child.find("fe-assignmentitem")
                if fe_assignment_item is not None and fe_assignment_item.text:
                    text += f' [assignment: {fe_assignment_item.text.strip()}]'
            # Add tail text after child elements
            if child.tail and child.tail.strip():
                text += ' ' + self._remove_newlines_and_extra_whitespaces(child.tail.strip())
        
        return self._remove_newlines_and_extra_whitespaces(text)
    
    def _insert_element_list_to_db(self, element_list_data: Dict[str, Any], db: Session) -> bool:
        """Insert element list data into the element_list_db table."""
        try:
            # Check if the element_index already exists
            existing = db.query(ElementListDb).filter(
                ElementListDb.element_index == element_list_data['element_index']
            ).first()
            
            if existing:
                # Update existing record
                existing.item_list = element_list_data['item_text']
                db.add(existing)
            else:
                # Create new record
                element_list = ElementListDb(
                    element=element_list_data['element'],
                    element_index=element_list_data['element_index'],
                    item_list=element_list_data['item_text']
                )
                db.add(element_list)
            
            return True
        except Exception as e:
            # Log error but don't fail the entire import
            print(f"Error inserting element list: {str(e)}")
            return False