import os
import sqlite3
from typing import Optional, List, Dic

class Database:
    def __init__(self, db_path = "Data.db", schema_path = "Schema.sql"):
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
            Test the connection to the database and verify all required tables exist
        '''
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Check if all required tables exist
                required_tables = ['users', 'chat_sessions', 'messages']
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name IN (?, ?, ?)
                """, tuple(required_tables))
                existing_tables = {row[0] for row in cursor.fetchall()}
                missing_tables = set(required_tables) - existing_tables
                if missing_tables:
                    raise ConnectionError(f"ERROR: Missing required tables: {', '.join(missing_tables)}")
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
        if not query:
            return False
        try:
            '''
                备注：
                此处的sqlite.connect返回一个Connection对象，是一个上下文管理器(@contextmanager)
                with语句开始，将会开始一个隐式事务
                with语句结束，如果没有发生异常，将会自动提交事务；如果有异常，将会自动回滚事务；处理结束后自动关闭链接
            '''
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

    def execute_batch(self, queries: list[str], params: list[tuple]):
        '''
            Execute a batch of queries to the database
                dedicated for INSERT, UPDATE, DELETE queries
        '''
        if not queries:
            return False
        if len(queries) != len(params):
            raise ValueError("ERROR: The number of queries and parameters must be the same")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for i in range(len(queries)):
                    cursor.execute(queries[i], params[i])
                return True
        except Exception as e:
            raise RuntimeError(f"ERROR: Failed to execute batch queries: {str(e)}")