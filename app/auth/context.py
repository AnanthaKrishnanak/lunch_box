from fastapi import Request

from app.auth.current_user import get_current_slack_user
from app.auth.slack import verify_slack_request
from app.core.deps import SlackClientDeps, UserServiceDeps


async def slack_context(
    request: Request,
    user_service: UserServiceDeps,
    slack_client: SlackClientDeps,
) -> None:
    await verify_slack_request(request)
    user = await get_current_slack_user(request, user_service, slack_client)
    request.state.user = user
