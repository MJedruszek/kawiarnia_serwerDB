from fastapi import FastAPI
from fastapi.websockets import WebSocket, WebSocketDisconnect
import asyncio
import json
from cafe_db_setup import get_db, init_db
from contextlib import asynccontextmanager
import mysql.connector


#importy z plików do queries
import staff_queries
import categories_queries
import order_status_queries
import table_queries
import schedule_queries
import order_queries
import products_queries

#poniższy kod stworzy serwer za pomocą websockets i umożliwi połączenie z nim, a także podstawowe interakcje CRUD
#DO WPISYWANIA W TERMINAL:
#uvicorn server:app --reload --host 0.0.0.0 --port 8000
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
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)

            #zajmij się requestem - każdy w osobnym ifie (nazwa requesta ta sama, co handler)
            #STAFF
            if data['action'] == 'get_all_staff':
                await staff_queries.handle_get_all_staff(websocket)
            elif data['action'] == 'create_staff':
                await staff_queries.handle_create_staff(websocket, data, manager)
            elif data['action'] == 'get_one_staff':
                await staff_queries.handle_get_one_staff(websocket, data)
            elif data['action'] == 'delete_staff':
                await staff_queries.handle_delete_staff(websocket, data, manager)
            elif data['action'] == 'edit_staff':
                await staff_queries.handle_edit_staff(websocket, data, manager)
            #KATEGORIE
            elif data['action'] == 'get_all_categories':
                await categories_queries.handle_get_all_categories(websocket)
            elif data['action'] == 'create_category':
                await categories_queries.handle_create_category(websocket, data, manager)
            elif data['action'] == 'delete_category':
                await categories_queries.handle_delete_category(websocket, data, manager)
            #STATUSY
            elif data['action'] == 'get_all_statuses':
                await order_status_queries.handle_get_all_statuses(websocket)
            elif data['action'] == 'create_status':
                await order_status_queries.handle_create_status(websocket, data, manager)
            elif data['action'] == 'delete_status':
                await order_status_queries.handle_delete_status(websocket, data, manager)
            #STOLIKI
            elif data['action'] == 'get_all_tables':
                await table_queries.handle_get_all_tables(websocket)
            elif data['action'] == 'create_table':
                await table_queries.handle_create_table(websocket, data, manager)
            elif data['action'] == 'delete_table':
                await table_queries.handle_delete_table(websocket, data, manager)
            elif data['action'] == 'edit_table':
                await table_queries.handle_edit_table(websocket, data, manager)
            elif data['action'] == 'change_table_state':
                await table_queries.handle_change_table_state(websocket, data, manager)
            #SCHEDULE
            elif data['action'] == 'create_schedule':
                await schedule_queries.handle_create_schedule(websocket, data, manager)
            elif data['action'] == 'delete_schedule':
                await schedule_queries.handle_delete_schedule(websocket, data, manager)
            elif data['action'] == 'get_schedule_by_employee':
                await schedule_queries.handle_get_schedule_by_employeeID(websocket, data)
            elif data['action'] == 'get_schedule_by_date':
                await schedule_queries.handle_get_schedule_by_date(websocket, data)
            #ZAMÓWIENIA
            elif data['action'] == 'get_all_orders':
                await order_queries.handle_get_all_orders(websocket)
            elif data['action'] == 'create_order':
                await order_queries.handle_create_order(websocket, data, manager)
            elif data['action'] == 'get_orders_by_status':
                await order_queries.handle_get_order_by_status(websocket, data)
            elif data['action'] == 'delete_order':
                await order_queries.handle_delete_order(websocket, data, manager)
            elif data['action'] == 'edit_order':
                await order_queries.handle_edit_order(websocket, data, manager)
            elif data['action'] == 'change_order_status':
                await order_queries.handle_change_order_status(websocket, data, manager)
            #PRODUKTY
            elif data['action'] == 'get_all_products':
                await products_queries.handle_get_all_products(websocket)
            elif data['action'] == 'create_product':
                await products_queries.handle_create_product(websocket, data, manager)
            elif data['action'] == 'get_products_by_category':
                await products_queries.handle_get_products_by_category(websocket, data)
            elif data['action'] == 'delete_product':
                await products_queries.handle_delete_product(websocket, data, manager)
            elif data['action'] == 'edit_product':
                await products_queries.handle_edit_product(websocket, data, manager)
            elif data['action'] == 'get_product_by_id':
                await products_queries.handle_get_one_product(websocket, data)
            else:
                print("Odebrano nieprawidłowy request")
    #Rozłączono
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    #Request nie był prawidłowy
    except json.JSONDecodeError:
        await websocket.send_json({"error": "Invalid JSON"})