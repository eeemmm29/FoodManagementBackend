# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, render_template, jsonify, session, Blueprint
from time import time
import json
from datetime import datetime, date
from collections import defaultdict
import sqlite3
from hashlib import sha256

from food_blueprint import food_bp, init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"

db = sqlite3.connect("chatData.db", check_same_thread=False)
cur = db.cursor()
cur.execute(
    "create table if not exists messages (id INTEGER PRIMARY KEY, datestr varchar, sender varchar, receiver varchar, message varchar)"
)
cur.execute(
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username varchar, password varchar)"
)
db.commit()


class DatabaseManager_gradeTracker:
    adminPassword = "11bebb901a5ccfb0cd9c62357ba15674aa2fa497778091d6cb06524da48eafec"

    def __init__(self, database_file):
        self.database_file = database_file

    def initialize_database(self):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()

        ### AITStudentsGradeTracker
        cur.execute(
            """create table if not exists users (
                    id INTEGER PRIMARY KEY,
                    name varchar,
                    username varchar,
                    password varchar,
                    email varchar,
                    phoneNumber varchar,
                    address varchar)"""
        )
        # cur.execute('''CREATE TABLE IF NOT EXISTS courses (
        #             course_id INT PRIMARY KEY,
        #             course_name VARCHAR)''')
        cur.execute(
            """CREATE TABLE IF NOT EXISTS grades (
                    examName integer,
                    studentUsername varchar,
                    grade integer,
                    date varchar,
                    teacherName varchar)"""
        )

        cur.execute(
            """create table if not exists feedback (
                    datetime varchar,
                    username varchar,
                    text varchar)"""
        )

        cur.execute(
            """create table if not exists logs (
                    time varchar,
                    action varchar,
                    success bit,
                    data varchar)"""
        )

        cur.execute(
            "insert into logs values (?, ?, ?, ?)",
            (self.datestr(), "creation", 1, "database initialized"),
        )

        connection.commit()
        connection.close()

    # def get_max_course_id(self):
    #     try:
    #         connection = sqlite3.connect(self.database_file)
    #         cur = connection.cursor()
    #         cur.execute("SELECT MAX(course_id) FROM courses")
    #         max_course_id = cur.fetchone()[0]
    #         connection.close()
    #         return max_course_id
    #     except sqlite3.Error as e:
    #         print("Error getting maximum course ID:", e)

    # def add_course(self, course_name):
    #     try:
    #         connection = sqlite3.connect(self.database_file)
    #         cur = connection.cursor()
    #         course_id = self.get_max_course_id() + 1
    #         cur.execute('''INSERT INTO courses VALUES (?, ?, ?)''', (course_id, course_name))
    #         connection.commit()
    #         connection.close()
    #     except sqlite3.Error as e:
    #         print("Error adding course:", e)

    def loginCheck(self, username, password):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?", (username, password)
        )
        user = cur.fetchone()
        if user:
            data = {"success": True, "message": "Login successful", "user": user}
            cur.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    self.datestr(),
                    "user login",
                    1,
                    f"username = {username}, password = {password}, message: {data['message']}",
                ),
            )
            connection.commit()
            connection.close()
            return jsonify(data)
        data = {"success": False, "message": "Incorrect username or password"}
        cur.execute(
            "insert into logs values (?, ?, ?, ?)",
            (
                self.datestr(),
                "user login",
                0,
                f"username = {username}, password = {password}, message: {data['message']}",
            ),
        )
        connection.commit()
        connection.close()
        return jsonify(data)

    def adminLoginCheck(self, password):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        if sha256(password.encode("utf-8")).hexdigest() == self.adminPassword:
            data = {"success": True, "message": "Admin login successful"}
            cur.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    self.datestr(),
                    "admin login",
                    1,
                    f"password = {password}, message: {data['message']}",
                ),
            )
            connection.commit()
            connection.close()
            return jsonify(data)
        data = {"success": False, "message": "Incorrect admin password"}
        cur.execute(
            "insert into logs values (?, ?, ?, ?)",
            (
                self.datestr(),
                "admin login",
                0,
                f", password = {password}, message: {data['message']}",
            ),
        )
        connection.commit()
        connection.close()
        return jsonify(data)

    def addGrade(self, studentUsername, examName, grade, teacherName):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        if not studentUsername or not examName or not grade:
            data = {"success": False, "message": "Please fill out all the spaces"}
            cur.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    self.datestr(),
                    "addGrade",
                    0,
                    f"studentUsername = {studentUsername}, examName = {examName}, grade = {grade}, teacherName = {teacherName}, message: {data['message']}",
                ),
            )
            connection.commit()
            connection.close()
            return jsonify(data)
        cur.execute("select * from users where username = ?", (studentUsername,))
        user = cur.fetchone()
        if user:
            cur.execute(
                "select * from grades where studentUsername = ? and examName = ? and date = ?",
                (studentUsername, examName, date.today().strftime("%d/%m/%Y")),
            )
            userAlready = cur.fetchone()
            if userAlready:
                data = {
                    "success": False,
                    "message": "Student with that name already has a grade in this exam",
                }
                cur.execute(
                    "insert into logs values (?, ?, ?, ?)",
                    (
                        self.datestr(),
                        "addGrade",
                        0,
                        f"studentUsername = {studentUsername}, examName = {examName}, grade = {grade}, teacherName = {teacherName}, message: {data['message']}",
                    ),
                )
                connection.commit()
                connection.close()
                return jsonify(data)
            cur.execute(
                "INSERT INTO grades (examName, studentUsername, grade, date, teacherName) VALUES (?, ?, ?, ?, ?)",
                [
                    examName,
                    studentUsername,
                    grade,
                    date.today().strftime("%d/%m/%Y"),
                    teacherName,
                ],
            )
            data = {"success": True, "message": "Grade added to the database"}
            cur.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    self.datestr(),
                    "addGrade",
                    1,
                    f"studentUsername = {studentUsername}, examName = {examName}, grade = {grade}, teacherName = {teacherName}, message: {data['message']}",
                ),
            )
            connection.commit()
            connection.close()
            return jsonify(data)
        data = {
            "success": False,
            "message": "Student with that name doesn't exist in the database",
        }
        cur.execute(
            "insert into logs values (?, ?, ?, ?)",
            (
                self.datestr(),
                "addGrade",
                0,
                f"studentUsername = {studentUsername}, examName = {examName}, grade = {grade}, teacherName = {teacherName}, message: {data['message']}",
            ),
        )
        connection.commit()
        connection.close()
        return jsonify(data)

    def addStudent(self, name, username, password, email, phoneNumber, address):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        if (
            not name
            or not username
            or not password
            or not email
            or not phoneNumber
            or not address
        ):
            data = {"success": False, "message": "Please fill out all the spaces"}
            cur.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    self.datestr(),
                    "addStudent",
                    0,
                    f"name = {name}, username = {username}, password = {password}, email = {email}, phoneNumber = {phoneNumber}, address = {address}, message: {data['message']}",
                ),
            )
            connection.commit()
            connection.close()
            return jsonify(data)
        cur.execute("select * from users where username = ?", (username,))
        user = cur.fetchone()
        if user:
            data = {
                "success": False,
                "message": "A student with that username already exists",
            }
            cur.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    self.datestr(),
                    "addStudent",
                    0,
                    f"name = {name}, username = {username}, password = {password}, email = {email}, phoneNumber = {phoneNumber}, address = {address}, message: {data['message']}",
                ),
            )
            connection.commit()
            connection.close()
            return jsonify(data)
        else:
            data = {"success": True, "message": "Student added to the database"}
            cur.execute(
                "INSERT INTO users (name, username, password, email, phoneNumber, address) VALUES (?, ?, ?, ?, ?, ?)",
                [name, username, password, email, phoneNumber, address],
            )
            cur.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    self.datestr(),
                    "addStudent",
                    1,
                    f"name = {name}, username = {username}, password = {password}, email = {email}, phoneNumber = {phoneNumber}, address = {address}, message: {data['message']}",
                ),
            )
            connection.commit()
            connection.close()
            return jsonify(data)

    def examsSearch(self, username, examName):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        cur.execute(
            "select * from grades where studentUsername = ? and examName = ?",
            (username, examName),
        )
        result = cur.fetchall()
        if result:
            data = {"success": True, "message": "exams searched", "data": result}
            cur.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    self.datestr(),
                    "examsSearch",
                    1,
                    f"username = {username}, examName = {examName}, message: {data['message']}",
                ),
            )
            connection.commit()
            connection.close()
            return jsonify(data)
        data = {"success": False, "message": "exams searched"}
        cur.execute(
            "insert into logs values (?, ?, ?, ?)",
            (
                self.datestr(),
                "examsSearch",
                0,
                f"username = {username}, examName = {examName}, message: {data['message']}",
            ),
        )
        connection.commit()
        connection.close()
        return jsonify(data)

    def sendFeedback(self, username, text):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        if not text:
            data = {"success": False, "message": "Please write your feedback"}
            cur.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    self.datestr(),
                    "sendFeedback",
                    0,
                    f"username: {username}, message: {data['message']}",
                ),
            )
            connection.commit()
            connection.close()
            return jsonify(data)
        cur.execute(
            "insert into feedback values (?, ?, ?)", (self.datestr(), username, text)
        )
        data = {"success": True, "message": "Feedback sent to the admin"}
        cur.execute(
            "insert into logs values (?, ?, ?, ?)",
            (
                self.datestr(),
                "sendFeedback",
                1,
                f"username: {username}, message: {data['message']}",
            ),
        )
        connection.commit()
        connection.close()
        return jsonify(data)

    def getDataAdmin(self):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        cur.execute("select * from users")
        users = cur.fetchall()
        cur.execute("select * from grades")
        grades = cur.fetchall()
        cur.execute(
            "select date, examName, round(avg(grade), 1) from grades group by examName, date"
        )
        gradesAverages = cur.fetchall()
        cur.execute("select count(*) from users")
        totalUsers = cur.fetchone()[0]
        cur.execute(
            "select date, examName, count(studentUsername) from grades group by examName, date"
        )
        coursesMissingUsers = cur.fetchall()
        connection.close()
        data = {
            "users": users,
            "grades": grades,
            "gradesAverages": gradesAverages,
            "totalUsers": totalUsers,
            "coursesMissingUsers": coursesMissingUsers,
        }
        return jsonify(data)

    def getDataUser(self, username):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        cur.execute("select * from grades where studentUsername = ?", (username,))
        grades = cur.fetchall()
        cur.execute(
            "select examName, date, round(avg(grade), 1) from grades where studentUsername = ? group by examName, date",
            (username,),
        )
        gradesAverages = cur.fetchall()
        connection.close()
        return jsonify({"grades": grades, "gradesAverages": gradesAverages})

    def datestr(self):
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def getFeedback(self):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        cur.execute("select * from feedback")
        feedback = cur.fetchall()
        connection.close()
        return jsonify({"feedback": feedback})

    def feedbackAccess(self):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        data = {"message": "feedback accessed"}
        cur.execute(
            "insert into logs values (?, ?, ?, ?)",
            (self.datestr(), "feedback access", 1, data["message"]),
        )
        connection.commit()
        connection.close()
        return jsonify(data)

    def getLogs(self):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        cur.execute("select * from logs")
        logs = cur.fetchall()
        connection.close()
        return jsonify({"logs": logs})

    def logsAccess(self):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        data = {"message": "logs accessed"}
        cur.execute(
            "insert into logs values (?, ?, ?, ?)",
            (self.datestr(), "logs access", 1, data["message"]),
        )
        connection.commit()
        connection.close()
        return jsonify(data)

    # def addToLogs(self, action, cur, data, dataArray):
    #     success = 1 if data['success'] == True else 0
    #     cur.execute('insert into logs values (?, ?, ?)', (action, success, dataArray.join(', ')))


