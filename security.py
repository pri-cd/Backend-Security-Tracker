import os
import hmac
import hashlib
from fastapi import Request, HTTPException

SECRET_KEY = os.getenv("HMAC_API_SECURE_KEY")

async def verify_signature(request: Request) -> bool:

    client_signature = request.headers.get("X-Signature")
    if not client_signature: 
        raise HTTPException(status_code=401, detail="Missing X-Signature header")

    body = await request.body()

    expect_signature = hmac.new(
        SECRET_KEY.encode('utf-8'), 
        body, digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(client_signature, expect_signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    return True
