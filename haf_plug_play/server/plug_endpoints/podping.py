"""Plug endpoints for podping."""
from sre_parse import State
from unittest import result
from fastapi import HTTPException

from haf_plug_play.database.access import ReadDb
from haf_plug_play.plugs.podping.podping import SearchQuery, StateQuery
from haf_plug_play.server.normalize import populate_by_schema

db = ReadDb().db

async def get_podping_counts(block_range=None):
    """Returns count summaries for podpings."""
    if block_range:
        if not isinstance(block_range, list):
            raise HTTPException(status_code=400, detail="Block range must be an array")
        for block_num in block_range:
            if not isinstance(block_num, int):
                raise HTTPException(status_code=400, detail="Block range items must be integers")
    sql = StateQuery.get_podping_counts(block_range)
    result = []
    res = db.db.select(sql) or []
    for entry in res:
        result.append(populate_by_schema(
            entry, ['url', 'count']
        ))
    return result

async def get_podping_url_latest(url:str):
    """Returns the `block_num` and `timestamp` from the latest update from a given URL."""
    sql_feed_update = StateQuery.get_podping_url_latest_payload(url)
    result = {}
    res = db.db.select(sql_feed_update) or None
    if res:
        result['feed_update'] = populate_by_schema(res[0], ['block_num', 'created'])
    return res
    