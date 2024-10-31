import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

def connect_db():
    """
    Establishes a connection to the MySQL database for the university.
    
    Returns:
        db (mysql.connector.connection_cext.CMySQLConnection): A MySQL connection object that allows 
        interaction with the university database.
    
    Note:
        Ensure mysql.connector is installed and accessible before calling this function.
    """
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    passwd = os.getenv("DB_PASS")
    database = os.getenv("DB_NAME")
    

    if not all([host, user, passwd, database]):
        raise EnvironmentError("One or more required environment variables are missing.")
    
    db = mysql.connector.connect(
        host=host,
        user=user,
        passwd=passwd,
        database=database,
        autocommit=True
    )

    return db