import sqlite3
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

def remove_extra_spaces(text):
    return ' '.join(text.split())

def generate_element_index(element, order):
    return f"{element}_{order}"

def inserteal_to_db_combined(xml_model):    
    # create database connection
    mydb = sqlite3.connect('resources/cc_db.sqlite')
    cursor = mydb.cursor()
    

    # get the current maximum id value for the tables
    cursor.execute("SELECT MAX(id) FROM aco_db")
    max_id_aco = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(id) FROM adv_db")
    max_id_adv = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(id) FROM agd_db")
    max_id_agd = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(id) FROM alc_db")
    max_id_alc = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(id) FROM ape_db")
    max_id_ape = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(id) FROM ase_db")
    max_id_ase = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(id) FROM ate_db")
    max_id_ate = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MAX(id) FROM ava_db")
    max_id_ava = cursor.fetchone()[0] or 0

    #Define the maximum id from each tables
    max_id_combined = max(max_id_aco, max_id_adv, max_id_agd, max_id_alc, max_id_ape, max_id_ase, max_id_ate, max_id_ava)

    # Define table locations for each class
    table_locations = {
    'aco - Composition': "aco_db",
    'adv - Development': "adv_db",
    'agd - Guidance documents': "agd_db",
    'alc - Life-cycle support': "alc_db",
    'ape - Protection Profile evaluation': "ape_db",
    'ase - Security Target evaluation': "ase_db",
    'ate - Tests': "ate_db",
    'ava - Vulnerability assessment': "ava_db",
    }

    #Get all the value from defining the element item path
    data_combined_db = [
            {
                "element_item" : "a-class - Vulnerability assessment - ava>a-family - Vulnerability analysis - ava_van>a-component - ava_van.5>ae-evaluator - ava_van.5.3e",
            },
            {
                "element_item" : "a-class - Vulnerability assessment - ava>a-family - Vulnerability analysis - ava_van>a-component - ava_van.5>ae-evaluator - ava_van.5.4e",
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
        element_from_path = last_part.replace("ae-developer - ", "")
        element_from_path = element_from_path.replace("ae-content - ", "")  # update based on previous state
        element_from_path = element_from_path.replace("ae-evaluator - ", "")  # update based on previous state


        # Extract the "component" value from the "element_path" variable
        component_path_parts = element_path.split('>')
        second_last_part = component_path_parts[-2]
        component_from_path = second_last_part.replace("a-component - ", "")

        # Extract the "family" value from the "element_path" variable
        family_path_parts = element_path.split('>')
        third_last_part = family_path_parts[-3]
        family_from_path = third_last_part.replace("a-family - ", "")

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
        class_from_path = class_path_part.replace("a-class - ", "")

        # Flip the order of the class value
        class_parts = class_from_path.split(' - ')
        flipped_class = " - ".join(reversed(class_parts))

        #Quick bug fix for flipped_class
        if flipped_class == "Tests - ate":
            _class = "ate - Tests"
        
        else:
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

    # commit the changes and close the database connection
    mydb.commit()
    mydb.close()
    print("Connection closed")
