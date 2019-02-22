from flask import Flask, render_template,request, redirect, session, flash
from mysqlconnection import connectToMySQL
import re
app = Flask(__name__)
@app.route("/")
def index():
    mysql=connectToMySQL("lead_gen_business")
    users = mysql.query_db("SELECT ")
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)