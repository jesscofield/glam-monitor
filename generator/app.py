import time
import random
import psycopg2
from datetime import datetime

DB_CONFIG = {
    "host": "db",
    "dbname": "glamdb",
    "user": "glam",
    "password": "glamsecret",
}

PRODUCTS = [
    "Lip Gloss",
    "Perfume",
    "Juicy Tracksuit",
    "Fur Coat",
    "Pink Heels",
]

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def create_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    product_name TEXT,
                    price NUMERIC,
                    glam_level INTEGER,
                    created_at TIMESTAMP
                )
            """)
            conn.commit()

def insert_order():
    product = random.choice(PRODUCTS)
    price = round(random.uniform(20, 300), 2)
    glam_level = random.randint(1, 10)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO orders (product_name, price, glam_level, created_at)
                VALUES (%s, %s, %s, %s)
            """, (product, price, glam_level, datetime.utcnow()))
            conn.commit()

def select_orders():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM orders")
            cur.fetchone()

if __name__ == "__main__":
    print("Glam Orders Generator started")
    create_table()

    while True:
        try:
            insert_order()
            if random.random() < 0.3:
                select_orders()

            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print("Error:", e)
            time.sleep(2)