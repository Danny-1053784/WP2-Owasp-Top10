import os
import sqlite3
from flask import Flask, session 

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


    def show_errors(self):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute("SELECT * FROM vragen WHERE leerdoel IS NULL OR vraag IS NULL OR auteur IS NULL")
        # An alternative for this 2 var approach is to set a sqlite row_factory on the connection
        table_headers = [column_name[0] for column_name in cursor.description]
        table_content = cursor.fetchall()

        # Note that this method returns 2 variables!
        return table_content, table_headers
        

    def update_null_value_objective(self, vragen, id):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE leerdoel SET vragen = '{vragen}' WHERE id = {id}")
        conn.commit()
        return True

    def update_null_value_author(self, author, id):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE author SET vragen = '{author}' WHERE id = {id}")
        conn.commit()
        return True


    def get_bad_questions(self):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute("SELECT * FROM vragen WHERE vraag LIKE '%<br>%' OR vraag LIKE '%&nbsp%'")
        # An alternative for this 2 var approach is to set a sqlite row_factory on the connection
        table_headers = [column_name[0] for column_name in cursor.description]
        table_content = cursor.fetchall()

        # Note that this method returns 2 variables!
        return table_content, table_headers

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

    def update_overview_leerdoel(self, leerdoel, id):
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