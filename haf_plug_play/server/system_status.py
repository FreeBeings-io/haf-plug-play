from haf_plug_play.database.access import ReadDb

db = ReadDb.db

class SystemStatus:
    sync_status = {}
    
    @classmethod
    def update_sync_status(cls, sync_status=None, plug_status=None):
        if sync_status:
            cls.sync_status['sync'] = sync_status
        if plug_status:
            cls.sync_status['plugs'] = plug_status

    @classmethod
    def get_sync_status(cls):
        glob_props = db.get_global_props()
        cls.sync_status['system'] = glob_props
        return cls.sync_status

