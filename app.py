from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://username:password@localhost/dbname"
)
db = SQLAlchemy(app)


class FoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(80))
    calories = db.Column(db.Integer)
    date = db.Column(db.String(10))


db.create_all()


@app.route("/food", methods=["POST"])
def add_food():
    data = request.json
    new_entry = FoodEntry(**data)
    db.session.add(new_entry)
    db.session.commit()
    return "", 201


@app.route("/food/today", methods=["GET"])
def get_todays_food():
    return jsonify(food_entries), 200


@app.route("/food/summary", methods=["GET"])
def get_calorie_summary():
    total_calories = sum(entry["calories"] for entry in food_entries)
    return jsonify({"total_calories": total_calories}), 200


@app.route("/food", methods=["DELETE"])
def clear_database():
    food_entries.clear()
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)
