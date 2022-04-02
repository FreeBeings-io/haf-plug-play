"""Plug endpoints for podping."""
from fastapi import HTTPException

from haf_plug_play.database.access import ReadDb
from haf_plug_play.plugs.podping.podping import SearchQuery, StateQuery
from haf_plug_play.server.normalize import populate_by_schema

db = ReadDb().db

async def get_podping_counts(block_range=None):
    """Returns count summaries for podpings.
    
    `block_range` <array(int)> (optional, default: `30 days; 864,000 blocks`): start and end block of ops to consider

    **Example params:**

    ```
    block_range=[62187823,63051823]
    ```
    """
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
    """Returns the latest feed update from a given URL.

    `url` <string>: the url of the podping

    **Example params:**
    
    ```
    url=https%3A%2F%2Ffeeds.captivate.fm%2Felmatutinodela91
    ```
    """
    sql_feed_update = StateQuery.get_podping_url_latest_feed_update(url)
    result = {}
    feed_updates = []
    res = db.db.select(sql_feed_update) or []
    if res:
        for entry in res:
            feed_updates.append(
                populate_by_schema(
                    entry, ['trx_id', 'block_num', 'created']
                ))
        result['feed_updates'] = feed_updates
    return result
    