from dotenv import load_dotenv
import os
import psycopg2

class PostgreDjangoDB():
    def __init__(self):
        load_dotenv()
        self.connection = None
        self.cursor = None

    # Makes a connection and returns a cursor
    def connect(self):
        """
        Function makes a conenction to postgresql database
        with env variables. Returns a cursor.
        """
        user = os.getenv("DATABASE_USER_P")
        database = os.getenv("DATABASE_NAME_P")
        host = os.getenv("DATABASE_HOST_P")
        password = os.getenv("DATABASE_PASSWORD_P")

        self.connection = psycopg2.connect(user=user, password=password, host=host, database=database)
        self.cursor = self.connection.cursor()

        return self.cursor

    def save_and_close(self):
        self.connection.commit()
        self.connection.close()

    

if __name__ == "__main__":
    PostgreDjangoDB().connect()