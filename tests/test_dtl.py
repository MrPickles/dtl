from datetime import timedelta

from dtl import __version__
from dtl.bot import this_person_wants_to_play_league as tpwtpl, parse_timer


def test_version():
    assert __version__ == "0.1.0"


def test_tpwtpl():
    # Basic cases
    assert tpwtpl("SL?")
    assert tpwtpl("sl?")
    assert tpwtpl("DTL?")
    assert tpwtpl("sl?")

    # Cases with other stuff before the question mark
    assert tpwtpl("SL alsdkfjalskdjfladf?")
    assert tpwtpl("DTL in 69 minutes?")

    # Negative cases
    assert not tpwtpl("potatoes?")
    assert not tpwtpl("So league?")
    assert not tpwtpl("SL")
    assert not tpwtpl("DTL")
    assert not tpwtpl("slick?")
    assert not tpwtpl("slow?")
    assert not tpwtpl("when you finally go to sleep?")


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
