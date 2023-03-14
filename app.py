import pymysql
from flask import Flask, render_template, request, redirect
app = Flask(__name__)

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



# TODO: UPDATE

# TODO: DELETE

app.run(debug=True)
