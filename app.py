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

    total_income = sum(r["amount"] for r in rows if r["type"] == "income")
    total_expense = sum(r["amount"] for r in rows if r["type"] == "expense")
    balance = total_income - total_expense


    return render_template(
        "index.html",
        transaction=rows,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance
    )

@app.route("/add", methods=["POST"])
def add_transaction():
    t_type = request.form.get("type")
    desc = request.form.get("description", "").strip()
    amount_str = request.form.get("amount", "").strip()

    #basic validation
    if t_type not in ("income", "expense"):
        return redirect(url_for("index"))
    if not desc:
        return redirect(url_for("index"))
    try:
        amount = float(amount_str)
        if amount < 0:
            return redirect(url_for("index"))
    except ValueError:
        return redirect(url_for("index"))
    
    conn = get_db_connection()
    conn.execute("""
                 INSERT INTO transactions (type, description, amount)
                 VALUES (?, ?, ?)
            """, (t_type, desc, amount))
    conn.commit()
    conn.close()

    return redirect(url_for("index"))

@app.route("/delete/<int:txn_id>", methods=["POST"])
def delete_transaction(txn_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM transactions WHERE id = ?", (txn_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=4020)