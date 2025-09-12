## 🔧 Fixed XML Text Truncation Issue

The XML parser was incorrectly truncating text that spanned across multiple XML elements with intermediate assignment markers. This caused important requirement text to be split into separate fragments instead of being properly concatenated.

**Example of the issue:**
```xml
<fe-item>
  The
  <fe-assignment>
    <fe-assignmentitem>new data</fe-assignmentitem>
  </fe-assignment>
  requirements of TOE shall be fullfiled
  <fe-assignment>
    <fe-assignmentitem>new data</fe-assignmentitem>
  </fe-assignment>
  by the vendor before writing TSS
</fe-item>
```

**Before:** Text appeared as separate truncated parts:
- "The"
- "[assignment: new data]" 
- "requirements of TOE shall be fullfiled"
- etc.

**After:** Text is properly concatenated:
- "The [assignment: new data] requirements of TOE shall be fullfiled [assignment: new data] by the vendor before writing TSS"

**Root Cause:** The `_parse_fe_list` method in `xml_parser_service.py` was missing logic to process `tail` text after XML elements, which is essential for concatenating text fragments that appear after child elements.

**Solution:** Added proper tail text processing logic that matches the behavior of the original Qt-based parser (`oldparser/xml_parser_model.py`).

## 📊 Added Table Pagination to Query Interface

The database query interface (`QueryData.vue`) was using a basic HTML table that couldn't handle large datasets effectively.

**Improvements:**
- Replaced simple HTML table with `vue3-easy-data-table` component
- Added pagination with 25 rows per page
- Implemented search functionality across all columns
- Added sortable column headers
- Integrated proper loading states
- Applied consistent dark theme styling

**Technical Changes:**
- Added EasyDataTable component with full configuration
- Implemented proper column mapping for family tables (handling both `class` and `class_field` properties)
- Added responsive design with proper column widths
- Integrated search and pagination controls
