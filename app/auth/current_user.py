from typing import cast

from fastapi import Request

from app.core.deps import SlackClientDeps, UserServiceDeps
from app.models.user import User
from app.schemas.user import UserCreate


async def get_current_slack_user(
    request: Request,
    user_service: UserServiceDeps,
    slack_client: SlackClientDeps,
) -> User:
    form = await request.form()

    slack_user_id = cast(str, form["user_id"])
    team_id = cast(str, form["team_id"])
    name = cast(str, form["user_name"])

    slack_user = await slack_client.users_info(user=slack_user_id)

    profile = slack_user["user"]["profile"]
    email = profile.get("email")

    existing_user = await user_service.get_by_slack_user_id(slack_user_id)
    if existing_user:
        return existing_user

    return await user_service.create(
        UserCreate(
            slack_user_id=slack_user_id,
            team_id=team_id,
            name=name,
            email=email,
        ),
    )
