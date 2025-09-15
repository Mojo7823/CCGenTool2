## Overview

This PR addresses the XML query and database insertion workflow issues by implementing a complete redesign of the Query Data page. The original issue was that users couldn't effectively browse and query the XML-generated family tables created by the XML import process.

## Problem Solved

The Query Data page was previously limited to only showing the general `components` table with hardcoded functionality. Users had no way to:
- Discover what tables were created by XML import
- Browse the 20+ family-specific tables (fau_db, fco_db, etc.)
- View actual imported XML data
- Search through table contents

## Solution

### 1. Enhanced Query Data Interface

![Enhanced Query Data Interface](https://github.com/user-attachments/assets/db54baef-83b4-4e9f-a7ef-e8af40b9bce6)

Completely redesigned the Query Data page to provide:
- **Organized table categories**: Functional Requirements, Assurance Requirements, Special Tables, and General
- **Real-time table counts**: Shows exactly how many items each table contains
- **Visual table selection**: Click any table to browse its contents with clear active state styling
- **Responsive grid layout**: Professional organization of all available tables

### 2. Complete Family Table Support

The interface now supports all XML-generated tables:

**Functional Requirements (11 tables)**: fau_db, fco_db, fcs_db, fdp_db, fia_db, fmt_db, fpr_db, fpt_db, fru_db, fta_db, ftp_db

**Assurance Requirements (8 tables)**: aco_db, adv_db, agd_db, alc_db, ape_db, ase_db, ate_db, ava_db

**Special/General (2 tables)**: element_list_db, components

### 3. Data Viewing and Search

![Working data view with search](https://github.com/user-attachments/assets/59aefc80-2ed2-47b5-8687-4f351c216bac)

Implemented full data browsing capabilities:
- **Table data display**: Shows actual imported XML data in structured table format
- **Real-time search**: Filter results across all table fields with debounced input
- **Empty state handling**: Clear messaging for empty tables with guidance to import XML data first
- **Dynamic updates**: Table counts and data refresh automatically after XML import

## Technical Implementation

### Key Changes

- **Complete QueryData.vue rewrite**: Replaced basic hardcoded table with dynamic family table browser
- **API integration**: Leverages existing `/families` and `/families/{table_name}` endpoints
- **Real-time data**: Fetches table counts and updates interface dynamically
- **Search functionality**: Implements debounced search across all table fields
- **Responsive design**: Professional styling with proper visual feedback

### Workflow Verification

Tested complete XML import → query workflow:
1. ✅ Upload sample `cc_2022.xml` file through XML Parser
2. ✅ Verify data populates appropriate family tables (fau_db: 2 items, ase_db: 4 items, etc.)
3. ✅ Query Data page immediately reflects updated table counts
4. ✅ Click any table to view actual imported data
5. ✅ Search functionality filters results in real-time

## Impact

This implementation fully resolves the XML query and database browsing requirements, providing users with:
- Complete visibility into XML import results
- Intuitive interface for exploring Common Criteria data
- Professional table browsing with search capabilities
- Clear understanding of database schema and content organization

The solution transforms the Query Data page from a basic empty interface into a comprehensive database exploration tool that makes the XML import functionality immediately useful and accessible.