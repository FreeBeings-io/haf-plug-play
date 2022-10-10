from haf_plug_play.database.access import select
from haf_plug_play.config import Config

HPP_PLUG_STATE_FIELDS = ['plug', 'latest_block_num', 'check_in', "defs->'props'->'enabled'"]

config = Config.config

def get_haf_sync_head():
    sql = f"SELECT hive.app_get_irreversible_block();"
    res = select(sql, ['head_block_num'])
    return res[0]

def get_plugs_status():
    fields = ", ".join(HPP_PLUG_STATE_FIELDS)
    sql = f"""
        SELECT {fields} FROM {config['schema']}.plug_state;
    """
    res = select(sql, ['plug', 'latest_block_num', 'check_in', 'enabled'])
    return res

def get_plug_status(plug):
    fields = ", ".join(HPP_PLUG_STATE_FIELDS)
    sql = f"""
        SELECT {fields} FROM {config['schema']}.plug_state WHERE plug='{plug}';
    """
    res = select(sql, HPP_PLUG_STATE_FIELDS)
    return res[0]