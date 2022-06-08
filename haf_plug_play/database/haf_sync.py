import os
import time

from haf_plug_play.config import Config
from haf_plug_play.database.access import WriteDb
from haf_plug_play.database.core import DbSetup
from haf_plug_play.database.plug_sync import PlugSync
from haf_plug_play.server.system_status import SystemStatus
from haf_plug_play.utils.tools import range_split

APPLICATION_CONTEXT = "plug_play"
BATCH_PROCESS_SIZE = 100000

db = WriteDb().db
config = Config.config

class HafSyncSetup:
    """Setup functions for core schema."""
    
    @classmethod
    def prepare_global_data(cls):
        """Prepares global data."""
        app_entry = db.select("SELECT 1 FROM hpp.apps WHERE app_name='polls';")
        if app_entry is None:
            db.execute(
                """
                    INSERT INTO hpp.apps (app_name, op_ids, enabled)
                    VALUES ('polls','{"polls"}',true);
                """, None
            )

    @classmethod
    def prepare_app_data(cls):
        """Prepares app data."""
        exists = db.select(
            f"SELECT hive.app_context_exists( '{APPLICATION_CONTEXT}' );"
        )[0][0]
        if exists is False:
            db.select(f"SELECT hive.app_create_context( '{APPLICATION_CONTEXT}' );")
            db.commit()
            print(f"HAF SYNC:: created context: {APPLICATION_CONTEXT}")
            exists = db.select(
            f"SELECT hive.app_context_exists( '{APPLICATION_CONTEXT}' );"
            )[0][0]

        # create schema and tables
        db.execute(f"CREATE SCHEMA IF NOT EXISTS hpp;")

        db.execute(
            f"""
                CREATE TABLE IF NOT EXISTS hpp.plug_play_ops(
                    id BIGSERIAL PRIMARY KEY,
                    hive_opid BIGINT NOT NULL,
                    block_num INTEGER NOT NULL,
                    timestamp TIMESTAMP,
                    transaction_id VARCHAR,
                    req_auths JSON,
                    req_posting_auths JSON,
                    op_id VARCHAR(128) NOT NULL,
                    op_json VARCHAR NOT NULL
                )
                INHERITS( hive.{APPLICATION_CONTEXT} );
            """, None
        )
        db.execute(
            """
                CREATE INDEX IF NOT EXISTS custom_json_ops_ix_hive_opid
                ON hpp.plug_play_ops (hive_opid);
            """, None
        )
        db.execute(
            """
                CREATE INDEX IF NOT EXISTS custom_json_ops_ix_block_num
                ON hpp.plug_play_ops (block_num);
            """, None
        )
        db.execute(
            """
                CREATE INDEX IF  NOT EXISTS custom_json_ops_ix_op_id
                ON hpp.plug_play_ops (op_id);
            """, None
        )
        db.execute(
            """
                CREATE TABLE IF NOT EXISTS hpp.apps(
                    app_name varchar(32) PRIMARY KEY,
                    op_ids varchar(31)[],
                    last_updated timestamp DEFAULT NOW(),
                    enabled boolean
                );
            """, None
        )
        db.execute(
            """
                CREATE TABLE IF NOT EXISTS hpp.plug_sync(
                    plug_name varchar(16) NOT NULL,
                    latest_hive_opid bigint DEFAULT 0
                );
            """, None
        )
        db.execute(
            """
                CREATE TABLE IF NOT EXISTS hpp.global_props(
                    head_hive_opid bigint DEFAULT 0,
                    head_block_num bigint DEFAULT 0,
                    head_block_time timestamp
                );
            """, None
        )
        db.execute(
            """
                INSERT INTO hpp.global_props (head_hive_opid)
                SELECT '0'
                WHERE NOT EXISTS (SELECT * FROM hpp.global_props);
            """, None
        )
        db.commit()
        # create update ops function
        db.execute(
            """
                CREATE OR REPLACE FUNCTION hpp.update_plug_play_ops( _first_block BIGINT, _last_block BIGINT )
                RETURNS void
                LANGUAGE plpgsql
                VOLATILE AS $function$
                    DECLARE
                        temprow RECORD;
                        _hive_opid BIGINT;
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
                                ppov.id AS hive_opid,
                                ppov.block_num,
                                ppov.timestamp,
                                ppov.trx_in_block,
                                (ppov.body::json -> 'value' -> 'required_auths')::json AS required_auths,
                                (ppov.body::json -> 'value' -> 'required_posting_auths')::json AS required_posting_auths,
                                ppov.body::json->'value'->>'id' AS op_id,
                                ppov.body::json->'value'->>'json' AS op_json,
                                pptv.trx_hash
                            FROM hive.plug_play_operations_view ppov
                            LEFT JOIN hive.plug_play_transactions_view pptv
                                ON pptv.block_num = ppov.block_num
                                AND pptv.trx_in_block = ppov.trx_in_block
                            WHERE ppov.block_num >= _first_block
                                AND ppov.block_num <= _last_block
                                AND ppov.op_type_id = 18
                            ORDER BY ppov.block_num, ppov.id
                        LOOP
                            _hive_opid := temprow.hive_opid;
                            _block_num := temprow.block_num;
                            _block_timestamp = temprow.timestamp;
                            _required_auths := temprow.required_auths;
                            _required_posting_auths := temprow.required_posting_auths;
                            _op_id := temprow.op_id;
                            _op_json := temprow.op_json;
                            _hash := temprow.trx_hash;
                            INSERT INTO hpp.plug_play_ops as ppops(
                                hive_opid, block_num, timestamp, transaction_id, req_auths,
                                req_posting_auths, op_id, op_json)
                            VALUES
                                (_hive_opid, _block_num, _block_timestamp, _hash, _required_auths,
                                _required_posting_auths, _op_id, _op_json);
                        END LOOP;
                        UPDATE hpp.global_props SET (head_hive_opid, head_block_num, head_block_time) = (_hive_opid, _block_num, _block_timestamp);
                    END;
                    $function$;
            """, None
        )
        db.commit()

