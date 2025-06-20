from fastapi.websockets import WebSocket, WebSocketDisconnect
import asyncio
import json
from cafe_db_setup import get_db, init_db
from contextlib import asynccontextmanager
import mysql.connector

#pełny CRUD + getter konkretnego statusu i zmiana samego statusu

async def handle_get_all_orders(websocket: WebSocket, data):
    with get_db() as conn:
        try:
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT 
                    `ID_order`,
                    ID_table,
                    ID_o_status,
                    price,
                    date,
                    ID_employee
                FROM `Order`
                ORDER BY ID_order
            """, )

            orders = []
            #wstaw dane do tablicy orders (podaj staff i order status jako string i jako ID)
            for o in cursor.fetchall():
                cursor.execute("SELECT employee_name FROM Staff WHERE ID_employee = %s", (o['ID_employee'],))
                employee = cursor.fetchone()
                if employee:
                    employee_name = employee['employee_name']
                else:
                    employee_name = "None"
                cursor.execute("SELECT status FROM order_status WHERE ID_o_status = %s", (o['ID_o_status'],))
                status = cursor.fetchone()
                if status:
                    status_name = status['status']
                else:
                    status_name = "None"
                orders.append( {
                    "ID_order": o["ID_order"],
                    "ID_table": o["ID_table"],
                    "ID_employee": o["ID_employee"],
                    "ID_o_status": o["ID_o_status"],
                    "employee": employee_name,
                    "o_status": status_name,
                    "price": o["price"],
                    "date": str(o["date"])
                } )            
            #wyślij dane w postaci pliku json
            await websocket.send_json({
                "type": "all_orders_data",
                "data": orders,
                "requestID": data['requestID']
            })
        except mysql.connector.Error as err:
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}",
                "requestID": data['requestID']
            })
            
#odebranie pojedynczego order będzie w order_products, tutaj niepotrzebne ze względu na brak możliwości wykorzystania

async def handle_create_order(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            cursor.execute("START TRANSACTION")
            #sprawdzamy, czy stolik istnieje:
            cursor.execute("SELECT 1 FROM Tables WHERE ID_table = %s", (data["ID_table"],))

            if not cursor.fetchone():
                await websocket.send_json({
                    "type": "error",
                    "message": f"Order with table ID {data['ID_table']} not found",
                    "requestID": data['requestID']
                })
                return

            #dodajemy nowego pracownika
            cursor.execute("INSERT INTO `Order` (ID_table, ID_o_status, price, ID_employee) "
                "VALUES (%s, 1, %s, %s)",(
                            data['ID_table'],
                            data['price'],
                            data['ID_employee']))
                
            new_id = cursor.lastrowid
            conn.commit()
            #informujemy o tym zainteresowanych
            await manager.broadcast({
                "type": "orders_updated",
                "action": "created",
                "ID_order": new_id,
                "ID_employee": data['ID_employee'],
                "requestID": data['requestID']
            })

            
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            print(f"Error: {err}")

async def handle_delete_order(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            order_id = data['ID_order']
            #czy ten order jest w bazie? jeśli nie, wyślij komunikat
            cursor.execute("SELECT 1 FROM `Order` WHERE ID_order = %s", (order_id,))

            if not cursor.fetchone():
                await websocket.send_json({
                    "type": "error",
                    "message": f"Order with ID {order_id} not found",
                    "requestID": data['requestID']
                })
                return
            #jeśli tak, kontynuuj
            cursor.execute("DELETE FROM `Order` WHERE ID_order = %s", (order_id,))
            conn.commit()
            #poinformuj zainteresowanych o zmianie
            await manager.broadcast({
                "type": "order_updated",
                "action": "deleted",
                "ID_order": order_id,
                "requestID": data['requestID']
            })
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}",
                "requestID": data['requestID']
            })

async def handle_edit_order(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            order_id = data['ID_order']
            #czy ten order jest w bazie? jeśli nie, wyślij komunikat
            cursor.execute("SELECT 1 FROM `Order` WHERE ID_order = %s", (order_id,))

            if not cursor.fetchone():
                await websocket.send_json({
                    "type": "error",
                    "message": f"Order with ID {order_id} not found",
                    "requestID": data['requestID']
                })
                return
            cursor.execute("SELECT 1 FROM Tables WHERE ID_table = %s", (data['ID_table'],))
            #Czy stolik istnieje? Jeśli nie, zwróć błąd
            if not cursor.fetchone():
                await websocket.send_json({
                    "type": "error",
                    "message": f"Order with table ID {data['ID_table']} not found",
                    "requestID": data['requestID']
                })
                return
            #jeśli tak, kontynuuj
            cursor.execute("START TRANSACTION")
            #edytujemy pracownika
            cursor.execute("""
                            UPDATE `Order`
                            SET ID_table = %s,
                                ID_o_status = %s,
                                price = %s,
                                date = %s,
                                ID_employee = %s
                            WHERE ID_order = %s
                        """,(
                            data['ID_table'],
                            data['ID_o_status'],
                            data['price'],
                            data['date'],
                            data['ID_employee'],
                            data['ID_order']))

            conn.commit()
            #informujemy o tym zainteresowanych
            await manager.broadcast({
                "type": "orders_updated",
                "action": "edited",
                "ID_order": order_id,
                "ID_employee": data['ID_employee'],
                "requestID": data['requestID']
            })

            
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            print(f"Error: {err}")

async def handle_get_order_by_status(websocket: WebSocket, data):
    with get_db() as conn:
        try:
            cursor = conn.cursor(dictionary=True)
            ID_status = data['ID_status']
            cursor.execute("SELECT status FROM order_status WHERE ID_o_status = %s", (ID_status,))
            status = cursor.fetchone()
            if status:
                status_name = status['status']
            else:
                status_name = "None"
                
            cursor.execute("""
                SELECT 
                    ID_order,
                    ID_table,
                    ID_o_status,
                    price,
                    date,
                    ID_employee
                FROM `Order`
                WHERE ID_o_status = %s
                ORDER BY ID_order
            """, (ID_status,))

            orders = []

            for o in cursor.fetchall():
                cursor.execute("SELECT employee_name FROM Staff WHERE ID_employee = %s", (o['ID_employee'],))
                employee = cursor.fetchone()
                if employee:
                    employee_name = employee['employee_name']
                else:
                    employee_name = "None"
                orders.append( {
                    "ID_order": o["ID_order"],
                    "ID_table": o["ID_table"],
                    "ID_employee": o["ID_employee"],
                    "employee": employee_name,
                    "price": o["price"],
                    "ID_o_status": o["ID_o_status"],
                    "status": status_name,
                    "date": str(o["date"])
                } )   
            
            await websocket.send_json({
                "type": "orders_by_status_data",
                "data": orders,
                "requestID": data['requestID']
            })
                
                
        except mysql.connector.Error as err:
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}",
                "requestID": data['requestID']
            })

async def handle_change_order_status(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            order_id = data['ID_order']
            #czy ten pracownik jest w bazie? jeśli nie, wyślij komunikat
            cursor.execute("SELECT 1 FROM `Order` WHERE ID_order = %s", (order_id,))

            if not cursor.fetchone():
                await websocket.send_json({
                    "type": "error",
                    "message": f"Order with ID {order_id} not found",
                    "requestID": data['requestID']
                })
                return
            #jeśli tak, kontynuuj
            cursor.execute("START TRANSACTION")
            #edytujemy pracownika
            cursor.execute("""
                            UPDATE `Order`
                            SET ID_o_status = %s
                            WHERE ID_order = %s
                        """,(
                            data['ID_o_status'],
                            data['ID_order']))

            conn.commit()
            #informujemy o tym zainteresowanych
            await manager.broadcast({
                "type": "orders_updated",
                "action": "edited",
                "ID_order": order_id,
                "requestID": data['requestID']
            })

            
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            print(f"Error: {err}")

async def handle_get_order_byID(websocket: WebSocket, data):
    with get_db() as conn:
        try:
            cursor = conn.cursor(dictionary=True)
            order_id = data['ID_order']

            cursor.execute("""
                SELECT
                    ID_table,
                    ID_o_status,
                    price,
                    date,
                    ID_employee
                FROM `Order`
                WHERE ID_order = %s

            """, (order_id,))

            order = cursor.fetchone()

            if order:
                cursor.execute("SELECT status FROM Order_Status WHERE ID_o_status = %s", (order["ID_o_status"],))
                s = cursor.fetchone()
                if s:
                    s_name = s['status']
                else:
                    s_name = "None"
                cursor.execute("SELECT employee_name FROM Staff WHERE ID_employee = %s", (order["ID_employee"],))
                employee = cursor.fetchone()
                if employee:
                    employee_name = employee['employee_name']
                else:
                    employee_name = "None"
                await websocket.send_json({
                    "type": "order_details",
                    "data": {
                        "ID_order": order_id,
                        "ID_table": order["ID_table"],
                        "ID_employee": order["ID_employee"],
                        "employee": employee_name,
                        "price": order["price"],
                        "ID_o_status": order["ID_o_status"],
                        "o_status": s_name,
                        "date": str(order["date"])
                    } ,
                    "requestID": data['requestID']
                })
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Order with ID {order_id} not found",
                    "requestID": data['requestID']
                })
                
                
        except mysql.connector.Error as err:
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}",
                "requestID": data['requestID']
            })

async def handle_create_empty_order(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            cursor.execute("START TRANSACTION")
            #dodajemy nowy order, jedynie  ID_employee
            cursor.execute("INSERT INTO `Order` (ID_table, ID_o_status, price, ID_employee) "
                "VALUES (NULL, 1, 0, %s)",(data['ID_employee'],))
                
            new_id = cursor.lastrowid
            conn.commit()
            #informujemy o tym zainteresowanych
            await manager.broadcast({
                "type": "orders_updated",
                "action": "created",
                "ID_order": new_id,
                "ID_employee": data['ID_employee'],
                "requestID": data['requestID']
            })

            
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            print(f"Error: {err}")

async def handle_edit_order_table(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            order_id = data['ID_order']
            #czy ten order jest w bazie? jeśli nie, wyślij komunikat
            cursor.execute("SELECT 1 FROM `Order` WHERE ID_order = %s", (order_id,))

            if not cursor.fetchone():
                await websocket.send_json({
                    "type": "error",
                    "message": f"Order with ID {order_id} not found",
                    "requestID": data['requestID']
                })
                return
            cursor.execute("SELECT 1 FROM Tables WHERE ID_table = %s", (data['ID_table'],))
            #Czy stolik istnieje? Jeśli nie, zwróć błąd
            if not cursor.fetchone():
                await websocket.send_json({
                    "type": "error",
                    "message": f"Order with table ID {data['ID_table']} not found",
                    "requestID": data['requestID']
                })
                return
            #jeśli tak, kontynuuj
            cursor.execute("START TRANSACTION")
            #edytujemy pracownika
            cursor.execute("""
                            UPDATE `Order`
                            SET ID_table = %s
                            WHERE ID_order = %s
                        """,(
                            data['ID_table'],
                            data['ID_order']))

            conn.commit()
            #informujemy o tym zainteresowanych
            await manager.broadcast({
                "type": "orders_updated",
                "action": "edited",
                "ID_order": order_id,
                "requestID": data['requestID']
            })

            
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            print(f"Error: {err}")

async def handle_get_order_by_table(websocket: WebSocket, data):
    with get_db() as conn:
        try:
            cursor = conn.cursor(dictionary=True)
            table_id = data['ID_table']

            cursor.execute("""
                SELECT 
                    ID_order,
                    price,
                    date,
                    ID_employee,
                    ID_o_status
                FROM `Order` 
                WHERE ID_table = %s AND ID_o_status != 5 AND ID_o_status != 6 

            """, (table_id,))

            order = cursor.fetchone()

            if order:
                cursor.execute("SELECT status FROM Order_Status WHERE ID_o_status = %s", (order["ID_o_status"],))
                s = cursor.fetchone()
                if s:
                    s_name = s['status']
                else:
                    s_name = "None"
                cursor.execute("SELECT employee_name FROM Staff WHERE ID_employee = %s", (order["ID_employee"],))
                employee = cursor.fetchone()
                if employee:
                    employee_name = employee['employee_name']
                else:
                    employee_name = "None"
                await websocket.send_json({
                    "type": "order_details",
                    "data": {
                        "ID_order": order["ID_order"],
                        "ID_table": data["ID_table"],
                        "ID_employee": order["ID_employee"],
                        "employee": employee_name,
                        "price": order["price"],
                        "ID_o_status": order["ID_o_status"],
                        "o_status": s_name,
                        "date": str(order["date"])
                    } ,
                    "requestID": data['requestID']
                })
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Order with table ID {table_id} not found",
                    "requestID": data['requestID']
                })
                
                
        except mysql.connector.Error as err:
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}",
                "requestID": data['requestID']
            })