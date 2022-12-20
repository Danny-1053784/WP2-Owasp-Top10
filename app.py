import os.path

import sys

from flask import Flask, render_template, redirect , request, session ,url_for, abort


from lib.tablemodel import DatabaseModel
from lib.loginmodel import UserDatabaseModel
from lib.demodatabase import create_demo_database

# This demo glues a random database and the Flask framework. If the database file does not exist,
# a simple demo dataset will be created.
LISTEN_ALL = "0.0.0.0"
FLASK_IP = LISTEN_ALL
FLASK_PORT = 81
FLASK_DEBUG = True

app = Flask(__name__)
app.secret_key = "ImNotABigFanOfFlask69"
# This command creates the "<application directory>/databases/testcorrect_vragen.db" path
DATABASE_FILE = os.path.join(app.root_path, 'databases', 'testcorrect_vragen.db')
USER_DATABASE_FILE = os.path.join(app.root_path, 'databases', 'user_details.db')
# Check if the database file exists. If not, create a demo database
if not os.path.isfile(DATABASE_FILE):
    print(f"Could not find database {DATABASE_FILE}, creating a demo database.")
    create_demo_database(DATABASE_FILE)
dbm = DatabaseModel(DATABASE_FILE)
dbu = UserDatabaseModel(USER_DATABASE_FILE)

# Main route that shows a list of tables in the database
# Note the "@app.route" decorator. This might be a new concept for you.
# It is a way to "decorate" a function with additional functionality. You
# can safely ignore this for now - or look into it as it is a really powerful
# concept in Python.

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/")
def getListTables():
    tables = dbm.get_table_list()
    return render_template(
        "tables.html", table_list=tables, database_file=DATABASE_FILE
    )



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
        tables = dbm.get_table_list()
        rows, column_names = dbm.get_table_content(table_name)
        return render_template(
            "table_details.html", rows=rows, columns=column_names, table_name=table_name, table_list=tables
        )

#Null values overview
@app.route("/overview")
def error_overview():
    rows, column_names = dbm.show_errors()
    tables = dbm.get_table_list()
    return render_template("overview.html", rows=rows, columns=column_names,table_list=tables, table_name="")



#The table with filtered questions (Bryan)
@app.route("/bad_questions")
def bad_questions():
    rows, column_names = dbm.get_bad_questions()
    tables = dbm.get_table_list()
    return render_template(
        "bad_questions.html", rows=rows, columns=column_names,table_list=tables, table_name="")


@app.route("/invalid_objective")
def invalid_objectives():
    rows, column_names = dbm.get_invalid_objective()
    tables = dbm.get_table_list()
    return render_template(
        "invalid_objective.html", rows=rows, columns=column_names,table_list=tables, table_name="")



@app.route("/update_invalid_objectives/<vraag_id>", methods=['GET', 'POST'])
def update_invalid_objective(vraag_id):
    if request.method == 'GET':
        leerdoel = dbm.read_invalid_objective(vraag_id)
        leerdoelen = dbm.read_invalid_objective_update()
        leerdoelen_name = dbm.read_invalid_objective_name_update()
        tables = dbm.get_table_list()
        return render_template(
            "invalid_objective_update.html" , vraag_id=vraag_id, leerdoel=leerdoel , table_list=tables , leerdoelen=leerdoelen, leerdoelen_name=leerdoelen_name
        )
        # haal vraag info op en toon vraag detail pagina
    elif request.method == "POST":
        leerdoel = request.form['leerdoel']
        session['leerdoel_id'] = leerdoel
        leerdoel_id = dbm.read_objective_id()      
        dbm.update_invalid_objective( leerdoel_id, vraag_id)
        return redirect(f'/invalid_objective')


@app.route("/update_overview/<vraag_id>", methods=['GET', 'POST'])
def update_invalid_objectives2(vraag_id):
    if request.method == 'GET':
        leerdoel = dbm.read_invalid_objective(vraag_id)
        auteur = dbm.auteur(vraag_id)
        leerdoelen_name = dbm.read_invalid_objective_name_update()
        auteur_name = dbm.read_invalid_auteur_name_update()
        tables = dbm.get_table_list()
        return render_template(
            "overview_update.html" , vraag_id=vraag_id, leerdoel=leerdoel,table_list=tables, auteur=auteur, leerdoelen_name=leerdoelen_name, auteur_name = auteur_name)
        # haal vraag info op en toon vraag detail pagina
    elif request.method == "POST":
        leerdoel = request.form['leerdoel']
        auteur = request.form['auteur']
        dbm.update_overview_leerdoel(leerdoel, vraag_id)
        dbm.update_overview_auteur(auteur, vraag_id)
        return redirect(f'/overview')

#edit table (Bryan)
@app.route("/update/<vraag_id>", methods=['GET', 'POST'])
def update(vraag_id):
    if request.method == 'GET':
        vraag = dbm.read_question(vraag_id)
        tables = dbm.get_table_list()
        return render_template(
            "question_details.html" , vraag_id=vraag_id, vraag=vraag ,table_list=tables
        )
        # haal vraag info op en toon vraag detail pagina
    elif request.method == "POST":
        vraag = request.form['vraag']
        dbm.save_question(vraag, vraag_id)
        return redirect(f'/bad_questions')

# Login function with username session and redirect (Danny)
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(dbu.user_login(username, password))
        if dbu.user_login(username, password):
            session['username'] = username
            tables = dbm.get_table_list()
            return render_template(
            "tables.html", table_list=tables, database_file=DATABASE_FILE)
        else:
            return redirect(url_for('index'))

# Logout (Danny)
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#Redirect for logo
@app.route('/logoRedirect')
def logoRedirect():
    tables = dbm.get_table_list()
    return render_template(
    "tables.html", table_list=tables, database_file=DATABASE_FILE)


if __name__ == "__main__":
    app.run(host=FLASK_IP, port=FLASK_PORT, debug=FLASK_DEBUG)

#Function to show image (Danny) 
def ShowImage():    
 app = Flask(__name__, static_url_path='/static')
 return app

ShowImage()