import sys
import time


from haf_plug_play.config import Config
from haf_plug_play.server.serve import run_server
from haf_plug_play.database.haf import Haf

config = Config.config

def run():
    try:
        """Runs main application processes and server."""
        print("---   Hive Plug & Play (HAF) started   ---")
        # start haf sync
        Haf.init()
        time.sleep(5)
        # run server
        run_server(config)
    except KeyboardInterrupt:
        # shutdown
        sys.exit()

if __name__ == "__main__":
    run()
