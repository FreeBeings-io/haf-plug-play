"""Plug endpoints for Hive Engine."""
import json
from fastapi import APIRouter, HTTPException
from datetime import datetime

from haf_plug_play.plugs.hive_engine.hive_engine import SearchQuery, StateQuery
from haf_plug_play.database.access import select
from haf_plug_play.tools import UTC_TIMESTAMP_FORMAT

router_hive_engine = APIRouter()

@router_hive_engine.get("/api/hive-engine/ops", tags=['hive-engine'])
async def get_ops(contract_name:str, contract_action:str):
    """Returns operations based on filter options."""
    sql = SearchQuery.get_he_ops(contract_name, contract_action)
    res = select(sql, ['created', 'block_num', 'payload', 'req_auths', 'req_posting_auths'])
    return res
