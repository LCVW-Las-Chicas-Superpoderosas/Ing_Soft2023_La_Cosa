import mysql.connector
from constants import DATABASE_URL, DATABASE_NAME, MYSQL_USER, MYSQL_PASS


def drop_database():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host=DATABASE_URL,
            user=MYSQL_USER,
            passwd=MYSQL_PASS)

        # Create a cursor object to execute SQL commands
        cursor = connection.cursor()

        # Drop Database
        cursor.execute(f'DROP DATABASE {DATABASE_NAME}')

        # Close the cursor and the connection
        cursor.close()
        connection.close()
    except Exception as e:
        raise Exception(f'Error dropping MySQL database: {e}')


if __name__ == '__main__':
    drop_database()