dm = DatabaseManager_gradeTracker("gradeTrackerData.db")
dm.initialize_database()


### AITStudentsGradeTracker
@app.route("/AITStudentsGradeTracker")
def trackerLogin():
    return render_template("AITStudentsGradeTracker.html")


@app.route("/trackerLoginCheck", methods=["POST"])
def trackerLoginCheck():
    d = request.json
    username = d.get("username")
    password = d.get("password")
    return dm.loginCheck(username, password)


@app.route("/trackerAdminLoginCheck", methods=["POST"])
def trackerAdminLoginCheck():
    d = request.json
    password = d.get("adminPassword")
    return dm.adminLoginCheck(password)


@app.route("/trackerAddGrade", methods=["POST"])
def trackerAddGrade():
    d = request.json
    studentUsername = d.get("studentUsername")
    examName = d.get("examName")
    grade = d.get("grade")
    teacherName = d.get("teacherName")
    return dm.addGrade(studentUsername, examName, grade, teacherName)


@app.route("/trackerAddStudent", methods=["POST"])
def trackerAddStudent():
    d = request.json
    name = d.get("name")
    username = d.get("username")
    password = d.get("password")
    email = d.get("email")
    phoneNumber = d.get("phoneNumber")
    address = d.get("address")
    return dm.addStudent(name, username, password, email, phoneNumber, address)


