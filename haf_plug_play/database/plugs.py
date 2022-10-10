import json

from haf_plug_play.config import Config

from haf_plug_play.database.core import DbSession

config = Config.config


class Plug:

    def __init__(self, name, defs) -> None:
        self.name = name
        self.defs = defs
        self.db_conn = DbSession(f"{config['schema']}-{self.name}")
        self.error = False
    
    def create_new_connection(self):
        if self.error == False:
            del self.db_conn
            self.db_conn = DbSession(f"{config['schema']}-{self.name}")

    def get_defs(self):
        return self.defs
    
    def disable(self):
        self.defs['props']['enabled'] = False
        _defs = json.dumps(self.defs)
        self.db_conn.execute(
            f"UPDATE hpp.plug_state SET defs = '{_defs}' WHERE plug = '{self.name}';"
        )
        self.db_conn.commit()
    
    def enable(self):
        self.defs['props']['enabled'] = True
        _defs = json.dumps(self.defs)
        self.db_conn.execute(
            f"UPDATE hpp.plug_state SET defs = '{_defs}' WHERE plug = '{self.name}';"
        )
        self.db_conn.commit()
    
    def terminate_sync(self):
        self.db_conn.execute(
            f"SELECT hpp.terminate_sync({self.name});"
        )
    
    def is_enabled(self):
        enabled = bool(
            self.db_conn.select_one(
                f"SELECT defs->'props'->'enabled' FROM hpp.plug_state WHERE plug ='{self.name}';"
            )
        )
        return enabled

    def is_connection_open(self):
        return self.db_conn.is_open()
    
    def running(self):
        running = self.db_conn.select_one(
            f"SELECT hpp.plug_running('{self.name}');")
        return running
    
    def is_long_running(self):
        long_running = self.db_conn.select_one(
            f"SELECT hpp.plug_long_running('{self.name}');")
        return long_running

class AvailablePlugs:

    plugs = dict[str, Plug]()

    @classmethod
    def add_plug(cls, plug_name, plug:Plug):
        cls.plugs[plug_name] = plug
