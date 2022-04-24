from datetime import datetime

from haf_plug_play.database.access import ReadDb
from haf_plug_play.server.normalize import normalize_types
from haf_plug_play.utils.tools import UTC_TIMESTAMP_FORMAT

db = ReadDb().db

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
        glob_props = normalize_types(db.get_global_props())
        cls.sync_status['system'] = glob_props
        timestamp = datetime.utcnow().strftime(UTC_TIMESTAMP_FORMAT)
        cur_time = datetime.strptime(timestamp, UTC_TIMESTAMP_FORMAT)
        sys_time = datetime.strptime(cls.sync_status['system']['head_block_time'], UTC_TIMESTAMP_FORMAT)
        diff = cur_time - sys_time
        health = "GOOD"
        if 'plugs' in cls.sync_status:
            for s in cls.sync_status['plugs']:
                if cls.sync_status['plugs'][s] != "synchronized":
                    health = "BAD"
        if diff.seconds > 30:
            health = "BAD"
        cls.sync_status['health'] = health
        cls.sync_status['timestamp'] = timestamp
        return cls.sync_status

    @classmethod
    def get_latest_block(cls):
        status = cls.get_sync_status()
        if 'system' in status:
            if 'head_block_num' in status['system']:
                return status['system']['head_block_num']
        return None
    
    @classmethod
    def is_healthy(cls):
        return cls.get_sync_status()['health']