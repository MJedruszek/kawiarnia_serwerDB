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
                    "ID_employee": s["ID_employee"],
                    "employee_name": s["employee_name"],
                    "job_title": s["job_title"],
                    "phone_number": s["phone_number"],
                    "mail": s["mail"]
                } )            
            #wyślij dane w postaci pliku json
            await websocket.send_json({
                "type": "all_staff_data",
                "data": staff_members,
                "requestID": data['requestID']
            })
            print("Sent data")
        except mysql.connector.Error as err:
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}"
            })
            
async def handle_get_one_staff(websocket: WebSocket, data):
    with get_db() as conn:
        try:
            cursor = conn.cursor(dictionary=True)
            staff_id = data['ID_employee']

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
                        "ID_employee": staff["ID_employee"],
                        "employee_name": staff["employee_name"],
                        "job_title": staff["job_title"],
                        "phone_number": staff["phone_number"],
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
                            data['employee_name'],
                            data['job_title'],
                            data['phone_number'],
                            data['mail']))
                
            new_id = cursor.lastrowid
            conn.commit()
            #informujemy o tym zainteresowanych
            await manager.broadcast({
                "type": "staff_updated",
                "action": "created",
                "ID_employee": new_id,
                "employee_name": data['employee_name'],
                "requestID": data['requestID']
            })

            
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            print(f"Error: {err}")

async def handle_delete_staff(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            staff_id = data['ID_employee']
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
                "ID_employee": staff_id,
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
            staff_id = data['ID_employee']
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
                            data['employee_name'],
                            data['job_title'],
                            data['phone_number'],
                            data['mail'],
                            data['ID_employee']))

            conn.commit()
            #informujemy o tym zainteresowanych
            await manager.broadcast({
                "type": "staff_updated",
                "action": "edited",
                "ID_employee": staff_id,
                "employee_name": data['employee_name'],
                "requestID": data['requestID']
            })

            
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            print(f"Error: {err}")