@app.route("/getDataAdmin", methods=["GET"])
def getDataAdmin():
    return dm.getDataAdmin()


@app.route("/getDataUser", methods=["POST"])
def getDataUser():
    d = request.json
    username = d.get("username")
    return dm.getDataUser(username)


@app.route("/examsSearch", methods=["POST"])
def examsSearch():
    d = request.json
    username = d["username"]
    examName = d["examName"]
    return dm.examsSearch(username, examName)


@app.route("/sendFeedback", methods=["POST"])
def sendFeedback():
    d = request.json
    username = d["username"]
    text = d["text"]
    return dm.sendFeedback(username, text)


@app.route("/getFeedback")
def getFeedback():
    return dm.getFeedback()


@app.route("/feedbackAccess")
def feedbackAccess():
    return dm.feedbackAccess()


@app.route("/getLogs", methods=["GET"])
def getLogs():
    return dm.getLogs()


@app.route("/logsAccess")
def logsAccess():
    return dm.logsAccess()


class DatabaseManager_MovieTheaterSales:
    adminPassword = "11bebb901a5ccfb0cd9c62357ba15674aa2fa497778091d6cb06524da48eafec"

    def __init__(self, database_file):
        self.database_file = database_file

    def initialize_database(self):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()

        cur.execute(
            """create table if not exists movies (
                    id INTEGER PRIMARY KEY,
                    title varchar,
                    description varchar,
                    showtime varchar,
                    tickets_total INTEGER,
                    tickets_available INTEGER)"""
        )

        cur.execute(
            """create table if not exists users (
                    id INTEGER PRIMARY KEY,
                    username varchar,
                    password varchar,
                    email varchar)"""
        )

        cur.execute(
            """CREATE TABLE IF NOT EXISTS seats (
                    id INTEGER PRIMARY KEY,
                    movie_id INTEGER,
                    row INTEGER,
                    seat INTEGER,
                    available BOOLEAN,
                    FOREIGN KEY (movie_id) REFERENCES movies(id))"""
        )

        cur.execute(
            """create table if not exists soldTickets (
                    id INTEGER PRIMARY KEY,
                    movie_id INTEGER,
                    user_id INTEGER,
                    seat_id INTEGER,
                    booking_time varchar,
                    FOREIGN KEY (movie_id) REFERENCES movies(id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (seat_id) REFERENCES seats(id))"""
        )

        cur.execute(
            """create table if not exists logs (
                    time varchar,
                    action varchar,
                    success bit,
                    data varchar)"""
        )

        cur.execute(
            "insert into logs values (?, ?, ?, ?)",
            (self.datestr(), "creation", 1, "database initialized"),
        )

        connection.commit()
        connection.close()

    def login(self, username, password):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?", (username, password)
        )
        user = cur.fetchone()
        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]  # Store username in session
            data = {"success": True, "message": "Login successful", "user": user}
            cur.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    self.datestr(),
                    "user login",
                    1,
                    f"username = {username}, password = {password}, message: {data['message']}",
                ),
            )
            connection.commit()
            connection.close()
            return jsonify(data)
        data = {"success": False, "message": "Incorrect username or password"}
        cur.execute(
            "insert into logs values (?, ?, ?, ?)",
            (
                self.datestr(),
                "user login",
                0,
                f"username = {username}, password = {password}, message: {data['message']}",
            ),
        )
        connection.commit()
        connection.close()
        return jsonify(data)

    def register(self, username, password, email):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()

        if user:
            data = {
                "success": False,
                "message": "A user with that username already exists",
            }
            cur.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    self.datestr(),
                    "user login",
                    0,
                    f"username = {username}, password = {password}, email = {email}, message: {data['message']}",
                ),
            )
            connection.commit()
            connection.close()
            return jsonify(data)
        else:
            cur.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, password, email),
            )
            data = {"success": True, "message": "Registration successful"}
            cur.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    self.datestr(),
                    "user registration",
                    1,
                    f"username = {username}, password = {password}, email = {email}, message: {data['message']}",
                ),
            )
            connection.commit()
            connection.close()
            session["user_id"] = cur.lastrowid
            session["username"] = username  # Store username in session
            return jsonify(data)

    def adminLogin(self, password):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        if sha256(password.encode("utf-8")).hexdigest() == self.adminPassword:
            session["isAdmin"] = True
            data = {"success": True, "message": "Admin login successful"}
            cur.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    self.datestr(),
                    "admin login",
                    1,
                    f"password = {password}, message: {data['message']}",
                ),
            )
            connection.commit()
            connection.close()
            return jsonify(data)
        data = {"success": False, "message": "Incorrect admin password"}
        cur.execute(
            "insert into logs values (?, ?, ?, ?)",
            (
                self.datestr(),
                "admin login",
                0,
                f", password = {password}, message: {data['message']}",
            ),
        )
        connection.commit()
        connection.close()
        return jsonify(data)

    def getMoviesTitles(self):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        cur.execute("select id, title from movies")
        movies = cur.fetchall()
        data = {"movies": movies, "isAdmin": "isAdmin" in session}
        connection.close()
        return jsonify(data)

    def getMovieDetails(self, movie_id):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        cur.execute(
            "SELECT id, title, description, showtime, tickets_total, tickets_available FROM movies WHERE id=?",
            (movie_id,),
        )
        movieDetails = cur.fetchone()
        connection.close()
        return movieDetails

    def addNewMovie(self, title, description, showtime, seatRows, seatsPerRow):
        tickets = seatRows * seatsPerRow
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        cur.execute(
            "INSERT INTO movies (title, description, showtime, tickets_total, tickets_available) VALUES (?, ?, ?, ?, ?)",
            (title, description, showtime, tickets, tickets),
        )
        movie_id = cur.lastrowid
        for row in range(seatRows, 0, -1):
            for seat in range(1, seatsPerRow + 1):
                cur.execute(
                    "INSERT INTO seats (movie_id, row, seat, available) VALUES (?, ?, ?, ?)",
                    (movie_id, row, seat, True),
                )
        data = {"success": True, "message": "Movie added to the database"}
        cur.execute(
            "insert into logs values (?, ?, ?, ?)",
            (
                self.datestr(),
                "Movie added to the database by admin",
                0,
                f"title = {title}, description = {description}, showtime = {showtime}, seatRows = {seatRows}, seatsPerRow = {seatsPerRow}, message: {data['message']}",
            ),
        )
        connection.commit()
        connection.close()
        return jsonify(data)

    def deleteMovie(self, movie_id):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        cur.execute("select * from movies where id = ?", (movie_id,))
        movie = cur.fetchone()
        if movie:
            cur.execute("delete from movies where id = ?", (movie_id,))
            cur.execute("delete from seats where movie_id = ?", (movie_id,))
            cur.execute("delete from soldTickets where id = ?", (movie_id,))
            data = {"success": True, "message": "Movie deleted from the database"}
            cur.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    self.datestr(),
                    "Movie deleted from the database by admin",
                    1,
                    f"movie_id = {movie_id}, message: {data['message']}",
                ),
            )
            connection.commit()
            connection.close()
            return jsonify(data)
        else:
            data = {"success": False, "message": "Movie deletion failed"}
            cur.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    self.datestr(),
                    "Movie deletion by admin failed",
                    0,
                    f"movie_id = {movie_id}, message: {data['message']}",
                ),
            )
            connection.commit()
            connection.close()
            return jsonify(data)

    def getSeats(self, movie_id):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        cur.execute(
            "SELECT id, row, seat, available FROM seats WHERE movie_id=?", (movie_id,)
        )
        seats = cur.fetchall()
        mySeats = []
        if "user_id" in session:
            cur.execute(
                "select seat_id from soldTickets where user_id = (?)",
                (session["user_id"],),
            )
            row = cur.fetchall()
            mySeats = [i[0] for i in row]
        connection.close()
        data = {"seats": seats, "mySeats": mySeats}
        return jsonify(data)

    def bookSeat(self, movie_id, seat_id):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        if "username" in session:
            cur.execute(
                "UPDATE seats SET available = 0 WHERE id = ? AND movie_id = ?",
                (seat_id, movie_id),
            )
            cur.execute(
                "UPDATE movies SET tickets_available = tickets_available - 1 WHERE id = ?",
                (movie_id,),
            )
            cur.execute(
                "insert into soldTickets (movie_id, user_id, seat_id, booking_time) values (?, ?, ?, ?)",
                (movie_id, session["user_id"], seat_id, self.datestr()),
            )
            data = {"success": True, "message": "Seat booked"}
            cur.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    self.datestr(),
                    "Seat booked",
                    1,
                    f"username = {session['username']}, movie_id = {movie_id}, seat_id = {seat_id}, message: {data['message']}",
                ),
            )
            connection.commit()
            connection.close()
            return jsonify(data)
        elif "isAdmin" in session:
            data = {"success": False, "message": "Admin cannot book a seat"}
            cur.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    self.datestr(),
                    "Failed seat booking attempt: Admin attempted to book a seat",
                    0,
                    f"movie_id = {movie_id}, seat_id = {seat_id}, message: {data['message']}",
                ),
            )
            connection.commit()
            connection.close()
            return jsonify(data)
        else:
            data = {
                "success": False,
                "message": "Please log in or register to book a seat",
            }
            cur.execute(
                "insert into logs values (?, ?, ?, ?)",
                (
                    self.datestr(),
                    "Failed seat booking attempt: A user tried booking a seat without loggin in",
                    0,
                    f"movie_id = {movie_id}, seat_id = {seat_id}, message: {data['message']}",
                ),
            )
            connection.commit()
            connection.close()
            return jsonify(data)

    def unbookSeat(self, movie_id, seat_id):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        cur.execute(
            "UPDATE seats SET available = 1 WHERE id = ? AND movie_id = ?",
            (seat_id, movie_id),
        )
        cur.execute(
            "UPDATE movies SET tickets_available = tickets_available + 1 WHERE id = ?",
            (movie_id,),
        )
        cur.execute("delete from soldTickets where seat_id = ?", (seat_id,))
        data = {"success": True, "message": "Seat unbooked"}
        cur.execute(
            "insert into logs values (?, ?, ?, ?)",
            (
                self.datestr(),
                "Seat unbooked",
                1,
                f"username = {session['username']}, movie_id = {movie_id}, seat_id = {seat_id}, message: {data['message']}",
            ),
        )
        connection.commit()
        connection.close()
        return jsonify(data)

    def getDataAdmin(self):
        connection = sqlite3.connect(self.database_file)
        cur = connection.cursor()
        cur.execute("select * from users")
        users = cur.fetchall()
        cur.execute("select * from movies")
        movies = cur.fetchall()
        connection.close()
        data = {"users": users, "movies": movies}
        return jsonify(data)

    def datestr(self):
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


