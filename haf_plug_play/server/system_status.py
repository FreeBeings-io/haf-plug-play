class SystemStatus:
    sync_status = None
    
    @classmethod
    def set_sync_status(cls, latest_block, latest_time, behind):
        cls.sync_status = {
            'latest_block': latest_block,
            'latest_block_time': latest_time,
            'behind': behind
        }
    
    @classmethod
    def get_sync_status(cls):
        return dict(cls.sync_status) if cls.sync_status is not None else None
    
    @classmethod
    def get_latest_block(cls):
        status = cls.get_sync_status()
        if status:
            return status['latest_block']
        return None
