import os.path

import sys
from flask import Flask, render_template, redirect , request, session ,url_for, abort, make_response
from io import StringIO
from flask_wtf import CSRFProtect

from lib.tablemodel import DatabaseModel
from lib.loginmodel import UserDatabaseModel
from lib.demodatabase import create_demo_database

# This demo glues a random database and the Flask framework. If the database file does not exist,
# a simple demo dataset will be created.
LISTEN_ALL = "0.0.0.0"
FLASK_IP = LISTEN_ALL
FLASK_PORT = 81
FLASK_DEBUG = True

import os
keycode = os.urandom(12).hex()

app = Flask(__name__)
app.secret_key = keycode
csrf = CSRFProtect(app)
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

#Login as landing page
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
    #If table is vragen show a different function that displays the id's for "leerdoel" and "auteur" as text (Danny)
    if table_name == "vragen":
        tables = dbm.get_table_list()
        rows, column_names = dbm.get_table_content_vragen()
        return render_template(
            "table_details.html", rows=rows, columns=column_names, table_name=table_name, table_list=tables
        )
    elif not table_name:
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

#Displays a list of all invalid objectives (Danny)
@app.route("/invalid_objective")
def invalid_objectives():
    rows, column_names = dbm.get_invalid_objective()
    tables = dbm.get_table_list()
    return render_template(
        "invalid_objective.html", rows=rows, columns=column_names,table_list=tables, table_name="")

#Displays a dropdown of all "leerdoelen" and updates it (Danny)
@app.route("/update_invalid_objectives/<vraag_id>", methods=['GET', 'POST'])
def update_invalid_objective(vraag_id):
    if request.method == 'GET':
        leerdoel = dbm.read_invalid_objective(vraag_id)
        vraag = dbm.read_question(vraag_id)
        leerdoelen = dbm.read_invalid_objective_update()
        leerdoelen_name = dbm.read_invalid_objective_name_update()
        tables = dbm.get_table_list()
        return render_template(
            "invalid_objective_update.html" , vraag_id=vraag_id, leerdoel=leerdoel , table_list=tables , leerdoelen=leerdoelen, leerdoelen_name=leerdoelen_name, vraag=vraag 
        )
        # Updates "leerdoel" with submit from the dropdown
    elif request.method == "POST":
        leerdoel = request.form['leerdoel']
        session['leerdoel_id'] = leerdoel
        leerdoel_id = dbm.read_objective_id()      
        dbm.update_invalid_objective( leerdoel_id, vraag_id)
        return redirect(f'/invalid_objective')


#read and update "Null" values with a dropdown (allows auteur and leerdoel to be updated at the same time) (Danny)
@app.route("/update_overview/<vraag_id>", methods=['GET', 'POST'])
def update_invalid_values(vraag_id):
    if request.method == 'GET':
        leerdoel = dbm.read_invalid_objective(vraag_id)
        auteur = dbm.auteur(vraag_id)
        vraag = dbm.read_question(vraag_id)
        leerdoelen_name = dbm.read_invalid_objective_name_update()
        auteur_name = dbm.read_invalid_auteur_name_update()
        tables = dbm.get_table_list()
        return render_template(
            "overview_update.html" , vraag_id=vraag_id, leerdoel=leerdoel,table_list=tables, auteur=auteur, leerdoelen_name=leerdoelen_name, auteur_name = auteur_name, vraag=vraag)
    # updates the leerdoel and auteur when both values are "Null" 
    if request.method == 'POST' and request.form.get('leerdoel') and request.form.get('auteur'):    
            leerdoel = request.form['leerdoel']
            auteur = request.form['auteur']
            session['leerdoel_overview_id'] = leerdoel
            session['auteur_overview_id'] = auteur
            read_objective_overview_id = dbm.read_objective_overview_id()  
            read_objective_auteur_id = dbm.read_auteur_overview_id()  
            dbm.update_invalid_objective(read_objective_overview_id, vraag_id)
            dbm.update_overview_auteur(read_objective_auteur_id, vraag_id)
            return redirect(f'/overview')
    # updates the leerdoel when value is "Null"  
    elif request.method == 'POST' and request.form.get('leerdoel'):
            leerdoel = request.form['leerdoel']
            session['leerdoel_overview_id'] = leerdoel
            read_objective_overview_id = dbm.read_objective_overview_id()  
            dbm.update_invalid_objective(read_objective_overview_id, vraag_id)
            return redirect(f'/overview')
    # updates the auteur when value is "Null"          
    elif request.method == 'POST' and request.form.get('auteur'):
            auteur = request.form['auteur']
            session['auteur_overview_id'] = auteur
            read_objective_auteur_id = dbm.read_auteur_overview_id()  
            dbm.update_overview_auteur(read_objective_auteur_id, vraag_id)
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
        # get info question and show question detail page
    elif request.method == "POST":
        vraag = request.form['vraag']
        dbm.save_question(vraag, vraag_id)
        return redirect(f'/table_details/vragen')

