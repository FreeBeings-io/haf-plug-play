class SystemStatus:
    sync_status = {}
    
    @classmethod
    def update_sync_status(cls, sys_status=None, plug_status=None):
        if sys_status:
            cls.sync_status['system'] = sys_status
        if plug_status:
            cls.sync_status['plugs'] = plug_status

    @classmethod
    def get_sync_status(cls):
        return cls.sync_status

