import os
import psycopg2

class DbSession:
    def __init__(self, config):
        # TODO: retrieve from env_variables
        self.conn = psycopg2.connect(f"dbname=haf user={config['db_username']} password={config['db_password']}")
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
        # check if it exists
        try:
            # TODO: retrieve authentication from config 
            cls.conn = psycopg2.connect(f"dbname=haf user={config['db_username']} password={config['db_password']}")
        except psycopg2.OperationalError as e:
            if "haf" in e.args[0] and "does not exist" in e.args[0]:
                print("No database found. Please create a 'haf' database in PostgreSQL.")
                os._exit(1)
            else:
                print(e)
                os._exit(1)