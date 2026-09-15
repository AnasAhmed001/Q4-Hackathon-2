import asyncio

from sqlalchemy import text

from src.database import engine


async def main() -> None:
    try:
        async with engine.connect() as conn:
            v = await conn.scalar(text("select 1"))
            print("db_ok", v)
    except Exception as e:
        print("db_error", type(e).__name__, str(e))


if __name__ == "__main__":
    asyncio.run(main())
