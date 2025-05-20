from fastapi.websockets import WebSocket, WebSocketDisconnect
import asyncio
import json
from cafe_db_setup import get_db, init_db
from contextlib import asynccontextmanager
import mysql.connector

#Create + Read + Delete

async def handle_get_all_categories(websocket: WebSocket):
    with get_db() as conn:
        try:
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT 
                    ID_category,
                    category_name
                FROM Categories
                ORDER BY category_name
            """, )

            categories = []
            #wstaw dane do tablicy categories
            for c in cursor.fetchall():
                categories.append( {
                    "id": c["ID_category"],
                    "name": c["category_name"]
                } )            
            #wyślij dane w postaci pliku json
            await websocket.send_json({
                "type": "all_category_data",
                "data": categories
            })
        except mysql.connector.Error as err:
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}"
            })

async def handle_create_category(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            cursor.execute("START TRANSACTION")
            #dodajemy nowego pracownika
            cursor.execute("INSERT INTO Categories (category_name) "
                "VALUE (%s)",(data['name'],))
                
            new_id = cursor.lastrowid
            conn.commit()
            #informujemy o tym zainteresowanych
            await manager.broadcast({
                "type": "category_updated",
                "action": "created",
                "id": new_id,
                "name": data['name']
            })

            
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            print(f"Error: {err}")

async def handle_delete_category(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            category_id = data['category_id']
            #czy ten pracownik jest w bazie? jeśli nie, wyślij komunikat
            cursor.execute("SELECT 1 FROM Categories WHERE ID_category = %s", (category_id,))

            if not cursor.fetchone():
                await websocket.send_json({
                    "type": "error",
                    "message": f"Category with ID {category_id} not found"
                })
                return
            #jeśli tak, kontynuuj
            cursor.execute("DELETE FROM Categories WHERE ID_category = %s", (category_id,))
            conn.commit()
            #poinformuj zainteresowanych o zmianie
            await manager.broadcast({
                "type": "category_updated",
                "action": "deleted",
                "id": category_id
            })
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}"
            })