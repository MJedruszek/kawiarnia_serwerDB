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


#asyncio.get_event_loop().run_until_complete(test_staff_query())
#asyncio.get_event_loop().run_until_complete(test_create_staff())
#asyncio.get_event_loop().run_until_complete(test_one_staff_query(2))
#asyncio.get_event_loop().run_until_complete(test_delete_staff(2))
#asyncio.get_event_loop().run_until_complete(test_staff_query())
#asyncio.get_event_loop().run_until_complete(test_edit_staff(2))
#asyncio.get_event_loop().run_until_complete(test_staff_query())


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
            "status": "Not ready"
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

# asyncio.get_event_loop().run_until_complete(test_statuses_query())
# #asyncio.get_event_loop().run_until_complete(test_create_status())
# asyncio.get_event_loop().run_until_complete(test_delete_status(2))
# asyncio.get_event_loop().run_until_complete(test_statuses_query())

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

# asyncio.get_event_loop().run_until_complete(test_tables_query())
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