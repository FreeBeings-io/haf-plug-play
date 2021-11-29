"""Plug endpoints for community ops."""
from os import name
from jsonrpcserver import method, Result, Success, Error, result
from haf_plug_play.database.access import ReadDb
from haf_plug_play.plugs.polls.polls import SearchQuery, StateQuery
from haf_plug_play.server.normalize import populate_by_schema

db = ReadDb().db

@method(name="plug_play_api.polls.get_polls_ops")
async def get_poll_ops(op_type=None, block_range=None) -> Result:
    """Returns a list of 'polls' ops within the specified block or time range."""
    sql = SearchQuery.poll_ops(
        op_type=op_type,
        block_range=block_range
    )
    result = []
    if sql:
        res = db.db.select(sql) or []
        for entry in res:
            result.append(populate_by_schema(
                entry, ['transaction_id', 'req_posting_auths', 'op_type', 'op_payload']
            ))

    return Success(result)

@method(name="plug_play_api.polls.get_polls_active")
async def get_polls_active(tag):
    """Returns a list of current active polls, filterable by tag."""
    assert isinstance(tag, str), "Poll tag must be a string"
    assert len(tag) <= 16, "Poll tags must be no more than 16 characters"
    sql = StateQuery.get_polls_active(tag)
    result = []
    res = db.db.select(sql) or []
    for entry in res:
        result.append(populate_by_schema(
            entry, ['author', 'permlink', 'question', 'answers', 'expires', 'tags']
        ))
    return Success(result)

@method(name="plug_play_api.polls.get_poll_votes")
async def get_poll_votes(author, permlink):
    """Returns votes for specified poll."""
    assert isinstance(author, str), "Poll author must be a string"
    assert len(author) <= 16, "Hive accounts must be no more than 16 characters"
    assert isinstance(permlink, str), "Poll permlink must be a string"
    assert len(permlink) <= 255, "Poll permlink must be no more than 255 characters"
    sql = StateQuery.get_poll_votes(author, permlink)
    result = []
    res = db.db.select(sql) or []
    for entry in res:
        result.append(populate_by_schema(
            entry, ['account', 'answer']
        ))
    return Success(result)