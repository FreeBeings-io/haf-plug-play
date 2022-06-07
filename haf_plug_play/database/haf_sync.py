import os
import time

from haf_plug_play.config import Config
from haf_plug_play.database.core import DbSession
from haf_plug_play.server.system_status import SystemStatus
from haf_plug_play.tools import range_split

APPLICATION_CONTEXT = "plug_play"
BATCH_PROCESS_SIZE = 100000
SOURCE_DIR = os.path.dirname(__file__) + "/sql"

config = Config.config


class HafSync:
    """Main HAF sync processes."""

    sync_enabled = False
    massive_sync_done = False

    @classmethod
    def init(cls):
        cls.sync_enabled = False
        cls.db = DbSession()
        cls.prepare_app_data()
        cls.setup_db()

    @classmethod
    def prepare_app_data(cls):
        exists = cls.db.select(
            f"SELECT hive.app_context_exists( '{APPLICATION_CONTEXT}' );"
        )[0][0]

        if exists is False:
            cls.db.select(f"SELECT hive.app_create_context( '{APPLICATION_CONTEXT}' );")
            cls.db.commit()
            print(f"HAF SYNC:: created context: '{APPLICATION_CONTEXT}'")
            exists = cls.db.select(
            f"SELECT hive.app_context_exists( '{APPLICATION_CONTEXT}' );"
            )[0][0]
        

    @classmethod
    def setup_db(cls):
        tables = open(f'{SOURCE_DIR}/tables.sql', 'r').read()
        functions = open(f'{SOURCE_DIR}/functions.sql', 'r').read()
        cls.db.execute(tables, None)
        cls.db.execute(functions, None)
        cls.db.execute(
            """
                INSERT INTO hpp.global_props (latest_block_num)
                SELECT '0'
                WHERE NOT EXISTS (SELECT * FROM hpp.global_props);
            """, None
        )
        cls.db.commit()

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
                blocks_range = cls.db.select(f"SELECT * FROM hive.app_next_block('{APPLICATION_CONTEXT}');")[0]
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
                    cls.db.select(f"SELECT hive.app_context_detach( '{APPLICATION_CONTEXT}' );")
                    print("HAF SYNC:: context detached")
                    cls.db.select(f"SELECT hive.app_context_attach( '{APPLICATION_CONTEXT}', {(config['global_start_block']-1)} );")
                    print("HAF SYNC:: context attached again")
                    blocks_range = cls.db.select(f"SELECT * FROM hive.app_next_block('{APPLICATION_CONTEXT}');")[0]
                    print(f"HAF SYNC:: blocks range: {blocks_range}")
                    (first_block, last_block) = blocks_range
                    massive_sync = True

                if massive_sync:
                    print("HAF SYNC:: starting massive sync")
                    steps = range_split(first_block, last_block, BATCH_PROCESS_SIZE)
                    tot = last_block - first_block
                    cls.db.select(f"SELECT hive.app_context_detach( '{APPLICATION_CONTEXT}' );")
                    for s in steps:
                        progress = int(((tot - (last_block - s[0])) / tot) * 100)
                        SystemStatus.update_sync_status(sync_status=f"Massive sync in progress: {s[0]} to {s[1]}    ({progress} %)")
                        try:
                            cls.db.select(f"SELECT hpp.update_ops( {s[0]}, {s[1]} );")
                            cls.db.commit()
                            error = False
                        except:
                            error = True
                            cls.db.conn.rollback()
                            rev_block = s[0] - 1
                            cls.db.select(f"SELECT hive.app_context_attach( '{APPLICATION_CONTEXT}', {rev_block} );")
                    if not error:
                        cls.db.select(f"SELECT hive.app_context_attach( '{APPLICATION_CONTEXT}', {s[1]} );")
                        print("HAF SYNC:: massive sync done")
                        massive_sync = False
                        cls.massive_sync_done = True
                    continue
                else:
                    cls.massive_sync_done = True
                SystemStatus.update_sync_status(sync_status=f"Synchronizing: {first_block} to {last_block}")
                try:
                    cls.db.select(f"SELECT hpp.update_ops( {first_block}, {last_block} );")
                    cls.db.commit()
                    SystemStatus.update_sync_status(sync_status=f"Synchronized... on block {last_block}")
                except:
                    cls.db.conn.rollback()
                    os._exit(1)
            time.sleep(sleep_timer)
