from fastapi import FastAPI
from fastapi.websockets import WebSocket, WebSocketDisconnect
import asyncio
import json
from cafe_db_setup import get_db, init_db
from contextlib import asynccontextmanager
import sqlite3

#poniższy kod stworzy serwer za pomocą websockets i umożliwi połączenie z nim, a także podstawowe interakcje CRUD

#klasa sterująca połączeniem z websockets
class ConnectionManager:
    #inicjalizacja połączenia (pustego)
    def __init__(self):
        self.active_connections = set()
    #inicjalizacja właściwego połączenia z websocket
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    #rozłączenie z serwerem
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    #przesłanie wiadomości 
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()

                                #stringi zawierające query do SQLite

#gettery (wszystkiego):##########################################################################################
s_get_all_staff ="""
    SELECT 
        ID_employee,
        employee_name,
        job_title,
        phone_number,
        mail
    FROM Staff
    ORDER BY employee_name
"""

#gettery (pojedynczego):#########################################################################################

#create:#########################################################################################################

#delete:#########################################################################################################

#update:#########################################################################################################

                                #funkcje potrzebne do wymiany dancyh z bazą:
#gettery (wszystkiego):##########################################################################################
async def handle_get_all_staff(websocket: WebSocket):
    with get_db() as conn:
        try:
            #wykonaj polecenie na bazie (pobierz dane)
            cursor = conn.execute(s_get_all_staff)
            staff_members = []
            #wstaw dane do tablicy staff_members
            for s in cursor.fetchall():
                staff_members.append( {
                    "id": s["ID_employee"],
                    "name": s["employee_name"],
                    "job": s["job_title"],
                    "phone": s["Phone_number"],
                    "mail": s["mail"]
                } )
            #wyślij dane w postaci pliku json
            await websocket.send_json({
                "type": "all_staff_data",
                "data": staff_members
            })
        except sqlite3.Error as e:
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {str(e)}"
            })
            
#gettery (pojedynczego):#########################################################################################

#create:#########################################################################################################

#delete:#########################################################################################################

#update:#########################################################################################################

                                #Funkcje bezpośrednio do działania API:
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    


app = FastAPI(lifespan=lifespan)

#funkcja do odbierania i wysyłania danych (wspólny endpoint)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            #odbierz dane od wejścia (request)
            data = await websocket.receive_json()

            #zajmij się requestem - każdy w osobnym ifie (nazwa requesta ta sama, co handler)
            if data['action'] == 'get_all_staff':
                await handle_get_all_staff(websocket)
            else:
                print("Odebrano nieprawidłowy request")
    #Rozłączono
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    #Request nie był prawidłowy
    except json.JSONDecodeError:
        await websocket.send_json({"error": "Invalid JSON"})