from fastapi.websockets import WebSocket, WebSocketDisconnect
import asyncio
import json
from cafe_db_setup import get_db, init_db
from contextlib import asynccontextmanager
import mysql.connector

#Create + Read + Delete

async def handle_get_all_statuses(websocket: WebSocket, data):
    with get_db() as conn:
        try:
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT 
                    ID_o_status,
                    status
                FROM order_status
                ORDER BY ID_o_status
            """, )

            statuses = []
            #wstaw dane do tablicy categories
            for s in cursor.fetchall():
                statuses.append( {
                    "ID_o_status": s["ID_o_status"],
                    "status": s["status"]
                } )            
            #wyślij dane w postaci pliku json
            await websocket.send_json({
                "type": "all_statuses_data",
                "data": statuses,
                "requestID": data['requestID']
            })
        except mysql.connector.Error as err:
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}",
                "requestID": data['requestID']
            })

async def handle_create_status(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            cursor.execute("START TRANSACTION")
            #dodajemy nowego pracownika
            cursor.execute("INSERT INTO order_status (status) "
                "VALUE (%s)",(data['status'],))
                
            new_id = cursor.lastrowid
            conn.commit()
            #informujemy o tym zainteresowanych
            await manager.broadcast({
                "type": "status_updated",
                "action": "created",
                "ID_o_status": new_id,
                "status": data['status'],
                "requestID": data['requestID']
            })

            
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            print(f"Error: {err}")

async def handle_delete_status(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            status_id = data['status_id']
            #czy ten pracownik jest w bazie? jeśli nie, wyślij komunikat
            cursor.execute("SELECT 1 FROM order_status WHERE ID_o_status = %s", (status_id,))

            if not cursor.fetchone():
                await websocket.send_json({
                    "type": "error",
                    "message": f"Category with ID {status_id} not found",
                    "requestID": data['requestID']
                })
                return
            #jeśli tak, kontynuuj
            cursor.execute("DELETE FROM order_status WHERE ID_o_status = %s", (status_id,))
            conn.commit()
            #poinformuj zainteresowanych o zmianie
            await manager.broadcast({
                "type": "status_updated",
                "action": "deleted",
                "ID_o_status": status_id,
                "requestID": data['requestID']
            })
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}",
                "requestID": data['requestID']
            })