from fastapi.websockets import WebSocket, WebSocketDisconnect
import asyncio
import json
from cafe_db_setup import get_db, init_db
from contextlib import asynccontextmanager
import mysql.connector

#pełny CRD, ale zamiast gettera wszystkiego getter po ID_order

async def handle_get_products_for_orderID(websocket: WebSocket, data):
    with get_db() as conn:
        try:
            cursor = conn.cursor(dictionary=True)
            ID_order = data['ID_order']
                
            cursor.execute("""
                SELECT 
                    ID_product,
                    quantity,
                    price
                FROM Order_Products
                WHERE ID_order = %s
                ORDER BY ID_product
            """, (ID_order,))

            products = []

            for p in cursor.fetchall():
                cursor.execute("SELECT product_name FROM Products WHERE ID_product = %s", (p['ID_product'],))
                product = cursor.fetchone()
                if product:
                    product_name = product['product_name']
                else:
                    product_name = "None"
                products.append( {
                    "ID_product": p["ID_product"],
                    "quantity": p["quantity"],
                    "price": p["price"],
                    "product_name": product_name
                } )   
            
            await websocket.send_json({
                "type": "products_by_orderID_data",
                "data": products,
                "ID_order": ID_order
            })
                
                
        except mysql.connector.Error as err:
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}"
            })

async def handle_create_product(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            cursor.execute("START TRANSACTION")
            #dodajemy nowego pracownika
            cursor.execute("INSERT INTO Order_Products (ID_order, ID_product, quantity, price) "
                "VALUES (%s, %s, %s, %s)",(
                            data['ID_order'],
                            data['ID_product'],
                            data['quantity'],
                            data['price']))
                
            conn.commit()
            #informujemy o tym zainteresowanych
            await manager.broadcast({
                "type": "order_products_updated",
                "action": "created",
                "ID_order": data['ID_order']
            })

            #Dodawanie ceny nowego produktu do Orderu:
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
                WHERE ID_order = %s
            """, (data['ID_order'],))

            order = cursor.fetchone()

            newprice = float(order["price"]) + float(data['price'])

            cursor.execute("START TRANSACTION")
            #edytujemy order
            cursor.execute("""
                            UPDATE `Order`
                            SET ID_table = %s,
                                ID_o_status = %s,
                                price = %s,
                                date = %s,
                                ID_employee = %s
                            WHERE ID_order = %s
                        """,(
                            order['ID_table'],
                            order['ID_o_status'],
                            newprice,
                            order['date'],
                            order['ID_employee'],
                            order['ID_order']))

            conn.commit()

            await manager.broadcast({
                "type": "orders_updated",
                "action": "edited",
                "id": order['ID_order'],
                "ID_employee": order['ID_employee']
            })
            
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            print(f"Error: {err}")

async def handle_delete_product(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor(dictionary=True)
            product_id = data['product_id']
            order_id = data['order_id']
            #czy ten pracownik jest w bazie? jeśli nie, wyślij komunikat
            cursor.execute("SELECT price FROM Order_Products WHERE ID_product = %s AND ID_order = %s", (product_id,order_id,))
            op = cursor.fetchone()
            if not op:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Products with ID {product_id} and {order_id} not found"
                })
                return
            oldprice = float(op["price"])
            #jeśli tak, kontynuuj
            cursor.execute("""DELETE FROM Order_Products WHERE ID_product = %s AND ID_order = %s;""",
                            (product_id,order_id,))
            conn.commit()
            #poinformuj zainteresowanych o zmianie
            await manager.broadcast({
                "type": "order_products_updated",
                "action": "deleted",
                "ID_product": product_id,
                "ID_order": order_id
            })

            #Odejmowanie ceny starego produktu od Orderu:
            
            cursor.execute("""
                SELECT 
                    `ID_order`,
                    ID_table,
                    ID_o_status,
                    price,
                    date,
                    ID_employee
                FROM `Order`
                WHERE ID_order = %s
            """, (order_id,))

            order = cursor.fetchone()

            newprice = float(order['price']) - oldprice

            cursor.execute("START TRANSACTION")
            #edytujemy order
            cursor.execute("""
                            UPDATE `Order`
                            SET ID_table = %s,
                                ID_o_status = %s,
                                price = %s,
                                date = %s,
                                ID_employee = %s
                            WHERE ID_order = %s
                        """,(
                            order['ID_table'],
                            order['ID_o_status'],
                            newprice,
                            order['date'],
                            order['ID_employee'],
                            order['ID_order']))

            conn.commit()

            await manager.broadcast({
                "type": "orders_updated",
                "action": "edited",
                "id": order['ID_order'],
                "ID_employee": order['ID_employee']
            })
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}"
            })
