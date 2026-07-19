from fastapi import Depends, FastAPI

from app.auth.context import slack_context
from app.routes.user import user_router

app = FastAPI(dependencies=[Depends(slack_context)])

app.include_router(user_router)
