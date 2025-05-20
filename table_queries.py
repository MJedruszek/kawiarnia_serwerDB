from fastapi.websockets import WebSocket, WebSocketDisconnect
import asyncio
import json
from cafe_db_setup import get_db, init_db
from contextlib import asynccontextmanager
import mysql.connector

#Create + Read + Delete

async def handle_get_all_tables(websocket: WebSocket):
    with get_db() as conn:
        try:
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT 
                    ID_table,
                    outside,
                    seats,
                    is_empty
                FROM Tables
                ORDER BY ID_table
            """, )

            tables = []
            #wstaw dane do tablicy categories
            for t in cursor.fetchall():
                tables.append( {
                    "id": t["ID_table"],
                    "outside": t["outside"],
                    "seats": t["seats"],
                    "is_empty": t["is_empty"]
                } )            
            #wyślij dane w postaci pliku json
            await websocket.send_json({
                "type": "all_tables_data",
                "data": tables
            })
        except mysql.connector.Error as err:
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}"
            })

async def handle_create_table(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            cursor.execute("START TRANSACTION")
            #dodajemy nowego pracownika
            cursor.execute("INSERT INTO Tables (outside, seats, is_empty) "
                "VALUE (%s, %s, 0)",(data['outside'],data['seats'],))
                
            new_id = cursor.lastrowid
            conn.commit()
            #informujemy o tym zainteresowanych (tylko ID, nie ma sensu dodawać tego w trakcie zmiany, więc migracja danych na początku zmiany wystarczy)
            await manager.broadcast({
                "type": "tables_updated",
                "action": "created",
                "id": new_id
            })

            
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            print(f"Error: {err}")

async def handle_delete_table(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            table_id = data['table_id']
            #czy ten pracownik jest w bazie? jeśli nie, wyślij komunikat
            cursor.execute("SELECT 1 FROM Tables WHERE ID_table = %s", (table_id,))

            if not cursor.fetchone():
                await websocket.send_json({
                    "type": "error",
                    "message": f"Table with ID {table_id} not found"
                })
                return
            #jeśli tak, kontynuuj
            cursor.execute("DELETE FROM Tables WHERE ID_table = %s", (table_id,))
            conn.commit()
            #poinformuj zainteresowanych o zmianie
            await manager.broadcast({
                "type": "tables_updated",
                "action": "deleted",
                "id": table_id
            })
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}"
            })