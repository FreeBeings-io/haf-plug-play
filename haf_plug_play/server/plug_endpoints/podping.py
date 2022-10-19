"""Plug endpoints for podping."""
import json
from fastapi import APIRouter, HTTPException
from datetime import datetime

from haf_plug_play.plugs.podping.podping import SearchQuery, StateQuery
from haf_plug_play.database.access import select
from haf_plug_play.tools import UTC_TIMESTAMP_FORMAT

router_podping = APIRouter()

@router_podping.get("/api/podping/history/counts", tags=['podping'])
async def get_podping_counts(block_range=None, limit: int = 20):
    """Returns count summaries for podpings.

    - `block_range` <array(int)> (optional, default: `30 days; 864,000 blocks`): start and end block of ops to consider
    - `limit` (int) (optional, default: 20 highest count items)

    **Example params:**

    ```
    block_range=[62187823,63051823]
    ```
    """
    if block_range:
        block_range = json.loads(block_range)
        if not isinstance(block_range, list):
            raise HTTPException(status_code=400, detail="Block range must be an array")
        for block_num in block_range:
            if not isinstance(block_num, int):
                raise HTTPException(
                    status_code=400, detail="Block range items must be integers"
                )
    sql = StateQuery.get_podping_counts(block_range, limit)
    result = select(sql, ['url', 'count']) or []
    return result

@router_podping.get("/api/podping/history/latest/iri", tags=['podping'])
async def get_podping_url_latest(iri:str, limit: int = 5):
    """Returns the latest feed update from a given URL.

    - `iri` <string(500)>: the url of the podping
    - `limit` <int> (default = 5): max number of results to return

    **Example params:**

    ```
    url=https%3A%2F%2Ffeeds.captivate.fm%2Felmatutinodela91
    ```
    """
    sql_feed_update = StateQuery.get_podping_url_latest_feed_update(iri, limit)
    result = {}
    feed_updates = select(sql_feed_update, ['trx_id', 'block_num', 'created', 'reason', 'medium'])
    if feed_updates:
        result["feed_updates"] = feed_updates
        result["iri"] = iri
        _time_since = datetime.utcnow() - datetime.strptime(feed_updates[0]['created'], UTC_TIMESTAMP_FORMAT)
        result["seconds_since_last_update"] = _time_since.seconds
    else:
        return []
    return result

@router_podping.get("/api/podping/history/latest/account", tags=['podping'])
async def get_podping_acc_latest(iri:str, limit: int = 5, acc:str = None):
    """Returns the latest feed update from a given account.

    - `acc` <string(16)>: the account that made the podping
    - `limit` <int> (default = 5): max number of results to return

    **Example params:**

    ```
    acc=podping.aaa
    ```
    """
    if acc is not None and len(acc) > 16:
        raise HTTPException(status_code=400, detail="Hive account must be no more than 16 chars")
    sql_feed_update = StateQuery.get_podping_acc_latest_feed_update(limit, acc)
    result = {}
    feed_updates = select(sql_feed_update, ['trx_id', 'block_num', 'created', 'reason', 'medium'])
    if feed_updates:
        result["feed_updates"] = feed_updates
        result["iri"] = iri
        _time_since = datetime.utcnow() - datetime.strptime(feed_updates[0]['created'], UTC_TIMESTAMP_FORMAT)
        result["seconds_since_last_update"] = _time_since.seconds
    else:
        return []
    return result
