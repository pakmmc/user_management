import pymysql
from flask import Flask, render_template, request, redirect, session
app = Flask(__name__)

# Allow flask to encrypt the session cookie.
app.secret_key = "any-random-string-reshrdjtfkygluvchfjkhlbh"

def create_connection():
    return pymysql.connect(
        host="10.0.0.17",
        user="mmc",
        # host="localhost",
        # user="root",
        password="********",
        db="mmc_test",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/")
def home():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users"
            cursor.execute(sql)
            result = cursor.fetchall()
    return render_template("home.html", result=result)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = """SELECT * FROM users
                    WHERE email = %s AND password = %s"""
                values = (
                    request.form["email"],
                    request.form["password"]
                )
                cursor.execute(sql, values)
                result = cursor.fetchone()
        if result:
            session["logged_in"] = True
            return redirect("/")
        else:
            return "Wrong username or password!"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        with create_connection() as connection:
            with connection.cursor() as cursor:
                # Any input from the user should be replaced by '%s',
                # so that their input isn't accidentally treated as bits of SQL.
                sql = """INSERT INTO users
                    (first_name, last_name, email, password, birthday)
                    VALUES (%s, %s, %s, %s, %s)"""
                values = (
                    request.form["first_name"],
                    request.form["last_name"],
                    request.form["email"],
                    request.form["password"],
                    request.form["birthday"]
                )
                cursor.execute(sql, values)
                connection.commit() # <-- NEW!!! Save to the database
        return redirect("/")
    else:
        return render_template("signup.html")

# /update?id=1
@app.route("/update", methods=["GET", "POST"])
def update():
    if request.method == "POST":
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = """UPDATE users SET
                    first_name = %s,
                    last_name = %s,
                    email = %s,
                    password = %s,
                    birthday = %s
                    WHERE id = %s
                """
                values = (
                    request.form['first_name'],
                    request.form['last_name'],
                    request.form['email'],
                    request.form['password'],
                    request.form['birthday'],
                    request.form['id']
                )
                cursor.execute(sql, values)
                connection.commit()
        return redirect("/")
    else:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE id = %s"
                values = (request.args["id"])
                cursor.execute(sql, values)
                result = cursor.fetchone()
        return render_template("update.html", result=result)

# /delete?id=1
@app.route("/delete")
def delete():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql = "DELETE FROM users WHERE id = %s"
            values = (request.args["id"])
            cursor.execute(sql, values)
            connection.commit()
    return redirect("/")

app.run(debug=True)
