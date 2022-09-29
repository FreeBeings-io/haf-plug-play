import os

class Config:
    config = {}

    @classmethod
    def validate(cls):
        pass

    @classmethod
    def load_config(cls):
        cls.config['db_host'] = os.environ.get('DB_HOST')
        cls.config['db_name'] = os.environ.get('DB_NAME')
        cls.config['db_username'] = os.environ.get('DB_USERNAME')
        cls.config['db_password'] = os.environ.get('DB_PASSWORD')
        cls.config['server_host'] = os.environ.get('SERVER_HOST')
        cls.config['server_port'] = os.environ.get('SERVER_PORT')
        cls.config['schema'] = os.environ.get('SCHEMA')
        cls.config['plugs'] = os.environ.get('PLUGS')

Config.load_config()
