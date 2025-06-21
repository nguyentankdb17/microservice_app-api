import time
from fastapi import Request, HTTPException
from typing import Dict, List


class RateLimiter:
    def __init__(self, times: int, seconds: int) -> None:
        self.times: int = times
        self.seconds: int = seconds
        self.requests: Dict[str, List[float]] = {}

    async def __call__(self, request: Request) -> None:
        client_ip: str = request.client.host
        current_time: float = time.time()

        # Initialize the client's request history if not already present
        if client_ip not in self.requests:
            self.requests[client_ip] = []

        # Filter out timestamps that are outside of the rate limit period
        self.requests[client_ip] = [
            timestamp
            for timestamp in self.requests[client_ip]
            if timestamp > current_time - self.seconds
        ]

        # Check if the number of requests exceeds the allowed limit
        if len(self.requests[client_ip]) >= self.times:
            raise HTTPException(status_code=409, detail="Too many requests, please try again later.")

        # Record the current request timestamp
        self.requests[client_ip].append(current_time)