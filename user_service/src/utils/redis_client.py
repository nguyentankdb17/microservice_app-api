import redis
from dotenv import load_dotenv
import os

load_dotenv()

redis_client = redis.Redis(
    host=os.getenv("REDIS_URL"),
    port=6379,
    db=0,
    decode_responses=True
)
