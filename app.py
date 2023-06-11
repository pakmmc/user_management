import pymysql
import hashlib
import uuid
import os
from flask import Flask, render_template, request, redirect, session, flash
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

def can_access():
    if "logged_in" in session:
        matching_id = session["id"] == int(request.args["id"])
        is_admin = session["role"] == "admin"
        return matching_id or is_admin
    else:
        return False

def encrypt(password):
    return hashlib.sha256(password.encode()).hexdigest()

def email_exists(email):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email = %s"
            values = (email)
            cursor.execute(sql, values)
            result = cursor.fetchone()
    return result is not None

# This runs before every page request.
# If it returns something, the request will be prevented.
@app.before_request
def restrict():
    restricted = ["admin_only"]
    if request.endpoint in restricted:
        if "logged_in" not in session or session["role"] != "admin":
            flash("Only admin can view that page.")
            return redirect('/')

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
                    encrypt(request.form["password"])
                )
                cursor.execute(sql, values)
                result = cursor.fetchone()
        if result:
            session["logged_in"] = True
            session["id"] = result["id"]
            session["first_name"] = result["first_name"]
            session["role"] = result["role"]
            return redirect("/")
        else:
            flash("Wrong username or password!")
            return redirect("/login")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        if email_exists(request.form["email"]):
            flash("That email already exists.")
            return redirect("/signup")
        with create_connection() as connection:
            with connection.cursor() as cursor:

                image = request.files["image"]
                if image:
                    # Choose a random filename to prevent clashes
                    ext = os.path.splitext(image.filename)[1]
                    image_path = "static/images/" + str(uuid.uuid4())[:8] + ext
                    image.save(image_path)
                else:
                    image_path = None

                # Any input from the user should be replaced by '%s',
                # so that their input isn't accidentally treated as bits of SQL.
                sql = """INSERT INTO users
                    (first_name, last_name, email, password, birthday, image)
                    VALUES (%s, %s, %s, %s, %s, %s)"""
                values = (
                    request.form["first_name"],
                    request.form["last_name"],
                    request.form["email"],
                    encrypt(request.form["password"]),
                    request.form["birthday"],
                    image_path
                )
                cursor.execute(sql, values)
                connection.commit() # <-- NEW!!! Save to the database

                # Select the new user details and store them in session
                sql = "SELECT * FROM users WHERE email = %s"
                values = (request.form["email"])
                cursor.execute(sql, values)
                result = cursor.fetchone()
                session["logged_in"] = True
                session["id"] = result["id"]
                session["first_name"] = result["first_name"]
                session["role"] = result["role"]

        return redirect("/")
    else:
        return render_template("signup.html")

# /view?id=1
@app.route("/view")
def view():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE id = %s"
            values = (request.args["id"])
            cursor.execute(sql, values)
            result = cursor.fetchone()
    return render_template("view.html", result=result)

# /post?id=1
@app.route("/post")
def post():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            sql = """SELECT * FROM posts
                    WHERE posts.id = %s"""
            values = (request.args["id"])
            cursor.execute(sql, values)
            result = cursor.fetchone()
    return render_template("post_view.html", result=result)

# /update?id=1
@app.route("/update", methods=["GET", "POST"])
def update():
    if not can_access():
        flash("You don't have permission to do that!")
        return redirect("/")

    if request.method == "POST":
        with create_connection() as connection:
            with connection.cursor() as cursor:

                password = request.form["password"]
                if password:
                    encrypted_password = encrypt(password)
                else:
                    encrypted_password = request.form["old_password"]

                image = request.files["image"]
                if image:
                    # Choose a random filename to prevent clashes
                    ext = os.path.splitext(image.filename)[1]
                    image_path = "static/images/" + str(uuid.uuid4())[:8] + ext
                    image.save(image_path)
                    if request.form["old_image"]:
                        os.remove(request.form["old_image"])
                else:
                    image_path = request.form["old_image"]

                sql = """UPDATE users SET
                    first_name = %s,
                    last_name = %s,
                    email = %s,
                    password = %s,
                    birthday = %s,
                    image = %s
                    WHERE id = %s
                """
                values = (
                    request.form['first_name'],
                    request.form['last_name'],
                    request.form['email'],
                    encrypted_password,
                    request.form['birthday'],
                    image_path,
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
    if not can_access():
        flash("You don't have permission to do that!")
        return redirect("/")
    
    with create_connection() as connection:
        with connection.cursor() as cursor:
            # Get the image path before deleting the user
            sql = "SELECT image FROM users WHERE id = %s"
            values = (request.args["id"])
            cursor.execute(sql, values)
            result = cursor.fetchone()
            if result["image"]:
                os.remove(result["image"])

            sql = "DELETE FROM users WHERE id = %s"
            values = (request.args["id"])
            cursor.execute(sql, values)
            connection.commit()
    return redirect("/")

# /checkemail?email=a@a
@app.route("/checkemail")
def check_email():
    return {
        "exists": email_exists(request.args["email"])
    }

# /admin?id=1&role=admin
@app.route("/admin")
def toggle_admin():
    if "logged_in" in session and session["role"] == "admin":
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = "UPDATE users SET role = %s WHERE id = %s"
                values = (
                    request.args["role"],
                    request.args["id"]
                )
                cursor.execute(sql, values)
                connection.commit()
    else:
        flash("You don't have permission to do that!")
    return redirect("/")

@app.route("/hidden")
def admin_only():
    return "Here is where I would put restricted content, if I had any."


app.run(debug=True)
