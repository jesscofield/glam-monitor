import os
import time
import threading
import psycopg2
from flask import Flask, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "glamdb")
DB_USER = os.getenv("DB_USER", "glam")
DB_PASSWORD = os.getenv("DB_PASSWORD", "glamsecret")

APP_UP = Gauge("app_up", "Exporter is running (1 = up)")
DB_REQUESTS = Counter(
    "db_requests_total",
    "Total DB requests performed by exporter",
    ["operation", "status"],
)
DB_LATENCY = Histogram(
    "db_request_duration_seconds",
    "DB request latency in seconds",
    ["operation"],
)

app = Flask(__name__)

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )

def run_query(operation: str, sql: str, fetchone: bool = False):
    start = time.time()
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                if fetchone:
                    cur.fetchone()
        DB_REQUESTS.labels(operation=operation, status="ok").inc()
    except Exception:
        DB_REQUESTS.labels(operation=operation, status="fail").inc()
        raise
    finally:
        DB_LATENCY.labels(operation=operation).observe(time.time() - start)

def probe_loop():
    # small delay so DB is ready
    time.sleep(3)
    APP_UP.set(1)

    while True:
        try:
            # “Ping” DB
            run_query("ping", "SELECT 1", fetchone=True)

            run_query("count_orders", "SELECT COUNT(*) FROM orders", fetchone=True)

        except Exception:
            pass

        time.sleep(2)

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.get("/")
def home():
    return {
        "service": "glam-exporter",
        "endpoints": ["/metrics"],
        "hint": "Prometheus scrapes /metrics",
    }

if __name__ == "__main__":
    t = threading.Thread(target=probe_loop, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=8000)