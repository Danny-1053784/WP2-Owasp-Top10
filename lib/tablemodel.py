import os
import sqlite3

import csv
from io import StringIO

from flask import Flask, session, make_response 

class DatabaseModel:
    """This class is a wrapper around the sqlite3 database. It provides a simple interface that maps methods
    to database queries. The only required parameter is the database file."""

    def __init__(self, database_file):
        self.database_file = database_file
        if not os.path.exists(self.database_file):
            raise FileNotFoundError(f"Could not find database file: {database_file}")

    # Using the built-in sqlite3 system table, return a list of all tables in the database
    def get_table_list(self):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        return tables

    # Given a table name, return the rows and column names
    def get_table_content(self, table_name):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(f"SELECT * FROM {table_name} ")
        # An alternative for this 2 var approach is to set a sqlite row_factory on the connection
        table_headers = [column_name[0] for column_name in cursor.description]
        table_content = cursor.fetchall()

        # Note that this method returns 2 variables!
        return table_content, table_headers

    #If table is vragen show a different function that displays the id's for "leerdoel" and "auteur" as text (Danny)
    def get_table_content_vragen(self ):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute("SELECT pt.id,pt.vraag,pb.leerdoel,pm.voornaam,pm.achternaam FROM `vragen`as pt LEFT JOIN `leerdoelen` as pb ON pt.leerdoel = pb.id LEFT JOIN `auteurs` as pm ON pt.auteur = pm.id")
        # An alternative for this 2 var approach is to set a sqlite row_factory on the connection
        table_headers = [column_name[0] for column_name in cursor.description]
        table_content = cursor.fetchall()

        # Note that this method returns 2 variables!
        return table_content, table_headers
    
    #Display all "vragen" where "leerdoel" or "auteur" is "Null"
    def show_errors(self):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute("SELECT * FROM vragen WHERE leerdoel IS NULL OR vraag IS NULL OR auteur IS NULL")
        # An alternative for this 2 var approach is to set a sqlite row_factory on the connection
        table_headers = [column_name[0] for column_name in cursor.description]
        table_content = cursor.fetchall()

        # Note that this method returns 2 variables!
        return table_content, table_headers

    def get_bad_questions(self):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute("SELECT * FROM vragen WHERE vraag LIKE '%<br>%' OR vraag LIKE '%&nbsp%'")
        # An alternative for this 2 var approach is to set a sqlite row_factory on the connection
        table_headers = [column_name[0] for column_name in cursor.description]
        table_content = cursor.fetchall()

        # Note that this method returns 2 variables!
        return table_content, table_headers

    def remove_delete_questions(self, id):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM vragen WHERE id ="+id)
        conn.commit()
        return True

    def read_question(self, id):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute("SELECT vraag FROM vragen WHERE id="+id)
        
        table_content = cursor.fetchone()[0]
       
        return table_content

    def save_question(self, vraag, id):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE vragen SET vraag = '{vraag}' WHERE id = {id}")
        conn.commit()
        return True

    def get_invalid_objective(self):
            cursor = sqlite3.connect(self.database_file).cursor()
            cursor.execute("SELECT * FROM vragen WHERE leerdoel NOT IN (SELECT id FROM leerdoelen)")
            # An alternative for this 2 var approach is to set a sqlite row_factory on the connection
            table_headers = [column_name[0] for column_name in cursor.description]
            table_content = cursor.fetchall()

            # Note that this method returns 2 variables!
            return table_content, table_headers

    def get_invalid_objective_update(self, id):
            cursor = sqlite3.connect(self.database_file).cursor()
            cursor.execute("SELECT leerdoel FROM leerdoelen WHERE id="+id)
            
            table_content = cursor.fetchone()[0]

            return table_content     

    def read_invalid_objective(self, id):
            cursor = sqlite3.connect(self.database_file).cursor()
            cursor.execute("SELECT leerdoel FROM vragen WHERE id="+id)
            
            table_content = cursor.fetchone()[0]
        
            return table_content

    def read_objective_id(self):
                cursor = sqlite3.connect(self.database_file).cursor()
                cursor.execute("SELECT id FROM leerdoelen WHERE leerdoel = ?", (session.get('leerdoel_id'),))
            
                table_content = cursor.fetchone()[0]
            
                return table_content

    def read_objective_overview_id(self):
                cursor = sqlite3.connect(self.database_file).cursor()
                cursor.execute("SELECT id FROM leerdoelen WHERE leerdoel = ?", (session.get('leerdoel_overview_id'),))
                
                table_content = cursor.fetchone()[0]
            
                return table_content

    def read_auteur_overview_id(self):
                cursor = sqlite3.connect(self.database_file).cursor()
                cursor.execute("SELECT id FROM auteurs WHERE achternaam = ?", (session.get('auteur_overview_id'),))
            
                table_content = cursor.fetchone()[0]
            
                return table_content

    def read_invalid_objective_update(self):
            cursor = sqlite3.connect(self.database_file).cursor()
            cursor.execute("SELECT id from leerdoelen group by id")

            table_content =[ table_content[0] for table_content in cursor.fetchall()]
            # Note that this method returns 2 variables!
            return table_content

    def read_invalid_objective_name_update(self):
            cursor = sqlite3.connect(self.database_file).cursor()
            cursor.execute("SELECT leerdoel,id from leerdoelen group by leerdoel")
           
            table_content =[ table_content[0] for table_content in cursor.fetchall()]
            # Note that this method returns 2 variables!
            return table_content
            
    def read_invalid_auteur_name_update(self):
            cursor = sqlite3.connect(self.database_file).cursor()
            cursor.execute("SELECT achternaam,id from auteurs")

            table_content =[ table_content[0] for table_content in cursor.fetchall()]
            # Note that this method returns 2 variables!
            return table_content            
                
    def update_invalid_objective(self, leerdoel, id):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE vragen SET leerdoel = '{leerdoel}' WHERE id = {id}")
        conn.commit()
        return True

    def update_overview_auteur(self, auteur, id):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE vragen SET auteur = '{auteur}' WHERE id = {id}")
        conn.commit()
        return True
        
    def auteur(self, id):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute("SELECT auteur FROM vragen WHERE id="+id)
    
        table_content = cursor.fetchone()[0]

        return table_content

    def update_name_MetPensioen(self):
    #changed column name 'met pensioen' to 'MetPensioen' because SQL has difficulties working with spaces in column names
        cursor_new_column = sqlite3.connect(self.database_file).cursor()
        cursor_new_column.execute("SELECT * FROM 'auteurs'")
        table_headers = [column_name[0] for column_name in cursor_new_column.description]
        if 'met pensioen' in table_headers:
            cursor_new_column.execute("ALTER TABLE 'auteurs' RENAME COLUMN 'met pensioen' to 'MetPensioen' ")
            cursor_new_column.fetchall()

    def user_input_selection(self, kolom, tabel, value1, value2):
        cursor = sqlite3.connect(self.database_file).cursor()
        
        if kolom in ['voornaam', 'achternaam']:
                value1 = value1.title()
                value2 = value2.title()

        if tabel == 'vragen':
            if kolom == 'leerdoel':
                kolom = 'pb.leerdoel'
            if kolom == 'id':
                kolom = 'pt.id'
            
            cursor.execute(f"SELECT pt.id,pt.vraag,pb.leerdoel,pm.voornaam,pm.achternaam FROM `vragen`as pt LEFT JOIN `leerdoelen` as pb ON pt.leerdoel = pb.id LEFT JOIN `auteurs` as pm ON pt.auteur = pm.id WHERE {kolom} BETWEEN '{value1}' and '{value2}' ORDER BY {kolom}")

        else:    
            cursor.execute(f"SELECT * FROM {tabel} WHERE {kolom} BETWEEN '{value1}' and '{value2}' ORDER BY {kolom}")

        table_headers = [column_name[0] for column_name in cursor.description]
        table_content = cursor.fetchall()

        return table_content, table_headers

    def download_csv_selection(self, kolom, tabel, value1, value2):
        
            si = StringIO()
            cw = csv.writer(si)

            
            cursor = sqlite3.connect(self.database_file).cursor()
            
            if kolom in ['voornaam', 'achternaam']:
                    value1 = value1.title()
                    value2 = value2.title()

            if tabel == 'vragen':
                if kolom == 'leerdoel':
                    kolom = 'pb.leerdoel'
                if kolom == 'id':
                    kolom = 'pt.id'
                
                cursor.execute(f"SELECT pt.id,pt.vraag,pb.leerdoel,pm.voornaam,pm.achternaam FROM `vragen`as pt LEFT JOIN `leerdoelen` as pb ON pt.leerdoel = pb.id LEFT JOIN `auteurs` as pm ON pt.auteur = pm.id WHERE {kolom} BETWEEN '{value1}' and '{value2}' ORDER BY {kolom}")

            else:    
                cursor.execute(f"SELECT * FROM {tabel} WHERE {kolom} BETWEEN '{value1}' and '{value2}' ORDER BY {kolom}")

            
            rows = cursor.fetchall()
            cw.writerow([column_name[0] for column_name in cursor.description])
            cw.writerows(rows)
            response = make_response(si.getvalue())
            return response

        