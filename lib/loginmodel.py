import os
import sqlite3


class UserDatabaseModel:
    """This class is a wrapper around the sqlite3 database. It provides a simple interface that maps methods
    to database queries. The only required parameter is the database file."""

    def __init__(self, user_database_file):
        self.user_database_file = user_database_file
        if not os.path.exists(self.user_database_file):
            raise FileNotFoundError(f"Could not find database file: {user_database_file}")

    # Login function (Danny)  
    def user_login(self,username, password):
            con = sqlite3.connect(self.user_database_file)
            cur = con.cursor()
            cur.execute('Select username,password FROM user WHERE username=? and password=?', (username, password))
            
            result = cur.fetchone()
            if result:
            # checks to see if user exists in db (shows in terminal)
                return True
            else:
                return False

