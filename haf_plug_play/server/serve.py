import ssl
from datetime import datetime
from aiohttp import web
from jsonrpcserver import method, async_dispatch
from haf_plug_play.server import api_endpoints
from haf_plug_play.server.system_status import SystemStatus
from haf_plug_play.server.normalize import normalize_types
from haf_plug_play.server.plug_endpoints import polls, podping


def run_server(config):
    app = web.Application()

    async def status_report(request):
        report = {
            'name': 'Hive Plug & Play',
            'sync': normalize_types(SystemStatus.get_sync_status()),
            'timestamp': datetime.utcnow().isoformat()
        }
        return web.json_response(status=200, data=report)
    
    
    async def handle(request):
        return web.Response(
            text=await async_dispatch(await request.text()), content_type="application/json"
        )

    app.router.add_post("/", handle)
    app.router.add_get("/", status_report)
    if config['ssl_cert'] != '' and config['ssl_key'] != '':
        context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS)
        context.load_cert_chain(
                config['ssl_cert'],
                config['ssl_key']
        )
    else:
        context = None
    web.run_app(
        app,
        host=config['server_host'],
        port=config['server_port'],
        ssl_context=context
    )