import asyncio
import aiohttp
import time


urls = [
    "localhost:8080/osobowe/bmw/m2?search%5Border%5D=created_at_first:desc",
    "localhost:8080/osobowe/bmw/z3",
    "localhost:8080/osobowe/bmw/m3",
    "localhost:8080/osobowe/bmw/m4",
    # "localhost:8080/osobowe/bmw/asdf",
]


async def get_data(session: aiohttp.ClientSession, url: str) -> dict:
    started_at = time.monotonic()
    async with session.get(f"http://{url}") as r:
        data = await r.json()
    print(f"{r.status} {time.monotonic() - started_at} {url} {len(data)}")
    return data


async def validate() -> None:
    async with aiohttp.ClientSession() as session:
        tasks = [get_data(session, url) for url in urls]
        output = await asyncio.gather(*tasks)
        print(f"Collected: {sum(map(len, output))} items")


if __name__ == "__main__":
    started_at = time.monotonic()
    asyncio.run(validate())
    print(f"Script took {time.monotonic() - started_at}")
