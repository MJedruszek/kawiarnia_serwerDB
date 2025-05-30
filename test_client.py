import asyncio
import websockets
import json

async def test_staff_query():
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print("Requesting staff data...")
        await websocket.send(json.dumps({
            "action": "get_all_staff"
        }))

        response = await websocket.recv()
        data = json.loads(response)
        print("Received data:")

        if data.get("type") == "all_staff_data":
            print("\nAll Staff Members:")
            for staff in data["data"]:
                print(f"\nID: {staff['id']}")
                print(f"Name: {staff['name']}")
                print(f"Position: {staff['job']}")
                print(f"Phone: {staff['phone']}")
                print(f"Email: {staff['mail']}")
        else:
            print("Error:", data.get("message", "Unknown error"))

        
async def test_create_staff():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        print("\nCreating new staff member...")
        await websocket.send(json.dumps({
            "action": "create_staff",
            "name": "Juliusz Slowacki",
            "job": "Manager",
            "phone": "987654321",
            "mail": "kordian.chmury@google.com"
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        
        if data.get("type") == "staff_updated" and data.get("action") == "created":
            print("\nNew Staff Created:")
            print(f"ID: {data['id']}")
            print(f"Name: {data['name']}")
        else:
            print("Error:", data.get("message", "Unknown error"))

async def test_one_staff_query(staff_id):
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print(f"\nFetching staff ID {staff_id}...")
        await websocket.send(json.dumps({
            "action": "get_one_staff",
            "staff_id": staff_id
        }))
    
        response = await websocket.recv()
        data = json.loads(response)

        if data.get("type") == "staff_details":
            staff = data["data"]
            print("\nStaff Details:")
            print(f"ID: {staff['id']}")
            print(f"Name: {staff['name']}")
            print(f"Position: {staff['job']}")
            print(f"Phone: {staff['phone']}")
            print(f"Email: {staff['mail']}")
        else:
            print("Error:", data.get("message", "Unknown error"))

async def test_delete_staff(staff_id):
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print(f"\nAttempting to delete staff ID {staff_id}...")

        #sprawdź, czy faktycznie istnieje
        await websocket.send(json.dumps({
            "action": "get_one_staff",
            "staff_id": staff_id
        }))
        verify_response = await websocket.recv()
        #jeśli nie, wypisz to i koniec
        if json.loads(verify_response).get("type") == "error":
            print(f"Cannot delete: Staff ID {staff_id} not found")
            return
        #jeśli tak, wyślij request
        await websocket.send(json.dumps({
            "action": "delete_staff",
            "staff_id": staff_id
        }))
        
        response = await websocket.recv()
        data = json.loads(response)

        if data.get("type") == "staff_updated" and data.get("action") == "deleted":
            print(f"\nSuccessfully deleted staff ID {staff_id}")
        else:
            print("\nDeletion failed:")
            print(f"Reason: {data.get('message')}")

async def test_edit_staff(staff_id):
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        print("\nCreating new staff member...")
        await websocket.send(json.dumps({
            "action": "edit_staff",
            "name": "Adam Mickiewicz",
            "job": "Barista",
            "phone": "123456789",
            "mail": "slowacki.najgorszy@google.com",
            "id" : staff_id
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        
        if data.get("type") == "staff_updated" and data.get("action") == "edited":
            print("\nStaff Edited:")
            print(f"ID: {data['id']}")
            print(f"Name: {data['name']}")
        else:
            print("Error:", data.get("message", "Unknown error"))


asyncio.get_event_loop().run_until_complete(test_staff_query())
asyncio.get_event_loop().run_until_complete(test_create_staff())
#asyncio.get_event_loop().run_until_complete(test_one_staff_query(2))
#asyncio.get_event_loop().run_until_complete(test_delete_staff(2))
#asyncio.get_event_loop().run_until_complete(test_staff_query())
#asyncio.get_event_loop().run_until_complete(test_edit_staff(2))
asyncio.get_event_loop().run_until_complete(test_staff_query())


                                    #DO CATEGORIES
async def test_categories_query():
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print("Requesting category data...")
        await websocket.send(json.dumps({
            "action": "get_all_categories"
        }))

        response = await websocket.recv()
        data = json.loads(response)
        print("Received data:")

        if data.get("type") == "all_category_data":
            print("\nAll Categories:")
            for category in data["data"]:
                print(f"\nID: {category['id']}")
                print(f"Name: {category['name']}")
        else:
            print("Error:", data.get("message", "Unknown error"))

async def test_create_category():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        print("\nCreating new category...")
        await websocket.send(json.dumps({
            "action": "create_category",
            "name": "Cold Drink"
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        
        if data.get("type") == "category_updated" and data.get("action") == "created":
            print("\nNew Category Created:")
            print(f"ID: {data['id']}")
            print(f"Name: {data['name']}")
        else:
            print("Error:", data.get("message", "Unknown error"))

async def test_delete_category(category_id):
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print(f"\nAttempting to delete category ID {category_id}...")
        #wyślij request
        await websocket.send(json.dumps({
            "action": "delete_category",
            "category_id": category_id
        }))
        
        response = await websocket.recv()
        data = json.loads(response)

        if data.get("type") == "category_updated" and data.get("action") == "deleted":
            print(f"\nSuccessfully deleted category ID {category_id}")
        else:
            print("\nDeletion failed:")
            print(f"Reason: {data.get('message')}")


#asyncio.get_event_loop().run_until_complete(test_categories_query())
#asyncio.get_event_loop().run_until_complete(test_delete_category(1))
#asyncio.get_event_loop().run_until_complete(test_categories_query())


                                    #DO order_status
async def test_statuses_query():
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print("Requesting status data...")
        await websocket.send(json.dumps({
            "action": "get_all_statuses"
        }))

        response = await websocket.recv()
        data = json.loads(response)
        print("Received data:")

        if data.get("type") == "all_statuses_data":
            print("\nAll statuses:")
            for status in data["data"]:
                print(f"\nID: {status['id']}")
                print(f"Status: {status['status']}")
        else:
            print("Error:", data.get("message", "Unknown error"))

async def test_create_status():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        print("\nCreating new status...")
        await websocket.send(json.dumps({
            "action": "create_status",
            "status": "In preparation"
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        
        if data.get("type") == "status_updated" and data.get("action") == "created":
            print("\nNew status Created:")
            print(f"ID: {data['id']}")
            print(f"Status: {data['status']}")
        else:
            print("Error:", data.get("message", "Unknown error"))

async def test_delete_status(status_id):
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print(f"\nAttempting to delete status ID {status_id}...")
        #wyślij request
        await websocket.send(json.dumps({
            "action": "delete_status",
            "status_id": status_id
        }))
        
        response = await websocket.recv()
        data = json.loads(response)

        if data.get("type") == "status_updated" and data.get("action") == "deleted":
            print(f"\nSuccessfully deleted status ID {status_id}")
        else:
            print("\nDeletion failed:")
            print(f"Reason: {data.get('message')}")

#asyncio.get_event_loop().run_until_complete(test_statuses_query())
#asyncio.get_event_loop().run_until_complete(test_create_status())
#asyncio.get_event_loop().run_until_complete(test_delete_status(4))
#asyncio.get_event_loop().run_until_complete(test_statuses_query())

                                    #DO Tables
async def test_tables_query():
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print("Requesting status data...")
        await websocket.send(json.dumps({
            "action": "get_all_tables"
        }))

        response = await websocket.recv()
        data = json.loads(response)
        print("Received data:")

        if data.get("type") == "all_tables_data":
            print("\nAll tables:")
            for table in data["data"]:
                print(f"\nID: {table['id']}")
                print(f"Outside: {table['outside']}")
                print(f"Seats: {table['seats']}")
                print(f"Is Empty: {table['is_empty']}")
                
        else:
            print("Error:", data.get("message", "Unknown error"))

async def test_create_table():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        print("\nCreating new table...")
        await websocket.send(json.dumps({
            "action": "create_table",
            "outside": 0,
            "seats": 3
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        
        if data.get("type") == "tables_updated" and data.get("action") == "created":
            print("\nNew table Created:")
            print(f"ID: {data['id']}")
        else:
            print("Error:", data.get("message", "Unknown error"))

async def test_delete_table(table_id):
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print(f"\nAttempting to delete table ID {table_id}...")
        #wyślij request
        await websocket.send(json.dumps({
            "action": "delete_table",
            "table_id": table_id
        }))
        
        response = await websocket.recv()
        data = json.loads(response)

        if data.get("type") == "tables_updated" and data.get("action") == "deleted":
            print(f"\nSuccessfully deleted table ID {table_id}")
        else:
            print("\nDeletion failed:")
            print(f"Reason: {data.get('message')}")

async def test_edit_table(table_id):
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        print("\nEditing a table...")
        await websocket.send(json.dumps({
            "action": "edit_table",
            "id": table_id,
            "outside": 0,
            "seats": 4
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        
        if data.get("type") == "tables_updated" and data.get("action") == "edited":
            print("\nTable edited:")
            print(f"ID: {data['id']}")
        else:
            print("Error:", data.get("message", "Unknown error"))

async def test_edit_table_state(table_id):
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        print("\nEditing a table...")
        await websocket.send(json.dumps({
            "action": "change_table_state",
            "id": table_id,
            "is_empty": 0
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        
        if data.get("type") == "tables_updated" and data.get("action") == "edited":
            print("\nTable edited:")
            print(f"ID: {data['id']}")
        else:
            print("Error:", data.get("message", "Unknown error"))

#asyncio.get_event_loop().run_until_complete(test_tables_query())
# asyncio.get_event_loop().run_until_complete(test_create_table())
# asyncio.get_event_loop().run_until_complete(test_edit_table(1))
# asyncio.get_event_loop().run_until_complete(test_edit_table_state(3))
# #asyncio.get_event_loop().run_until_complete(test_delete_table(2))
# asyncio.get_event_loop().run_until_complete(test_tables_query())

                                    #DO SCHEDULE

async def test_create_schedule():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        print("\nCreating new schedule...")
        await websocket.send(json.dumps({
            "action": "create_schedule",
            "date": "2025-10-11",
            "ID_employee": 3,
            "shift": "Evening"
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        
        if data.get("type") == "schedule_updated" and data.get("action") == "created":
            print("\nNew schedule Created:")
            print(f"ID: {data['id']}")
            print(f"Date: {data['date']}")
        else:
            print("Error:", data.get("message", "Unknown error"))

async def test_delete_schedule(schedule_id):
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print(f"\nAttempting to delete schedule ID {schedule_id}...")
        #wyślij request
        await websocket.send(json.dumps({
            "action": "delete_schedule",
            "schedule_id": schedule_id
        }))
        
        response = await websocket.recv()
        data = json.loads(response)

        if data.get("type") == "schedule_updated" and data.get("action") == "deleted":
            print(f"\nSuccessfully deleted schedule ID {schedule_id}")
        else:
            print("\nDeletion failed:")
            print(f"Reason: {data.get('message')}")

async def test_get_schedule_by_staffID(id):
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print("Requesting schedule data by employee...")
        await websocket.send(json.dumps({
            "action": "get_schedule_by_employee",
            "employee_id": id
        }))

        response = await websocket.recv()
        data = json.loads(response)
        print("Received data:")

        if data.get("type") == "schedule_by_staff_data":
            print(f"\nAll of {data['name']} scheduled shifts:")
            for schedule in data["data"]:
                print(f"\nID: {schedule['id']}")
                print(f"Date: {schedule['date']}")
                print(f"Shift: {schedule['shift']}")
                
        else:
            print("Error:", data.get("message", "Unknown error"))

async def test_get_schedule_by_date(date):
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print("Requesting schedule data by date...")
        await websocket.send(json.dumps({
            "action": "get_schedule_by_date",
            "date": date
        }))

        response = await websocket.recv()
        data = json.loads(response)
        print("Received data:")

        if data.get("type") == "schedule_by_date_data":
            print(f"\nAll of the shifts scheduled for {date}:")
            for schedule in data["data"]:
                print(f"\nID: {schedule['id']}")
                print(f"Employee: {schedule['employee_name']}")
                print(f"Employee ID: {schedule['ID_employee']}")
                print(f"Shift: {schedule['shift']}")
                
                
        else:
            print("Error:", data.get("message", "Unknown error"))

#asyncio.get_event_loop().run_until_complete(test_create_schedule())
#asyncio.get_event_loop().run_until_complete(test_delete_schedule(5))
#asyncio.get_event_loop().run_until_complete(test_get_schedule_by_date("2025-10-11"))
#asyncio.get_event_loop().run_until_complete(test_get_schedule_by_staffID(1))

                                    #ORDERS

async def test_order_query():
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print("Requesting order data...")
        await websocket.send(json.dumps({
            "action": "get_all_orders"
        }))

        response = await websocket.recv()
        data = json.loads(response)
        print("Received data:")

        if data.get("type") == "all_orders_data":
            print("\nAll Orders:")
            for order in data["data"]:
                print(f"\nID: {order['ID_order']}")
                print(f"Table ID: {order['ID_table']}")
                print(f"Employee: {order['ID_employee']}, {order['employee']}")
                print(f"Status: {order['ID_o_status']}, {order['o_status']}")
                print(f"Price: {order['price']} zł")
                print(f"Date: {order['date']}")
        else:
            print("Error:", data.get("message", "Unknown error"))

        
async def test_create_order():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        print("\nCreating new order...")
        await websocket.send(json.dumps({
            "action": "create_order",
            "ID_table": 3,
            "price": 19.99,
            "ID_employee": 1
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        
        if data.get("type") == "orders_updated" and data.get("action") == "created":
            print("\nNew Order Created:")
            print(f"ID: {data['id']}")
            print(f"Employee: {data['employee']}")
        else:
            print("Error:", data.get("message", "Unknown error"))

async def test_delete_order(order_id):
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print(f"\nAttempting to delete order ID {order_id}...")

        #wyślij request
        await websocket.send(json.dumps({
            "action": "delete_order",
            "order_id": order_id
        }))
        
        response = await websocket.recv()
        data = json.loads(response)

        if data.get("type") == "order_updated" and data.get("action") == "deleted":
            print(f"\nSuccessfully deleted order ID {order_id}")
        else:
            print("\nDeletion failed:")
            print(f"Reason: {data.get('message')}")

async def test_edit_order(order_id):
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        print("\nEditing order...")
        await websocket.send(json.dumps({
            "action": "edit_order",
            "ID_table": 1,
            "ID_o_status": 2,
            "price": 22.00,
            "date": "2025-04-21 19:58:35",
            "ID_employee": 4,
            "id": order_id
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        
        if data.get("type") == "orders_updated" and data.get("action") == "edited":
            print("\nOrder Edited:")
            print(f"ID: {data['id']}")
            print(f"Employee: {data['ID_employee']}")
        else:
            print("Error:", data.get("message", "Unknown error"))


async def test_get_order_by_statusID(id):
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print("Requesting order data...")
        await websocket.send(json.dumps({
            "action": "get_orders_by_status",
            "ID_status": id
        }))

        response = await websocket.recv()
        data = json.loads(response)
        print("Received data:")

        if data.get("type") == "orders_by_status_data":
            print(f"\nAll Orders with status:{data['status']}")
            for order in data["data"]:
                print(f"\nID: {order['ID_order']}")
                print(f"Table ID: {order['ID_table']}")
                print(f"Employee: {order['ID_employee']}, {order['employee']}")
                print(f"Price: {order['price']} zł")
                print(f"Date: {order['date']}")
        else:
            print("Error:", data.get("message", "Unknown error"))


async def test_edit_order_status(order_id):
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        print("\nEditing order status...")
        await websocket.send(json.dumps({
            "action": "change_order_status",
            "id": order_id,
            "ID_o_status": 2
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        
        if data.get("type") == "orders_updated" and data.get("action") == "edited":
            print("\nOrder Edited:")
            print(f"ID: {data['id']}")
        else:
            print("Error:", data.get("message", "Unknown error"))


#asyncio.get_event_loop().run_until_complete(test_order_query())
#asyncio.get_event_loop().run_until_complete(test_create_order())
#asyncio.get_event_loop().run_until_complete(test_delete_order(4))
#asyncio.get_event_loop().run_until_complete(test_edit_order(3))
#asyncio.get_event_loop().run_until_complete(test_edit_order_status(5))
#asyncio.get_event_loop().run_until_complete(test_get_order_by_statusID(2))
#asyncio.get_event_loop().run_until_complete(test_order_query())


async def test_products_query():
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print("Requesting products data...")
        await websocket.send(json.dumps({
            "action": "get_all_products"
        }))

        response = await websocket.recv()
        data = json.loads(response)
        print("Received data:")

        if data.get("type") == "all_products_data":
            print("\nAll Products:")
            for product in data["data"]:
                print(f"\nID: {product['id']}")
                print(f"Name: {product['name']}")
                print(f"Price: {product['price']} zł")
                print(f"Quantity: {product['quantity']}")
                print(f"Prep time: {product['prep_time']} min")
                print(f"Category: {product['ID_category']}, {product['category_name']}")
                print(f"Expiration date: {product['expiration_date']}")
        else:
            print("Error:", data.get("message", "Unknown error"))

        
async def test_create_product():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        print("\nCreating new staff member...")
        await websocket.send(json.dumps({
            "action": "create_product",
            "name": "Iced Vanilla Late",
            "price": 15.99,
            "quantity": 10,
            "prep_time": 3.0,
            "expiration_date": "2025-05-31",
            "ID_category": 4
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        
        if data.get("type") == "products_updated" and data.get("action") == "created":
            print("\nNew Product Created:")
            print(f"ID: {data['id']}")
            print(f"Name: {data['name']}")
        else:
            print("Error:", data.get("message", "Unknown error"))

async def test_one_product_query(product_id):
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print(f"\nFetching product ID {product_id}...")
        await websocket.send(json.dumps({
            "action": "get_product_by_id",
            "product_id": product_id
        }))
    
        response = await websocket.recv()
        data = json.loads(response)

        if data.get("type") == "product_details":
            product = data["data"]
            print("\nProduct Details:")
            print(f"\nID: {product['id']}")
            print(f"Name: {product['name']}")
            print(f"Price: {product['price']} zł")
            print(f"Quantity: {product['quantity']}")
            print(f"Prep time: {product['prep_time']} min")
            print(f"Category: {product['ID_category']}, {product['category_name']}")
            print(f"Expiration date: {product['expiration_date']}")
        else:
            print("Error:", data.get("message", "Unknown error"))

async def test_delete_product(product_id):
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print(f"\nAttempting to delete product ID {product_id}...")

        #sprawdź, czy faktycznie istnieje
        await websocket.send(json.dumps({
            "action": "get_product_by_id",
            "product_id": product_id
        }))
        verify_response = await websocket.recv()
        #jeśli nie, wypisz to i koniec
        if json.loads(verify_response).get("type") == "error":
            print(f"Cannot delete: Product ID {product_id} not found")
            return
        #jeśli tak, wyślij request
        await websocket.send(json.dumps({
            "action": "delete_product",
            "product_id": product_id
        }))
        
        response = await websocket.recv()
        data = json.loads(response)

        if data.get("type") == "products_updated" and data.get("action") == "deleted":
            print(f"\nSuccessfully deleted product ID {product_id}")
        else:
            print("\nDeletion failed:")
            print(f"Reason: {data.get('message')}")

async def test_edit_product(product_id):
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        print("\nEditing product...")
        await websocket.send(json.dumps({
            "action": "edit_product",
            "name": "Black coffee",
            "price": 9.99,
            "ID_category": 4,
            "quantity": 20,
            "prep_time": 2.0,
            "expiration_date": "2025-06-14",
            "id": product_id
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        
        if data.get("type") == "products_updated" and data.get("action") == "edited":
            print("\nProduct Edited:")
            print(f"ID: {data['id']}")
            print(f"Name: {data['name']}")
        else:
            print("Error:", data.get("message", "Unknown error"))

async def test_get_products_by_category(id):
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print("Requesting products data...")
        await websocket.send(json.dumps({
            "action": "get_products_by_category",
            "ID_category": id
        }))

        response = await websocket.recv()
        data = json.loads(response)
        print("Received data:")

        if data.get("type") == "products_by_categories_data":
            print(f"\nAll Producs with category:{data['category_name']}")
            for product in data["data"]:
                print(f"\nID: {product['id']}")
                print(f"Name: {product['name']}")
                print(f"Price: {product['price']} zł")
                print(f"Quantity: {product['quantity']}")
                print(f"Prep time: {product['prep_time']} min")
                print(f"Expiration date: {product['expiration_date']}")
        else:
            print("Error:", data.get("message", "Unknown error"))

#asyncio.get_event_loop().run_until_complete(test_products_query())
#asyncio.get_event_loop().run_until_complete(test_create_product())
#asyncio.get_event_loop().run_until_complete(test_create_product())
#asyncio.get_event_loop().run_until_complete(test_one_product_query(2))
#asyncio.get_event_loop().run_until_complete(test_delete_product(3))
#asyncio.get_event_loop().run_until_complete(test_staff_query())
#asyncio.get_event_loop().run_until_complete(test_edit_product(2))
#asyncio.get_event_loop().run_until_complete(test_get_products_by_category(4))
#asyncio.get_event_loop().run_until_complete(test_products_query())

async def test_get_products_by_orderID(id):
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print("Requesting products data...")
        await websocket.send(json.dumps({
            "action": "get_products_by_orderID",
            "ID_order": id
        }))

        response = await websocket.recv()
        data = json.loads(response)
        print("Received data:")

        if data.get("type") == "products_by_orderID_data":
            print(f"\nAll Products with order nr:{data['ID_order']}")
            for product in data["data"]:
                print(f"\nProduct: {product['ID_product']}, {product['product_name']}")
                print(f"Price: {product['price']}")
                print(f"Quantity: {product['quantity']}")
        else:
            print("Error:", data.get("message", "Unknown error"))


async def test_create_order_product():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        print("\nCreating new order product member...")
        await websocket.send(json.dumps({
            "action": "create_order_product",
            "ID_order": 3,
            "ID_product": 2,
            "quantity": 1,
            "price": 10.99
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        
        if data.get("type") == "order_products_updated" and data.get("action") == "created":
            print("\nNew Order Product Created:")
            print(f"ID: {data['ID_order']}")
        else:
            print("Error:", data.get("message", "Unknown error"))

async def test_delete_order_product(product_id, order_id):
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        print(f"\nAttempting to delete product ID {product_id}, {order_id}...")

        #wyślij request
        await websocket.send(json.dumps({
            "action": "delete_order_product",
            "product_id": product_id,
            "order_id": order_id
        }))
        
        response = await websocket.recv()
        data = json.loads(response)

        if data.get("type") == "order_products_updated" and data.get("action") == "deleted":
            print(f"\nSuccessfully deleted product ID {product_id}, {order_id}")
        else:
            print("\nDeletion failed:")
            print(f"Reason: {data.get('message')}")

#asyncio.get_event_loop().run_until_complete(test_order_query())
# asyncio.get_event_loop().run_until_complete(test_products_query())

#asyncio.get_event_loop().run_until_complete(test_delete_order_product(2,3))
#asyncio.get_event_loop().run_until_complete(test_create_order_product())
#asyncio.get_event_loop().run_until_complete(test_create_order_product())
#asyncio.get_event_loop().run_until_complete(test_get_products_by_orderID(3))
#asyncio.get_event_loop().run_until_complete(test_get_products_by_orderID(3))
#asyncio.get_event_loop().run_until_complete(test_order_query())


