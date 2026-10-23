import asyncio
from types import SimpleNamespace

import aiohttp
import discord

from dtl.bot import LeagueBot
from dtl.health import health_server


def test_health_endpoint_tracks_connection_and_cleans_up():
    async def check():
        state = {"ready": False, "closed": False}
        bot = SimpleNamespace(
            is_ready=lambda: state["ready"],
            is_closed=lambda: state["closed"],
            latency=float("inf"),
        )
        async with health_server(bot, port=0) as site:
            server = site._server
            host, port = server.sockets[0].getsockname()
            assert host == "127.0.0.1"
            async with aiohttp.ClientSession(trust_env=False) as session:

                async def status(expected):
                    async with session.get(f"http://{host}:{port}/health") as response:
                        assert response.status == expected
                        assert (await response.json())["status"] == (
                            "ready" if expected == 200 else "not_ready"
                        )

                await status(503)
                state["ready"] = True
                await status(503)
                bot.latency = 0.05
                await status(200)
                state["ready"] = False
                await status(503)
                state["ready"] = True
                await status(200)
                state["closed"] = True
                await status(503)
        assert not server.is_serving()

    asyncio.run(check())


def test_bot_starts_health_server_before_discord_login(monkeypatch):
    calls = []

    async def start(client, token, *, reconnect):
        calls.append((token, reconnect))
        async with aiohttp.ClientSession(trust_env=False) as session:
            async with session.get("http://127.0.0.1:8080/health") as response:
                assert response.status == 503

    monkeypatch.setattr(discord.Client, "start", start)
    asyncio.run(LeagueBot().start("test-token", reconnect=False))
    assert calls == [("test-token", False)]
