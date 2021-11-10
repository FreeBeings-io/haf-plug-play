import os
from threading import Thread

from haf_plug_play.config import Config
from haf_plug_play.server.serve import run_server
from haf_plug_play.server.system_status import SystemStatus
from haf_plug_play.database.haf_sync import HafSync
from haf_plug_play.database.plug_sync import PlugInitSetup, PlugSync

config = Config.config

def run():
    print("---   Hive Plug & Play (HAF) started   ---")
    # start haf sync
    HafSync.init()
    HafSync.toggle_sync()
    Thread(target=HafSync.main_loop).start()
    # start plug sync
    PlugInitSetup.init()
    PlugSync.start_sync()
    run_server(config)


if __name__ == "__main__":
    run()