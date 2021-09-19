from haf_plug_play.database.handlers import PlugPlayDb
from haf_plug_play.config import Config

config = Config.config

class DbAccess:
    db = PlugPlayDb(config)