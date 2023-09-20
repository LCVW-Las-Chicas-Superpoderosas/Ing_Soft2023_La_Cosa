import mysql.connector

DATABASE_URL = "localhost"
MYSQL_USER = 'root'

try:
    # Connect to MySQL server (assumes root user with no password)
    connection = mysql.connector.connect(
        host=DATABASE_URL,
        user=MYSQL_USER,
        passwd=MYSQL_USER)
    # Create a cursor object to execute SQL commands

    cursor = connection.cursor()
    # Create the database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS ing_2023")

    # Close the cursor and the connection
    cursor.close()
    connection.close()
except Exception as e:
    raise Exception(f"Error creating MySQL database: {e}")
