import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from dtl.bot import LeagueBot
from dtl.commands import spongebob_command
from dtl.util import spongebob_text


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Hello world", "hElLo WoRlD"),
        ("HELLO world", "hElLo WoRlD"),
        ("a! 123 b🙂c", "a! 123 B🙂c"),
        ("ab\ncd", "aB\ncD"),
        ("éö中a", "éÖ中a"),
        ("", ""),
    ],
)
def test_spongebob_text(text, expected):
    assert spongebob_text(text) == expected


def test_spongebob_command_registration_and_response():
    bot = LeagueBot()
    bot.tree.add_command(spongebob_command)
    command = bot.tree.get_command("spongebob")
    assert command.parameters[0].required
    assert command.parameters[0].max_value == 1000
    response = SimpleNamespace(send_message=AsyncMock())
    asyncio.run(command.callback(SimpleNamespace(response=response), "@everyone hello"))
    args, kwargs = response.send_message.call_args
    assert args == ("@eVeRyOnE hElLo",)
    assert kwargs["allowed_mentions"].to_dict()["parse"] == []


@pytest.mark.parametrize(
    "text", ["   ", "İΐ" * 500], ids=["whitespace", "unicode-expansion"]
)
def test_spongebob_command_rejects_empty_or_expanded_long_text(text):
    response = SimpleNamespace(send_message=AsyncMock())
    asyncio.run(spongebob_command.callback(SimpleNamespace(response=response), text))
    assert response.send_message.call_args.kwargs["ephemeral"] is True
