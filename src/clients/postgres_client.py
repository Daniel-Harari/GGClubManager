import psycopg2


class PGClient:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
    

    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def connect(self):
        self.connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.connection.cursor()

    def query(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def execute(self, query):
        self.cursor.execute(query)
        return self.cursor.rowcount

    def close(self):
        self.cursor.close()
        self.connection.close()

    def commit(self):
        self.connection.commit()

if __name__ == "__main__":
    with PGClient(
        host="sheepit.c7aqecseq98y.eu-central-1.rds.amazonaws.com",
        port=5432,
        user="sheepmaster",
        password="Ihatedavid321",
        database="postgres"
    ) as client:
        result = client.query(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE'
            AND table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name;
            """)
        print(result)
