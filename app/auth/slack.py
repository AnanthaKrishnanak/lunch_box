from fastapi import HTTPException, Request, status
from slack_sdk.signature import SignatureVerifier

from app.core.settings import settings

signature_verifier = SignatureVerifier(settings.SLACK_SIGNING_SECRET)


async def verify_slack_request(request: Request) -> None:
    body = await request.body()

    if not signature_verifier.is_valid_request(
        body=body,
        headers=request.headers,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Slack signature",
        )