class HafSync:
    """Main HAF sync processes."""

    sync_enabled = False

    @classmethod
    def init(cls):
        """Initialize the class."""
        DbSetup.check_db()
        HafSyncSetup.prepare_app_data()
        HafSyncSetup.prepare_global_data()

    @classmethod
    def toggle_sync(cls, enabled=True):
        """Turns sync on and off."""
        cls.sync_enabled = enabled

    @classmethod
    def main_loop(cls):
        """Main application loop."""
        massive_sync = False
        config['global_start_block'] = int(config['global_start_block'])
        sleep_timer = 1
        while True:
            if cls.sync_enabled is True:
                # get blocks range
                try:
                    blocks_range = db.select(f"SELECT * FROM hive.app_next_block('{APPLICATION_CONTEXT}');")[0]
                except:
                    # reattach context
                    db_block = db.select("SELECT head_block_num FROM hpp.global_props")[0][0]
                    db.select(f"SELECT hive.app_context_attach( '{APPLICATION_CONTEXT}', {(db_block-1)} );")
                    blocks_range = db.select(f"SELECT * FROM hive.app_next_block('{APPLICATION_CONTEXT}');")[0]
                #print(f"Blocks range: {blocks_range}")
                (first_block, last_block) = blocks_range
                if not blocks_range:
                    time.sleep(0.2)
                    continue
                if not first_block:
                    time.sleep(0.2)
                    continue
                if (last_block - first_block) > 4:
                    # fast sync to catch up
                    sleep_timer = 0.1
                else:
                    sleep_timer = 0.25
                if blocks_range[0] < config['global_start_block']:
                    print(f"HAF SYNC:: starting from global_start_block: {config['global_start_block']}")
                    db.select(f"SELECT hive.app_context_detach( '{APPLICATION_CONTEXT}' );")
                    print("HAF SYNC:: context detached")
                    db.select(f"SELECT hive.app_context_attach( '{APPLICATION_CONTEXT}', {(config['global_start_block']-1)} );")
                    print("HAF SYNC:: context attached again")
                    blocks_range = db.select(f"SELECT * FROM hive.app_next_block('{APPLICATION_CONTEXT}');")[0]
                    print(f"HAF SYNC:: blocks range: {blocks_range}")
                    (first_block, last_block) = blocks_range
                    massive_sync = True

                if massive_sync:
                    print("HAF SYNC:: starting massive sync")
                    steps = range_split(first_block, last_block, BATCH_PROCESS_SIZE)
                    tot = last_block - first_block
                    db.select(f"SELECT hive.app_context_detach( '{APPLICATION_CONTEXT}' );")
                    for s in steps:
                        progress = int(((tot - (last_block - s[0])) / tot) * 100)
                        SystemStatus.update_sync_status(sync_status=f"Massive sync in progress: {s[0]} to {s[1]}    ({progress} %)")
                        try:
                            db.select(f"SELECT hpp.update_plug_play_ops( {s[0]}, {s[1]} );")
                            db.commit()
                            error = False
                        except:
                            error = True
                            db.conn.rollback()
                            rev_block = s[0] - 1
                            db.select(f"SELECT hive.app_context_attach( '{APPLICATION_CONTEXT}', {rev_block} );")
                    if not error:
                        db.select(f"SELECT hive.app_context_attach( '{APPLICATION_CONTEXT}', {s[1]} );")
                        print("HAF SYNC:: massive sync done")
                        massive_sync = False
                        PlugSync.toggle_plug_sync()
                    continue
                PlugSync.toggle_plug_sync(False)
                SystemStatus.update_sync_status(sync_status=f"Synchronizing: {first_block} to {last_block}")
                try:
                    db.select(f"SELECT hpp.update_plug_play_ops( {first_block}, {last_block} );")
                    db.commit()
                    SystemStatus.update_sync_status(sync_status=f"Synchronized... on block {last_block}")
                    PlugSync.toggle_plug_sync()
                except:
                    db.conn.rollback()
                    os._exit(1)
            time.sleep(sleep_timer)
