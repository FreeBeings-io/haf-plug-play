import json
import os
import re
from haf_plug_play.database.access import select, write
from haf_plug_play.database.core import DbSession

from haf_plug_play.tools import INSTALL_DIR

SOURCE_DIR = os.path.dirname(__file__) + "/sql"


class Haf:

    db = DbSession()

    @classmethod
    def _is_valid_plug(cls, module):
        return bool(re.match(r'^[a-z]+[_]*$', module))

    @classmethod
    def _check_context(cls, plug, start_block):
        exists = cls.db.select(
            f"SELECT hive.app_context_exists( '{plug}' );"
        )[0][0]
        if exists is False:
            cls.db.select(f"SELECT hive.app_create_context( '{plug}' );")
            cls.db.select(f"SELECT hive.app_context_detach( '{plug}' );")
            cls.db.select(f"SELECT hive.app_context_attach( '{plug}', {(start_block-1)} );")
            cls.db.commit()
            print(f"HAF SYNC:: created context: '{plug}'")
    
    @classmethod
    def _check_schema(cls, plug, functions, tables):
        exists = bool(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name='{plug}';")
        if not exists:
            cls.db.execute(tables, None)
            cls.db.execute(functions, None)
    
    @classmethod
    def _check_defs(cls, plug, defs):
        _block = defs['props']['start_block'] - 1
        has = select(f"SELECT plug FROM hpp.plug_state WHERE plug='{plug}'", ['plug'], True)
        defs = json.dumps(defs)
        if has is not None:
            # update
            sql = f"""
                UPDATE hpp.plug_state SET defs='{defs}', latest_block_num={_block} WHERE plug='{plug}';
            """
        else:
            # insert
            sql = f"""
                    INSERT INTO hpp.plug_state (plug, hooks, latest_block_num)
                    VALUES ('{plug}', '{defs}', {_block});
                """
        done = write(sql)
        if done is not True:
            raise Exception(f"Failed to save defs to DB for plug: '{plug}")

    @classmethod
    def _init_plugs(cls):
        plug_list = [f.name for f in os.scandir(dir) if cls._is_valid_plug(f.name)]
        for plug in plug_list:
            wd = f'{INSTALL_DIR}/plugs/{plug}'
            defs = json.loads(open(f'{wd}/defs.json', 'r').read())
            functions = open(f'{wd}/functions.sql', 'r').read()
            tables = open(f'{wd}/tables.sql', 'r').read()
            cls._check_context(plug, defs['props']['start_block'])
            cls._check_schema(plug, functions, tables)
            cls._check_defs(plug, defs)
        
    @classmethod
    def _init_hpp(cls):
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
    def init(cls):
        cls._init_hpp()
        cls._init_plugs()