from datetime import datetime

import uvicorn
from fastapi import FastAPI

from haf_plug_play.server.plug_endpoints import polls, podping

from haf_plug_play.server.system_status import SystemStatus
from haf_plug_play.server.normalize import normalize_types

app = FastAPI(openapi_url="/api/openapi.json")

async def root():
    """Reports the status of Hive Plug & Play."""
    report = {
        'name': 'Hive Plug & Play',
        'sync': normalize_types(SystemStatus.get_sync_status()),
        'timestamp': datetime.utcnow().isoformat()
    }
    return report

# SYSTEM

app.add_api_route("/api", root, tags=["system"], methods=["GET"], summary="System status")

# POLLS

app.add_api_route(
    "/api/polls/new_permlink",
    polls.get_poll_permlink,
    tags=["polls"],
    methods=["POST"],
    summary="A valid and unique permlink to use with a new poll"
)
app.add_api_route(
    "/api/polls/ops",
    polls.get_poll_ops,
    tags=["polls"],
    methods=["GET"],
    summary="A list of 'polls' ops within the specified block or time range"
)
app.add_api_route(
    "/api/polls/active",
    polls.get_polls_active,
    tags=["polls"],
    methods=["GET"],
    summary="A list of current active polls, filterable by tag"
)
app.add_api_route(
    "/api/polls/{author}/{permlink}",
    polls.get_poll,
    tags=["polls"],
    methods=["GET"],
    summary="A poll and its vote details"
)
app.add_api_route(
    "/api/polls/{author}/{permlink}/votes",
    polls.get_poll_votes,
    tags=["polls"],
    methods=["GET"],
    summary="Votes for specified poll"
)
app.add_api_route(
    "/api/polls/{author}",
    polls.get_polls_user,
    tags=["polls"],
    methods=["GET"],
    summary="Polls created by the specified user"
)

# PODPING

app.add_api_route(
    "/api/podping/history/counts",
    podping.get_podping_counts,
    tags=["podping"],
    methods=["GET"],
    summary="Returns count summaries for podpings"
)

app.add_api_route(
    "/api/podping/history/latest/url",
    podping.get_podping_url_latest,
    tags=["podping"],
    methods=["GET"],
    summary="Returns block_num and timestamp of latest updates"
)

def run_server(config):
    """Run server."""

    if config['ssl_cert'] != '' and config['ssl_key'] != '':
        uvicorn.run(
            app,
            host=config['server_host'],
            port=int(config['server_port']),
            log_level="info",
            ssl_certfile=config['ssl_cert'],
            ssl_keyfile=config['ssl_key'],
            reload=True
        )
    else:
        uvicorn.run(
            app,
            host=config['server_host'],
            port=int(config['server_port']),
            log_level="info"
        )

