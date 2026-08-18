from flask import Flask, request, jsonify, render_template
import sqlite3
import os

app = Flask(__name__)

DATABASE = "finance.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/transactions", methods=["GET"])
def get_transactions():
    connection = get_db_connection()

    transactions = connection.execute("""
        SELECT id, description, amount, type, created_at
        FROM transactions
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return jsonify([dict(transaction) for transaction in transactions])


@app.route("/api/transactions", methods=["POST"])
def add_transaction():
    data = request.get_json()

    description = data.get("description")
    amount = data.get("amount")
    transaction_type = data.get("type")

    if not description or amount is None or transaction_type not in ["income", "expense"]:
        return jsonify({
            "error": "Invalid transaction data"
        }), 400

    try:
        amount = float(amount)
    except ValueError:
        return jsonify({
            "error": "Amount must be a number"
        }), 400

    if amount <= 0:
        return jsonify({
            "error": "Amount must be greater than zero"
        }), 400

    connection = get_db_connection()

    connection.execute("""
        INSERT INTO transactions (description, amount, type)
        VALUES (?, ?, ?)
    """, (description, amount, transaction_type))

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Transaction added successfully"
    }), 201


@app.route("/api/transactions/<int:transaction_id>", methods=["DELETE"])
def delete_transaction(transaction_id):
    connection = get_db_connection()

    cursor = connection.execute("""
        DELETE FROM transactions
        WHERE id = ?
    """, (transaction_id,))

    connection.commit()
    connection.close()

    if cursor.rowcount == 0:
        return jsonify({
            "error": "Transaction not found"
        }), 404

    return jsonify({
        "message": "Transaction deleted successfully"
    })


@app.route("/api/summary", methods=["GET"])
def get_summary():
    connection = get_db_connection()

    income_result = connection.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type = 'income'
    """).fetchone()

    expense_result = connection.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type = 'expense'
    """).fetchone()

    connection.close()

    total_income = income_result[0]
    total_expense = expense_result[0]
    balance = total_income - total_expense

    return jsonify({
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance
    })


if __name__ == "__main__":
    initialize_database()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )