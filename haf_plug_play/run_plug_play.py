import os
import re
import sys
import time

from threading import Thread

from haf_plug_play.config import Config
from haf_plug_play.database.access import write
from haf_plug_play.server.serve import run_server
from haf_plug_play.database.haf import Haf
from haf_plug_play.tools import INSTALL_DIR

config = Config.config

def run():
    try:
        """Runs main application processes and server."""
        print("---   Hive Plug & Play (HAF) started   ---")
        # start haf sync
        Haf.init()
        # run server
        run_server(config)
    except KeyboardInterrupt:
        # shutdown
        sys.exit()

if __name__ == "__main__":
    run()
