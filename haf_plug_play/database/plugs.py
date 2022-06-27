import json
from operator import truediv
import time
from typing import Dict
from haf_plug_play.database.core import DbSession


class Plug:

    def __init__(self, name, defs) -> None:
        self.name = name
        self.defs = defs
        self.db_conn = DbSession()
        self.error = False
    
    def create_new_connection(self):
        if self.error == False:
            del self.db_conn
            self.db_conn = DbSession()

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
        running = self.db_conn.select_exists(
            f"SELECT * FROM hpp.plug_state WHERE plug = '{self.name}' AND run_start=true AND run_finish=false")
        return running
    
    def start(self):
        try:
            print(f"{self.name}:: starting")
            self.db_conn.execute(f"CALL hpp.sync_plug( '{self.name}' );")
        except Exception as err:
            print(f"Plug error: '{self.name}'")
            print(err)
            self.error = True
            self.db_conn.conn.close()

class AvailablePlugs:

    plugs = Dict[str, Plug]()

    @classmethod
    def add_plug(cls, plug_name, plug:Plug):
        cls.plugs[plug_name] = plug

    @classmethod
    def plug_watch(cls):
        while True:
            for _plug in cls.plugs.items():
                plug = cls.plugs[_plug[0]]
                if not plug.running() or not plug.is_connection_open():
                    if plug.is_enabled():
                        print(f"{_plug[0]}:: creating new DB connection.")
                        plug.create_new_connection()
                        if plug.error is True:
                            plug.disable()
                            plug.error = False
                        else:
                            plug.start()
            time.sleep(60)
