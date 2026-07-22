from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from slack_sdk.errors import SlackApiError

from app.tasks.notify import notify


@pytest.fixture
def slack_client():
    client = AsyncMock()
    client.conversations_open.return_value = {
        "ok": True,
        "channel": {"id": "D123"},
    }
    client.chat_postMessage.return_value = {"ok": True}
    return client


async def test_notify_opens_dm_and_posts_message(slack_client):
    with patch("app.tasks.notify.get_slack_client", return_value=slack_client):
        await notify("Lunch confirmed", "U999")

    slack_client.conversations_open.assert_awaited_once_with(users=["U999"])
    slack_client.chat_postMessage.assert_awaited_once_with(
        channel="D123",
        text="Lunch confirmed",
    )


async def test_notify_skips_post_when_open_not_ok(slack_client):
    slack_client.conversations_open.return_value = {
        "ok": False,
        "error": "user_not_found",
    }

    with patch("app.tasks.notify.get_slack_client", return_value=slack_client):
        await notify("Lunch confirmed", "U999")

    slack_client.chat_postMessage.assert_not_awaited()


async def test_notify_swallows_slack_api_error(slack_client):
    slack_client.conversations_open.side_effect = SlackApiError(
        message="boom",
        response=MagicMock(data={"ok": False, "error": "invalid_auth"}),
    )

    with patch("app.tasks.notify.get_slack_client", return_value=slack_client):
        await notify("Lunch confirmed", "U999")

    slack_client.chat_postMessage.assert_not_awaited()


async def test_notify_swallows_unexpected_error(slack_client):
    slack_client.conversations_open.side_effect = RuntimeError("network down")

    with patch("app.tasks.notify.get_slack_client", return_value=slack_client):
        await notify("Lunch confirmed", "U999")

    slack_client.chat_postMessage.assert_not_awaited()
