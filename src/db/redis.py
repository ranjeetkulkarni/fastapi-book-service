import redis.asyncio as aioredis
from .main import get_session # Just in case, though not strictly needed for this file alone

# 1. Connect to Redis (Ensure Redis is running!)
# decode_responses=True gives us Strings instead of Bytes
token_blocklist = aioredis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# 2. Add Token to Blocklist (JTI = JWT ID)
async def add_jti_to_blocklist(jti: str) -> None:
    # Save token ID for 3600 seconds (1 hour)
    await token_blocklist.set(name=jti, value="", ex=3600)

# 3. Check if Token is Blocked
async def token_in_blocklist(jti: str) -> bool:
    jti = await token_blocklist.get(jti)
    return jti is not None