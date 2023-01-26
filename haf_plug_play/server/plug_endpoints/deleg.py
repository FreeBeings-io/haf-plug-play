"""Plug endpoints for Delegations API."""
import json
from fastapi import APIRouter, HTTPException
from datetime import datetime

from haf_plug_play.plugs.deleg.deleg import SearchQuery, StateQuery
from haf_plug_play.database.access import select
from haf_plug_play.tools import UTC_TIMESTAMP_FORMAT

router_deleg = APIRouter()

@router_deleg.get("/api/deleg/account", tags=['deleg'])
async def get_acc_bals(account:str):
    """Returns delegation balances for account."""
    if len(account) > 16:
        raise HTTPException(status_code=400, detail="Hive account must be no more than 16 chars")
    sql = StateQuery.get_deleg_account_bals(account)
    res = select(sql, ['balances'])
    result = {
        'account': account,
        'balances': res['balances']
    }
    return result
