from haf_plug_play.database.handlers import PlugPlayDb

class SystemStatus:
    sync_status = None
    db = None

    @classmethod
    def init(cls, config):
        cls.db = PlugPlayDb(config)

    @classmethod
    def get_sync_status(cls):
        status = cls.db.get_sync_status()
        return status
    
    @classmethod
    def get_latest_block(cls):
        status = cls.get_sync_status()
        if status:
            return status['latest_block']
        return None
