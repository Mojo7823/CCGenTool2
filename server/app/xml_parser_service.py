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
                'tables_used': []
            }
        
        components_imported = 0
        components_failed = 0
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
        
        try:
            db.commit()
            return {
                'success': True,
                'message': f"Successfully imported {components_imported} components",
                'components_imported': components_imported,
                'components_failed': components_failed,
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
        
        # Find all f-element and a-element tags in the XML
        for element in self.xml_doc.xpath('.//f-element | .//a-element'):
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
        text = element.text.strip() if element.text else ''
        
        for child in element:
            if child.tag == 'assignment':
                # Handle assignment elements
                assign_item = child.find("assignmentitem")
                if assign_item is not None and assign_item.text:
                    text += f' [assignment: {assign_item.text.strip()}]'
                # Add tail text after assignment
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
                # Handle selections
                text += ' [selection: '
                selection_items = child.findall('fe-selectionitem')
                items_text = [item.text.strip() for item in selection_items if item.text and item.text.strip()]
                if items_text:
                    text += ', '.join(items_text)
                text += ']'
                if child.tail and child.tail.strip():
                    text += ' ' + self._remove_newlines_and_extra_whitespaces(child.tail.strip())
            elif child.tail and child.tail.strip():
                # Add any tail text after other elements
                text += ' ' + self._remove_newlines_and_extra_whitespaces(child.tail.strip())
        
        return self._remove_newlines_and_extra_whitespaces(text)
    
    def _is_valid_component(self, component_data: Dict[str, str]) -> bool:
        """Check if component data has sufficient information to be valid."""
        return bool(component_data.get('element') and component_data.get('element_item'))