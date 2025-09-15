This PR fixes critical issues with the XML parser's handling of Common Criteria assignment elements and improves the user experience with modal notifications.

## Issues Fixed

### 1. XML Assignment Element Parsing
The parser was incorrectly handling `<assignment>` elements containing `<assignmentitem>` tags and tail text. For example, this XML structure:

```xml
<f-element id="fpr_ano.2.1">
  The TSF shall ensure that
  <assignment>
    <assignmentitem>set of users and/or subjects</assignmentitem>
    <assignmentnotes>
      <para>the author should specify the set of users...</para>
    </assignmentnotes>
  </assignment>
  are unable to determine the real user name bound to
  <assignment>
    <assignmentitem>list of subjects and/or operations and/or objects</assignmentitem>
  </assignment>
  .
</f-element>
```

Was being parsed incorrectly, missing the assignment placeholders and tail text. Now correctly produces:
```
The TSF shall ensure that [assignment: set of users and/or subjects] are unable to determine the real user name bound to [assignment: list of subjects and/or operations and/or objects] .
```

### 2. Component Extraction and Display
- Fixed component hierarchy extraction logic in `extract_components_from_element()` 
- Replaced problematic Vue DataTable component with a simple HTML table that reliably displays extracted components
- Added proper component count display showing "Extracted Components (3)" with the actual parsed data

### 3. User Experience Improvements
- Added comprehensive modal notification system for parsing and database import operations
- Modals show success/error states with detailed information and expandable error details
- Improved visual feedback with icons and proper styling
- Modal system works for both "Parse XML" and "Parse & Import to Database" operations

## Technical Changes

**Backend (`server/app/xml_parser_service.py`):**
- Enhanced `extract_text_content()` to properly handle assignment elements with `<assignmentitem>` children
- Fixed text extraction to include tail text after assignment elements
- Improved component hierarchy extraction from XML structure

**Frontend (`web/src/views/XmlParser.vue`):**
- Added modal notification system with success/error states
- Replaced DataTable with simple HTML table for reliable component display
- Enhanced error handling with detailed modal feedback
- Added modal styling with proper visual indicators

## Testing
Verified with the problematic `fpr_ano.2.1` element that was mentioned in the issue. The parser now correctly:
- Extracts assignment text with proper formatting
- Displays all components in a working table
- Shows appropriate success/error modals
- Maintains proper component hierarchy information