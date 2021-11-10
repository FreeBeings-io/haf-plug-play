import time

from haf_plug_play.database.haf_sync import DbSession
from haf_plug_play.utils.tools import range_split

db = DbSession()

BATCH_PROCESS_SIZE = 1000

class PlugInitSetup:

    @classmethod
    def setup_follow():
        pass # TODO

class PlugSync:

    @classmethod
    def sync_follow():
        while True:
            head_hive_rowid = db.select("SELECT head_hive_rowid FROM global_props;")[0]
            app_hive_rowid = db.select("SELECT latest_hive_rowid FROM app_sync WHERE app_name = 'global';")[0]
            if (head_hive_rowid - app_hive_rowid) > 1000:
                steps = range_split((app_hive_rowid + 1), head_hive_rowid, BATCH_PROCESS_SIZE)
                for s in steps:
                    progress = round((s[1]/head_hive_rowid) * 100, 2)
                    print(f"FOLLOW:: processing {s[0]} to {s[1]}     {progress}%")
                    db.select(f"SELECT public.hpp_follow_update( {s[0]}, {s[1]} );")
                    db.commit()
            elif (head_hive_rowid - app_hive_rowid) > 0:
                print(f"FOLLOW:: processing {app_hive_rowid+1} to {head_hive_rowid}")
                db.select(f"SELECT public.hpp_follow_update( {app_hive_rowid+1}, {head_hive_rowid} );")
                db.commit()
            time.sleep(0.5)

if __name__ == "__main__":
    PlugSync.sync_follow()