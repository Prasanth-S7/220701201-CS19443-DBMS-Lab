import mysql.connector
from datetime import datetime
import bcrypt

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="prasanth",
        database="rms"
    )
    return connection

"""def generateInvoice(customer_id, product_ids):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM customers WHERE id = %s", (customer_id,))
        customer = cursor.fetchone()
        if customer is None:
            raise Exception("Customer not found")

        products = []
        total_cost = 0
        for product_id in product_ids:
            cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            product = cursor.fetchone()
            if product is None:
                raise Exception(f"Product with ID {product_id} not found")
            products.append(product)
            total_cost += product[3]

        invoice_number = datetime.now().strftime("%Y%m%d%H%M%S")
        # Insert invoice details into the database
        cursor.execute("INSERT INTO invoices (invoice_number, customer_id, total_cost) VALUES (%s, %s, %s)",
                       (invoice_number, customer_id, total_cost))
        invoice_id = cursor.lastrowid

        # Insert invoice items
        for product in products:
            cursor.execute("INSERT INTO invoice_items (invoice_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                           (invoice_id, product[0], 1, product[3]))  # Assuming quantity is 1 for each product

        # Commit the transaction
        connection.commit()

        # Return generated invoice details
        return {
            "invoice_number": invoice_number,
            "customer": customer,
            "products": products,
            "total_cost": total_cost
        }

    except Exception as e:
        print(f"Error generating invoice: {e}")
        connection.rollback()
        return None

    finally:
        cursor.close()
        connection.close()


invoice = generateInvoice(1, [1, 2, 3])
if invoice:
    print("Invoice generated successfully:")
    print(invoice)
else:
    print("Failed to generate invoice")
"""
#********************************************************** ADDING STOCKS ****************************************************************

def add_product(name, category, price,quantity):
    # Validate input data
    print("add product")
    if not name or quantity<= 0:
        print("Invalid product details")
        return False

    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM products WHERE name = %s", (name,))
    product = cursor.fetchone()
    if product:
        new_quantity = product[4] + quantity  # Assuming quantity is in the third column
        cursor.execute("UPDATE products SET stock = %s WHERE name = %s", (new_quantity, name))
        connection.commit()
        print(f"Stock quantity for product '{name}' updated to {new_quantity}")
    else:
        try:
            # Execute SQL INSERT query to add the product
            cursor.execute("INSERT INTO products (name, category, price, stock) VALUES (%s, %s, %s, %s)",
                        (name, category, price,quantity))

            # Commit the transaction
            connection.commit()
            print("Product added successfully")
            return True

        except Exception as e:
            print(f"Error adding product: {e}")
            connection.rollback()
            return False

        finally:
            cursor.close()
            connection.close()

#add_product("Check", "Candy",5.000 ,3)

#*************************************************** REMOVE STOCKS ********************************************************************
def removeProduct(name, quantity):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        if not name:
            print("Name is required")
            return False

        cursor.execute("SELECT name, stock FROM products WHERE name = %s", (name,))
        product = cursor.fetchone()

        if product is None:
            print("No products found with the given name")
            return False

        current_stock = product[1]

        if current_stock < quantity:
            print("Current stock is less than the quantity you have specified")
            return False
        else:
            new_stock = current_stock - quantity
            if new_stock < 0:
                new_stock = 0
            cursor.execute("UPDATE products SET stock = %s WHERE name = %s", (new_stock, name))
            connection.commit()
            print(f"Stock quantity for product '{name}' reduced to {new_stock}")
            return True

    except Exception as e:
        print(f"Error removing product: {e}")
        return False

    finally:
        cursor.close()
        connection.close()

#************************************************searching a particular product **********************************************************
def searchProduct(name):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT name FROM products WHERE name LIKE %s", (name + "%",))
        products = cursor.fetchall()
        print(products)

        if products:
            alike_items = []
            print("Products starting with '{}' found:".format(name))
            for product in products:
                alike_items.append(product[0])
                print(alike_items)
            return alike_items
        else:
            print("No products found starting with '{}'".format(name))

    except Exception as e:
        print(f"Error searching for products: {e}")

    finally:
        cursor.close()
        connection.close()
#searchProduct("Or")


#************************************************ Login**********************************************


def login(username, password):
    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Retrieve the stored hashed password for the given username
        cursor.execute("SELECT password FROM employee WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result is None:
            print("Username not found")
            return False

        stored_hashed_password = result[0]

        # Check if the provided password matches the stored password
        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
            print("Login successful")
            return True
        else:
            print("Login failed")
            return False
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        cursor.close()
        connection.close()

#**************************************************insert employee *******************************************************

def sign_up(username, password):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:    
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO employee (username, password, role) VALUES (%s, %s, %s)", (username, hashed_password,"admin"))
        connection.commit()
        print("Signup successful")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

#**************************get user credentials******************

def get_employee_details(username):
    try:
        connection = get_db_connection()
        
        cursor = connection.cursor()

        cursor.execute("SELECT id, age, email, role, gender FROM employee WHERE username = %s", (username,))
        
        result = cursor.fetchone()

        if result:
            id, age, email, role, gender = result
            return id, age, email, role, gender
        else:
            print("No employee found with the provided username.")
            return None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

#********************************************insert employee***********************************
def insert_employee(username, age, gender, email, name, password, role):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        sql = "INSERT INTO employee (username, age, gender, email, name, password, role) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (username, age, gender, email, name, hashed_password.decode('utf-8'), role)
        cursor.execute(sql, values)

        connection.commit()

        print("Employee inserted successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

#**********************************************get employee details*************************************************************
def get_all_employee_details(): 
    try:
        connection = get_db_connection()
        
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT name, username, email, age, gender, role FROM employee")
        
        rows = cursor.fetchall()

        employee_details = [{column: value for column, value in row.items()} for row in rows]

        return employee_details
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
#**********************************************get product details*************************************************************

def get_all_product_details():
    try:
        connection = get_db_connection()
        
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT id, name, category, price, stock, description FROM products")
        
        rows = cursor.fetchall()

        product_details = [{column: value for column, value in row.items()} for row in rows]

        return product_details
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
#**********************************************update product ***************************************************
def update_product_handler(product_name, product_description, product_stock, product_price, product_category):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        update_query = """
        UPDATE products
        SET 
            description = %s,
            stock = %s,
            price = %s,
            category = %s
        WHERE name = %s
        """
        cursor.execute(update_query, (product_description, int(product_stock), float(product_price), product_category, product_name))
        connection.commit()

        print(f"Product {product_name} updated successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
#********************************update emp handler ***********************************
            
def update_emp_handler(emp_name, emp_username, emp_email, emp_role, emp_age,emp_gender):
    print(emp_username)
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        update_query = """
        UPDATE employee
        SET 
            name = %s,
            username = %s,
            role = %s,
            age = %s,
            email = %s
        WHERE username = %s
        """
        cursor.execute(update_query, (emp_name, emp_username, emp_role, emp_age, emp_email,emp_username))
        connection.commit()

        print(f"Employee {emp_username} updated successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
