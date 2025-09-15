This PR addresses two critical usability issues in the database interface:

## 🎨 Fixed Table Color Accessibility Issue

The query data tables had poor color contrast with alternating dark/light rows that made text difficult to read, especially where dark backgrounds blended with the font color. This created accessibility barriers for users.

**Changes made:**
- Removed the `alternating` property from EasyDataTable components
- Updated CSS variables to use clean white backgrounds with high contrast dark text
- Improved hover states with subtle light gray backgrounds

**Before:** Dark alternating rows with poor text visibility
![Before Fix - Query Table](https://github.com/user-attachments/assets/0e3fa6d5-3e9c-415e-b293-5999fc3a69ee)

**After:** Clean white backgrounds with excellent readability
![After Fix - Query Table](https://github.com/user-attachments/assets/9edd8abe-0147-4222-8902-44eb7b6ea6ff)

## 🔧 Implemented Table Selection for Modify Data Page

The modify data page was completely empty and only worked with the general `components` table, making it impossible to edit the family-specific tables that contain the actual imported XML data.

**Changes made:**
- Added a "Table Location" dropdown with all available database tables organized by category:
  - Functional Requirements (fau_db, fco_db, fcs_db, etc.)
  - Assurance Requirements (aco_db, adv_db, agd_db, etc.)
  - Special Tables (element_list_db)
  - General (components)
- Implemented full CRUD functionality for family-specific tables
- Added new backend endpoints for family table operations
- Dynamic loading of table data based on user selection

**Before:** Empty page with no functionality
![Before Fix - Modify Page](https://github.com/user-attachments/assets/b9a95ee0-5f49-492b-b08b-595c8dcdaa23)

**After:** Full table selection and CRUD functionality
![After Fix - Modify Page](https://github.com/user-attachments/assets/9c01fef1-cc1a-4bfa-a86d-a5c8e9b9303d)

## 🔧 Technical Implementation

**Frontend Updates:**
- `QueryData.vue`: Improved accessibility with white table backgrounds and high contrast text
- `ModifyData.vue`: Complete rewrite with table selection dropdown and support for family-specific tables

**Backend Updates:**
- Added `POST /families/{table_name}` for creating components in family tables
- Added `PUT /families/{table_name}/{item_id}` for updating family table components  
- Added `DELETE /families/{table_name}/{item_id}` for deleting family table components
- Proper error handling and validation for all new endpoints

## ✅ Testing Verified

All CRUD operations have been thoroughly tested:
- ✅ Create: Successfully adds new components to selected family tables
- ✅ Read: Properly loads and displays data from selected tables
- ✅ Update: Saves edits to existing components correctly
- ✅ Delete: Removes components from tables as expected
- ✅ Table Selection: Dropdown correctly loads data for all table types

The application now provides a complete, accessible interface for managing database components across all table types, with the imported XML data fully accessible for modification.