MovieTheaterSalesData_dm = DatabaseManager_MovieTheaterSales("MovieTheaterSalesData.db")
MovieTheaterSalesData_dm.initialize_database()

movies_blueprint = Blueprint(
    "movies",
    __name__,
    url_prefix="/movies",
    template_folder="movies/templates",
    static_folder="movies/static",
)


@movies_blueprint.route("/")
def movies():
    return render_template("movies.html")


@movies_blueprint.route("/register", methods=["GET", "POST"])
def moviesRegister():
    if request.method == "POST":
        d = request.json
        username = d["username"]
        password = d["password"]
        email = d["email"]
        return MovieTheaterSalesData_dm.register(username, password, email)
    return render_template("register.html")


@movies_blueprint.route("/login", methods=["GET", "POST"])
def moviesLogin():
    if request.method == "POST":
        d = request.json
        username = d["username"]
        password = d["password"]
        return MovieTheaterSalesData_dm.login(username, password)
    return render_template("login.html")


@movies_blueprint.route("/check_login")
def moviesCheck_login():
    if "username" in session:
        return jsonify(logged_in=True, is_admin=False, username=session["username"])
    elif "isAdmin" in session:
        return jsonify(logged_in=True, is_admin=True, username="Admin")
    else:
        return jsonify(logged_in=False)


