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


asyncio.get_event_loop().run_until_complete(test_staff_query())