import mysql.connector
from mysql.connector import pooling
from contextlib import contextmanager

#poniższy kod stworzy bazę danych i umożliwi nawiązanie z nią połączenia

create_table_categories = """
CREATE TABLE IF NOT EXISTS Categories (
    ID_category INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(255)
);
"""

create_table_order = """
CREATE TABLE IF NOT EXISTS `Order` (
    ID_order INT AUTO_INCREMENT PRIMARY KEY,
    ID_table INT,  -- Reference to Tables, "no table - takeout" if null
    ID_o_status INT,  -- Reference to order_status
    price DOUBLE,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ID_employee INT NOT NULL,  -- Reference to Staff
    FOREIGN KEY (ID_table) REFERENCES Tables(ID_table),
    FOREIGN KEY (ID_o_status) REFERENCES order_status(ID_o_status),
    FOREIGN KEY (ID_employee) REFERENCES Staff(ID_employee)
);
"""

create_table_order_products = """
CREATE TABLE IF NOT EXISTS Order_Products (
    ID_order INT,
    ID_product INT,
    quantity INT,
    price DOUBLE,
    PRIMARY KEY (ID_order, ID_product),
    FOREIGN KEY (ID_order) REFERENCES `Order`(ID_order),
    FOREIGN KEY (ID_product) REFERENCES Products(ID_product)
);
"""

create_table_order_status = """
CREATE TABLE IF NOT EXISTS order_status (
    ID_o_status INT AUTO_INCREMENT PRIMARY KEY,
    status VARCHAR(255)
);
"""

create_table_products = """
CREATE TABLE IF NOT EXISTS Products (
    ID_product INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(255),
    price DOUBLE,  -- Price in zł
    quantity INT,
    ID_category INT,  -- Category reference (drink, food, dessert)
    prep_time DOUBLE,  -- Preparation time in minutes
    expiration_date DATE,
    FOREIGN KEY (ID_category) REFERENCES Categories(ID_category)
);
"""

create_table_schedule = """
CREATE TABLE IF NOT EXISTS Schedule (
    ID_schedule INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    ID_employee INT NOT NULL,
    shift VARCHAR(255),  -- shift data type replaced with VARCHAR
    FOREIGN KEY (ID_employee) REFERENCES Staff(ID_employee)
);
"""

create_table_staff = """
CREATE TABLE IF NOT EXISTS Staff (
    ID_employee INT AUTO_INCREMENT PRIMARY KEY,
    job_title VARCHAR(255),  -- jobs data type replaced with VARCHAR
    employee_name VARCHAR(255),  -- Storing both name and surname as a single string
    phone_number VARCHAR(20),
    mail VARCHAR(255)
);
"""

create_table_tables = """
CREATE TABLE IF NOT EXISTS Tables (
    ID_table INT AUTO_INCREMENT PRIMARY KEY,
    outside BOOLEAN,
    seats INT,
    is_empty BOOLEAN
);
"""

#do logowania
db_config = {
    "host": "localhost",
    "user": "cafe_user",
    "password": "password",
    "database": "cafe_db"
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="cafe_pool",
    pool_size=5,
    **db_config
)

#funkcja inicjalizująca bazę danych
def initialize(cursor):
    cursor.execute("CREATE DATABASE IF NOT EXISTS cafe_db")
    cursor.execute(create_table_categories)
    cursor.execute(create_table_staff)
    cursor.execute(create_table_tables)
    cursor.execute(create_table_order_status)
    cursor.execute(create_table_products)
    cursor.execute(create_table_schedule)
    cursor.execute(create_table_order)
    cursor.execute(create_table_order_products)
    cursor.execute("""INSERT INTO Order_Status (ID_o_status, status) VALUES (1, "Just ordered") ON DUPLICATE KEY UPDATE status = "Just ordered";""")
    cursor.execute("""INSERT INTO Order_Status (ID_o_status, status) VALUES (2, "Preparing") ON DUPLICATE KEY UPDATE status = "Preparing";""")
    cursor.execute("""INSERT INTO Order_Status (ID_o_status, status) VALUES (3, "Ready") ON DUPLICATE KEY UPDATE status = "Ready";""")
    cursor.execute("""INSERT INTO Order_Status (ID_o_status, status) VALUES (4, "Served") ON DUPLICATE KEY UPDATE status = "Served";""")
    cursor.execute("""INSERT INTO Order_Status (ID_o_status, status) VALUES (5, "Paid") ON DUPLICATE KEY UPDATE status = "Paid";""")
    cursor.execute("""INSERT INTO Order_Status (ID_o_status, status) VALUES (6, "Cancelled") ON DUPLICATE KEY UPDATE status = "Cancelled";""")
    
    

#funkcje inicjalizujące i getujące bazę danych
@contextmanager
#tworzy połączenie z bazą
def get_db():
    conn = connection_pool.get_connection()
    try:
        yield conn
    finally:
        conn.close()
#tworzy bazę danych, ze sprawdzeniem, czy tabele już istnieją
def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        initialize(cursor)
        conn.commit()


