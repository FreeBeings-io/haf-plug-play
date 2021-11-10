from haf_plug_play.database.handlers import PlugPlayDb
from haf_plug_play.database.plug_sync import PlugSync

class SystemStatus:
    sync_status = None
    db = None

    @classmethod
    def init(cls, config):
        cls.db = PlugPlayDb(config)

    @classmethod
    def get_sync_status(cls, plugs=[]):
        result = {}
        result['system_status'] = cls.db.get_sync_status()
        plugs.extend(['follow', 'reblog', 'community'])
        _plugs = {}
        for p in plugs:
            if p in PlugSync.plug_sync_states:
                _plugs[p] = PlugSync.plug_sync_states[p]
        result['plugs'] = _plugs
        return result
    
    @classmethod
    def get_latest_block(cls):
        status = cls.get_sync_status()
        if status:
            return status['latest_block']
        return None
