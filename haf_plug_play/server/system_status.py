from datetime import datetime

from haf_plug_play.database.handlers import get_haf_sync_head, get_plugs_status
from haf_plug_play.tools import UTC_TIMESTAMP_FORMAT, normalize_types
from haf_plug_play.utils.hive import make_request



class SystemStatus:
    sync_status = {}

    @classmethod
    def get_sync_status(cls):
        glob_props = normalize_types(get_haf_sync_head())
        plugs = normalize_types(get_plugs_status())
        cls.sync_status['haf_system'] = glob_props
        cls.sync_status['plugs'] = plugs
        head = make_request('condenser_api.get_dynamic_global_properties')['head_block_number']
        sys_head = cls.sync_status['haf_system']['head_block_num']
        diff = head - sys_head
        health = "GOOD"
        for s in cls.sync_status['plugs']:
            if (s['latest_block_num'] or 0) < (glob_props['head_block_num']-10) and s['enabled'] is True:
                health = "BAD"
        if diff > 30:
            health = "BAD"
        cls.sync_status['health'] = health
        cls.sync_status['timestamp'] = datetime.strftime(datetime.utcnow(), UTC_TIMESTAMP_FORMAT)
        return cls.sync_status

    @classmethod
    def get_latest_block(cls):
        return get_haf_sync_head()['head_block_num']
    
    @classmethod
    def is_healthy(cls):
        return cls.get_sync_status()['health']