@movies_blueprint.route("/adminLogin", methods=["POST"])
def moviesAdminLogin():
    d = request.json
    password = d["password"]
    return MovieTheaterSalesData_dm.adminLogin(password)


@movies_blueprint.route("/logout")
def moviesLogout():
    if "isAdmin" in session:
        session.pop("isAdmin", None)
    else:
        session.pop("username", None)
        session.pop("user_id", None)
    return jsonify({"success": True})


@movies_blueprint.route("/adminPanel")
def adminPanel():
    if "isAdmin" in session:
        return render_template("adminPanel.html")
    else:
        return render_template("unsuccessfulAdmin.html")


@movies_blueprint.route("/addNewMovie", methods=["GET", "POST"])
def addNewMovie():
    if request.method == "POST":
        d = request.json
        title = d["title"]
        description = d["description"]
        showtime = " ".join(d["showtime"].split("T"))
        seatRows = int(d["seatRows"])
        seatsPerRow = int(d["seatsPerRow"])
        return MovieTheaterSalesData_dm.addNewMovie(
            title, description, showtime, seatRows, seatsPerRow
        )
    if "isAdmin" in session:
        return render_template("addNewMovie.html")
    else:
        return render_template("unsuccessfulAdmin.html")


@movies_blueprint.route("/deleteMovie/<int:movie_id>", methods=["DELETE"])
def deleteMovie(movie_id):
    return MovieTheaterSalesData_dm.deleteMovie(movie_id)


