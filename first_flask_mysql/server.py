from flask import Flask, render_template,request, redirect, session, flash
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL    # import the function that will return an instance of a connection
app = Flask(__name__)
app.secret_key="this is a secret key lol"
bcrypt= Bcrypt(app)
@app.route("/")
def index():
    mysql = connectToMySQL('flask_friends')	        # call the function, passing in the name of our db
    friends = mysql.query_db('SELECT * FROM friends;')  # call the query_db function, pass in the query as a string
    print(friends)
    return render_template("index.html", all_friends= friends)
@app.route("/create_friend", methods=["POST"])
def add_friend_to_db():
    is_valid = True
    if len(request.form['fname'])<1:
        is_valid=False
        flash("Please enter a first name")
    if len(request.form['lname'])<1:
        is_valid=False
        flash("Please enter a last name")
    if len(request.form['occ'])<1:
        is_valid=False
        flash("Occupation should be at least 2 characters")
    if is_valid:
        mysql = connectToMySQL("flask_friends")
        query = "INSERT INTO friends (first_name, last_name, occupation, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(occup)s, NOW(), NOW());"
        data= {
            "fn": request.form["fname"],
            "ln": request.form["lname"],
            "occup": request.form["occ"]
        }
        new_friend_id = mysql.query_db(query, data)
        flash("Friend successfully added!")
    return redirect("/")
if __name__ == "__main__":
    app.run(debug=True)