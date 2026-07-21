from fastapi import HTTPException, Request, status

from app.auth.current_user import get_current_slack_user
from app.auth.slack import verify_slack_request
from app.core.deps import SlackClientDeps, UserServiceDeps
from app.core.settings import settings


async def slack_context(
    request: Request,
    user_service: UserServiceDeps,
    slack_client: SlackClientDeps,
) -> None:
    if settings.DEV_MODE:
        # In DEV_MODE, skip Slack signature verification so /docs works locally.
        # We look for a user with slack_user_id="DEV" in the DB.
        # Create one via POST /users or seed the DB manually.
        dev_user = await user_service.get_by_slack_user_id("DEV")
        if dev_user is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "DEV_MODE is enabled but no dev user found. "
                    "Create a user with slack_user_id='DEV' in the DB first."
                ),
            )
        request.state.user = dev_user
        return

    await verify_slack_request(request)
    user = await get_current_slack_user(request, user_service, slack_client)
    request.state.user = user
