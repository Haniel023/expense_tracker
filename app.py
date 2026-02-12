from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DB_NAME = "expenses.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
                 CREATE TABLE IF NOT EXISTS transactions(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 type TEXT NOT NULL,
                 description TEXT NOT NULL,
                 amount REAL NOT NULL,
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                 )
            """)
    conn.commit()
    conn.close()

@app.route("/", methods=["GET"])
def index():
    conn = get_db_connection()
    rows = conn.execute("""
                        SELECT * FROM transactions
                        ORDER BY created_at DESC, id DESC
                    """).fetchall()
    conn.close()

    total_income = sum(r["amount"] for r in rows if r ["type"] == "income")