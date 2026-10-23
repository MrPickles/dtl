import math
from contextlib import asynccontextmanager

from aiohttp import web


@asynccontextmanager
async def health_server(bot, port=8080):
    async def health(request):
        ready = bot.is_ready() and not bot.is_closed() and math.isfinite(bot.latency)
        return web.json_response(
            {"status": "ready" if ready else "not_ready"},
            status=200 if ready else 503,
        )

    app = web.Application()
    app.router.add_get("/health", health)
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    try:
        site = web.TCPSite(runner, "127.0.0.1", port)
        await site.start()
        yield site
    finally:
        await runner.cleanup()
