from flask import Flask, render_template,request, redirect, session, flash
from mysqlconnection import connectToMySQL   # import the function that will return an instance of a connection
import re
from flask_bcrypt import Bcrypt
app = Flask(__name__)
bcrypt=Bcrypt(app)
app.secret_key="this key is secret"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASS_REGEX= re.compile(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{6,12}$")
@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)

# SQL query format
# mysql = connectToMySQL("users")
#     query = "INSERT INTO messages (message, sender_id, receiver_id, created_at, updated_at) VALUES (%(message)s, %(sender)s, %(receiver)s, NOW(), NOW());"
#     data= {
#         "message": request.form["message"],
#         "sender": session['user_id'],
#         "receiver": request.form["receiver_id"]
#     }
#     message= mysql.query_db(query,data)

# adding session
# if 'user_id' not in session:
#         session['user_id']=new_user_id
#     else:
#         session['user_id']=new_user_id

# deleting session
# if 'user_id' in session:
#         session.pop("user_id")

# matching regex
# if not EMAIL_REGEX.match(request.form['email']):
#         is_valid = False
#         flash("Please enter a valid e-mail.")