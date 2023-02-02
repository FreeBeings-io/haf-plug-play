"""Plug endpoints for Delegations API."""
from fastapi import APIRouter, HTTPException, Request

from haf_plug_play.plugs.deleg.deleg import SearchQuery, StateQuery
from haf_plug_play.database.access import select
from haf_plug_play.server.buffer import Buffer

SCHEMA_DELEG_HIST = ['id', 'created', 'delegator', 'amount']
SCHEMA_DELEG = ['id', 'delegator', 'amount']

router_deleg = APIRouter()

@router_deleg.get("/api/deleg/account", tags=['deleg'])
async def get_acc_bals(request: Request, account:str):
    """Returns delegation balances for account."""
    if len(account) > 16:
        raise HTTPException(status_code=400, detail="Hive account must be no more than 16 chars")
    # check buffer
    _buffer = Buffer.check_buffer(request['path'])
    if _buffer is not None:
        return _buffer
    # prrocess request
    sql = StateQuery.get_deleg_account_bals(account)
    res = select(sql, ['balances'])[0]
    result = {
        'account': account,
        'balances': res['balances'] or {}
    }
    Buffer.update_buffer(request['path'], result)
    return result

@router_deleg.get('/api/deleg/in', tags=['deleg'])
async def get_acc_in(request: Request, account:str, limit:int=100):
    """Returns current delegations made to given account."""
    limit = 100 if limit > 100 else limit
    if len(account) > 16:
        raise HTTPException(status_code=400, detail="Hive account must be no more than 16 chars")
    # check buffer
    _buffer = Buffer.check_buffer(request['path'])
    if _buffer is not None:
        return _buffer
    # prrocess request
    sql = StateQuery.get_deleg_in(account, limit)
    result = select(sql, SCHEMA_DELEG) or []
    Buffer.update_buffer(request['path'], result)
    return result

@router_deleg.get('/api/deleg/out', tags=['deleg'])
async def get_acc_out(request: Request, account:str, limit:int=100):
    """Returns current delegations made from a given account."""
    limit = 100 if limit > 100 else limit
    if len(account) > 16:
        raise HTTPException(status_code=400, detail="Hive account must be no more than 16 chars")
    # check buffer
    _buffer = Buffer.check_buffer(request['path'])
    if _buffer is not None:
        return _buffer
    # prrocess request
    sql = StateQuery.get_deleg_out(account, limit)
    result = select(sql, SCHEMA_DELEG) or []
    Buffer.update_buffer(request['path'], result)
    return result

@router_deleg.get('/api/deleg/history/in', tags=['deleg'])
async def get_history_in(request: Request, account:str, limit:int=100, descending:bool=True):
    """Returns historical delegations made to given account."""
    limit = 100 if limit > 100 else limit
    if len(account) > 16:
        raise HTTPException(status_code=400, detail="Hive account must be no more than 16 chars")
    # check buffer
    _buffer = Buffer.check_buffer(request['path'])
    if _buffer is not None:
        return _buffer
    # prrocess request
    sql = SearchQuery.get_deleg_in(account, limit, descending)
    result = select(sql, SCHEMA_DELEG_HIST) or []
    Buffer.update_buffer(request['path'], result)
    return result

@router_deleg.get('/api/deleg/history/out', tags=['deleg'])
async def get_history_out(request: Request, account:str, limit:int=100, descending:bool=True):
    """Returns historical delegations made from a given account."""
    limit = 100 if limit > 100 else limit
    if len(account) > 16:
        raise HTTPException(status_code=400, detail="Hive account must be no more than 16 chars")
    # check buffer
    _buffer = Buffer.check_buffer(request['path'])
    if _buffer is not None:
        return _buffer
    # prrocess request
    sql = SearchQuery.get_deleg_out(account, limit, descending)
    result = select(sql, SCHEMA_DELEG_HIST) or []
    Buffer.update_buffer(request['path'], result)
    return result
