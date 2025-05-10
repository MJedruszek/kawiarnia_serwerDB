import sqlite3
from contextlib import contextmanager

#poniższy kod stworzy bazę danych i umożliwi nawiązanie z nią połączenia

create_table_categories = """
CREATE TABLE IF NOT EXISTS Categories (
    ID_category INTEGER PRIMARY KEY,
    category_name VARCHAR
);
"""

create_table_order = """
CREATE TABLE IF NOT EXISTS "Order" (
    ID_order INTEGER PRIMARY KEY,
    ID_table INTEGER,  -- Reference to Tables, "no table - takeout" if null
    ID_o_status INTEGER,  -- Reference to order_status
    price DOUBLE,
    date TIMESTAMP,
    ID_employee INTEGER NOT NULL,  -- Reference to Staff
    FOREIGN KEY (ID_table) REFERENCES Tables(ID_table),
    FOREIGN KEY (ID_o_status) REFERENCES order_status(ID_o_status),
    FOREIGN KEY (ID_employee) REFERENCES Staff(ID_employee)
);
"""

create_table_order_products = """
CREATE TABLE IF NOT EXISTS Order_Products (
	ID_order INTEGER,
	ID_product INTEGER,
	quantity INTEGER,
	price DOUBLE,
	CONSTRAINT ORDER_PRODUCTS_PK PRIMARY KEY (ID_order,ID_product),
	CONSTRAINT FK_Order_Products_Order FOREIGN KEY (ID_order) REFERENCES "Order"(ID_order),
	CONSTRAINT FK_Order_Products_Products_2 FOREIGN KEY (ID_product) REFERENCES Products(ID_product)
);
"""

create_table_order_status = """
CREATE TABLE IF NOT EXISTS order_status (
    ID_o_status INTEGER PRIMARY KEY,
    status VARCHAR
);
"""

create_table_products = """
CREATE TABLE IF NOT EXISTS Products (
    ID_product INTEGER PRIMARY KEY,
    product_name VARCHAR,
    price DOUBLE,  -- Price in złotówkach
    quantity INTEGER,
    ID_category INTEGER,  -- Category reference (drink, food, dessert)
    prep_time DOUBLE,  -- Preparation time in minutes
    expiration_date DATE,
    FOREIGN KEY (ID_category) REFERENCES Categories(ID_category)
);
"""

create_table_schedule = """
CREATE TABLE IF NOT EXISTS Schedule (
    ID_schedule INTEGER PRIMARY KEY,
    date DATE,
    ID_employee INTEGER NOT NULL,
    shift VARCHAR,  -- shift data type replaced with VARCHAR
    FOREIGN KEY (ID_employee) REFERENCES Staff(ID_employee)
);
"""

create_table_staff = """
CREATE TABLE IF NOT EXISTS Staff (
    ID_employee INTEGER PRIMARY KEY,
    job_title VARCHAR,  -- jobs data type replaced with VARCHAR
    employee_name VARCHAR,  -- Storing both name and surname as a single string
    phone_number VARCHAR,
    mail VARCHAR
);
"""

create_table_tables = """
CREATE TABLE IF NOT EXISTS Tables (
	ID_table INTEGER,
	outside BOOLEAN,
	seats INTEGER, is_empty BOOLEAN,
	CONSTRAINT TABLES_PK PRIMARY KEY (ID_table)
);
"""

#funkcja inicjalizująca bazę danych
def initialize(cursor):
    cursor.execute(create_table_categories)
    cursor.execute(create_table_order)
    cursor.execute(create_table_order_products)
    cursor.execute(create_table_order_status)
    cursor.execute(create_table_products)
    cursor.execute(create_table_schedule)
    cursor.execute(create_table_staff)
    cursor.execute(create_table_tables)

#funkcje inicjalizujące i getujące bazę danych
@contextmanager
#tworzy połączenie z bazą
def get_db():
    conn = sqlite3.connect("cafe.db")
    conn.row_factory = sqlite3.Row  # Access columns by name
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
#wyświetla tabele z bazy danych
def test_db():
    with get_db as conn:
        cursor = conn.cursor()

        print("DB stworzone w pythonie: ")

        for row in cursor.execute("SELECT name FROM sqlite_master"):
            print(row)

