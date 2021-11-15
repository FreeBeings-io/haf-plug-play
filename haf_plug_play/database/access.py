from haf_plug_play.database.handlers import PlugPlayDb
from haf_plug_play.database.core import DbSession
from haf_plug_play.config import Config

config = Config.config

class ReadDb:
    def __init__(self) -> None:
        self.db = PlugPlayDb(config)

class WriteDb:
    def __init__(self) -> None:
        self.db = DbSession(config)