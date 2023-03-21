import logging
import psycopg2 as postgres


# Import logger
log = logging.getLogger(__name__)


class PostgreSQLDB:
    def __init__(self, host, db_name, username, password):
        self.host = host
        self.db_name = db_name
        self.username = username
        self.password = password
        self._connect()

    def _connect(self):
        self.connection = postgres.connect(
            "host={} dbname={} user={} password={}".format(
                self.host, self.db_name, self.username, self.password
            )
        )
        self.cursor = self.connection.cursor()

    def close(self):
        self.cursor.close()
        self.connection.close()

    def run_query(self, query):
        self.cursor.execute(query)

    def fetch_results(self):
        return self.cursor.fetchall()

    def insert(self, insert_query, values_list):
        self.cursor.execute(insert_query, values_list)
        self.connection.commit()

    def commit(self):
        self.connection.commit()

    def get_all_databases(self):
        all_dbs_query = 'SELECT datname FROM pg_database ' \
                        'WHERE datistemplate = false'
        self.run_query(query=all_dbs_query)
        dbs = self.fetch_results()
        dbs_list = []
        for db_name in dbs:
            dbs_list.append(db_name[0])
        return dbs_list

    def get_all_tables(self):
        all_tables_query = "SELECT table_name FROM information_schema.tables " \
                           "WHERE table_schema = 'public'"
        self.run_query(query=all_tables_query)
        tables = self.fetch_results()
        tables_list = []
        for table in tables:
            tables_list.append(table[0])
        return tables_list

    def does_table_exist(self, table_name):
        tables_list = self.get_all_tables()
        if table_name in tables_list:
            return True
        else:
            return False

    def drop_table(self, table_name):
        self.cursor.execute('DROP TABLE {0}'.format(table_name))
