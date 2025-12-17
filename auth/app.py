import os
import sqlite3
import secrets
import time
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.getenv("AUTH_DB", "/data/auth.db")
TOKEN_TTL_SECONDS = int(os.getenv("TOKEN_TTL_SECONDS", "86400"))  # 24h

DEFAULT_USER = os.getenv("DEFAULT_USER", "vip")
DEFAULT_PASS = os.getenv("DEFAULT_PASS", "1234")

app = Flask(__name__)

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                token TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                expires_at INTEGER NOT NULL
            )
        """)
        # seed default user if missing
        cur = conn.execute("SELECT username FROM users WHERE username = ?", (DEFAULT_USER,))
        if cur.fetchone() is None:
            conn.execute(
                "INSERT INTO users(username, password_hash) VALUES(?, ?)",
                (DEFAULT_USER, generate_password_hash(DEFAULT_PASS)),
            )
        conn.commit()

def issue_token(username: str) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + TOKEN_TTL_SECONDS
    with db() as conn:
        conn.execute(
            "INSERT INTO tokens(token, username, expires_at) VALUES(?, ?, ?)",
            (token, username, expires_at),
        )
        conn.commit()
    return token

def get_bearer_token() -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    return None

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    with db() as conn:
        cur = conn.execute("SELECT username, password_hash FROM users WHERE username = ?", (username,))
        row = cur.fetchone()

    if row is None or not check_password_hash(row["password_hash"], password):
        return jsonify({"error": "invalid credentials"}), 401

    token = issue_token(username)
    return jsonify({"token": token, "token_type": "Bearer", "expires_in": TOKEN_TTL_SECONDS})

@app.get("/verify")
def verify():
    token = get_bearer_token()
    if not token:
        return ("Unauthorized", 401)

    now = int(time.time())
    with db() as conn:
        cur = conn.execute(
            "SELECT token, username, expires_at FROM tokens WHERE token = ?",
            (token,),
        )
        row = cur.fetchone()

    if row is None or row["expires_at"] < now:
        return ("Unauthorized", 401)

    # 200 = OK for Nginx auth_request
    return ("OK", 200)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)