import psycopg2

class DBConnection(object):

    def __init__(self, host, port, database, user, password):
        self.HOST = host
        self.PORT = port
        self.DATABASE = database
        self.USER = user
        self.PASSWORD = password

    def connect(self):
        connection = psycopg2.connect(host=self.HOST, port=self.PORT,
                    database=self.DATABASE, user=self.USER, password=self.PASSWORD)

        return connection


