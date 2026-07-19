from fastapi import Depends, FastAPI

from app.auth.context import slack_context
from app.routes.holiday import holiday_router
from app.routes.system_settings import system_settings_router
from app.routes.user import user_router

app = FastAPI(dependencies=[Depends(slack_context)])

app.include_router(user_router)
app.include_router(system_settings_router)
app.include_router(holiday_router)
