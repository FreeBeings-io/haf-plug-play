"""Plug endpoints for the polls protocol."""
import re

from fastapi import HTTPException, APIRouter

from haf_plug_play.database.access import ReadDb
from haf_plug_play.plugs.polls.polls import SearchQuery, StateQuery
from haf_plug_play.server.normalize import populate_by_schema

db = ReadDb().db
router_polls = APIRouter()

def _does_poll_exist(author:str,permlink:str):
    """Checks whether the given poll exists already in the database."""

    sql = f"""
        SELECT 1 FROM hpp.polls_content
        WHERE author = '{author}' AND permlink = '{permlink}';
    """
    exists = bool(db.db.select(sql))
    return exists

@router_polls.post("/api/polls/new_permlink", tags=['polls'])
async def get_poll_permlink(author:str, question:str):
    """Returns a valid and unique permlink to use with a new poll.
    
    - `author` <string(16)>: Hive account name of the author
    - `question` <string(255)>: Question asked by the poll

    **Example params:**

    ```
    author="imwatsi"
    question="What do you think the price of Hive will be next year"
    ```
    """

    if not isinstance(author, str):
        raise HTTPException(status_code=400, detail="Poll author must be a string")
    if not len(author) <= 16:
        raise HTTPException(
            status_code=400,
            detail="Poll author must be no more than 16 characters"
        )
    if not isinstance(question, str):
        raise HTTPException(
            status_code=400,
            detail="Poll question must be a string"
        )
    if not len(question) <= 255:
        raise HTTPException(
            status_code=400,
            detail="Poll question must be no more than 255 characters"
        )
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
            if total_len > 32:
                break
            clean_title += f"{w}-"
        plink = re.sub(r'[^a-z-]+', '', clean_title[:-1].lower())
        if tries > 0:
            plink = f"{plink}-{str(tries)}"
        exists = _does_poll_exist(author, plink)
        if not exists:
            break
        else:
            tries += 1
    return plink

@router_polls.get("/api/polls/ops", tags=['polls'])
async def get_poll_ops(op_type:str, block_range=None):
    """Returns a list of 'polls' ops within the specified block range.
    
    - `op_type` <string>: ( valid options: create | vote )
    - `block_range` <array(int)>: (optional, default: `24 hours; 28,800 blocks`); start and end block of ops to consider

    **Example params:**

    ```
    `op_type`="create"
    `block_range=[63040238,63069038]
    ```
    """

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

    return result

@router_polls.get("/api/polls/active", tags=['polls'])
async def get_polls_active(tag=""):
    """Returns a list of current active polls, filterable by tag.
    
    - `tag` <string(500)>: (optional)

    **Example params:**

    ```
    `tag`="@author/permlink"
    ```
    """
    if not isinstance(tag, str):
        raise HTTPException(status_code=400, detail="Poll tag must be a string")
    if not len(tag) <= 16:
        raise HTTPException(status_code=400, detail="Poll tags must be no more than 16 characters")
    sql = StateQuery.get_polls_active(tag)
    result = []
    res = db.db.select(sql) or []
    for entry in res:
        result.append(populate_by_schema(
            entry, ['author', 'permlink', 'question', 'answers', 'expires', 'tag', 'created']
        ))
    return result

router_polls.get("/api/polls/{author}/{permlink}", tags=['polls'])
async def get_poll(author: str, permlink:str, summary=True):
    """Returns a poll and vote details.
    
    - `author` <string(16)>: Hive account that created the poll
    - `permlink` <string(255)>: The permlink of the poll
    - `summary` <boolean>: (optional) Choose to include a summary of the poll's votes,  not a full list

    **Example params:**

    ```
    `author`="@imwatsi.test"
    `permlink`="do-you-like-polls"
    `summary`=true
    ```
    """
    if not isinstance(author, str):
        raise HTTPException(
            status_code=400,
            detail="Poll author must be a string"
        )
    if not len(author) <= 16:
        raise HTTPException(
            status_code=400,
            detail="Poll author must be no more than 16 characters"
        )
    if not isinstance(permlink, str):
        raise HTTPException(
            status_code=400,
            detail="Poll permlink must be a string"
        )
    if not len(permlink) <= 255:
        raise HTTPException(
            status_code=400,
            detail="Poll permlink must be no more than 255 characters"
        )
    sql = StateQuery.get_poll(author,permlink)
    _votes = []
    res = db.db.select(sql) or None
    if not res:
        raise HTTPException(
            status_code=400,
            detail="Poll not found"
        )
    result = populate_by_schema(res[0], ['author', 'permlink', 'question'
                'answers', 'expires', 'tag', 'created'])
    if summary:
        sql = StateQuery.get_poll_votes_summary(author,permlink)
        res = db.db.select(sql) or []
        for entry in res:
            _votes.append(populate_by_schema(entry, ['answer', 'count']))
    else:
        sql = StateQuery.get_poll_votes(author,permlink)
        res = db.db.select(sql) or []
        for entry in res:
            _votes.append(populate_by_schema(entry, ['account', 'answer']))
    result['votes'] = _votes
    return result

@router_polls.get("/api/polls/{author}/{permlink}/votes", tags=['polls'])
async def get_poll_votes(author: str, permlink: str):
    """Returns votes for specified poll.

    - `author` <string(16)>: Hive account that created the poll
    - `permlink` <string(255)>: The permlink of the poll

    **Example params:**
    ```
    `author`="@imwatsi.test"
    `permlink`="do-you-like-polls"
    ```
    """
    if not isinstance(author, str):
        raise HTTPException(
            status_code=400,
            detail="Poll author must be a string"
        )
    if not len(author) <= 16:
        raise HTTPException(
            status_code=400,
            detail="Hive accounts must be no more than 16 characters"
        )
    if not isinstance(permlink, str):
        raise HTTPException(
            status_code=400,
            detail="Poll permlink must be a string"
    )
    if not len(permlink) <= 255:
        raise HTTPException(
            status_code=400,
            detail="Poll permlink must be no more than 255 characters"
        )
    sql = StateQuery.get_poll_votes(author, permlink)
    result = []
    res = db.db.select(sql) or []
    for entry in res:
        result.append(populate_by_schema(
            entry, ['account', 'answer']
        ))
    return result

@router_polls.get("/api/polls/{author}", tags=['polls'])
async def get_polls_user(author: str, active=False, tag=""):
    """Returns polls created by the specified user.
    
    - `author` <string(16)>: Hive account that created the poll
    - `active` <boolean>: (default: `false`) Only include active polls, `true` | `false`
    - `tag` <string(500)>: (optional)

    **Example params:**
    ```
    `author`="@imwatsi.test"
    `permlink`="do-you-like-polls"
    ```
    """
    if not isinstance(author, str):
        raise HTTPException(
            status_code=400,
            detail="Poll author must be a string"
        )
    if not len(author) <= 16:
        raise HTTPException(
            status_code=400,
            detail="Hive accounts must be no more than 16 characters"
        )
    if not isinstance(active, bool):
        raise HTTPException(
            status_code=400,
            detail="Active parameter must be boolean"
        )
    if tag:
        if not isinstance(tag, str):
            raise HTTPException(
                status_code=400,
                detail="Poll tag must be a string"
            )
        if not len(tag) <= 16:
            raise HTTPException(
                status_code=400,
                detail="Poll tags must be no more than 16 characters"
            )
    sql = StateQuery.get_polls_user(author,active,tag)
    result = []
    res = db.db.select(sql) or []
    for entry in res:
        result.append(populate_by_schema(
            entry, ['permlink', 'question', 'answers', 'expires', 'tag', 'created']
        ))
    return result
