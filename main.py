from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from app.auth.context import slack_context
from app.core.exceptions import ConflictError, NotFoundError
from app.routes.holiday import holiday_router
from app.routes.reservation import reservation_router
from app.routes.system_settings import system_settings_router
from app.routes.user import user_router

app = FastAPI(dependencies=[Depends(slack_context)])


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": exc.message})


app.include_router(user_router)
app.include_router(system_settings_router)
app.include_router(holiday_router)
app.include_router(reservation_router)
