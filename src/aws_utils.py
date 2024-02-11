import pymysql
from typing import Tuple
import os
from dotenv import load_dotenv
load_dotenv()


def connect_to_database() -> Tuple[pymysql.Connection, pymysql.Connection.cursor]:
    """
    Connect to the database
    
    Returns:
        pymysql.Connection: The connection object
        pymysql.Connection.cursor: The cursor object
    """
    try:
        conn = pymysql.connect(
            host = os.getenv("DB_HOST"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASS"),
            database = os.getenv("DB_NAME"),
            port = int(os.getenv("DB_PORT"))
        )
        return conn, conn.cursor()
    except Exception as e:
        print(f"Database connection failed due to {e}")
        return None, None


def query_db(cursor: pymysql.Connection.cursor, query: str) -> tuple:
    """
    Query the database

    Args:
        cursor (pymysql.Connection.cursor): The connection object
        query (str): The query to execute

    Returns:
        list: The results of the query
    """
    try:
        # Execute a query
        cursor.execute(query)
        # Fetch the results
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Query failed due to {e}")
        return None

    

if __name__ == "__main__":
    conn, cursor = connect_to_database()
    query = "SELECT * FROM raw_paragraphs"
    records = query_db(cursor, query)
    print(type(records))
    print(len(records))
    print(records[0])
    cursor.close()
    conn.close()
    # Figure out the best way to combine the location and time data into the string. maybe just do + " Location: {location}, Month: {month}, Year: {year}"
