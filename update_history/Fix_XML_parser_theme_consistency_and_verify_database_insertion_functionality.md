This PR addresses theme inconsistencies in the XML parser and verifies that the database insertion functionality works correctly.

## Issues Fixed

### Theme Consistency
The XML parser was using light theme colors that didn't match the main dashboard's dark theme. This created a jarring visual inconsistency when navigating between different parts of the application.

**Before:**
- XMLTreeNode component used light theme colors (`text-gray-800`, `bg-white`, `border-gray-300`)
- Success messages had inconsistent styling
- Tree view had poor contrast in dark theme context

**After:**
- Updated XMLTreeNode to use dark theme colors (`text-gray-300`, `bg-gray-800`, `border-gray-700`)
- Success messages now match the application's dark theme
- Consistent visual experience throughout the application

### Database Insertion Verification
Tested and verified that the "Parse & Import to Database" functionality works correctly:
- Successfully parsed a test XML file with 185 components
- Confirmed database insertion completes without errors
- Verified that the extracted component data is properly structured in the table view

## Technical Changes

1. **XMLTreeNode.vue**: Updated CSS classes to use dark theme colors for better consistency
2. **Database Models**: Verified the existing database schema handles XML component data correctly
3. **Testing**: Manually tested XML parsing and database insertion with a real Common Criteria XML file

## Screenshots

**Before (Light theme inconsistency):**
![Before Fix](https://github.com/user-attachments/assets/f2d06b70-c186-404d-a570-090a87908a15)

**After (Consistent dark theme):**
![After Fix](https://github.com/user-attachments/assets/ec979eb6-7e00-4906-bfca-a61e5a998e5e)

The XML parser now provides a seamless user experience with consistent theming and reliable database functionality.