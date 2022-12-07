import os.path

import sys

from flask import Flask, render_template, redirect , request,  url_for, abort

from lib.tablemodel import DatabaseModel
from lib.demodatabase import create_demo_database

# This demo glues a random database and the Flask framework. If the database file does not exist,
# a simple demo dataset will be created.
LISTEN_ALL = "0.0.0.0"
FLASK_IP = LISTEN_ALL
FLASK_PORT = 81
FLASK_DEBUG = True

app = Flask(__name__)
# This command creates the "<application directory>/databases/testcorrect_vragen.db" path
DATABASE_FILE = os.path.join(app.root_path, 'databases', 'testcorrect_vragen.db')

# Check if the database file exists. If not, create a demo database
if not os.path.isfile(DATABASE_FILE):
    print(f"Could not find database {DATABASE_FILE}, creating a demo database.")
    create_demo_database(DATABASE_FILE)
dbm = DatabaseModel(DATABASE_FILE)

# Main route that shows a list of tables in the database
# Note the "@app.route" decorator. This might be a new concept for you.
# It is a way to "decorate" a function with additional functionality. You
# can safely ignore this for now - or look into it as it is a really powerful
# concept in Python.

@app.route("/")
def index():
    return render_template("index.html")


#redirect to tables page (Danny)
@app.route("/")
def showTables():
    tables = dbm.get_table_list()
    return render_template(
        "tables.html", table_list=tables, database_file=DATABASE_FILE
    )

# The table route displays the content of a table
@app.route("/table_details/<table_name>")
def table_content(table_name=None):
    if not table_name:
        return "Missing table name", 400  # HTTP 400 = Bad Request
    else:
        rows, column_names = dbm.get_table_content(table_name)
        return render_template(
            "table_details.html", rows=rows, columns=column_names, table_name=table_name
        )

#The table with filtered questions (Bryan)
@app.route("/bad_questions")
def bad_questions():
    rows, column_names = dbm.get_bad_questions()
    return render_template(
        "table_details.html", rows=rows, columns=column_names, table_name="")


#edit table (Bryan)
@app.route("/update/<vraag_id>", methods=['GET', 'POST'])
def update(vraag_id):
    if request.method == 'GET':
        vraag = dbm.read_question(vraag_id)
        return render_template(
            "question_details.html" , vraag_id=vraag_id, vraag=vraag 
        )
        # haal vraag info op en toon vraag detail pagina
    elif request.method == "POST":
        my_data.vraag = request.form['vraag']
        my_data = Data.query.get(vraag_id) 
        db.session.commit()


#redirect for form login to tables page (when post is send go to showtables function )(Danny)
@app.route('/succesLogin', methods=['GET', 'POST'])
def succesLogin():
    if request.method == 'POST':
        return showTables()
    elif request.method == 'GET':
        return redirect('/')
    else:
        return 'Not a valid request method for this route'


if __name__ == "__main__":
    app.run(host=FLASK_IP, port=FLASK_PORT, debug=FLASK_DEBUG)

#Function to show image (Danny) 
def ShowImage():    
 app = Flask(__name__, static_url_path='/static')
 return app

ShowImage()