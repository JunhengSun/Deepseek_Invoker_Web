import os
import sqlite3
from typing import Optional, List, Dict

class Database:
    def __init__(self, db_path = "Database.db", schema_path = "Schema.sql"):
        self.db_path = db_path
        self.schema_path = schema_path
        if not self.db_path or not self.schema_path:
            raise ValueError("ERROR: Database path or schema path is not set")
        self._init_database()
    
    def _init_database(self):
        '''
            Initialize the database
                1. if the database exists, test the connection
                2. if the database does not exist, create the database
        '''
        if os.path.exists(self.db_path):
            self._test_connection()
        else:
            self._create_database()

    def _test_connection(self) -> bool:
        '''
            Test the connection to the database
        '''
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # TODO: need a more specific test
                cursor.execute("SELECT 1") 
                return True
        except Exception as e:
            raise ConnectionError(f"ERROR: Failed to connect to the database: {str(e)}")

    def _create_database(self) -> bool:
        '''
            create the database
        '''
        try:
            with sqlite3.connect(self.db_path) as conn:
                with open(self.schema_path, "r", encoding="utf-8") as f:
                    schema = f.read()
                conn.executescript(schema)
                return True
        except Exception as e:
            raise RuntimeError(f"ERROR: Failed to create database: {str(e)}") 
    
    def execute(self, query: str, params: Optional[tuple] = None, fetchone: Optional[bool] = False, fetchall: Optional[bool] = False):
        '''
            Execute a query to the database
                Return Type:
                1. cursor.fetchone() if fetchone is True
                2. cursor.fetchall() if fetchall is True
                3. True if the query is successful, otherwise raise an exception
        '''
        try:
            with sqlite3.connect(self.db_path) as conn:
                # set to row factory
                conn.row_factory = sqlite3.Row

                # execute the query
                cursor = conn.cursor()
                cursor.execute(query, params)

                # return result(s)
                if fetchone:
                    return cursor.fetchone()
                elif fetchall:
                    return cursor.fetchall()
                return True
        except Exception as e:
            raise RuntimeError(f"ERROR: Failed to execute query: {str(e)}")
        

            
            
            
            


        

    

        