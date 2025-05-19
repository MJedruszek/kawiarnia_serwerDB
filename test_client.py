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
asyncio.get_event_loop().run_until_complete(test_one_staff_query(2))
#asyncio.get_event_loop().run_until_complete(test_delete_staff(2))
#asyncio.get_event_loop().run_until_complete(test_staff_query())
#asyncio.get_event_loop().run_until_complete(test_edit_staff(2))
asyncio.get_event_loop().run_until_complete(test_staff_query())
