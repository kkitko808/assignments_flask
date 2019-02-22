from flask import Flask, render_template,request, redirect, session, flash
from mysqlconnection import connectToMySQL   # import the function that will return an instance of a connection
import re
from flask_bcrypt import Bcrypt
app = Flask(__name__)
bcrypt=Bcrypt(app)
app.secret_key="this key is secret"
@app.route("/")
def index():
    return render_template("index.html")
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASS_REGEX= re.compile(r"^[0-9a-zA-Z\s\r\n@!#\$\^%&*()+=\-\[\]\\\';,\.\/\{\}\|\":<>\?]+$")
@app.route("/register_user", methods=["POST"])
def add_user_to_db():
    #setting a variable to determine if you move on to after registration or an element is invalid
    is_valid = True
    check_pass=True
    if len(request.form['fname'])<1 or not request.form['fname'].isalpha():
        is_valid = False
        flash("Please enter a valid first name.")
    if len(request.form['lname'])<1 or not request.form['fname'].isalpha():
        is_valid = False
        flash("Please enter a valid last name.")
    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Please enter a valid e-mail.")
    if len(request.form['user_pass'])<8 or not PASS_REGEX.match(request.form['user_pass']):
        is_valid = False
        check_pass = False
        flash("Please enter a valid password.")
    if check_pass and request.form['user_pass']!=request.form['user_pass_conf']:
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
    if 'user_id' not in session:
        session['user_id']=new_user_id
    else:
        session['user_id']=new_user_id
    return redirect("/pokes")
@app.route("/pokes")
def show_user():
    if not "user_id" in session:
        return redirect("/")
    mysql = connectToMySQL("users")
    one_user=mysql.query_db("SELECT * FROM users where id = "+str(session['user_id'])+";")
    mysql = connectToMySQL("users")
    messages_from_user=mysql.query_db("SELECT * FROM messages where sender_id = "+str(session['user_id'])+";")
    mysql = connectToMySQL("users")
    all_users=mysql.query_db("SELECT * FROM users where id!="+str(session['user_id'])+";")
    mysql = connectToMySQL("users")
    messages_for_user=mysql.query_db("SELECT * FROM messages where receiver_id = "+str(session['user_id'])+";")
    mysql = connectToMySQL("users")
    message_info=mysql.query_db("SELECT messages.id, messages.sender_id, messages.receiver_id, users.first_name as sender, messages.message, messages.created_at FROM messages JOIN users ON users.id = messages.sender_id AND messages.receiver_id= 61;")
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
    return render_template("pokes.html", user=one_user, sent_count=session['sent_messages'], received_count=session['received_messages'], messages_for_user=messages_for_user, all_users=all_users, messages=message_info)
@app.route("/login_user", methods=["POST"])
def show_login():
    is_valid=True
    mysql = connectToMySQL("users")
    query = "SELECT * FROM users WHERE users.email =%(em)s;"
    data= {
        "em": request.form['email'],
    }
    one_user= mysql.query_db(query, data)
    if not one_user:
        is_valid= False
        flash("Sorry, you could not be logged in.")
        return redirect("/")
    if bcrypt.check_password_hash(one_user[0]['password'], request.form['user_pass']):
        if'user_id' not in session:
            session['user_id']=one_user[0]['id']
        else:
            session['user_id']=one_user[0]['id']
        return redirect("/pokes")
    flash("Sorry, you could not be logged in.")
    return redirect("/")
@app.route("/send_message", methods=['POST'])
def send_message():
    print(request.form)
    mysql = connectToMySQL("users")
    query = "INSERT INTO messages (message, sender_id, receiver_id, created_at, updated_at) VALUES (%(message)s, %(sender)s, %(receiver)s, NOW(), NOW());"
    data= {
        "message": request.form["message"],
        "sender": session['user_id'],
        "receiver": request.form["receiver_id"]
    }
    message= mysql.query_db(query,data)
    return redirect("/pokes")
@app.route("/logout_user")
def logout_user():
    if 'user_id' in session:
        session.pop("user_id")
        flash("You've been logged out.")
    return redirect("/")
@app.route("/delete/<id>")
def delete_message(id):
    if not 'user_id' in session:
        return redirect("/")
    mysql = connectToMySQL("users")
    query="SELECT id FROM messages where id=%(id)s;"
    data={
        "id":id
    }
    message_to_delete = mysql.query_db(query,data)
    if not message_to_delete:
        return redirect("/")
    mysql = connectToMySQL("users")
    query = ("SELECT * FROM users JOIN messages ON messages.receiver_id=users.id WHERE messages.receiver_id=%(user)s AND messages.id=%(message_id)s")
    data={
        "user":session['user_id'],
        "message_id":message_to_delete[0]['id']
    }
    messages_isfor_user=mysql.query_db
    print("*"*180, messages_isfor_user)
    if not messages_isfor_user:
        return redirect('/')
    mysql = connectToMySQL("users")
    query=mysql.query_db("DELETE FROM messages where id="+str(id)+";")
    return redirect("/pokes")
@app.route("/email", methods=['POST'])
def email():
    found=False
    mysql=connectToMySQL("users")
    query= "SELECT email from users WHERE email = %(email)s;"
    data = { "email": request.form['email'] }
    result = mysql.query_db(query, data)
    if result:
        found = True
    return render_template('partials/index.html', found=found)
@app.route("/searchbar", methods=['POST'])
def searchbar():
    found=False
    mysql=connectToMySQL("users")
    query= "SELECT * from users WHERE first_name LIKE %%(searchbar)s;"
    data = { "searchbar": request.form['searchbar']+ "%" }
    users = mysql.query_db(query, data)
    if users:
        found = True
    return render_template('partials/search.html', found=found, users=users)
if __name__ == "__main__":
    app.run(debug=True)