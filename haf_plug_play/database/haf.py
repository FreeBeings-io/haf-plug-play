import json
import os
import re
from threading import Thread
from haf_plug_play.database.core import DbSession
from haf_plug_play.database.plugs import AvailablePlugs, Plug
from haf_plug_play.config import Config

from haf_plug_play.tools import INSTALL_DIR, get_plug_list, schemafy

SOURCE_DIR = os.path.dirname(__file__) + "/sql"

config = Config.config

class Haf:

    db = DbSession(f"{config['schema']}-setup")
    plug_list = []

    @classmethod
    def _is_valid_plug(cls, module):
        return bool(re.match(r'^[a-z]+[_]*[a-z]*', module))
    
    @classmethod
    def _check_schema(cls, plug, tables):
        exists = cls.db.select(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name='{config['schema']}_{plug}';")
        if exists is None:
            cls.db.execute(f"CREATE SCHEMA IF NOT EXISTS {config['schema']}_{plug}")
            cls.db.execute(tables, None)
            cls.db.commit()
    
    @classmethod
    def _update_functions(cls, functions):
        cls.db.execute(functions, None)
        cls.db.commit()
    
    @classmethod
    def _check_defs(cls, plug, defs):
        _block = defs['props']['start_block'] - 1
        has = cls.db.select_exists(f"SELECT plug FROM {config['schema']}.plug_state WHERE plug='{plug}'")
        # generate used op type ids array
        _op_ids = []
        for op in defs['ops'].keys():
            _op_ids.append(op)
            defs['ops'][op] = defs['ops'][op].replace(f"{plug}.", f"{config['schema']}_{plug}.")
        defs['op_ids'] = _op_ids
        defs['props']['enabled'] = plug in config['plugs']
        if has is False:
            cls.db.execute(
                f"""
                    INSERT INTO {config['schema']}.plug_state (plug, defs, latest_block_num, enabled)
                    VALUES ('{plug}', '{json.dumps(defs)}', {_block}, {defs['props']['enabled']});
                """)
        else:
            cls.db.execute(
                f"""
                    UPDATE {config['schema']}.plug_state SET defs='{json.dumps(defs)}', enabled={defs['props']['enabled']} WHERE plug='{plug}';
                """
            )
        cls.db.commit()
        return defs

    @classmethod
    def _init_plugs(cls):
        working_dir = f'{INSTALL_DIR}/plugs'
        for plug in get_plug_list():
            defs = json.loads(open(f'{working_dir}/{plug}/defs.json', 'r', encoding='UTF-8').read())
            functions = schemafy(open(f'{working_dir}/{plug}/functions.sql', 'r', encoding='UTF-8').read(), plug)
            tables = schemafy(open(f'{working_dir}/{plug}/tables.sql', 'r', encoding='UTF-8').read(), plug)
            updated_defs = cls._check_defs(plug, defs)
            if updated_defs['props']['enabled'] is True:
                cls._check_schema(plug, tables)
                cls._update_functions(functions)
                AvailablePlugs.add_plug(plug, Plug(plug, updated_defs))

    @classmethod
    def _init_hpp(cls):
        cls.db.execute(f"CREATE SCHEMA IF NOT EXISTS {config['schema']};")
        tables = schemafy(open(f'{SOURCE_DIR}/tables.sql', 'r', encoding='UTF-8').read())
        functions = schemafy(open(f'{SOURCE_DIR}/functions.sql', 'r', encoding='UTF-8').read())
        sync = schemafy(open(f'{SOURCE_DIR}/sync.sql', 'r', encoding='UTF-8').read())
        cls.db.execute(tables)
        cls.db.execute(functions)
        cls.db.execute(sync)
        cls.db.execute(
            f"""
                INSERT INTO {config['schema']}.global_props (sync_enabled)
                SELECT 'true'
                WHERE NOT EXISTS (SELECT * FROM {config['schema']}.global_props);
            """, None
        )
        cls.db.commit()

    @classmethod
    def _cleanup(cls):
        """Stops any running sync procedures from previous instances."""
        running = cls.db.select_one(f"SELECT {config['schema']}.is_sync_running('{config['schema']}-main');")
        if running is True:
            cls.db.execute(f"SELECT {config['schema']}.terminate_main_sync('{config['schema']}-main');")
        cmds = [
            f"DROP SCHEMA {config['schema']} CASCADE;",
        ]
        working_dir = f'{INSTALL_DIR}/plugs'
        cls.plug_list = [f.name for f in os.scandir(working_dir) if cls._is_valid_plug(f.name)]
        for plug in cls.plug_list:
            cmds.append(f"DROP SCHEMA {config['schema']}_{plug} CASCADE")
        if config['reset'] == 'true':
            for cmd in cmds:
                try:
                    cls.db.execute(cmd)
                except Exception as err:
                    print(f"Reset encountered error: {err}")
            cls._init_hpp()

    @classmethod
    def _start_sync(cls):
        print("Starting main sync process...")
        db_main = DbSession(f"{config['schema']}-main")
        db_main.execute(f"CALL {config['schema']}.sync_main();")

    @classmethod
    def init(cls):
        cls._init_hpp()
        cls._cleanup()
        cls._init_plugs()
        Thread(target=cls._start_sync, name="sync").start()