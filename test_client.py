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
            "name": "Szymon Holownia",
            "job": "Priest",
            "phone": "098433285",
            "mail": "referendum@google.com"
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        
        if data.get("type") == "staff_created":
            print("\nNew Staff Created:")
            print(f"ID: {data['id']}")
            print(f"Name: {data['name']}")
        else:
            print("Error:", data.get("message", "Unknown error"))


#asyncio.get_event_loop().run_until_complete(test_staff_query())
asyncio.get_event_loop().run_until_complete(test_create_staff())
asyncio.get_event_loop().run_until_complete(test_staff_query())