from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from dtl import __version__
from dtl.bot import LeagueBot
from dtl.triggers import giphy_time, so_league
from dtl.util import parse_timer


class DummyBot:
    def __init__(self):
        self.user = object()

    def is_rate_limited(self):
        return False


class DummyMessage(SimpleNamespace):
    pass


@pytest.mark.parametrize("debug,cooldown", [(False, 900), (True, 2)])
def test_gif_cooldown_refreshes_after_each_reset(monkeypatch, debug, cooldown):
    bot = LeagueBot(debug=debug)
    now = datetime(2030, 1, 1)
    monkeypatch.setattr("dtl.bot.datetime", SimpleNamespace(now=lambda: now))

    assert not bot.is_rate_limited()
    bot.reset_rate_limit()
    assert bot.is_rate_limited()

    now += timedelta(seconds=cooldown - 1)
    assert bot.is_rate_limited()
    now += timedelta(seconds=1)
    assert not bot.is_rate_limited()

    bot.reset_rate_limit()
    assert bot.is_rate_limited()
    now += timedelta(seconds=cooldown)
    assert not bot.is_rate_limited()


def test_gif_silence_preserves_explicit_timestamp(monkeypatch):
    bot = LeagueBot()
    now = datetime(2030, 1, 1)
    monkeypatch.setattr("dtl.bot.datetime", SimpleNamespace(now=lambda: now))

    bot.reset_rate_limit(now + timedelta(hours=1))
    now += timedelta(hours=1)
    assert bot.is_rate_limited()
    now += timedelta(minutes=15)
    assert not bot.is_rate_limited()


def test_version():
    assert __version__ == "0.1.0"


def test_so_league_trigger_detection():
    # Basic cases
    assert so_league(None, DummyMessage(content="SL?")) is not None
    assert so_league(None, DummyMessage(content="sl?")) is not None
    assert so_league(None, DummyMessage(content="DTL?")) is not None

    # Cases with other stuff before the question mark
    assert so_league(None, DummyMessage(content="SL alsdkfjalskdjfladf?")) is not None
    assert so_league(None, DummyMessage(content="DTL in 69 minutes?")) is not None

    # Negative cases
    assert so_league(None, DummyMessage(content="potatoes?")) is None
    assert so_league(None, DummyMessage(content="So league?")) is None
    assert so_league(None, DummyMessage(content="SL")) is None
    assert so_league(None, DummyMessage(content="DTL")) is None
    assert so_league(None, DummyMessage(content="slick?")) is None
    assert so_league(None, DummyMessage(content="slow?")) is None
    assert (
        so_league(None, DummyMessage(content="when you finally go to sleep?")) is None
    )


def test_parse_timer():
    assert parse_timer("SL?") is None
    assert parse_timer("SL asdf 5 min?") is None
    assert parse_timer("SL in -1 hour?") is None
    assert parse_timer("SL 1 hour?") is None

    # Parsing minutes
    assert parse_timer("SL in 15 minutes?") == timedelta(minutes=15)
    assert parse_timer("SL in 5 min?") == timedelta(minutes=5)
    assert parse_timer("SL in 10 m?") == timedelta(minutes=10)

    # Parsing hours
    assert parse_timer("DTL in 1 hour?") == timedelta(hours=1)
    assert parse_timer("DTL in 3 hrs?") == timedelta(hours=3)
    assert parse_timer("DTL in 1.5 h?") == timedelta(hours=1.5)

    # Out-of-bound values
    assert parse_timer("DTL in 4 hours?") is None
    assert parse_timer("DTL in 5 hours?") is None
    assert parse_timer("DTL in 4 minutes?") is None
    assert parse_timer("DTL in 3 minutes?") is None


def test_pizza_time_trigger_detection():
    bot = DummyBot()

    assert giphy_time(bot, DummyMessage(content="pizza", mentions=[])) is not None
    assert giphy_time(bot, DummyMessage(content="pizza time", mentions=[])) is not None
    assert giphy_time(bot, DummyMessage(content="pIzZA TiMe", mentions=[])) is not None
    assert giphy_time(bot, DummyMessage(content="family time", mentions=[])) is not None

    assert giphy_time(bot, DummyMessage(content="piazza", mentions=[])) is None
    assert giphy_time(bot, DummyMessage(content="??????", mentions=[])) is None
