# Importing the flask class. An instance of this class will be
# the WSGI application
from flask import Flask, redirect, url_for, request, render_template
import sqlite3
from random import randint

# Make a connection to the database
con = sqlite3.connect('mydatabase.db', check_same_thread=False)
cur = con.cursor()

# Creating an instance of the Flask class
app = Flask(__name__)

# Create unique user IDs
def unique_id():
    seed = 23  # Set your desired seed value
    while True:
        yield seed
        seed += 1

unique_sequence = unique_id()

# Define the homepage
@app.route("/")
def home():
    return render_template("items.html", content="Passing this from backend")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["email"]
        return redirect(url_for("user", usr=user))
    else:
        return render_template("login.html")

@app.route('/read-form', methods=['POST'])
def read_form():
    # Get the form data as Python ImmutableDict datatype
    data = request.form
    response = ""
    if request.method == 'POST':
        if request.form['submit_button'] == 'submit':
            data = request.form
            cur.execute("SELECT * FROM USERS WHERE email = ?", [data["userEmail"]])
            result = cur.fetchone()
            if result and result[1] == data["userEmail"] and result[2] == data["userPassword"]:
                return redirect(url_for("user", usr=data["userEmail"]))
            elif result and result[1] == data["userEmail"] and result[2] != data["userPassword"]:
                return render_template("login.html", content="Incorrect Password")
        elif request.form['submit_button'] == 'register':
            data = request.form
            cur.execute("SELECT * FROM USERS WHERE email = ?", [data["userEmail"]])
            result = cur.fetchone()
            if result:
                return render_template("login.html", content="User Already Exists")
            else:
                # Creating a random ID for user.
                ascii_values = [ord(c) for c in data["userEmail"]]
                user_id = randint(1, 999) + sum(ascii_values)
                cur.execute("INSERT INTO USERS VALUES (?, ?, ?)", (user_id, data["userEmail"], data["userPassword"]))
                con.commit()
                return redirect(url_for("user", usr=data["userEmail"]))
    # return render_template("formdata.html", content=response)
    ## Return the extracted information

@app.route("/users")
def display_users():
    cur.execute('SELECT * FROM users')
    rows = cur.fetchall()
    return render_template('showusers.html', usr=rows)

@app.route('/items')
def items():
    return render_template('items.html')

@app.route("/<usr>")
def user(usr):
    return render_template("user.html", usr="user", content=usr)

@app.route("/delete-user/<int:user_id>", methods=["GET"])
def delete_user(user_id):
    cur.execute("DELETE FROM USERS WHERE id=?", (user_id,))
    con.commit()
    return redirect(url_for("display_users"))

if __name__ =="__main__":
    app.run(host='0.0.0.0', debug=True)
