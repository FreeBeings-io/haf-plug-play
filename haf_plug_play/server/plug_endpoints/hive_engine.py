"""Plug endpoints for Hive Engine."""
import json
from fastapi import APIRouter, HTTPException
from datetime import datetime

from haf_plug_play.plugs.hive_engine.hive_engine import SearchQuery, StateQuery
from haf_plug_play.database.access import select
from haf_plug_play.tools import UTC_TIMESTAMP_FORMAT

router_hive_engine = APIRouter()

@router_hive_engine.get("/api/hive-engine/nft", tags=['hive-engine'])
async def get_nft(symbol:str):
    """Returns details about an NFT.

    """
    pass

