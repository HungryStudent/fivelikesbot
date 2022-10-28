import asyncio

from utils.db import reset_rating


async def main():
    await reset_rating()

asyncio.run(main())