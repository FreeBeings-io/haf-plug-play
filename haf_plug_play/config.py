import json
import os

HOME_DIR = os.environ.get('PLUG_PLAY_HOME') or "/etc/haf-plug-play"

CONFIG_FIELDS = [
    'db_username', 'db_password', 'server_host',
    'server_port', 'ssl_cert', 'ssl_key'
]


class Config:
    config = {}

    @classmethod
    def validate(cls):
        pass

    @classmethod
    def load_config(cls, config_file):
        values = {}
        if not os.path.isdir(HOME_DIR):
            os.mkdir(HOME_DIR)
        if not os.path.exists(config_file):
            print(config_file)
            new_conf = open(config_file, 'w')
            new_conf.writelines(f"{field}=\n" for field in CONFIG_FIELDS)
            new_conf.close()
            print(
                'No config file detected. A blank one has been created.\n'
                'Populate it with the correct details and restart haf-plug-play.'
            )
            os._exit(1)
        f = open(config_file, 'r').readlines()
        for line in f:
            if '=' in line:
                setting = line.split('=')
                _key = setting[0]
                assert _key in CONFIG_FIELDS, f"invalid config key detected {_key}"
                _value = setting[1].strip('\n ')
                if '[' in _value or '{' in _value:
                    values[_key] = json.loads(_value)
                else:
                    values[_key] = _value
        cls.config = values
        cls.validate()

Config.load_config(HOME_DIR + "/config.ini")