@movies_blueprint.route("/<int:movie_id>/seats", methods=["GET"])
def seats(movie_id):
    return MovieTheaterSalesData_dm.getSeats(movie_id)


@movies_blueprint.route("/getMoviesTitles", methods=["GET"])
def getMoviesTitles():
    return MovieTheaterSalesData_dm.getMoviesTitles()


@movies_blueprint.route("/<int:movie_id>", methods=["GET"])
def movieDetails(movie_id):
    movie = MovieTheaterSalesData_dm.getMovieDetails(movie_id)
    if movie:
        return render_template("movieDetails.html", movie=movie)
    else:
        return "Movie not found", 404


@movies_blueprint.route("/<int:movie_id>/book", methods=["POST"])
def bookSeat(movie_id):
    seat_id = request.json["seat_id"]
    return MovieTheaterSalesData_dm.bookSeat(movie_id, seat_id)


@movies_blueprint.route("/<int:movie_id>/unbook", methods=["POST"])
def unbookSeat(movie_id):
    seat_id = request.json["seat_id"]
    return MovieTheaterSalesData_dm.unbookSeat(movie_id, seat_id)


@movies_blueprint.route("/getDataAdmin", methods=["GET"])
def getDataAdmin():
    return MovieTheaterSalesData_dm.getDataAdmin()


