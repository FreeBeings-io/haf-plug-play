"""API endpoints."""
from os import name
from jsonrpcserver import method, Result, Success, Error

from haf_plug_play.database.access import DbAccess
from haf_plug_play.server.system_status import SystemStatus
from haf_plug_play.server.normalize import normalize_types

db = DbAccess.db

@method(name="plug_play_api.ping")
async def ping():
    return Success("pong")

@method(name="plug_play_api.get_sync_status")
async def get_sync_status(plugs=[]):
    return Success(normalize_types(SystemStatus.get_sync_status(plugs)))

@method(name="plug_play_api.get_ops_by_block")
async def get_ops_by_block(block_num):
    """Returns a list of ops within the specified block number."""
    status = SystemStatus.get_sync_status()
    if not status: return [] # TODO: error handling/reporting
    latest = status['latest_block']
    if block_num > latest: return []
    return Success(db.get_ops_by_block(block_num))
