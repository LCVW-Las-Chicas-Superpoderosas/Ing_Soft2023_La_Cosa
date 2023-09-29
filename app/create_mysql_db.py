import mysql.connector
from constants import DATABASE_URL, MYSQL_PASS, MYSQL_USER



def create_database(database):
    try:
        # Connect to MySQL server (assumes root user with no password)
        connection = mysql.connector.connect(
            host=DATABASE_URL,
            user=MYSQL_USER,
            passwd=MYSQL_PASS)

        # Create a cursor object to execute SQL commands
        cursor = connection.cursor()

        # Create the database if it doesn't exist
        cursor.execute(f'CREATE DATABASE IF NOT EXISTS {database}')

        # Close the cursor and the connection
        cursor.close()
        connection.close()
    except Exception as e:
        raise Exception(f'Error creating MySQL database: {e}')


if __name__ == '__main__':
    create_database('ing_2023')
