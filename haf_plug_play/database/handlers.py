from haf_plug_play.database.access import select

HPP_PLUG_STATE_FIELDS = ['plug', 'latest_block_num', 'check_in', "defs->'props'->'enabled'"]

def get_haf_sync_head():
    sql = f"""
        SELECT num, created_at FROM hive.blocks ORDER BY num DESC LIMIT 1;
    """
    res = select(sql, ['head_block_num', 'head_block_time'])
    return res[0]

def get_plugs_status():
    fields = ", ".join(HPP_PLUG_STATE_FIELDS)
    sql = f"""
        SELECT {fields} FROM hpp.plug_state;
    """
    res = select(sql, ['plug', 'latest_block_num', 'check_in', 'enabled'])
    return res

def get_plug_status(plug):
    fields = ", ".join(HPP_PLUG_STATE_FIELDS)
    sql = f"""
        SELECT {fields} FROM hpp.plug_state WHERE plug='{plug}';
    """
    res = select(sql, HPP_PLUG_STATE_FIELDS)
    return res[0]