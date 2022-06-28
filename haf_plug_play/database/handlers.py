from haf_plug_play.database.access import select

HPP_GLOBAL_PROPS_FIELDS = [
    'latest_block_num', 'latest_block_time', 'sync_enabled'
]
HPP_PLUG_STATE_FIELDS = ['latest_block_num', 'run_start', 'run_finish']

def get_global_latest_state():
    fields = ", ".join(HPP_GLOBAL_PROPS_FIELDS)
    sql = f"""
        SELECT {fields} FROM hpp.global_props;
    """
    res = select(sql, HPP_GLOBAL_PROPS_FIELDS)
    return res[0]

def get_plugs_status():
    fields = ", ".join(HPP_PLUG_STATE_FIELDS)
    sql = f"""
        SELECT {fields} FROM hpp.plug_state;
    """
    res = select(sql, HPP_PLUG_STATE_FIELDS)
    return res

def get_plug_status(plug):
    fields = ", ".join(HPP_PLUG_STATE_FIELDS)
    sql = f"""
        SELECT {fields} FROM hpp.plug_state WHERE plug='{plug}';
    """
    res = select(sql, HPP_PLUG_STATE_FIELDS)
    return res[0]