from flask import Blueprint, request, jsonify
import sqlite3
from datetime import date

food_bp = Blueprint("food", __name__)
DATABASE = "FoodManagement.db"


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Food (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                food_name TEXT NOT NULL,
                calories INTEGER NOT NULL,
                date TEXT NOT NULL
            )
            """
        )
        conn.commit()


@food_bp.route("/add_food", methods=["POST"])
def add_food():
    data = request.json
    food_name = data.get("food_name")
    calories = data.get("calories")
    date = data.get("date")

    if not food_name or calories is None or not date:
        return jsonify({"error": "Invalid input"}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Food (food_name, calories, date)
            VALUES (?, ?, ?)
            """,
            (food_name, calories, date),
        )
        conn.commit()
        return jsonify({"message": "Food added successfully"}), 201


@food_bp.route("/todays_food", methods=["GET"])
def todays_food():
    today = date.today().isoformat()
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM Food WHERE date = ?
            """,
            (today,),
        )
        rows = cursor.fetchall()
        return jsonify(
            [
                {"id": row[0], "food_name": row[1], "calories": row[2], "date": row[3]}
                for row in rows
            ]
        )


@food_bp.route("/calorie_summary", methods=["GET"])
def calorie_summary():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT date, SUM(calories) as totalCalories 
            FROM Food 
            GROUP BY date
            """
        )
        rows = cursor.fetchall()
        summary = [{"date": row[0], "totalCalories": row[1]} for row in rows]
        return jsonify(summary)


@food_bp.route("/clear_database", methods=["POST"])
def clear_database():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Food")
        conn.commit()
        return jsonify({"message": "Database cleared successfully"}), 200
