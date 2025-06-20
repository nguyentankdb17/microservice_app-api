import httpx
from fastapi import HTTPException, Request, status
import os
from dotenv import load_dotenv

load_dotenv()


async def verify_token(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{os.getenv('USER_SERVICE_URL')}/api/user/user-info",
                headers=headers,
            )
            res.raise_for_status()
            return res.json()
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired token",
        )


async def require_admin(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=403, detail="Authorization header missing"
        )

    token = auth_header.replace("Bearer ", "")
    user = await verify_token(token)

    if not user.get("is_admin"):
        raise HTTPException(
            status_code=403,
            detail=(
                "Admin feature only. "
                "You do not have permission to access this feature."
            ),
        )

    return user
