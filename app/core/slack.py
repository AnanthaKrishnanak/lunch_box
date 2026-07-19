from slack_sdk.web.async_client import AsyncWebClient

from app.core.settings import settings

slack_client = AsyncWebClient(token=settings.SLACK_BOT_TOKEN)


def get_slack_client() -> AsyncWebClient:
    return slack_client
