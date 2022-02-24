"""Plug endpoints for the polls protocol."""
import re
from jsonrpcserver import method, Result, Success, Error, result
from haf_plug_play.database.access import ReadDb
from haf_plug_play.plugs.polls.polls import SearchQuery, StateQuery
from haf_plug_play.server.normalize import populate_by_schema

db = ReadDb().db

def does_poll_exist(author,permlink):
    sql = f"""
        SELECT 1 FROM public.hpp_polls_content
        WHERE author = '{author}' AND permlink = '{permlink}';
    """
    exists = bool(db.db.select(sql))
    return exists

@method(name="plug_play_api.polls.get_poll_permlink")
async def get_poll_permlink(author, question):
    """Returns a valid and unique permlink to use with a new poll."""
    assert isinstance(author, str), "Poll author must be a string"
    assert len(author) <= 16, "Poll author must be no more than 16 characters"
    assert isinstance(question, str), "Poll question must be a string"
    assert len(question) <= 255, "Poll question must be no more than 255 characters"
    _body = question
    _body = _body.replace("&", " and ")
    _body = _body.replace("  ", " ")
    tries = 0
    while True:
        _clean_title = _body.split(' ')
        clean_title = ""
        total_len = 0
        for w in _clean_title:
            total_len += len(w)
            if total_len > 32: break
            clean_title += f"{w}-"
        plink = re.sub(r'[^a-z-]+', '', clean_title[:-1].lower())
        if tries > 0: plink = f"{plink}-{str(tries)}"
        exists = does_poll_exist(author, plink)
        if not exists:
            break
        else:
            tries += 1
    return Success(plink)

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
async def get_polls_active(tag=None):
    """Returns a list of current active polls, filterable by tag."""
    assert isinstance(tag, str), "Poll tag must be a string"
    assert len(tag) <= 16, "Poll tags must be no more than 16 characters"
    sql = StateQuery.get_polls_active(tag)
    result = []
    res = db.db.select(sql) or []
    for entry in res:
        result.append(populate_by_schema(
            entry, ['author', 'permlink', 'question', 'answers', 'expires', 'tag', 'created']
        ))
    return Success(result)

@method(name="plug_play_api.polls.get_poll")
async def get_poll(author,permlink, summary=True):
    """Returns a poll and vote details."""
    assert isinstance(author, str), "Poll author must be a string"
    assert len(author) <= 16, "Poll author must be no more than 16 characters"
    assert isinstance(permlink, str), "Poll permlink must be a string"
    assert len(permlink) <= 255, "Poll permlink must be no more than 255 characters"
    sql = StateQuery.get_poll(author,permlink)
    _votes = []
    res = db.db.select(sql) or None
    result = populate_by_schema(res[0], ['author', 'permlink', 'question'
                'answers', 'expires', 'tag', 'created'])
    if summary:
        sql = StateQuery.get_poll_votes_summary(author,permlink)
        res = db.db.select(sql) or None
        for entry in res:
            _votes.append(populate_by_schema(entry, ['answer', 'count']))
    else:
        sql = StateQuery.get_poll_votes(author,permlink)
        res = db.db.select(sql) or None
        for entry in res:
            _votes.append(populate_by_schema(entry, ['account', 'answer']))
    result['votes'] = _votes
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

@method(name="plug_play_api.polls.get_polls_user")
async def get_polls_user(author, active=False, tag=None):
    """Returns polls created by the specified user."""
    assert isinstance(author, str), "Poll author must be a string"
    assert len(author) <= 16, "Hive accounts must be no more than 16 characters"
    assert isinstance(active, bool), "Active parameter must be boolean"
    if tag:
        assert isinstance(tag, str), "Poll tag must be a string"
        assert len(tag) <= 16, "Poll tags must be no more than 16 characters"
    sql = StateQuery.get_polls_user(author,active,tag)
    result = []
    res = db.db.select(sql) or []
    for entry in res:
        result.append(populate_by_schema(
            entry, ['permlink', 'question', 'answers', 'expires', 'tag', 'created']
        ))
    return Success(result)
