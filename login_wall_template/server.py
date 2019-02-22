from flask import Flask, render_template,request, redirect, session, flash
from mysqlconnection import connectToMySQL   # import the function that will return an instance of a connection
import re
from flask_bcrypt import Bcrypt
app = Flask(__name__)
bcrypt=Bcrypt(app)
app.secret_key="this key is secret"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASS_REGEX= re.compile(r"^[0-9a-zA-Z\s\r\n@!#\$\^%&*()+=\-\[\]\\\';,\.\/\{\}\|\":<>\?]+$")
# default route when entering localhost:5000
@app.route("/")
def home_redirect():
    return redirect("/main")
@app.route("/main")
def index():
    if 'user_id' in session:
        session.pop("user_id")
    return render_template("index.html")
#route after clicking register form button on index page
@app.route("/register_user", methods=["POST"])
def add_user_to_db():
    #setting a variable to determine if you move on to after registration or an element is invalid
    is_valid = True
    check_pass=True
    if len(request.form['name'])<1 or not request.form['name'].isalpha():
        is_valid = False
        flash("Please enter a valid first name.")
    if len(request.form['alias'])<1 or not request.form['alias'].isalnum():
        is_valid = False
        flash("Please enter a valid alias.")
    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Please enter a valid e-mail.")
    if not len(request.form['user_pass'])>8 or not PASS_REGEX.match(request.form['user_pass']):
        is_valid = False
        check_pass = False
        flash("Please enter a valid password.")
    if check_pass and request.form['user_pass']!=request.form['user_pass_conf']:
        is_valid = False
        flash("Please confirm the same password")
    if not request.form['dob']:
        is_valid = False
        flash("Please enter a date of birth")
    if not is_valid:
        return redirect("/main")
    #setting pw_hash to be a bcrypted password
    pw_hash=bcrypt.generate_password_hash(request.form['user_pass'])
    mysql = connectToMySQL("users")
    query = "INSERT INTO users (name, alias, email, password, dob, created_at, updated_at) VALUES (%(fn)s, %(ali)s, %(em)s, %(pass)s, %(dob)s, NOW(), NOW());"
    data= {
        "fn": request.form["name"],
        "ali": request.form["alias"],
        "em": request.form['email'],
        "dob":request.form['dob'],
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
    return redirect("/pokes")
@app.route("/poke/<id>")
def poke_user(id):
    mysql = connectToMySQL("users")
    # INSERT INTO `users`.`pokes` (`sender_id`, `receiver_id`) VALUES ('71', '73');
    query= "INSERT INTO pokes (sender_id, receiver_id) VALUES (%(send)s, %(rec)s)"
    data={
        "send": session['user_id'],
        "rec": id
    }
    new_poke = mysql.query_db(query, data)
    return redirect("/pokes")
@app.route("/pokes")
def show_user():
    if 'user_id' not in session:
        return redirect('/main')
    #makes one_user a variable that is the full table of the current logged in or registered user
    mysql = connectToMySQL("users")
    one_user=mysql.query_db("SELECT * FROM users where id = "+str(session['user_id'])+";")
    #makes pokes_for_user which is a variable that is all the pokes sent by the user used to show count later
    mysql = connectToMySQL("users")
    pokes_from_user=mysql.query_db("SELECT * FROM pokes where sender_id = "+str(session['user_id'])+";")
    #makes all_users which includes every user that isnt the current one signed in
    mysql = connectToMySQL("users")
    all_users=mysql.query_db("SELECT *, Count(sender_id) AS amount_pokes FROM users LEFT JOIN pokes ON users.id = pokes.receiver_id WHERE users.id != "+str(session['user_id'])+" GROUP BY (users.id) ORDER BY COUNT(receiver_id) DESC;")
    mysql = connectToMySQL("users")
    pokes_total=mysql.query_db("SELECT COUNT(name) AS pokes_total FROM users JOIN pokes ON users.id = pokes.sender_id WHERE pokes.receiver_id="+str(session['user_id'])+";")
    #makes pokes_for_user which includes all the pokes sent to the current session user
    mysql = connectToMySQL("users")
    pokes_for_user=mysql.query_db("SELECT name, COUNT(name) AS pokes_from FROM users JOIN pokes ON users.id = pokes.sender_id WHERE pokes.receiver_id="+str(session['user_id'])+" GROUP BY(name) ORDER BY pokes_from DESC;")
    #makes poke_info which has pokes.id, pokes.sender_id, pokes.receiver_id, users.first_name as sender, pokes.poke, pokes.created_at joining pokes and users where the users.id and pokes.sender_id
    mysql = connectToMySQL("users")
    poke_info=mysql.query_db("SELECT pokes.id, pokes.sender_id, pokes.receiver_id, users.name AS sender, pokes.created_at FROM pokes JOIN users ON users.id = pokes.sender_id AND pokes.receiver_id= "+str(session['user_id'])+";")
    print("*"*100,all_users)
    if not pokes_from_user:
        session['sent_pokes']=0
    if pokes_from_user:
        session['sent_pokes']=len(pokes_from_user)
    if not pokes_for_user:
        session['received_pokes']=0
    if pokes_for_user:
        session['received_pokes']=len(pokes_for_user)
    if not pokes_total:
        session['pokes_total']=0
    if pokes_total:
        session['pokes_total']=pokes_total[0]['pokes_total']
    return render_template("pokes.html", user=one_user, sent_count=session['sent_pokes'], received_count=session['received_pokes'], pokes_total=session['pokes_total'], pokes_for_user=pokes_for_user, all_users=all_users, pokes=poke_info)
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
        return redirect("/main")
    if bcrypt.check_password_hash(one_user[0]['password'], request.form['user_pass']):
        if'user_id' not in session:
            session['user_id']=one_user[0]['id']
        else:
            session['user_id']=one_user[0]['id']
        return redirect("/pokes")
    flash("Sorry, you could not be logged in.")
    return redirect("/main")
@app.route("/send_poke", methods=['POST'])
def send_poke():
    print(request.form)
    mysql = connectToMySQL("users")
    query = "INSERT INTO pokes (poke, sender_id, receiver_id, created_at, updated_at) VALUES (%(poke)s, %(sender)s, %(receiver)s, NOW(), NOW());"
    data= {
        "poke": request.form["poke"],
        "sender": session['user_id'],
        "receiver": request.form["receiver_id"]
    }
    poke= mysql.query_db(query,data)
    return redirect("/pokes")
@app.route("/logout_user")
def logout_user():
    if 'user_id' in session:
        session.pop("user_id")
    flash("You've been logged out.")
    return redirect("/main")
@app.route("/delete/<id>")
def delete_poke(id):
    mysql = connectToMySQL("users")
    query=mysql.query_db("DELETE FROM pokes where id="+str(id)+";")
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