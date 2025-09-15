# XML Parser Integration

This document describes the integration of the old Common Criteria XML parser into the new Vue.js/Python backend system.

## Overview

The XML Parser feature allows users to upload Common Criteria XML files, parse their hierarchical structure, and import the parsed components into the database for further processing.

## Features

### 1. XML File Upload
- Drag and drop or click to select XML files
- File validation (only .xml files accepted)
- UTF-8 encoding support

### 2. XML Parsing
- Parses Common Criteria XML structure including:
  - f-class (Functional Classes)
  - a-class (Assurance Classes)
  - f-family/a-family (Families)
  - f-component/a-component (Components)
  - f-element/a-element (Elements)
  - EAL (Evaluation Assurance Levels)
- Extracts nested text content including assignments and selections
- Maintains hierarchical relationships

### 3. Tree Visualization
- Interactive tree view of parsed XML structure
- Expandable/collapsible nodes
- Color-coded node types:
  - Red: Classes (f-class, a-class)
  - Blue: Families (f-family, a-family)
  - Green: Components (f-component, a-component)
  - Orange: Elements (f-element, a-element)
  - Purple: EAL components

### 4. Database Integration
- Automatic extraction of component data
- Import parsed components to database
- Preserves hierarchical relationships in flattened structure
- Error handling and reporting

## API Endpoints

### POST /xml/parse
Parses an uploaded XML file and returns the structured data.

**Request:**
- Content-Type: multipart/form-data
- Body: XML file

**Response:**
```json
{
  "success": true,
  "data": { ... },
  "components": [ ... ]
}
```

### POST /xml/import
Parses an XML file and imports components to the database.

**Request:**
- Content-Type: multipart/form-data
- Body: XML file

**Response:**
```json
{
  "success": true,
  "message": "Successfully imported 18 components",
  "components_imported": 18,
  "components_failed": 0,
  "errors": null
}
```

## Usage

1. Navigate to the "XML Parser" page in the sidebar
2. Click "Choose XML File" to select a Common Criteria XML file
3. Choose one of the following actions:
   - **Parse XML**: Preview the structure without importing
   - **Parse & Import to Database**: Parse and import components

## Technical Implementation

### Backend (Python/FastAPI)
- `xml_parser_service.py`: Core XML parsing logic adapted from original Qt code
- `lxml` library for XML processing
- FastAPI endpoints for file upload and processing
- SQLAlchemy integration for database operations

### Frontend (Vue.js)
- `XmlParser.vue`: Main XML parser interface
- `XMLTreeNode.vue`: Recursive tree component for displaying parsed structure
- File upload handling with FormData
- Axios for API communication

## Migration from Old Code

The integration successfully migrates functionality from the original Qt-based parser:

### Original Code (`oldparser/`)
- `xml_parser.py`: Qt GUI application
- `xml_parser_model.py`: Qt-based tree model with XML parsing

### New Implementation
- Removed Qt dependencies (PySide6, QStandardItem, etc.)
- Converted Qt tree model to plain Python data structures
- Replaced Qt file dialogs with web file upload
- Maintained core XML parsing logic and structure
- Added REST API endpoints for web integration

## Example XML Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<cc>
  <f-class name="FCO" id="FCO">
    <f-family name="FCO_CPC" id="FCO_CPC">
      <f-component name="FCO_CPC.1" id="FCO_CPC.1">
        <f-element id="FCO_CPC.1.1">
          The TSF shall be capable of generating cryptographic keys...
        </f-element>
      </f-component>
    </f-family>
  </f-class>
</cc>
```

This structure is parsed into a hierarchical tree and components are extracted for database storage.