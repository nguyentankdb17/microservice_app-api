import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def verify_user_token(token: str):
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = await client.get(f"{os.getenv("USER_SERVICE_URL")}/api/user/user-info", headers=headers)
            response.raise_for_status()
            return response.json() # return user information
        except httpx.HTTPStatusError as e:
            raise Exception("Unauthorized: Invalid token")
