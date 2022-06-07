from haf_plug_play.database.access import select

HPP_GLOBAL_PROPS_FIELDS = [
    'latest_block_num', 'latest_hive_rowid', 'latest_hpp_op_id',
    'latest_block_time', 'sync_enabled'
]
HPP_MODULE_STATE_FIELDS = ['module', 'latest_hpp_op_id']

def get_global_latest_state():
        fields = ", ".join(HPP_GLOBAL_PROPS_FIELDS)
        sql = f"""
            SELECT {fields} FROM hpp.global_props;
        """
        res = select(sql, HPP_GLOBAL_PROPS_FIELDS)
        return res[0]
    
def get_global_latest_hpp_op_id():
    state = get_global_latest_state()
    return state['latest_hpp_op_id']

def get_plug_latest_hpp_op_id(plug):
    fields = ", ".join(HPP_MODULE_STATE_FIELDS)
    sql = f"""
        SELECT {fields} FROM hpp.plug_state
        WHERE plug = '{plug}';
    """
    res = select(sql, HPP_MODULE_STATE_FIELDS)
    return res[0]
