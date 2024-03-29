import decimal
import os

from datetime import datetime
import re

from haf_plug_play.config import Config

HIVE_NODES = [
    "https://api.hive.blog",
    "https://api.openhive.network",
    "https://anyx.io",
    "https://rpc.ausbit.dev",
    "https://api.deathwing.me",
    "https://hive-api.arcange.eu"
]

UTC_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"
INSTALL_DIR = os.path.dirname(__file__)

config = Config.config

def _is_valid_plug(module):
    return bool(re.match(r'^[a-z]+[_]*[a-z]*', module))

def get_plug_list():
    working_dir = f'{INSTALL_DIR}/plugs'
    plug_list = [f.name for f in os.scandir(working_dir) if _is_valid_plug(f.name)]
    return plug_list

def schemafy(data:str, plug=None):
    _data = data.replace('hpp.', f"{config['schema']}.")
    if plug is not None:
        return _data.replace(f"{plug}.", f"{config['schema']}_{plug}.")
    return _data

def check_required_keys(required, provided_keys, op_context):
    missing = []
    for k in required:
        if k not in provided_keys:
            missing.append(k)
    assert len(missing) == 0, f"missing keys for {op_context}: {missing}"

def check_allowed_keys(allowed, provided_keys, op_context):
    unsupported = []
    for k in provided_keys:
        if k not in allowed:
            unsupported.append(k)
    assert len(unsupported) == 0, f"unsupported keys provided for {op_context}: {unsupported}"

def get_cleaned_dict(og_values, keys, keep=False):
    result = {}
    for k in og_values:
        if (k in keys) == keep:
            result[k] = og_values[k]
    return result

def range_split(first, last, size):
    a = first
    b = first
    result = []
    while True:
        a += size
        if a >= last:
            result.append((b,last))
            return result
        elif a < last:
            result.append((b,a))
            b = a+1

def populate_by_schema(data, fields):
    result = {}
    for i in range(len(fields)):
        result[fields[i]] = data[i]
    return result

def _normalize(data):
    if isinstance(data, dict):
        for k in data:
            if isinstance(data[k], decimal.Decimal):
                data[k] = float(data[k])
            elif isinstance(data[k], datetime):
                data[k] = datetime.strftime(data[k], UTC_TIMESTAMP_FORMAT)
        return data

def normalize_types(data):
    if isinstance(data, list) or isinstance(data, tuple):
        res = []
        for l in data:
            res.append(_normalize(l))
        return res
    elif isinstance(data, dict):
        return _normalize(data)
    return data