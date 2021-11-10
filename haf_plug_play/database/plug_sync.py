from threading import Thread
import time

from haf_plug_play.database.haf_sync import DbSession
from haf_plug_play.utils.tools import range_split

db = DbSession()

BATCH_PROCESS_SIZE = 100000


class PlugInitSetup:

    @classmethod
    def setup_follow():
        pass # TODO

class PlugSync:

    # plug_name: state (None, loaded, syncing (10%), synced)
    plug_sync_states = {
        'follow': None,
        'reblog': None,
        'community': None
    }

    @classmethod
    def sync_follow(cls):
        print('Starting plug sync: follow')
        cls.plug_sync_states['follow'] = 'loaded'
        while True:
            head_hive_rowid = db.select("SELECT head_hive_rowid FROM global_props;")[0]
            app_hive_rowid = db.select("SELECT latest_hive_rowid FROM app_sync WHERE app_name = 'global';")[0]
            if (head_hive_rowid - app_hive_rowid) > 1000:
                steps = range_split((app_hive_rowid + 1), head_hive_rowid, BATCH_PROCESS_SIZE)
                for s in steps:
                    progress = round((s[1]/head_hive_rowid) * 100, 2)
                    cls.plug_sync_states['follow'] = f'synchronizing ({progress} %'
                    print(f"FOLLOW:: processing {s[0]} to {s[1]}     {progress}%")
                    db.select(f"SELECT public.hpp_follow_update( {s[0]}, {s[1]} );")
                    db.commit()
            elif (head_hive_rowid - app_hive_rowid) > 0:
                print(f"FOLLOW:: processing {app_hive_rowid+1} to {head_hive_rowid}")
                cls.plug_sync_states['follow'] = f'synchronizing ({progress} %'
                db.select(f"SELECT public.hpp_follow_update( {app_hive_rowid+1}, {head_hive_rowid} );")
                db.commit()
            cls.plug_sync_states['follow'] = 'synchronized'
            time.sleep(0.5)
    
    @classmethod
    def start_sync(cls):
        Thread(target=cls.sync_follow).start()

if __name__ == "__main__":
    PlugSync.sync_follow()