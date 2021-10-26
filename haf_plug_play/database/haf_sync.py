import os
import psycopg2

APPLICATION_CONTEXT = "plug_play"
BATCH_PROCESS_SIZE = 100000

config = {
    'db_username': 'postgres',
    'db_password': 'pass.word',
    'server_host': '127.0.0.0',
    'server_port': '8080',
    'ssl_cert': '',
    'ssl_key': ''
}

class DbSession:
    def __init__(self):
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
    def check_db(cls):
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
    
    @classmethod
    def prepare_global_data(cls):
        app_entry = db.select(f"SELECT 1 FROM public.apps WHERE app_name='global';")
        if app_entry is None:
            db.execute(
                """
                    INSERT INTO public.apps (app_name, op_ids, enabled)
                    VALUES ('global','{"follow", "community"}',true);
                """, None
            )

    @classmethod
    def prepare_app_data(cls):
        # prepare app data
        db = DbSession()
        exists = db.select(
            f"SELECT hive.app_context_exists( '{APPLICATION_CONTEXT}' );"
        )[0][0]
        print(exists)
        if exists == False:
            db.select(f"SELECT hive.app_create_context( '{APPLICATION_CONTEXT}' );")
            db.commit()
        # create table
        db.execute(
            f"""
                CREATE TABLE IF NOT EXISTS public.plug_play_ops(
                    id integer PRIMARY KEY,
                    block_num integer NOT NULL,
                    transaction_id char(40) NOT NULL,
                    req_auths json,
                    req_posting_auths json,
                    op_id varchar(128) NOT NULL,
                    op_json varchar(10192) NOT NULL
                )
                INHERITS( hive.{APPLICATION_CONTEXT} );
            """, None
        )
        db.execute(
            f"""
                CREATE INDEX IF NOT EXISTS custom_json_ops_ix_block_num
                ON public.plug_play_ops (block_num);
            """, None
        )
        db.execute(
            f"""
                CREATE INDEX IF  NOT EXISTS custom_json_ops_ix_op_id
                ON public.plug_play_ops (op_id);
            """, None
        )
        db.execute(
            f"""
                CREATE TABLE IF NOT EXISTS public.apps(
                    app_name varchar(32) PRIMARY KEY,
                    op_ids varchar(16)[],
                    last_updated timestamp DEFAULT NOW(),
                    enabled boolean
                );
            """, None
        )
        db.execute(
            f"""
                CREATE TABLE IF NOT EXISTS public.app_sync(
                    app_name varchar(32) NOT NULL REFERENCES apps (app_name),
                    latest_hive_rowid integer,
                    state_hive_rowid integer
                );
            """, None
        )
        db.execute(
            f"""
                CREATE TABLE IF NOT EXISTS public.global_props(
                    head_hive_rowid integer
                );
            """, None
        )
        db.execute(
            f"""
                INSERT INTO public.global_props (head_hive_rowid)
                SELECT '0'
                WHERE NOT EXISTS (SELECT * FROM public.global_props);
            """, None
        )
        db.commit()
        # create update ops functions
        db.execute(
            f"""
                CREATE OR REPLACE FUNCTION public.update_plug_play_ops( _first_block INT, _last_block INT )
                RETURNS void
                LANGUAGE plpgsql
                VOLATILE AS $function$
                    BEGIN
                        INSERT INTO public.plug_play_ops as ppops(
                            id, block_num, transaction_id, req_auths, req_posting_auths, op_id, op_json)
                        SELECT
                            ppov.id,
                            ppov.block_num,
                            encode(pptv.trx_hash::bytea,'escape'),
                            (ppov.body::json -> 'value' -> 'required_auths')::json,
                            (ppov.body::json -> 'value' -> 'required_posting_auths')::json,
                            ppov.body::json->'value'->>'id',
                            ppov.body::json->'value'->>'json'
                        FROM hive.{APPLICATION_CONTEXT}_operations_view ppov
                        JOIN hive.{APPLICATION_CONTEXT}_transactions_view pptv
                            ON ppov.block_num = pptv.block_num
                            AND ppov.trx_in_block = pptv.trx_in_block
                        WHERE ppov.block_num >= _first_block
                            AND ppov.block_num <= _last_block
                            AND ppov.op_type_id = 18;
                    UPDATE public.global_props
                        SET head_hive_rowid = (SELECT MAX(hive_rowid) FROM public.plug_play_ops);
                    END;
                    $function$
            """, None
        )
        db.commit()
        cls.conn.close()

db = DbSession()

def split(first, last, size):
    count = 0
    result = []
    for i in range(first, last+1):
        if i == last:
            result.append((_first, i))
        if count == 0:
            _first = i
        elif count == size:
            _last = i
            result.append((_first,_last))
            count = 0
            continue
        count += 1
    return result

def main_loop():
    while True:
        # get blocks range
        blocks_range = db.select(f"SELECT * FROM hive.app_next_block('{APPLICATION_CONTEXT}');")[0]
        print(f"Blocks range: {blocks_range}")
        if not blocks_range:
            continue
        (first_block, last_block) = blocks_range
        if not first_block:
            continue

        if (last_block - first_block) > 100:
            steps = split(first_block, last_block, BATCH_PROCESS_SIZE)
            for s in steps:
                db.select(f"SELECT hive.app_context_detach( '{APPLICATION_CONTEXT}' );")
                print("context detached")
                print(f"processing {s[0]} to {s[1]}")
                db.select(f"SELECT public.update_plug_play_ops( {s[0]}, {s[1]} );")
                print("batch sync done")
                db.select(f"SELECT hive.app_context_attach( '{APPLICATION_CONTEXT}', {s[1]} );")
                print("context attached again")
                db.commit()
                continue

        print(db.select(f"SELECT public.update_plug_play_ops( {first_block}, {last_block} );"))
        db.commit()


DbSetup.check_db()
DbSetup.prepare_app_data()
DbSetup.prepare_global_data()

if __name__ == "__main__":
    main_loop()