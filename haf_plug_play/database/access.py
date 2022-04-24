from haf_plug_play.database.handlers import PlugPlayDb
from haf_plug_play.database.core import DbSession

class ReadDb:
    def __init__(self) -> None:
        self.db = PlugPlayDb()

class WriteDb:
    def __init__(self) -> None:
        self.db = DbSession()