app.register_blueprint(movies_blueprint)


@app.route("/")
# def hello_world():
#     return 'Hello from Flask!'
def test():
    return "<h1>Default</h1>"


@app.route("/power")
def power():
    a = request.args.get("a")
    b = request.args.get("b")
    return f"The {b}th power of {a} is {int(a)**int(b)}"


@app.route("/about")
def h():
    return render_template("index.html")


@app.route("/kamok")
def kamok():
    return render_template("kamok.html")


@app.route("/kamok2")
def kamok2():
    return render_template("kamok2.html")


@app.route("/kamok3")
def kamok3():
    return render_template("kamok3.html")


@app.route("/calc")
def calc():
    return render_template("My JavaScript Calculator.html")


@app.route("/square")
def sqare():
    val = request.args.get("num")
    return json.dumps({"square": int(val) ** 2, "cube": int(val) ** 3})


messages = {}


class Message:
    def __init__(self, sender, receiver, text):
        self.sender = sender
        self.receiver = receiver
        self.text = text
        self.datestring = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def to_string(self):
        return "{} {}->{}:\t{}".format(
            self.datestring, self.sender, self.receiver, self.text
        )


class Chat:
    def __init__(self):
        self.messages = defaultdict(list)

    def add_message(self, sender, receiver, text):
        new_message = Message(sender, receiver, text)
        self.messages[sender].append(new_message)
        self.messages[receiver].append(new_message)

    def get_messages(self, username):
        result = []
        if username in self.messages:
            for x in self.messages[username]:
                result.append(x.to_string())

        return result


# chat = Chat()


@app.route("/give")
def give():
    return jsonify(db)


@app.route("/login", methods=["POST"])
def login():
    d = request.json
    username = d["username"]
    password = d["password"]

    if not username or not password:
        return jsonify({"success": False, "message": "Missing username or password"})

    cur.execute("select count(*) from users")
    if cur.fetchone()[0] > 0:
        cur.execute(
            "select * from users where username = ? and password = ?",
            (username, password),
        )
        user = cur.fetchone()
        if user:
            return jsonify({"success": True, "message": "Login successful"})
    return jsonify({"success": False, "message": "Incorrect username or password"})


@app.route("/signup", methods=["POST"])
def signup():
    d = request.json
    username = d["username"]
    password = d["password"]

    if not username or not password:
        return jsonify({"success": False, "message": "Missing username or password"})

    cur.execute("select count(*) from users")
    if cur.fetchone()[0] > 0:
        cur.execute("SELECT * FROM users WHERE username = '?'", (username,))
        exist = cur.fetchone()
        if exist:
            return jsonify({"success": False, "message": "Username already exists"})
    else:
        exist = False

    cur.execute(
        "INSERT INTO users (username, password) VALUES ('?', '?')", (username, password)
    )
    db.commit()
    return jsonify({"success": True, "message": "User registered successfully"})


def datestr():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


@app.route("/bek")
def bek():
    return render_template("bek.html")


@app.route("/post", methods=["POST"])
def post():
    d = request.json
    fromm = d["from"]
    to = d["to"]
    msg = d["message"]
    # time = d['time']
    cur.execute(
        f'insert into messages values ("{datestr()}", "{fromm}", "{to}", "{msg}")'
    )
    db.commit()

    # if fromm in messages:
    #     if to in messages[fromm]:
    #         messages[fromm][to].append({'message': msg, 'time': time})
    #     else:
    #         messages[fromm][to] = [{'message': msg, 'time': time}]
    # else:
    #     messages[fromm] = {to: [{'message': msg, 'time': time}]}

    # chat.add_message(fromm, to, msg)

    # return jsonify({"result": "Success", "time": time})
    return jsonify({"result": "Success"})


@app.route("/get_messages")
def get_messages():
    username = request.args.get("username")
    result = cur.execute(
        f'select * from messages where sender = "{username}" or receiver="{username}"'
    ).fetchall()
    return jsonify(result)


@app.route("/messages")
def messages():
    return jsonify(messages)


@app.route("/Lab20240423")
def Lab20240423():
    return render_template("Lab20240423.html")


@app.route("/calculate", methods=["GET"])
def calculate():
    d = request.args.to_dict()
    d1 = d["d1"]
    d2 = d["d2"]
    op = d["op"]
    if op == "plus":
        result = float(d1) + float(d2)
    elif op == "minus":
        result = float(d1) - float(d2)
    elif op == "multiply":
        result = float(d1) * float(d2)
    elif op == "divide":
        if float(d2) == 0:
            return jsonify({"result": "Division by zero ERROR"})
        result = float(d1) / float(d2)

    return jsonify({"result": result})


