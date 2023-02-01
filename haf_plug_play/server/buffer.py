from datetime import datetime, timedelta

class Buffer:

    buffer ={}
    
    @classmethod
    def check_buffer(cls, path):
        if path not in cls.buffer:
            return None
        data = cls.buffer[path]
        if data['timestamp'] + timedelta(seconds=3) >= datetime.utcnow():
            return data['data']
        else:
            return None
    
    @classmethod
    def update_buffer(cls, path, payload):
        cls.buffer[path] = {
            'timestamp': datetime.utcnow(),
            'data': payload
        }