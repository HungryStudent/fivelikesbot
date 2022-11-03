from utils.db import reset_rating
import asyncio


async def main():
    await reset_rating()


asyncio.run(main())
