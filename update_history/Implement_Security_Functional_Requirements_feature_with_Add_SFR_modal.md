This PR implements the complete Security Functional Requirements feature as requested, including a new sidebar menu and a comprehensive Add SFR modal for creating Security Functional Requirements (SFRs) in the Common Criteria evaluation tool.

## 🎯 Features Implemented

### New Navigation Menu
- Added "Security Requirements" menu to the sidebar with "Security Functional Requirements" submenu
- Integrated seamlessly with existing navigation structure using Vue Router

### Add SFR Modal
The modal provides a complete workflow for creating SFRs with three main components:

1. **SFR Class Dropdown**: Displays all functional family classes with descriptions:
   - fau - Security audit
   - fco - Communication  
   - fcs - Cryptographic support
   - fdp - User data protection
   - fia - Identification and authentication
   - fmt - Security management
   - fpr - Privacy
   - fpt - Protection of the TSF
   - fru - Resource utilisation
   - fta - TOE access
   - ftp - Trusted path/channels

2. **SFR Components Dropdown**: Dynamically populated based on selected class
   - Example: Selecting "fcs - Cryptographic support" loads components like fcs_ckm.1, fcs_ckm.2, etc.
   - Fetches data from family-specific database tables (fcs_db, fru_db, etc.)

3. **SFR Preview**: WYSIWYG editor with formatting controls
   - Automatically displays element and element_item data for selected components
   - Supports both single and multiple element scenarios
   - Example: fcs_ckm.1.1 shows single element, fru_prs.1 shows multiple elements (fru_prs.1.1 and fru_prs.1.2)

## 🔧 Technical Implementation

### Frontend (Vue.js)
- Created `SecurityFunctionalRequirements.vue` component with modal functionality
- Added routing configuration for `/security/sfr` path
- Updated sidebar navigation with accordion-style menu

### Backend Integration
- Leverages existing FastAPI endpoints:
  - `/families` - Lists all functional family tables
  - `/families/{table_name}` - Fetches components for specific family
- Real-time data fetching and component population

### User Experience
- Progressive disclosure: Components dropdown disabled until class selected
- Finalize button disabled until component selected
- Success confirmation with class and component details
- Cancel functionality to close modal

## 📱 Screenshots

**Security Functional Requirements Page:**
![Security Functional Requirements](https://github.com/user-attachments/assets/56d70aac-12c2-49a5-b0c6-6be2b9519725)

**Complete Add SFR Modal with FCS Example:**
![Add SFR Modal](https://github.com/user-attachments/assets/1957ca6f-b717-49fa-9950-dbc8967a349d)

## ✅ Validation

Tested scenarios include:
- FCS class with single element (fcs_ckm.1.1)
- FRU class with multiple elements (fru_prs.1.1, fru_prs.1.2)
- WYSIWYG editor formatting functionality
- Complete workflow from class selection to SFR finalization

The implementation fully satisfies the requirements specified in the issue, providing a user-friendly interface for managing Security Functional Requirements in the Common Criteria evaluation workflow.
