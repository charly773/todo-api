import os
import time

import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "tododb")
DB_USER = os.getenv("DB_USER", "todouser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "todopass")
DATABASE_URL = os.getenv("DATABASE_URL")

memory_todos = []


def get_connection():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def wait_for_db(max_retries=10, delay=2):
    for attempt in range(1, max_retries + 1):
        try:
            conn = get_connection()
            conn.close()
            return True
        except Exception:
            if attempt == max_retries:
                return False
            time.sleep(delay)
    return False


def init_db():
    if not wait_for_db(max_retries=5, delay=1):
        return False

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS todos (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL
                );
                """
            )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


@app.route("/")
def home():
    return jsonify({"msg": "ok"})


@app.route("/todos", methods=["GET"])
def get_todos():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id, title FROM todos ORDER BY id ASC")
            rows = cur.fetchall()
        conn.close()
        return jsonify({"todos": [{"id": row[0], "title": row[1]} for row in rows]})
    except Exception:
        return jsonify({"todos": memory_todos})


@app.route("/todos", methods=["POST"])
def create_todo():
    payload = request.get_json(silent=True) or {}
    title = payload.get("title")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "title is required"}), 400

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO todos (title) VALUES (%s) RETURNING id, title",
                (title.strip(),),
            )
            todo_id, todo_title = cur.fetchone()
        conn.commit()
        conn.close()
        return jsonify({"id": todo_id, "title": todo_title}), 201
    except Exception:
        memory_todos.append({"title": title.strip()})
        return jsonify(memory_todos[-1]), 201


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
