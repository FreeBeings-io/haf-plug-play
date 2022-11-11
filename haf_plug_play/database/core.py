import os
import psycopg2

from haf_plug_play.config import Config

config = Config.config

class DbSession:
    def __init__(self, app):
        self.app = app
        self.new_conn()
    
    def new_conn(self):
        self.conn = psycopg2.connect(
            host=config['db_host'],
            database=config['db_name'],
            user=config['db_username'],
            password=config['db_password'],
            connect_timeout=5,
            application_name=self.app,
            keepalives=1,
            keepalives_idle=5,
            keepalives_interval=2,
            keepalives_count=2
        )
        self.conn.autocommit = True

    def select(self, sql):
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
            res = cur.fetchall()
            cur.close()
        except Exception as e:
            print(e)
            print(f"SQL:  {sql}")
            self.conn.rollback()
            cur.close()
            raise Exception ('DB error occurred')
        if len(res) == 0:
            return None
        else:
            return res

    def select_one(self, sql):
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
            res = cur.fetchone()
            cur.close()
        except Exception as e:
            print(e)
            print(f"SQL:  {sql}")
            self.conn.rollback()
            cur.close()
            raise Exception ('DB error occurred')
        if len(res) == 0:
            return None
        else:
            return res[0]
    
    def select_exists(self, sql):
        res = self.select_one(f"SELECT EXISTS ({sql});")
        return res

    def execute(self, sql,  data=None):
        cur = self.conn.cursor()
        try:
            if data:
                cur.execute(sql, data)
            else:
                cur.execute(sql)
            cur.close()
        except psycopg2.OperationalError as err:
            if "connection" in err.args[0] and "closed" in err.args[0]:
                print(f"Connection lost. Reconnecting...")
                self.new_conn()
                cur = self.conn.cursor()
                if data:
                    cur.execute(sql, data)
                else:
                    cur.execute(sql)
                cur.close()
        except Exception as e:
            print(e)
            print(f"SQL:  {sql}")
            print(f"DATA:   {data}")
            self.conn.rollback()
            cur.close()
            raise Exception({'data': data, 'sql': sql})

    def commit(self):
        self.conn.commit()
    
    def is_open(self):
        return self.conn.closed == 0


class DbSetup:

    @classmethod
    def check_db(cls):
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