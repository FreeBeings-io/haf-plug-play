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
    sql = StateQuery.get_deleg_account_bals(account)
    res = select(sql, ['account', 'given', 'received'])
    return res