name = "AIT Chat"
users = []  # names
messages = {}  # key = sender, value = [{receiver, time, message }]
groups = {}


@app.route("/send")
def send():
    sender = request.args.get("sender")
    receiver = request.args.get("receiver")
    msg = request.args.get("msg")
    if sender not in users:
        users.append(sender)
    if receiver not in users:
        users.append(receiver)

    if sender not in messages:
        messages[sender] = []

    messages[sender].append({"receiver": receiver, "time": time(), "message": msg})
    chat_messages = open("chat.txt", "a")
    chat_messages.write(
        f"sender: {sender}, receiver: {receiver}, time: {time()}, message: {msg}<br>"
    )
    chat_messages.close()

    # print()
    # print(messages)
    # print()
    return messages


@app.route("/create_group")
def create_group():
    info = request.args.to_dict()
    group_name = info.get("group_name")
    members = [val for i, val in info.items() if i != "group_name"]
    groups[group_name] = {"members": members, "messages": {}}
    return f"""group "{group_name}" with members:<br>{members}<br>has been created"""


@app.route("/add_to_group")
def add_to_group():
    group_name = request.args.get("group_name")
    if group_name not in groups:
        return f"""group "{group_name}" doesn't exist<br>Use the function create_group to create a group"""
    member_name = request.args.get("member_name")
    groups[group_name]["members"].append(member_name)
    return '''Member {member_name} has been added to the group "{group_name}"'''


@app.route("/send_to_group")
def send_to_group():
    group_name = request.args.get("group_name")
    sender = request.args.get("sender")
    msg = request.args.get("msg")
    if group_name not in groups:
        return f"""group "{group_name}" doesn't exist<br>Use the function create_group to create a group"""
    if sender not in groups[group_name]["members"]:
        return "Sender not in group<br>Use the function add_to_group to add a member to a group"
    if sender not in groups[group_name]["messages"]:
        groups[group_name]["messages"][sender] = []
    groups[group_name]["messages"][sender].append({"time": time(), "message": msg})
    chat_messages = open("chat.txt", "a")
    chat_messages.write(
        f"group: {group_name}, sender: {sender}, time: {time()}, message: {msg}<br>"
    )
    chat_messages.close()
    return groups[group_name]["messages"]


@app.route("/get_from_single_user")
def get_from_single_user():
    sender = request.args.get("sender")
    receiver = request.args.get("receiver")
    if sender not in messages:
        return []

    output = []

    for d in messages[sender]:
        if d["receiver"] == receiver:
            output.append(d)

    return output


### Web Dev Lab
### 1. show all messages sent by sender


@app.route("/get_from_sender")
def get_from_sender():
    sender = request.args.get("sender")
    return messages.get(sender, [])


### 2. show all messages in database


@app.route("/get_all_messages")
def get_all_messages():
    # if not chat_messages.read():
    #     return "chat empty"
    chat_messages = open("chat.txt", "r")
    output = chat_messages.read()
    chat_messages.close()
    return output


### 3. show all messages received by receiver


@app.route("/get_by_receiver")
def get_by_receiver():
    receiver = request.args.get("receiver")
    output = []
    for i in messages:
        if i["receiver"] == receiver:
            output.append(i)
    return output


@app.route("/get_groups")
def get_groups():
    return groups


@app.route("/clear_chat")
def clear():
    messages.clear()
    chat_messages = open("chat.txt", "r+")
    chat_messages.truncate(0)
    chat_messages.close()
    return "all chat messages have been cleared"


@app.route("/clear_groups")
def clear_groups():
    groups.clear()
    return "all groups have been cleared"


# if __name__ == "__main__":
#     while True:
#         instruction = input('instruction: ')
#         match instruction:
#             case 'send':
#                 sender = input('Sender: ')
#                 receiver = input('Receiver: ')
#                 message = input('Message: ')
#                 send(sender, receiver, message)
#             case 'get single':
#                 sender = input('sender: ')
#                 receiver = input('receiver: ')
#                 print(f'messages sent by {sender} to {receiver} are : ', get_from_single_user(sender, receiver))
#             case 'get from sender':
#                 sender = input('sender: ')
#                 print(f'messages sent by {sender} are: {get_from_sender(sender)}')
#             case 'get all':
#                 print(f'All messages: {get_all_messages()}')
#             case 'get by receiver':
#                 receiver = input('receiver: ')
#                 print(f'Messages received by {receiver}: {get_by_receiver(receiver)}')


### From here 2024.11.12 Food Management

init_db()
# Register the blueprint
app.register_blueprint(food_bp, url_prefix="/food")

if __name__ == "__main__":
    app.run(debug=True)
