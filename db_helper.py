import mysql.connector

# Centralized database configuration dictionary
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "WarAnshu1!",
    "database": "pandeyji_eatery"
}

def get_connection():
    """Establishes and returns a fresh MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)


def get_next_orderid():
    """Retrieves the next sequential order ID from the database."""
    cnx = get_connection()
    cursor = cnx.cursor()
    cursor.execute("SELECT MAX(order_id) FROM orders")
    result = cursor.fetchone()
    cursor.close()
    cnx.close()
    
    # Comma unpacking: Safely extracts value from tuple e.g. (44,) -> 44
    if result:
        (max_id,) = result
        if max_id is not None:
            return max_id + 1
    return 1


def get_order_status(order_id: int):
    """Queries and returns the raw string status of a given order ID."""
    if order_id is None:
        return None

    cnx = get_connection()
    cursor = cnx.cursor()
    cursor.execute("SELECT status FROM order_tracking WHERE order_id = %s", (order_id,))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()
    
    # Comma unpacking: Safely extracts string status from tuple e.g. ("in transit",) -> "in transit"
    if result:
        (status,) = result
        return status
    return None


def insert_order(food_item: str, quantity: int, order_id: int):
    """Inserts a single item and its quantity into an active order."""
    cnx = get_connection()
    cursor = cnx.cursor()
    try:
        cursor.callproc('insert_order_item', (food_item, quantity, order_id))
        cnx.commit()
        return 1
    except mysql.connector.Error as err:
        print(f"Error inserting order: {err}")
        cnx.rollback()
        return -1
    finally:
        cursor.close()
        cnx.close()
        

def get_order_total(order_id: int):
    """Calculates the total price of an order using the MySQL User-Defined Function."""
    cnx = get_connection()
    cursor = cnx.cursor()
    cursor.execute("SELECT get_total_order_price(%s)", (order_id,))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()
    
    # Comma unpacking: Safely extracts numerical float from tuple e.g. (21.50,) -> 21.50
    if result:
        (total,) = result
        if total is not None:
            return total
    return 0


def insert_order_tracking(order_id: int, status: str):
    """Initialises tracking status for a new order."""
    cnx = get_connection()
    cursor = cnx.cursor()
    try:
        cursor.execute("INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)", (order_id, status))
        cnx.commit()
        return 1
    except mysql.connector.Error as err:
        print(f"Error inserting order tracking: {err}")
        cnx.rollback()
        return -1
    finally:
        cursor.close()
        cnx.close()