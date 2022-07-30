import os

class Config:
    config = {}

    @classmethod
    def validate(cls):
        pass

    @classmethod
    def load_config(cls):
        cls.config['db_host'] = os.environ.get('PORT')
        cls.config['db_name'] = os.environ.get('DB_NAME')
        cls.config['db_username'] = os.environ.get('DB_USERNAME')
        cls.config['db_password'] = os.environ.get('DB_PASSWORD')
        cls.config['server_host'] = os.environ.get('SERVER_HOST')
        cls.config['server_port'] = os.environ.get('SERVER_PORT')

Config.load_config()
