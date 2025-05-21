from fastapi.websockets import WebSocket, WebSocketDisconnect
import asyncio
import json
from cafe_db_setup import get_db, init_db
from contextlib import asynccontextmanager
import mysql.connector

#Create + Delete + Read dla danego pracownika + Read dla danej daty

async def handle_create_schedule(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            cursor.execute("START TRANSACTION")
            #dodajemy nowego pracownika
            cursor.execute("INSERT INTO Schedule (date, ID_employee, shift) "
                "VALUE (%s, %s, %s)",(data['date'],data['ID_employee'], data['shift'],))
                
            new_id = cursor.lastrowid
            conn.commit()
            #informujemy o tym zainteresowanych
            await manager.broadcast({
                "type": "schedule_updated",
                "action": "created",
                "id": new_id,
                "date": data['date'],
                "ID_employee": data['ID_employee']
            })

            
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            print(f"Error: {err}")

async def handle_delete_schedule(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            schedule_id = data['schedule_id']
            #czy ten pracownik jest w bazie? jeśli nie, wyślij komunikat
            cursor.execute("SELECT 1 FROM Schedule WHERE ID_schedule = %s", (schedule_id,))

            if not cursor.fetchone():
                await websocket.send_json({
                    "type": "error",
                    "message": f"Schedule with ID {schedule_id} not found"
                })
                return
            #jeśli tak, kontynuuj
            cursor.execute("DELETE FROM Schedule WHERE ID_schedule = %s", (schedule_id,))
            conn.commit()
            #poinformuj zainteresowanych o zmianie
            await manager.broadcast({
                "type": "schedule_updated",
                "action": "deleted",
                "id": schedule_id
            })
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}"
            })


async def handle_get_schedule_by_employeeID(websocket: WebSocket, data):
    with get_db() as conn:
        try:
            cursor = conn.cursor(dictionary=True)
            employee_id = data['employee_id']

            cursor.execute("SELECT employee_name FROM Staff WHERE ID_employee = %s", (employee_id,))
            employee = cursor.fetchone()
            if employee:
                employee_name = employee['employee_name']
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Staff with ID {employee_id} not found"
                })
                return

            cursor.execute("""
                SELECT 
                    ID_schedule,
                    date,
                    shift
                FROM Schedule
                WHERE ID_employee = %s
                ORDER BY date
            """, (employee_id,))

            schedules = []

            for s in cursor.fetchall():
                schedules.append( {
                    "id": s["ID_schedule"],
                    "date": str(s["date"]),
                    "shift": s["shift"]
                } )   
            
            await websocket.send_json({
                "type": "schedule_by_staff_data",
                "data": schedules,
                "name": employee_name
            })
                
                
        except mysql.connector.Error as err:
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}"
            })

async def handle_get_schedule_by_date(websocket: WebSocket, data):
    with get_db() as conn:
        try:
            cursor = conn.cursor(dictionary=True)
            date = data['date']

            cursor.execute("""
                SELECT 
                    ID_schedule,
                    ID_employee,
                    shift
                FROM Schedule
                WHERE date = %s
                ORDER BY ID_employee
            """, (date,))

            schedules = []

            for s in cursor.fetchall():
                cursor.execute("SELECT employee_name FROM Staff WHERE ID_employee = %s", (s['ID_employee'],))
                employee = cursor.fetchone()
                if employee:
                    employee_name = employee['employee_name']
                else:
                    employee_name = "None"
                schedules.append( {
                    "id": s["ID_schedule"],
                    "shift": s["shift"],
                    "employee_name": employee_name,
                    "ID_employee": s["ID_employee"]
                } )   
            
            await websocket.send_json({
                "type": "schedule_by_date_data",
                "data": schedules
            })
                
                
        except mysql.connector.Error as err:
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}"
            })