from os import truncate
from threading import Thread
import time

from haf_plug_play.database.access import WriteDb
from haf_plug_play.server.system_status import SystemStatus
from haf_plug_play.utils.tools import range_split
from haf_plug_play.plugs.follow.follow import WDIR_FOLLOW
from haf_plug_play.plugs.reblog.reblog import WDIR_REBLOG

BATCH_PROCESS_SIZE = 100000


class PlugInitSetup:

    db = WriteDb().db

    @classmethod
    def init(cls):
        cls.setup_follow()
        cls.setup_reblog()
        cls.db.conn.close()

    @classmethod
    def setup_follow(cls):
        tables = open(f'{WDIR_FOLLOW}/tables.sql', 'r').read()
        functions = open(f'{WDIR_FOLLOW}/functions.sql', 'r').read()
        cls.db.execute(tables, None)
        cls.db.execute(functions, None)
        cls.db.commit()

    @classmethod
    def setup_reblog(cls):
        tables = open(f'{WDIR_REBLOG}/tables.sql', 'r').read()
        functions = open(f'{WDIR_REBLOG}/functions.sql', 'r').read()
        cls.db.execute(tables, None)
        cls.db.execute(functions, None)
        cls.db.commit()

class PlugSync:

    # plug_name: state (None, loaded, syncing (10%), synced)
    plug_sync_states = {
        'follow': None,
        'reblog': None,
        'community': None
    }

    plug_sync_enabled = False

    @classmethod
    def toggle_sync(cls, enabled=True):
        cls.plug_sync_enabled = enabled
    
    @classmethod
    def sync_reblog(cls):
        print('Starting plug sync: reblog')
        db = WriteDb().db
        cls.plug_sync_states['reblog'] = 'loaded'
        while True:
            if cls.plug_sync_enabled is True:
                head_hive_rowid = db.select("SELECT head_hive_rowid FROM global_props;")
                assert head_hive_rowid is not None, "Null head_hive_rowid found"
                if head_hive_rowid:
                    head_hive_rowid = head_hive_rowid[0][0]
                else:
                    head_hive_rowid = 0
                _app_hive_rowid = db.select("SELECT latest_hive_rowid FROM plug_sync WHERE plug_name = 'reblog';")
                if _app_hive_rowid is None:
                    db.execute(
                        """INSERT INTO plug_sync (plug_name,latest_hive_rowid,state_hive_rowid,latest_hive_head_block)
                            VALUES ('reblog',0,0,0);""", None)
                    db.commit()
                if not _app_hive_rowid:
                    app_hive_rowid = 0
                else:
                    app_hive_rowid = _app_hive_rowid[0][0]
                if (head_hive_rowid - app_hive_rowid) > 1000:
                    steps = range_split((app_hive_rowid + 1), head_hive_rowid, BATCH_PROCESS_SIZE)
                    for s in steps:
                        progress = round((s[1]/head_hive_rowid) * 100, 2)
                        cls.plug_sync_states['reblog'] = f'synchronizing ({progress} %'
                        SystemStatus.update_sync_status(plug_status=cls.plug_sync_states)
                        print(f"REBLOG:: processing {s[0]} to {s[1]}     {progress}%")
                        db.select(f"SELECT public.hpp_reblog_update( {s[0]}, {s[1]} );")
                        db.commit()
                elif (head_hive_rowid - app_hive_rowid) > 0:
                    print(f"REBLOG:: processing {app_hive_rowid+1} to {head_hive_rowid}")
                    cls.plug_sync_states['reblog'] = f'synchronizing ({progress} %'
                    db.select(f"SELECT public.hpp_reblog_update( {app_hive_rowid+1}, {head_hive_rowid} );")
                    db.commit()
                if head_hive_rowid != 0:
                    cls.plug_sync_states['reblog'] = 'synchronized'
                SystemStatus.update_sync_status(plug_status=cls.plug_sync_states)
            else:
                cls.plug_sync_states['reblog'] = 'paused'
            time.sleep(0.5)

    @classmethod
    def sync_follow(cls):
        print('Starting plug sync: follow')
        db = WriteDb().db
        cls.plug_sync_states['follow'] = 'loaded'
        while True:
            if cls.plug_sync_enabled is True:
                head_hive_rowid = db.select("SELECT head_hive_rowid FROM global_props;")
                assert head_hive_rowid is not None, "Null head_hive_rowid found"
                if head_hive_rowid:
                    head_hive_rowid = head_hive_rowid[0][0]
                else:
                    head_hive_rowid = 0
                _app_hive_rowid = db.select("SELECT latest_hive_rowid FROM plug_sync WHERE plug_name = 'follow';")
                if _app_hive_rowid is None:
                    db.execute(
                        """INSERT INTO plug_sync (plug_name,latest_hive_rowid,state_hive_rowid,latest_hive_head_block)
                            VALUES ('follow',0,0,0);""", None)
                    db.commit()
                if not _app_hive_rowid:
                    app_hive_rowid = 0
                else:
                    app_hive_rowid = _app_hive_rowid[0][0]
                if (head_hive_rowid - app_hive_rowid) > 1000:
                    steps = range_split((app_hive_rowid + 1), head_hive_rowid, BATCH_PROCESS_SIZE)
                    for s in steps:
                        progress = round((s[1]/head_hive_rowid) * 100, 2)
                        cls.plug_sync_states['follow'] = f'synchronizing {progress} %'
                        SystemStatus.update_sync_status(plug_status=cls.plug_sync_states)
                        print(f"FOLLOW:: processing {s[0]} to {s[1]}     {progress}%")
                        db.select(f"SELECT public.hpp_follow_update( {s[0]}, {s[1]} );")
                        db.commit()
                elif (head_hive_rowid - app_hive_rowid) > 0:
                    print(f"FOLLOW:: processing {app_hive_rowid+1} to {head_hive_rowid}")
                    cls.plug_sync_states['follow'] = f'synchronizing ({progress} %'
                    db.select(f"SELECT public.hpp_follow_update( {app_hive_rowid+1}, {head_hive_rowid} );")
                    db.commit()
                if head_hive_rowid != 0:
                    cls.plug_sync_states['follow'] = 'synchronized'
                SystemStatus.update_sync_status(plug_status=cls.plug_sync_states)
            else:
                cls.plug_sync_states['follow'] = 'paused'
            time.sleep(0.5)
    
    @classmethod
    def start_sync(cls):
        Thread(target=cls.sync_follow).start()
        Thread(target=cls.sync_reblog).start()

if __name__ == "__main__":
    PlugSync.start_sync()
