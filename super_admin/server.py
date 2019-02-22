from flask import Flask, render_template,request, redirect, session, flash
from mysqlconnection import connectToMySQL   # import the function that will return an instance of a connection
import re
from flask_bcrypt import Bcrypt
app = Flask(__name__)
bcrypt=Bcrypt(app)
app.secret_key="this key is secret"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASS_REGEX= re.compile(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{6,12}$")
# default route when entering localhost:5000
@app.route("/")
def index():
    return render_template("index.html")
#route after clicking register form button on index page
@app.route("/register_user", methods=["POST"])
def add_user_to_db():
    #setting a variable to determine if you move on to after registration or an element is invalid
    is_valid = True
    if len(request.form['fname'])<1:
        is_valid = False
        flash("Please enter a first name.")
    if len(request.form['lname'])<1:
        is_valid = False
        flash("Please enter a last name.")
    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Please enter a valid e-mail.")
    if len(request.form['user_pass'])<2:
        is_valid = False
        flash("Please enter a valid password.")
    if request.form['user_pass']!=request.form['user_pass_conf']:
        is_valid = False
        flash("Please confirm the same password")
    if not is_valid:
        return redirect("/")
    #setting pw_hash to be a bcrypted password
    pw_hash=bcrypt.generate_password_hash(request.form['user_pass'])
    mysql = connectToMySQL("users")
    query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(em)s, %(pass)s, NOW(), NOW());"
    data= {
        "fn": request.form["fname"],
        "ln": request.form["lname"],
        "em": request.form['email'],
        "pass": pw_hash
    }
    print(pw_hash)
    new_user_id = mysql.query_db(query, data)
    #setting a session with user id
    if 'user_id' not in session:
        session['user_id']=new_user_id
    else:
        session['user_id']=new_user_id
    #redirecting to new route that can be used to display the page to prevent refreshing the page re-entering info
    return redirect("/result")

@app.route("/result")
def show_user():
    #makes one_user a variable that is the full table of the current logged in or registered user
    mysql = connectToMySQL("users")
    one_user=mysql.query_db("SELECT * FROM users where id = "+str(session['user_id'])+";")
    #makes messages_for_user which is a variable that is all the messages sent by the user used to show count later
    mysql = connectToMySQL("users")
    messages_from_user=mysql.query_db("SELECT * FROM messages where sender_id = "+str(session['user_id'])+";")
    #makes all_users which includes every user that isnt the current one signed in
    mysql = connectToMySQL("users")
    all_users=mysql.query_db("SELECT * FROM users where id!="+str(session['user_id'])+";")
    #makes messages_for_user which includes all the messages sent to the current session user
    mysql = connectToMySQL("users")
    messages_for_user=mysql.query_db("SELECT * FROM messages where receiver_id = "+str(session['user_id'])+";")
    #makes message_info which has messages.id, messages.sender_id, messages.receiver_id, users.first_name as sender, messages.message, messages.created_at joining messages and users where the users.id and messages.sender_id
    mysql = connectToMySQL("users")
    message_info=mysql.query_db("SELECT messages.id, messages.sender_id, messages.receiver_id, users.first_name as sender, messages.message, messages.created_at FROM messages JOIN users ON users.id = messages.sender_id AND messages.receiver_id= "+str(session['user_id']+";")
    mysql = connectToMySQL("users")
    sender_first_name=mysql.query_db("SELECT users.first_name where ")
    if messages_from_user==False:
        session['sent_messages']=0
    if len(messages_from_user)>=0:
            session['sent_messages']=len(messages_from_user)
    if messages_for_user==False:
        session['received_messages']=0
    if len(messages_for_user)>=0:
            session['received_messages']=len(messages_for_user)
    return render_template("result.html", user=one_user, sent_count=session['sent_messages'], received_count=session['received_messages'], messages_for_user=messages_for_user, all_users=all_users, messages=message_info)

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