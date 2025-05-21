from fastapi.websockets import WebSocket, WebSocketDisconnect
import asyncio
import json
from cafe_db_setup import get_db, init_db
from contextlib import asynccontextmanager
import mysql.connector

#pełny CRUD + getter po kategorii

async def handle_get_all_products(websocket: WebSocket):
    with get_db() as conn:
        try:
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT 
                    ID_product,
                    product_name,
                    price,
                    quantity,
                    ID_category,
                    prep_time,
                    expiration_date
                FROM Products
                ORDER BY product_name
            """, )

            products = []
            #wstaw dane do tablicy staff_members
            for p in cursor.fetchall():
                cursor.execute("SELECT category_name FROM Categories WHERE ID_category = %s", (p['ID_category'],))
                category = cursor.fetchone()
                if category:
                    category_name = category['category_name']
                else:
                    category_name = "None"
                products.append( {
                    "id": p["ID_product"],
                    "name": p["product_name"],
                    "price": p["price"],
                    "quantity": p["quantity"],
                    "prep_time": p["prep_time"],
                    "expiration_date": str(p["expiration_date"]),
                    "ID_category": p["ID_category"],
                    "category_name": category_name
                } )            
            #wyślij dane w postaci pliku json
            await websocket.send_json({
                "type": "all_products_data",
                "data": products
            })
        except mysql.connector.Error as err:
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}"
            })
            
async def handle_get_one_product(websocket: WebSocket, data):
    with get_db() as conn:
        try:
            cursor = conn.cursor(dictionary=True)
            product_id = data['product_id']

            cursor.execute("""
                SELECT 
                    product_name,
                    price,
                    quantity,
                    ID_category,
                    prep_time,
                    expiration_date
                FROM Products
                WHERE ID_product = %s
            """, (product_id,))

            product = cursor.fetchone()

            if product:
                cursor.execute("SELECT category_name FROM Categories WHERE ID_category = %s", (product["ID_category"],))
                category = cursor.fetchone()
                if category:
                    category_name = category['category_name']
                else:
                    category_name = "None"
                await websocket.send_json({
                    "type": "product_details",
                    "data": {
                        "id": product_id,
                        "name": product["product_name"],
                        "price": product["price"],
                        "quantity": product["quantity"],
                        "prep_time": product["prep_time"],
                        "expiration_date": str(product["expiration_date"]),
                        "ID_category": product["ID_category"],
                        "category_name": category_name
                    } 
                })
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Products with ID {product_id} not found"
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
            cursor.execute("INSERT INTO Products (product_name, price, quantity, ID_category, prep_time, expiration_date) "
                "VALUES (%s, %s, %s, %s, %s, %s)",(
                            data['name'],
                            data['price'],
                            data['quantity'],
                            data['ID_category'],
                            data['prep_time'],
                            data['expiration_date']))
                
            new_id = cursor.lastrowid
            conn.commit()
            #informujemy o tym zainteresowanych
            await manager.broadcast({
                "type": "products_updated",
                "action": "created",
                "id": new_id,
                "name": data['name']
            })

            
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            print(f"Error: {err}")

async def handle_delete_product(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            product_id = data['product_id']
            #czy ten pracownik jest w bazie? jeśli nie, wyślij komunikat
            cursor.execute("SELECT 1 FROM Products WHERE ID_product = %s", (product_id,))

            if not cursor.fetchone():
                await websocket.send_json({
                    "type": "error",
                    "message": f"Products with ID {product_id} not found"
                })
                return
            #jeśli tak, kontynuuj
            cursor.execute("DELETE FROM Products WHERE ID_product = %s", (product_id,))
            conn.commit()
            #poinformuj zainteresowanych o zmianie
            await manager.broadcast({
                "type": "products_updated",
                "action": "deleted",
                "id": product_id
            })
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}"
            })

async def handle_edit_product(websocket: WebSocket, data, manager):
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            product_id = data['id']
            #czy ten pracownik jest w bazie? jeśli nie, wyślij komunikat
            cursor.execute("SELECT 1 FROM Products WHERE ID_product = %s", (product_id,))

            if not cursor.fetchone():
                await websocket.send_json({
                    "type": "error",
                    "message": f"Products with ID {product_id} not found"
                })
                return
            #jeśli tak, kontynuuj
            cursor.execute("START TRANSACTION")
            #edytujemy produkt
            cursor.execute("""
                            UPDATE Products
                            SET product_name = %s,
                                price = %s,
                                quantity = %s,
                                ID_category = %s,
                                prep_time = %s,
                                expiration_date = %s
                            WHERE ID_product = %s
                        """,(
                            data['name'],
                            data['price'],
                            data['quantity'],
                            data['ID_category'],
                            data['prep_time'],
                            data['expiration_date'],
                            data['id']))

            conn.commit()
            #informujemy o tym zainteresowanych
            await manager.broadcast({
                "type": "products_updated",
                "action": "edited",
                "id": product_id,
                "name": data['name']
            })

            
        except mysql.connector.Error as err:
            if conn: conn.rollback()
            print(f"Error: {err}")


async def handle_get_products_by_category(websocket: WebSocket, data):
    with get_db() as conn:
        try:
            cursor = conn.cursor(dictionary=True)
            ID_category = data['ID_category']
            cursor.execute("SELECT category_name FROM Categories WHERE ID_category = %s", (ID_category,))
            category = cursor.fetchone()
            if category:
                category_name = category['category_name']
            else:
                category_name = "None"
                
            cursor.execute("""
                SELECT 
                    ID_product,
                    product_name,
                    price,
                    quantity,
                    prep_time,
                    expiration_date
                FROM Products
                WHERE ID_category = %s
                ORDER BY product_name
            """, (ID_category,))

            products = []

            for p in cursor.fetchall():
                products.append( {
                    "id": p["ID_product"],
                    "name": p["product_name"],
                    "price": p["price"],
                    "quantity": p["quantity"],
                    "prep_time": p["prep_time"],
                    "expiration_date": str(p["expiration_date"])
                } )   
            
            await websocket.send_json({
                "type": "products_by_categories_data",
                "data": products,
                "category_name": category_name
            })
                
                
        except mysql.connector.Error as err:
            await websocket.send_json({
                "type": "error",
                "message": f"Database error: {err}"
            })