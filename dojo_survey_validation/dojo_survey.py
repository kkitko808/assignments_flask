from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL
app=Flask(__name__)
app.secret_key="ayy bruh lmao"
@app.route('/')
def index():
    return render_template("index.html")
@app.route('/result', methods=['POST'])
def create_user():
    is_valid = True
    if len(request.form['name'])<1:
        is_valid=False
        flash("Please enter a first name")
    if len(request.form['comment'])>120:
        is_valid=False
        flash("Please shorten your comment")
    if not is_valid:
        return redirect("/")

    #Selects language/location ID to put into dojo users rather than input them as the name
    mysql = connectToMySQL("dojo_users")
    query ="SELECT id FROM languages WHERE language = %(lg)s;"
    data= {
        "lg": request.form['language']
    }
    #Language_id is the ID of the language they selected
    language_id=mysql.query_db(query,data)
    mysql = connectToMySQL("dojo_users")
    query ="SELECT id FROM locations WHERE location = %(lc)s;"
    data= {
        "lc": request.form['location']
    }
    #Location_id is the ID of the location they selected
    location_id=mysql.query_db(query,data)
    

    mysql = connectToMySQL("dojo_users")
    query = "INSERT INTO dojo_users(name, locations_id, languages_id, comment, created_at, updated_at) VALUES(%(nm)s, %(lc)s, %(lg)s, %(cm)s, NOW(), NOW());"
    data= {
    "nm": request.form['name'],
    "lc": str(location_id[0]['id']),
    "lg": str(language_id[0]['id']),
    "cm": request.form['comment'],
    }
    user_id= mysql.query_db(query,data)
    mysql = connectToMySQL("dojo_users")
    #retrieve language, location, user_name and comment 
    mysql = connectToMySQL("dojo_users")
    user = mysql.query_db("SELECT languages.language, locations.location, dojo_users.name, dojo_users.comment FROM dojo_users.dojo_users JOIN dojo_users.languages ON dojo_users.languages.id= dojo_users.languages_id JOIN dojo_users.locations ON dojo_users.locations.id= dojo_users.dojo_users.locations_id WHERE dojo_users.dojo_users.id = "+str(user_id)+";")
    print(user_id)
    print(user)
    return render_template("result.html", user=user)    
if __name__=="__main__":
    app.run(debug=True)

# SELECT languages.language, locations.location, dojo_users.name, dojo_users.comment FROM dojo_users.dojo_users JOIN dojo_users.languages ON dojo_users.languages.id= dojo_users.languages_id JOIN dojo_users.locations ON dojo_users.locations.id= dojo_users.dojo_users.locations_id WHERE dojo_users.dojo_users.id = 1;
# user = mysql.query_db("SELECT * FROM dojo_users WHERE id ="+str(user_id)+";")