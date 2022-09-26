import json
import os
import re
from threading import Thread
from haf_plug_play.database.core import DbSession
from haf_plug_play.database.plugs import AvailablePlugs, Plug
from haf_plug_play.config import Config

from haf_plug_play.tools import INSTALL_DIR

SOURCE_DIR = os.path.dirname(__file__) + "/sql"

MAIN_CONTEXT = "hpp"

config = Config.config

class Haf:

    db = DbSession("hpp-main")
    plug_list = []

    @classmethod
    def _is_valid_plug(cls, module):
        return bool(re.match(r'^[a-z]+[_]*$', module))

    @classmethod
    def _check_context(cls, name, start_block=None):
        exists = cls.db.select_one(
            f"SELECT hive.app_context_exists( '{name}' );"
        )
        if exists is False:
            cls.db.select(f"SELECT hive.app_create_context( '{name}' );")
            if start_block is not None:
                cls.db.select(f"SELECT hive.app_context_detach( '{name}' );")
                cls.db.select(f"SELECT hive.app_context_attach( '{name}', {(start_block-1)} );")
            cls.db.commit()
            print(f"HAF SYNC:: created context: '{name}'")
    
    @classmethod
    def _check_schema(cls, plug, tables):
        exists = cls.db.select(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name='{plug}';")
        if exists is None:
            cls.db.execute(tables, None)
            cls.db.commit()
    
    @classmethod
    def _update_functions(cls, functions):
        cls.db.execute(functions, None)
        cls.db.commit()
    
    @classmethod
    def _check_defs(cls, plug, defs):
        _block = defs['props']['start_block'] - 1
        has = cls.db.select_exists(f"SELECT plug FROM hpp.plug_state WHERE plug='{plug}'")
        # generate used op type ids array
        _op_ids = []
        for op in defs['ops'].keys():
            _op_ids.append(op)
        defs['op_ids'] = _op_ids
        defs['props']['enabled'] = plug in config['plugs']
        if has is False:
            cls.db.execute(
                f"""
                    INSERT INTO hpp.plug_state (plug, defs, latest_block_num, enabled)
                    VALUES ('{plug}', '{json.dumps(json.dumps(defs))}', {_block}, {defs['props']['enabled']});
                """)
        else:
            cls.db.execute(
                f"""
                    UPDATE hpp.plug_state SET defs='{json.dumps(defs)}', enabled={defs['props']['enabled']} WHERE plug='{plug}';
                """
            )
        return defs

    @classmethod
    def _init_plugs(cls):
        working_dir = f'{INSTALL_DIR}/plugs'
        cls.plug_list = [f.name for f in os.scandir(working_dir) if cls._is_valid_plug(f.name)]
        for plug in cls.plug_list:
            defs = json.loads(open(f'{working_dir}/{plug}/defs.json', 'r', encoding='UTF-8').read())
            functions = open(f'{working_dir}/{plug}/functions.sql', 'r', encoding='UTF-8').read()
            tables = open(f'{working_dir}/{plug}/tables.sql', 'r', encoding='UTF-8').read()
            updated_defs = cls._check_defs(plug, defs)
            if updated_defs['props']['enabled'] is True:
                cls._check_schema(plug, tables)
                cls._update_functions(functions)
                AvailablePlugs.add_plug(plug, Plug(plug, updated_defs))

    @classmethod
    def _init_hpp(cls):
        cls._check_context(MAIN_CONTEXT)
        tables = open(f'{SOURCE_DIR}/tables.sql', 'r', encoding='UTF-8').read()
        functions = open(f'{SOURCE_DIR}/functions.sql', 'r', encoding='UTF-8').read()
        sync = open(f'{SOURCE_DIR}/sync.sql', 'r', encoding='UTF-8').read()
        cls.db.execute(tables)
        cls.db.execute(functions)
        cls.db.execute(sync)
        cls.db.execute(
            """
                INSERT INTO hpp.global_props (sync_enabled)
                SELECT 'true'
                WHERE NOT EXISTS (SELECT * FROM hpp.global_props);
            """, None
        )
        cls.db.commit()

    @classmethod
    def _start_sync(cls):
        print("Starting main sync process...")
        cls.db.execute(f"CALL hpp.sync_main();")

    @classmethod
    def init(cls):
        cls._init_hpp()
        cls._init_plugs()
        Thread(target=cls._start_sync).start()