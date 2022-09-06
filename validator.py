import asyncio
import aiohttp
import time


urls = [
    "localhost:8080/osobowe/bmw/m2?search%5Border%5D=created_at_first:desc",
    "localhost:8080/osobowe/bmw/z3",
    "localhost:8080/osobowe/bmw/m3",
    "localhost:8080/osobowe/bmw/m4",
]


async def get_data(url):
    started_at = time.monotonic()
    async with aiohttp.ClientSession() as session:
        async with session.get("http://" + url) as r:
            print(r.status)
            data = await r.json()
    print(f"Url {url} took {time.monotonic() - started_at}")
    return data


async def validate():
    tasks = [get_data(url) for url in urls]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    started_at = time.monotonic()
    asyncio.run(validate())
    print(f"Script took {time.monotonic() - started_at}")
