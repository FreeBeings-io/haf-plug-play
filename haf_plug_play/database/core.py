import os
import psycopg2

class DbSession:
    def __init__(self, config):
        self.conn = psycopg2.connect(
            host=config['db_host'],
            database=config['db_name'],
            user=config['db_username'],
            password=config['db_password'],
            connect_timeout=3,
            keepalives=1,
            keepalives_idle=5,
            keepalives_interval=2,
            keepalives_count=2
        )
        self.conn.autocommit = False
        self.cur = self.conn.cursor()

    def select(self, sql):
        self.cur.execute(sql)
        res = self.cur.fetchall()
        if len(res) == 0:
            return None
        else:
            return res

    def execute_immediate(self, sql,  data):
        self.cur.execute(sql, data)
        self.conn.commit()

    def get_query(self,sql, data):
        return self.cur.mogrify(sql,data)

    def execute(self, sql, data):
        try:
            if data:
                self.cur.execute(sql, data)
            else:
                self.cur.execute(sql)

        except Exception as e:
            print(e)
            print(f"SQL:  {sql}")
            print(f"DATA:   {data}")
            self.conn.rollback()
            raise Exception ('DB error occurred')

    def commit(self):
        self.conn.commit()


class DbSetup:

    @classmethod
    def check_db(cls, config):
        try:
            cls.conn = psycopg2.connect(
            host=config['db_host'],
            database=config['db_name'],
            user=config['db_username'],
            password=config['db_password'],
            connect_timeout=3,
            keepalives=1,
            keepalives_idle=5,
            keepalives_interval=2,
            keepalives_count=2
        )
        except psycopg2.OperationalError as e:
            if config['db_name'] in e.args[0] and "does not exist" in e.args[0]:
                print(f"No database found. Please create a '{config['db_name']}' database in PostgreSQL.")
                os._exit(1)
            else:
                print(e)
                os._exit(1)