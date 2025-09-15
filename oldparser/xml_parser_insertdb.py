import sqlite3
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

def remove_extra_spaces(text):
    return ' '.join(text.split())

def generate_element_index(element, order):
    return f"{element}_{order}"

def insert_to_db_combined(db_filename,xml_model):

    # create database connection
    mydb = sqlite3.connect(db_filename)
    cursor = mydb.cursor()

    # get the current maximum id value for the tables
    cursor.execute("SELECT MAX(id) FROM fau_db")
    max_id_fau = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(id) FROM fco_db")
    max_id_fco = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(id) FROM fcs_db")
    max_id_fcs = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(id) FROM fia_db")
    max_id_fia = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(id) FROM fmt_db")
    max_id_fmt = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(id) FROM fpr_db")
    max_id_fpr = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(id) FROM fpt_db")
    max_id_fpt = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(id) FROM fru_db")
    max_id_fru = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(id) FROM fta_db")
    max_id_fta = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(id) FROM ftp_db")
    max_id_ftp = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(id) FROM element_list_db")
    max_id_element_list = cursor.fetchone()[0] or 0

    #Define the maximum id from each tables
    max_id_combined = max(max_id_fau,max_id_fco,max_id_fcs,max_id_fia,max_id_fmt,max_id_fpr,max_id_fpt,max_id_fru,max_id_fta,max_id_ftp, max_id_element_list)

    # Define table locations for each class
    table_locations = {
    "fau - Security audit": "fau_db",
    "fco - Communication": "fco_db",
    "fcs - Cryptographic support": "fcs_db",
    "fdp - User data protection": "fdp_db",
    "fia - Identification and authentication": "fia_db",
    "fmt - Security management": "fmt_db",
    "fpr - Privacy": "fpr_db",
    "fpt - Protection of the TSF": "fpt_db",
    "fru - Resource utilisation": "fru_db",
    "fta - TOE access": "fta_db",
    "ftp - Trusted path/channels": "ftp_db",
    }

    #Get all the value from defining the element item path
    data_combined_db = [
        #FAU ARP (1) 
            #FAU ARP 1 (1)

### for fpt_db table
    #FPT_FLS (1)
        #fpt_fls.1 (1)
            {
                "element_item": "f-class - Protection of the TSF - fpt>f-family - Fail secure - fpt_fls>f-component - fpt_fls.1>f-element - fpt_fls.1.1"
            }, 
    #FPT_ITA (1)
        #fpt_ita.1 (1)
            {
                "element_item": "f-class - Protection of the TSF - fpt>f-family - Availability of exported TSF data - fpt_ita>f-component - fpt_ita.1>f-element - fpt_ita.1.1"
            },
    ]


    data_element_list_db = [
        #FAU GEN.1.1 (3)
        {
            "item_list": "f-class - Security audit - fau>f-family - Security audit data generation - fau_gen>f-component - fau_gen.1>f-element - fau_gen.1.1",
            "order": 1
        },
        {
            "item_list": "f-class - Security audit - fau>f-family - Security audit data generation - fau_gen>f-component - fau_gen.1>f-element - fau_gen.1.1",
            "order": 2
        },

        {
            "item_list": "f-class - Security audit - fau>f-family - Security audit data generation - fau_gen>f-component - fau_gen.1>f-element - fau_gen.1.1",
            "order": 3
        },
        #FAU GEN.1.2 (2)
        {
            "item_list": "f-class - Security audit - fau>f-family - Security audit data generation - fau_gen>f-component - fau_gen.1>f-element - fau_gen.1.2",
            "order": 1
        },
        {
            "item_list": "f-class - Security audit - fau>f-family - Security audit data generation - fau_gen>f-component - fau_gen.1>f-element - fau_gen.1.2",
            "order": 2
        },
        #FAU SAA 1.2 (2)
        {
            "item_list": "f-class - Security audit - fau>f-family - Security audit analysis - fau_saa>f-component - fau_saa.1>f-element - fau_saa.1.2",
            "order": 1
        },
        {
            "item_list": "f-class - Security audit - fau>f-family - Security audit analysis - fau_saa>f-component - fau_saa.1>f-element - fau_saa.1.2",
            "order": 2
        },
        #FAU SEL 1.1 (2)
        {
            "item_list": "f-class - Security audit - fau>f-family - Security audit event selection - fau_sel>f-component - fau_sel.1>f-element - fau_sel.1.1",
            "order": 1
        },
        {
            "item_list": "f-class - Security audit - fau>f-family - Security audit event selection - fau_sel>f-component - fau_sel.1>f-element - fau_sel.1.1",
            "order": 2
        },
        #fdp_iff.2.6(3)
        {
            "item_list": "f-class - User data protection - fdp>f-family - Information flow control functions - fdp_iff>f-component - fdp_iff.2>f-element - fdp_iff.2.6",
            "order": 1
        },
        {
            "item_list": "f-class - User data protection - fdp>f-family - Information flow control functions - fdp_iff>f-component - fdp_iff.2>f-element - fdp_iff.2.6",
            "order": 2
        },        
        {
            "item_list": "f-class - User data protection - fdp>f-family - Information flow control functions - fdp_iff>f-component - fdp_iff.2>f-element - fdp_iff.2.6",
            "order": 3
        },
        #fta_ssl.1.1 (2)
        {
            "item_list": "f-class - TOE access - fta>f-family - Session locking and termination - fta_ssl>f-component - fta_ssl.1>f-element - fta_ssl.1.1",
            "order": 1
        },
        {
            "item_list": "f-class - TOE access - fta>f-family - Session locking and termination - fta_ssl>f-component - fta_ssl.1>f-element - fta_ssl.1.1",
            "order": 2
        },
        #fta_ssl.2.1 (2)
        {
            "item_list": "f-class - TOE access - fta>f-family - Session locking and termination - fta_ssl>f-component - fta_ssl.2>f-element - fta_ssl.2.1",
            "order": 1
        },
        {
            "item_list": "f-class - TOE access - fta>f-family - Session locking and termination - fta_ssl>f-component - fta_ssl.2>f-element - fta_ssl.2.1",
            "order": 2
        },
    ]

    replace_all = False


    # Process data for combined_db
    for row in data_combined_db:
        element_path = row["element_item"]

        # get the element_item value from the xml_model instance
        item = xml_model.root_item
        for part in element_path.split('>'):
            for row in range(item.rowCount()):
                child = item.child(row)
                if child.data(Qt.DisplayRole) == part:
                    item = child
                    break
            else:
                print(f"No item found for path: {element_path}")
                mydb.close()  # Close the database connection
                print("Connection Closed (Item not Found)")
                return
        while item.hasChildren():
            item = item.child(0)
        element_item = item.data(Qt.DisplayRole)

        # Extract the "element" value from the "element_path" variable
        element_path_parts = element_path.split('>')
        last_part = element_path_parts[-1]
        element_from_path = last_part.replace("f-element - ", "")

        # Extract the "component" value from the "element_path" variable
        component_path_parts = element_path.split('>')
        second_last_part = component_path_parts[-2]
        component_from_path = second_last_part.replace("f-component - ", "")

        # Extract the "family" value from the "element_path" variable
        family_path_parts = element_path.split('>')
        third_last_part = family_path_parts[-3]
        family_from_path = third_last_part.replace("f-family - ", "")

        # Flip the order of the family value
        family_parts = family_from_path.split(' - ')
        flipped_family = " - ".join(reversed(family_parts))

        # Get Component by using element_path
        component_path = '>'.join(element_path.split('>')[:-1])

        # find the item for the "component" path
        item = xml_model.root_item
        for part in component_path.split('>'):
            for row in range(item.rowCount()):
                child = item.child(row)
                if child.data(Qt.DisplayRole) == part:
                    item = child
                    break
            else:
                print(f"No item found for path: {component_path}")
                mydb.close()  # Close the database connection
                print("Connection Closed (Item not Found)")
                return

        # Initialize component_name
        component_name = ""

        # Look for the "name = ..." item among the children of the "component" item
        for row in range(item.rowCount()):
            child = item.child(row)
            if child.data(Qt.DisplayRole).startswith("name = "):
                component_name = child.data(Qt.DisplayRole)
                component_name = component_name.replace("name = ", "")
                component_name = remove_extra_spaces(component_name)  # Remove extra spaces
                break
        else:
            print(f"No 'name = ...' item found for component path: {component_path}")
            mydb.close()  # Close the database connection
            print("Connection Closed (Item not Found)")
        
        # Extract the "class" value from the "element_path" variable
        class_path_part = element_path_parts[0]
        class_from_path = class_path_part.replace("f-class - ", "")

        # Flip the order of the class value
        class_parts = class_from_path.split(' - ')
        flipped_class = " - ".join(reversed(class_parts))

        _class = flipped_class
        target_table = table_locations[_class] # Reference the table location using the class name

        # check if the element already exists in the database
        sql = f"SELECT * FROM {target_table} WHERE element=%s"
        cursor.execute(sql, (element_from_path,))
        result = cursor.fetchone()

        if result is None:
            max_id_combined += 1
            sql = f"INSERT INTO {target_table} (id, class, family, component, component_name, element, element_item) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values = (max_id_combined, _class, flipped_family, component_from_path, component_name, element_from_path, element_item)
            cursor.execute(sql, values)

            #print confirmation if success or not
            if cursor.rowcount == 1:
                print("Row inserted successfully")
            else:
                print("Row insertion failed")

        else:
            # If replace_all is False, ask the user if they want to replace the existing record
            if not replace_all:
                msg_box = QMessageBox()
                msg_box.setText(f"The element {element_from_path} already exists in the database. Do you want to replace it?")
                msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.YesToAll)
                choice = msg_box.exec()

                if choice == QMessageBox.YesToAll:
                    replace_all = True
            else:
                choice = QMessageBox.Yes

            if choice == QMessageBox.Yes:
                sql = f"UPDATE {target_table} SET class=%s, family=%s, component=%s, component_name=%s, element_item=%s WHERE element=%s"
                values = (_class, flipped_family, component_from_path, component_name, element_item, element_from_path)
                cursor.execute(sql, values)

                #print confirmation if success or not
                if cursor.rowcount == 1:
                    print("Row updated successfully")
                else:
                    print("Row already same, no update needed")

    # Process data data_element_list_db:
    for data_row in data_element_list_db:
        # define the class, family, component, element, and element_name values
        item_list_path = data_row["item_list"]
        order = data_row["order"]


        # Extract the "element" value from the "item_list_path" variable
        item_list_path_parts = item_list_path.split('>')
        last_part = item_list_path_parts[-1]
        _element = last_part.replace("f-element - ", "")

        element_index = generate_element_index(_element, order)


        # get the element_item value from the xml_model instance
        item = xml_model.root_item
        for part in item_list_path.split('>'):
            for child_row in range(item.rowCount()):
                child = item.child(child_row)
                if child.data(Qt.DisplayRole) == part:
                    item = child
                    break
            else:
                print(f"No item found for path: {item_list_path}")
                mydb.close()  # Close the database connection
                print("Connection Closed (Item not Found)")
                return

        desired_order = data_row["order"]
        while item.hasChildren():
            if desired_order < item.rowCount():
                item = item.child(desired_order)
            else:
                print(f"No item found at the specified order for element: {_element}")
                mydb.close()  # Close the database connection
                print("Connection Closed (Item not Found)")
                break

        item_list_path = item.data(Qt.DisplayRole)

        # check if the element_index already exists in the database
        sql = "SELECT * FROM element_list_db WHERE element_index=%s"
        cursor.execute(sql, (element_index,))
        result = cursor.fetchone()

        if result is None:
            # insert the values into the database
            max_id_combined += 1
            sql = "INSERT INTO element_list_db (id, element, element_index, item_list) VALUES (%s, %s, %s, %s)"
            values = (max_id_combined, _element, element_index, item_list_path)
            cursor.execute(sql, values)

            #print confirmation if success or not
            if cursor.rowcount == 1:
                print("Row inserted successfully")
            else:
                print("Row insertion failed")

        else:
            # If replace_all is False, ask the user if they want to replace the existing record
            if not replace_all:
                msg_box = QMessageBox()
                msg_box.setText(f"The index element {element_index} already exists in the database. Do you want to replace it?")
                msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.YesToAll)
                choice = msg_box.exec()

                if choice == QMessageBox.YesToAll:
                    replace_all = True
            else:
                choice = QMessageBox.Yes

            if choice == QMessageBox.Yes:
                # update the existing record
                sql = "UPDATE element_list_db SET item_list=%s WHERE element_index=%s"
                values = (item_list_path, element_index)
                cursor.execute(sql, values)

                #print confirmation if success or not
                if cursor.rowcount == 1:
                    print("Row updated successfully")
                else:
                    print("Row already same, no update needed")

    # commit the changes and close the database connection
    mydb.commit()
    mydb.close()
    print("Connection closed")
