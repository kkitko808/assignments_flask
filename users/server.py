from flask import Flask, render_template,request, redirect
from mysqlconnection import connectToMySQL    # import the function that will return an instance of a connection
app = Flask(__name__)
app.secret_key="this key is secret"
@app.route("/users")
def index():
    mysql = connectToMySQL('users')	        # call the function, passing in the name of our db
    users = mysql.query_db('SELECT * FROM users;')  # call the query_db function, pass in the query as a string
    return render_template("index.html", all_users= users)
@app.route("/users/new")
def new_user():
    return render_template("create.html")
@app.route("/user_create", methods=["POST"])
def add_user_to_db():
    mysql = connectToMySQL("users")
    query = "INSERT INTO users (first_name, last_name, email, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(em)s, NOW(), NOW());"
    data= {
        "fn": request.form["fname"],
        "ln": request.form["lname"],
        "em": request.form['email']
    }
    new_user_id = mysql.query_db(query, data)
    return redirect("/users/"+str(new_user_id))
@app.route("/user_update/<id>", methods=["POST"])
def modify(id):
    mysql = connectToMySQL("users")
    query = "UPDATE users SET first_name=%(fn)s, last_name=%(ln)s, email=%(ln)s, updated_at=NOW() WHERE users.id= %(id)s;"
    data= {
        "id": id,
        "fn": request.form["fname"],
        "ln": request.form["lname"],
        "em": request.form['email']
    }
    new_user_id = mysql.query_db(query, data)
    return redirect(f"/users/{id}")
@app.route("/users/<id>")
def user_show(id):
    mysql = connectToMySQL("users")
    one_user=mysql.query_db("SELECT * FROM users where id = "+str(id)+";")
    return render_template("show.html", user=one_user)
@app.route("/users/delete/<num>")
def delete(num):
    mysql = connectToMySQL("users")
    mysql.query_db("DELETE FROM users WHERE (id ="+str(num)+ ");")
    return redirect("/users")
@app.route("/users/update/<id>")
def mod_field(id):
    mysql = connectToMySQL("users")
    user=mysql.query_db("SELECT * FROM users where id = "+str(id)+";")
    return render_template("update.html", user=user)

if __name__ == "__main__":
    app.run(debug=True)