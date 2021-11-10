from haf_plug_play.database.handlers import PlugPlayDb
from haf_plug_play.database.core import DbSession
from haf_plug_play.config import Config

config = Config.config

class ReadDb:
    db = PlugPlayDb(config)

class WriteDb:
    db = DbSession(config)