"""
XML Parser Service for Common Criteria XML files.
Adapted from the original Qt-based xml_parser_model.py to work with web backend.
"""
from typing import Dict, List, Any, Optional
from lxml import etree
import re


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
        
        for child_element in xml_doc:
            if child_element.tag in ['f-class', 'a-class', 'eal', 'cap']:
                self._create_node_from_element(self.root_node, child_element)
        
        return {
            'success': True,
            'data': self.root_node.to_dict() if self.root_node else None,
            'components': self._extract_components()
        }
    
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
        """Parse text of an f-element that may contain fe-assignment and/or fe-selection elements."""
        text = element.text.strip() if element.text else ''
        
        for child in element:
            if child.tag == 'fe-assignment':
                fe_item = child.find("fe-assignmentitem")
                if fe_item is not None and fe_item.text:
                    text += f' [assignment: {fe_item.text.strip()}] '
                if child.tail and child.tail.strip():
                    text += self._remove_newlines_and_extra_whitespaces(child.tail.strip())
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
                    text += '] '
                    if child.tail and child.tail.strip():
                        text += self._remove_newlines_and_extra_whitespaces(child.tail.strip())
            elif child.tail and child.tail.strip():
                text += ' ' + self._remove_newlines_and_extra_whitespaces(child.tail.strip())
        
        return text
    
    def _remove_newlines_and_extra_whitespaces(self, text: str) -> str:
        """Remove newlines and extra whitespace characters."""
        return re.sub(r'\s+', ' ', text.strip())
    
    def _extract_components(self) -> List[Dict[str, str]]:
        """Extract component data suitable for database insertion."""
        components = []
        if self.root_node:
            self._extract_components_from_node(self.root_node, components, [])
        return components
    
    def _extract_components_from_node(self, node: XmlNode, components: List[Dict[str, str]], path: List[str]) -> None:
        """Recursively extract components from nodes."""
        current_path = path + [node.label]
        
        # Skip root node in path
        if node.label == "Root":
            for child in node.children:
                self._extract_components_from_node(child, components, [])
            return
        
        # Extract component information based on the node structure
        component_data = {
            'class_name': '',
            'family': '',
            'component': '',
            'component_name': '',
            'element': '',
            'element_item': ''
        }
        
        # Parse path to extract component information
        if len(current_path) >= 1:
            # Extract class information
            class_info = current_path[0]
            if ' - ' in class_info:
                parts = class_info.split(' - ')
                component_data['class_name'] = parts[0]
                if len(parts) > 1:
                    component_data['component_name'] = parts[1]
        
        if len(current_path) >= 2:
            # Extract family information
            family_info = current_path[1]
            if ' - ' in family_info:
                parts = family_info.split(' - ')
                component_data['family'] = parts[0]
        
        if len(current_path) >= 3:
            # Extract component information
            component_info = current_path[2]
            if ' - ' in component_info:
                parts = component_info.split(' - ')
                component_data['component'] = parts[0]
        
        if len(current_path) >= 4:
            # Extract element information
            component_data['element'] = current_path[3]
        
        # If this is a leaf node with data, add element_item
        if not node.children and node.data:
            component_data['element_item'] = node.data
        elif len(node.children) == 1 and not node.children[0].children:
            component_data['element_item'] = node.children[0].label
        
        # Only add if we have meaningful data
        if any(component_data.values()):
            components.append(component_data)
        
        # Recursively process children
        for child in node.children:
            if child.children:  # Only process if child has children (not leaf nodes)
                self._extract_components_from_node(child, components, current_path)