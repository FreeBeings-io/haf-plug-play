import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from haf_plug_play import config

from haf_plug_play.server.plug_endpoints.podping import router_podping
from haf_plug_play.server.plug_endpoints.hive_engine import router_hive_engine
from haf_plug_play.server.plug_endpoints.deleg import router_deleg

from haf_plug_play.server.system_status import SystemStatus
from haf_plug_play.tools import normalize_types, get_plug_list
from haf_plug_play.utils.api_metadata import TITLE, DESCRIPTION, VERSION, CONTACT, LICENSE, TAGS_METADATA

PLUG_ROUTERS = {
    'podping': router_podping,
    'hive_engine': router_hive_engine,
    'deleg': router_deleg
}

config = config.Config.config

app = FastAPI(
    title=TITLE,
    description=DESCRIPTION,
    version=VERSION,
    contact=CONTACT,
    license_info=LICENSE,
    openapi_tags=TAGS_METADATA,
    openapi_url="/api/openapi.json",
    docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

for plug in get_plug_list():
    if plug in config['plugs']:
        app.include_router(PLUG_ROUTERS[plug])

async def root():
    """Reports the status of Hive Plug & Play."""
    report = {
        'name': 'Hive Plug & Play',
        'status': normalize_types(SystemStatus.get_sync_status())
    }
    return report

# SYSTEM

app.add_api_route("/api", root, tags=["system"], methods=["GET"], summary="System status")

def run_server():
    """Run server."""
    uvicorn.run(
        "haf_plug_play.server.serve:app",
        host=config['server_host'],
        port=int(config['server_port']),
        log_level="info",
        reload=False,
        workers=int(config['server_workers'])
    )
