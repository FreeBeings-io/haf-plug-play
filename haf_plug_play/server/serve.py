
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from haf_plug_play.server.plug_endpoints.podping import router_podping

from haf_plug_play.server.system_status import SystemStatus
from haf_plug_play.tools import normalize_types
from haf_plug_play.utils.api_metadata import TITLE, DESCRIPTION, VERSION, CONTACT, LICENSE, TAGS_METADATA


app = FastAPI(
    title=TITLE,
    description=DESCRIPTION,
    version=VERSION,
    contact=CONTACT,
    license_info=LICENSE,
    openapi_tags=TAGS_METADATA,
    openapi_url="/api/openapi.json",
    docs_url="/"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_podping)

async def root():
    """Reports the status of Hive Plug & Play."""
    report = {
        'name': 'Hive Plug & Play',
        'status': normalize_types(SystemStatus.get_sync_status())
    }
    return report

# SYSTEM

app.add_api_route("/api", root, tags=["system"], methods=["GET"], summary="System status")

def run_server(config):
    """Run server."""
    uvicorn.run(
        "haf_plug_play.server.serve:app",
        host=config['server_host'],
        port=int(config['server_port']),
        log_level="info",
        reload=True
    )
