"""Plug endpoints for community ops."""
from jsonrpcserver import method, Result, Success, Error

from haf_plug_play.plugs.community.community import SearchOps
from haf_plug_play.server.system_status import SystemStatus
from haf_plug_play.server.normalize import populate_by_schema

@method(name="plug_play_api.get_subscribe_ops")
async def get_subscribe_ops(context, community, block_range=None):
    """Returns a list of community subscribe ops within the specified block."""
    db = context['db']
    sql = SearchOps.subscribe(community, block_range=block_range)
    result = []
    if sql:
        res = db.db.select(sql)  or []
        for entry in res:
            result.append(populate_by_schema(
                entry, ['account']
            ))
    return result

@method(name="plug_play_api.get_unsubscribe_ops")
async def get_unsubscribe_ops(context, community, block_range=None):
    """Returns a list of community unsubscribe ops within the specified block range."""
    db = context['db']
    sql = SearchOps.unsubscribe(community, block_range=block_range)
    result = []
    if sql:
        res = db.db.select(sql) or []
        for entry in res:
            result.append(populate_by_schema(
                entry, ['account']
            ))
    return result

@method(name="plug_play_api.get_flag_post_ops")
async def get_flag_post_ops(context, community=None, account=None, permlink=None, notes=None, block_range=None):
    """Returns a list of `flagPost` ops within the speicified block range."""
    db = context['db']
    sql = SearchOps.flag_post(community, account, permlink, notes, block_range)
    result = []
    if sql:
        res = db.db.select(sql) or []
        for entry in res:
            result.append(populate_by_schema(
                entry, ['acc_auths', 'account', 'permlink', 'notes']
            ))
    return result