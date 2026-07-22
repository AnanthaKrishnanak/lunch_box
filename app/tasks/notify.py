import logging

from slack_sdk.errors import SlackApiError

from app.core.slack import get_slack_client

logger = logging.getLogger(__name__)


async def notify(message: str, slack_user_id: str) -> None:
    slack_client = get_slack_client()

    try:
        response = await slack_client.conversations_open(users=[slack_user_id])
        if not response.get("ok"):
            logger.error(
                "Failed to open Slack DM for %s: %s",
                slack_user_id,
                response.get("error"),
            )
            return

        dm_channel_id = response["channel"]["id"]
        await slack_client.chat_postMessage(
            channel=dm_channel_id,
            text=message,
        )
    except SlackApiError:
        logger.exception(
            "Slack API error while notifying user %s",
            slack_user_id,
        )
    except Exception:
        logger.exception(
            "Unexpected error while notifying user %s",
            slack_user_id,
        )
