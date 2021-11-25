import json
from jsonrpcserver import method, Result, Success, Error

from haf_plug_play.database.access import ReadDb
from haf_plug_play.plugs.reblog.reblog import SearchOps, StateQuery
from haf_plug_play.server.normalize import populate_by_schema

db = ReadDb().db

@method(name="plug_play_api.reblog.get_reblog_ops")
async def get_reblog_ops(account=None, author=None,  block_range=None):
    sql = SearchOps.reblog(
        reblog_account=account,
        blog_author=author,
        block_range=block_range
    )
    result = []
    if sql:
        res = db.db.select(sql) or []
        for entry in res:
            result.append(populate_by_schema(
                entry, ['transaction_id', 'acc_auths', 'account', 'author', 'permlink']
            ))

    return Success(result)

@method(name="plug_play_api.reblog.get_account_reblogs")
async def get_follow_ops(account) -> Result:
    """Returns a list of reblogs that an account has made."""
    sql = StateQuery.get_account_reblogs(account=account)
    result = []
    if sql:
        res = db.db.select(sql) or []
        for entry in res:
            result.append(populate_by_schema(
                entry, ['author', 'permlink']
            ))

    return Success(result)