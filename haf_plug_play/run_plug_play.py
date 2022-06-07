import os
import re
import sys
import time

from threading import Thread

from haf_plug_play.config import Config
from haf_plug_play.database.access import write
from haf_plug_play.server.serve import run_server
from haf_plug_play.database.haf_sync import HafSync
from haf_plug_play.database.plug_processor import HookProcessor
from haf_plug_play.tools import INSTALL_DIR

config = Config.config

class Plugs:

    def __init__(self) -> None:
        self.modules = {}

    def _is_valid_plug(self, module):
        return bool(re.match(r'^[a-z]+[_]*$', module))

    def _init_modules_db(self):
        for m in self.modules:
            sql = f"""
                INSERT INTO hpp.plug_state (module)
                SELECT ('{m}')
                WHERE NOT EXISTS (SELECT * FROM hpp.plug_state WHERE module = '{m}');
            """
            write(sql)
    
    def _load(self):
        dir = f'{INSTALL_DIR}/modules'
        module_list = [f.name for f in os.scandir(dir) if self._is_valid_plug(f.name)]
        for m in module_list:
            if m not in self.modules:
                self.modules[m] = HookProcessor(m)
                self._init_modules_db()

    def _refresh_modules(self):
        # TODO: periodically run _load()
        while True:
            self._load()
            time.sleep(120)

    def start(self):
        self._load()
        for m in self.modules.keys():
            self.modules[m].start()

def run():
    try:
        """Runs main application processes and server."""
        print("---   Hive Plug & Play (HAF) started   ---")
        # start haf sync
        HafSync.init()
        HafSync.toggle_sync()
        Thread(target=HafSync.main_loop).start()
        # start Plug & Play modules
        while not HafSync.massive_sync_done:
            time.sleep(1)
        modules = Plugs()
        modules.start()
        # run server
        run_server(config)
    except KeyboardInterrupt:
        # shutdown
        sys.exit()


if __name__ == "__main__":
    run()
