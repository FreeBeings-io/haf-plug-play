import time

from haf_plug_play.config import Config
from haf_plug_play.database.access import WriteDb
from haf_plug_play.database.core import DbSetup
from haf_plug_play.database.plug_sync import PlugSync
from haf_plug_play.server.system_status import SystemStatus
from haf_plug_play.utils.tools import range_split

APPLICATION_CONTEXT = "plug_play"
GLOBAL_START_BLOCK = 59913162
BATCH_PROCESS_SIZE = 100000

db = WriteDb().db
config = Config.config

class HafSyncSetup:
    
    @classmethod
    def prepare_global_data(cls):
        app_entry = db.select(f"SELECT 1 FROM public.apps WHERE app_name='polls';")
        if app_entry is None:
            db.execute(
                """
                    INSERT INTO public.apps (app_name, op_ids, enabled)
                    VALUES ('polls','{"polls"}',true);
                """, None
            )

    @classmethod
    def prepare_app_data(cls):
        # prepare app data
        exists = db.select(
            f"SELECT hive.app_context_exists( '{APPLICATION_CONTEXT}' );"
        )[0][0]
        print(exists)
        if exists == False:
            db.select(f"SELECT hive.app_create_context( '{APPLICATION_CONTEXT}' );")
            db.commit()
            print("Created context: plug_play")
            exists = db.select(
            f"SELECT hive.app_context_exists( '{APPLICATION_CONTEXT}' );"
            )[0][0]
            print(exists)
        # create table
        db.execute(
            f"""
                CREATE TABLE IF NOT EXISTS public.plug_play_ops(
                    id BIGSERIAL PRIMARY KEY,
                    block_num INTEGER NOT NULL,
                    timestamp TIMESTAMP,
                    transaction_id CHAR(40),
                    req_auths JSON,
                    req_posting_auths JSON,
                    op_id VARCHAR(128) NOT NULL,
                    op_json VARCHAR NOT NULL
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
                CREATE TABLE IF NOT EXISTS public.plug_sync(
                    plug_name varchar(16) NOT NULL,
                    latest_hive_rowid bigint DEFAULT 0,
                    state_hive_rowid bigint DEFAULT 0
                );
            """, None
        )
        db.execute(
            f"""
                CREATE TABLE IF NOT EXISTS public.global_props(
                    head_hive_rowid bigint DEFAULT 0,
                    head_block_num bigint DEFAULT 0,
                    head_block_time timestamp
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
        # create update ops function
        db.execute(
            f"""
                CREATE OR REPLACE FUNCTION public.update_plug_play_ops( _first_block BIGINT, _last_block BIGINT )
                RETURNS void
                LANGUAGE plpgsql
                VOLATILE AS $function$
                    DECLARE
                        temprow RECORD;
                        _id BIGINT;
                        _head_hive_rowid BIGINT;
                        _block_num INTEGER;
                        _block_timestamp TIMESTAMP;
                        _required_auths JSON;
                        _required_posting_auths JSON;
                        _op_id VARCHAR;
                        _op_json VARCHAR;
                        _hash VARCHAR;
                        _transaction_id VARCHAR(40);
                    BEGIN
                        FOR temprow IN
                            SELECT
                                ppov.id,
                                ppov.id AS head_hive_rowid,
                                ppov.block_num,
                                ppov.timestamp,
                                ppov.trx_in_block,
                                (ppov.body::json -> 'value' -> 'required_auths')::json AS required_auths,
                                (ppov.body::json -> 'value' -> 'required_posting_auths')::json AS required_posting_auths,
                                ppov.body::json->'value'->>'id' AS op_id,
                                ppov.body::json->'value'->>'json' AS op_json
                            FROM hive.plug_play_operations_view ppov
                            WHERE ppov.block_num >= _first_block
                                AND ppov.block_num <= _last_block
                                AND ppov.op_type_id = 18
                            ORDER BY ppov.block_num, ppov.id
                        LOOP
                            _id := temprow.id;
                            _block_num := temprow.block_num;
                            _head_hive_rowid = temprow.head_hive_rowid;
                            _block_timestamp = temprow.timestamp;
                            _required_auths := temprow.required_auths;
                            _required_posting_auths := temprow.required_posting_auths;
                            _op_id := temprow.op_id;
                            _op_json := temprow.op_json;
                            _hash := (
                                SELECT pptv.trx_hash FROM hive.plug_play_transactions_view pptv
                                WHERE pptv.block_num = temprow.block_num
                                AND pptv.trx_in_block = temprow.trx_in_block);
                            _transaction_id := encode(_hash::bytea, 'escape');
                            INSERT INTO public.plug_play_ops as ppops(
                                id, block_num, timestamp, transaction_id, req_auths,
                                req_posting_auths, op_id, op_json)
                            VALUES
                                (_id, _block_num, _block_timestamp, _transaction_id, _required_auths,
                                _required_posting_auths, _op_id, _op_json);
                        END LOOP;
                        UPDATE global_props SET (head_hive_rowid, head_block_num, head_block_time) = (_head_hive_rowid, _block_num, _block_timestamp);
                    END;
                    $function$;
            """, None
        )
        db.commit()

class HafSync:

    sync_enabled = False
    
    @classmethod
    def init(cls):
        DbSetup.check_db(config)
        HafSyncSetup.prepare_app_data()
        HafSyncSetup.prepare_global_data()
    
    @classmethod
    def toggle_sync(cls, enabled=True):
        cls.sync_enabled = enabled

    @classmethod
    def main_loop(cls):
        while True:
            if cls.sync_enabled is True:
                # get blocks range
                blocks_range = db.select(f"SELECT * FROM hive.app_next_block('{APPLICATION_CONTEXT}');")[0]
                #print(f"Blocks range: {blocks_range}")
                PlugSync.toggle_sync()
                if not blocks_range:
                    time.sleep(0.5)
                    continue
                (first_block, last_block) = blocks_range
                if not first_block:
                    time.sleep(0.5)
                    continue
                if blocks_range[0] < GLOBAL_START_BLOCK:
                    db.select(f"SELECT hive.app_context_detach( '{APPLICATION_CONTEXT}' );")
                    db.select(f"SELECT hive.app_context_attach( '{APPLICATION_CONTEXT}', {(GLOBAL_START_BLOCK-1)} );")
                    blocks_range = db.select(f"SELECT * FROM hive.app_next_block('{APPLICATION_CONTEXT}');")[0]

                if (last_block - first_block) > 100:
                    PlugSync.toggle_sync(False)
                    steps = range_split(first_block, last_block, BATCH_PROCESS_SIZE)
                    for s in steps:
                        db.select(f"SELECT hive.app_context_detach( '{APPLICATION_CONTEXT}' );")
                        print("context detached")
                        print(f"processing {s[0]} to {s[1]}")
                        progress = round(((s[0]/last_block) * 100),2)
                        SystemStatus.update_sync_status(sync_status=f"Massive sync in progress: {s[0]} to {s[1]}    ({progress} %)")
                        db.select(f"SELECT public.update_plug_play_ops( {s[0]}, {s[1]} );")
                        print("batch sync done")
                        db.select(f"SELECT hive.app_context_attach( '{APPLICATION_CONTEXT}', {s[1]} );")
                        print("context attached again")
                        db.commit()
                    continue
                SystemStatus.update_sync_status(sync_status=f"Synchronizing: {first_block} to {last_block}")
                db.select(f"SELECT public.update_plug_play_ops( {first_block}, {last_block} );")
                SystemStatus.update_sync_status(sync_status=f"Synchronized... on block {last_block}")
                db.commit()
            time.sleep(0.5)



if __name__ == "__main__":
    HafSync.init()
    HafSync.toggle_sync()
    HafSync.main_loop()