#redirect Delete question (Bryan)
@app.route("/delete_question")
def delete_question(id):
    rows, column_names = dbm.remove_delete_questions(id)
    tables = dbm.get_table_list()
    return render_template(
        "delete_question.html", rows=rows, columns=column_names,table_list=tables, table_name="")

#Delete question based on ID (Bryan)
@app.route("/delete/<id>", methods=['GET', 'POST'])
def delete(id):
    if request.method == 'GET':
        vraag = dbm.read_question(id)
        tables = dbm.get_table_list()
        return render_template(
            "delete_question.html" , vraag_id=id, vraag=vraag ,table_list=tables
        )
    elif request.method == "POST":
        dbm.remove_delete_questions(id)
        return redirect(f'/table_details/vragen')

#route where user can select what he wants to analyze
@app.route('/selection', methods = ["POST", "GET"])
def selection():
    tables = dbm.get_table_list()    
    return render_template("selection.html",table_list=tables, table_name="",)

#result of selection made by user 
@app.route('/confirmed_selection', methods = ["POST"])
def confirmed_selection():
    tables = dbm.get_table_list()
    selected_table = str(tables[int(request.form.get('first'))])
    session['sel_table'] = str(tables[int(request.form.get('first'))])
    selected_column = str(request.form.get('second'))
    session['sel_column'] = str(request.form.get('second'))
    value1 = str(request.form.get('value1'))
    session['v1'] = str(request.form.get('value1'))
    value2 = str(request.form.get('value2'))
    session['v2'] = str(request.form.get('value2'))

    rows, column_names = dbm.user_input_selection(selected_column, 
        selected_table, value1, value2)
    
    return render_template("confirmed_selection.html", rows=rows, 
        columns=column_names, table_name="", table_list=tables)

#route to download selection made by user as csv file
@app.route('/download_csv', methods = ["POST", "GET"])
def download_csv():
    tables = dbm.get_table_list()
    selected_table = session.get('sel_table')
    selected_column = session.get('sel_column')
    value1 = session.get('v1')
    value2 = session.get('v2')
    dbm.download_csv_selection(selected_column, selected_table, value1, value2)

    rows, column_names = dbm.user_input_selection(selected_column, 
        selected_table, value1, value2)

    return render_template("confirmed_selection.html", rows=rows, 
        columns=column_names, table_name="", table_list=tables)   

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

#Redirect for logo (Danny)
@app.route('/logoRedirect')
def logoRedirect():
    tables = dbm.get_table_list()
    return render_template(
    "tables.html", table_list=tables, database_file=DATABASE_FILE)

#changes column name 'met pensioen' if needed
def update_name_MetPensioen():
    dbm.update_name_MetPensioen()

if __name__ == "__main__":
    app.run(host=FLASK_IP, port=FLASK_PORT, debug=FLASK_DEBUG)

#Function to show image (Danny) 
def ShowImage():    
 app = Flask(__name__, static_url_path='/static')
 return app

ShowImage()