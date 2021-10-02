"""Plug endpoints for community ops."""
import json
from jsonrpcserver import method, Result, Success, Error

from haf_plug_play.database.access import DbAccess
from haf_plug_play.plugs.follow.follow import SearchOps, StateOps
from haf_plug_play.server.system_status import SystemStatus
from haf_plug_play.server.normalize import populate_by_schema

db = DbAccess.db

@method(name="plug_play_api.follow.get_follow_ops")
async def get_follow_ops(follower=None, followed=None,  block_range=None) -> Result:
    """Returns a list of global follow ops within the specified block or time range."""
    sql = SearchOps.follow(
        follower_account=follower,
        followed_account=followed,
        block_range=block_range
    )
    result = []
    if sql:
        res = db.db.select(sql) or []
        for entry in res:
            _json = json.loads(entry[1])
            _entry = [
                entry[0],
                _json['follower'],
                _json['following'],
                _json['what']
            ]
            result.append(populate_by_schema(
                _entry, ['acc_auths', 'follower', 'following', 'what']
            ))

    return Success(result)

@method(name="plug_play_api.follow.get_reblog_ops")
async def get_reblog_ops(reblog_account=None, author=None, permlink=None, block_range=None) -> Result:
    """Returns a list of global reblog ops within the specified block or time range."""
    sql = SearchOps.reblog(
        reblog_account=reblog_account,
        blog_author=author,
        blog_permlink=permlink,
        block_range=block_range
    )
    result = []
    if sql:
        res = db.db.select(sql) or []
        for entry in res:
            result.append(populate_by_schema(
                entry, ['acc_auths', 'account', 'author', 'permlink']
            ))
    return Success(result)

@method(name="plug_play_api.follow.get_reblog_ops")
async def get_account_followers(account):
    """Returns the list of accounts a Hive account is following."""
    assert isinstance(account, str), "the Hive account must be a string"
    assert len(account) <= 16, "Hive account names must be no more than 16 characters"
    sql = StateOps.followers(account)
    result = []
    res = db.db.select(sql) or []
    for entry in res:
        result.append(entry, ['account', 'what'])
    return Success(result)