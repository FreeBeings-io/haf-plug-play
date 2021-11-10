import os.path

from haf_plug_play.database.haf_sync import DbSession

db = DbSession()

class PrepareFunctions:

    @classmethod
    def follow(cls):
        functions = open(os.path.dirname(__file__) + '/../plugs/follow/functions.sql').read()
        tables = open(os.path.dirname(__file__) + '/../plugs/follow/tables.sql').read()
        db.execute(functions, None)
        db.execute(tables, None)

PrepareFunctions.follow()