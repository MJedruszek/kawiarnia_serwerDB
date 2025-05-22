from fastapi.websockets import WebSocket, WebSocketDisconnect
import asyncio
import json
from cafe_db_setup import get_db, init_db
from contextlib import asynccontextmanager
import mysql.connector

#pełny CRUD + getter pojedynczego pracownika

async def handle_get_all_staff(websocket: WebSocket,data):
    with get_db() as conn:
        try:
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT 
                    ID_employee,
                    employee_name,
                    job_title,
                    phone_number,
                    mail
                FROM Staff
                ORDER BY ID_employee
            """, )

            staff_members = []
            #wstaw dane do tablicy staff_members
            for s in cursor.fetchall():
                staff_members.append( {
                    "id": s["ID_employee"],
                    "name": s["employee_name"],
                    "job": s["job_title"],
                    "phone": s["phone_number"],
                    "mail": s["mail"]
                } )            
            #wyślij dane w postaci pliku json
            await websocket.send_json({
                "type": "all_staff_data",
                "data": staff_members,
                "requestID": data['requestID']
            })
        except mysql.connector.Error as err:
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}"
            })
            
async def handle_get_one_staff(websocket: WebSocket, data):
    with get_db() as conn:
        try:
            cursor = conn.cursor(dictionary=True)
            staff_id = data['staff_id']

            cursor.execute("""
                SELECT 
                    ID_employee,
                    employee_name,
                    job_title,
                    phone_number,
                    mail
                FROM Staff
                WHERE ID_employee = %s
            """, (staff_id,))

            staff = cursor.fetchone()

            if staff:
                await websocket.send_json({
                    "type": "staff_details",
                    "data": {
                        "id": staff["ID_employee"],
                        "name": staff["employee_name"],
                        "job": staff["job_title"],
                        "phone": staff["phone_number"],
                        "mail": staff["mail"]
                    } ,
                    "requestID": data['requestID']
                })
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Staff with ID {staff_id} not found",
                    "requestID": data['requestID']
                })
                
                
        except mysql.connector.Error as err:
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}",
                "requestID": data['requestID']
            })

async def handle_create_staff(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            cursor.execute("START TRANSACTION")
            #dodajemy nowego pracownika
            cursor.execute("INSERT INTO Staff (employee_name, job_title, phone_number, mail) "
                "VALUES (%s, %s, %s, %s)",(
                            data['name'],
                            data['job'],
                            data['phone'],
                            data['mail']))
                
            new_id = cursor.lastrowid
            conn.commit()
            #informujemy o tym zainteresowanych
            await manager.broadcast({
                "type": "staff_updated",
                "action": "created",
                "id": new_id,
                "name": data['name'],
                "requestID": data['requestID']
            })

            
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            print(f"Error: {err}")

async def handle_delete_staff(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            staff_id = data['staff_id']
            #czy ten pracownik jest w bazie? jeśli nie, wyślij komunikat
            cursor.execute("SELECT 1 FROM Staff WHERE ID_employee = %s", (staff_id,))

            if not cursor.fetchone():
                await websocket.send_json({
                    "type": "error",
                    "message": f"Staff with ID {staff_id} not found",
                    "requestID": data['requestID']
                })
                return
            #jeśli tak, kontynuuj
            cursor.execute("DELETE FROM Staff WHERE ID_employee = %s", (staff_id,))
            conn.commit()
            #poinformuj zainteresowanych o zmianie
            await manager.broadcast({
                "type": "staff_updated",
                "action": "deleted",
                "id": staff_id,
                "requestID": data['requestID']
            })
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}",
                "requestID": data['requestID']
            })

async def handle_edit_staff(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            staff_id = data['id']
            #czy ten pracownik jest w bazie? jeśli nie, wyślij komunikat
            cursor.execute("SELECT 1 FROM Staff WHERE ID_employee = %s", (staff_id,))

            if not cursor.fetchone():
                await websocket.send_json({
                    "type": "error",
                    "message": f"Staff with ID {staff_id} not found",
                    "requestID": data['requestID']
                })
                return
            #jeśli tak, kontynuuj
            cursor.execute("START TRANSACTION")
            #edytujemy pracownika
            cursor.execute("""
                            UPDATE Staff
                            SET employee_name = %s,
                                job_title = %s,
                                phone_number = %s,
                                mail = %s
                            WHERE ID_employee = %s
                        """,(
                            data['name'],
                            data['job'],
                            data['phone'],
                            data['mail'],
                            data['id']))

            conn.commit()
            #informujemy o tym zainteresowanych
            await manager.broadcast({
                "type": "staff_updated",
                "action": "edited",
                "id": staff_id,
                "name": data['name'],
                "requestID": data['requestID']
            })

            
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            print(f"Error: {err}")