from aiohttp import web

#
# async def hello(request):
#     return web.Response(text="Hello, world")
#
#
# async def dupa(request):
#     return web.Response(text="dupa")
#
#
# app = web.Application()
# app.add_routes([web.get('/', hello)])
# app.add_routes([web.post('/', dupa)])
#
# web.run_app(app)

# search: https://www.otomoto.pl/osobowe/bmw/x3?search[order]=created_at_first:desc&page=3
#
# 6100851901 https://www.otomoto.pl/oferta/bmw-seria-5-2xm-pakiet-x-drive-zawiesz-pneumatyczne-hedup-webasto-alcantara-fv23-ID6ESyh7.html
# https://www.otomoto.pl/api/v1/ad/6100851901
#
# phone number
# 6098801334 https://www.otomoto.pl/oferta/bmw-seria-4-420d-f32-sport-line-polski-salon-ID6EJVPs.html
# 6EJVPs
# curl https://www.otomoto.pl/ajax/misc/contact/all_phones/6ESyh7/
#
#
# wiecej od tego uzytkownika:
# https://www.otomoto.pl/api/v1/recommenders/ad/6100851901

import asyncio
import aiohttp
import itertools
from lxml.html import fromstring
from typing import Union
import time


# url = "https://www.otomoto.pl/osobowe/bmw/m2?search%5Border%5D=created_at_first%3Adesc&page=1"
url_with_query = "https://www.otomoto.pl/osobowe/bmw/m2?search%5Border%5D=created_at_first:desc"
ad_json_url = "https://www.otomoto.pl/api/v1/ad/{}/"
db = dict()
ssl = True


def concatenate_lists(list_: Union[list, tuple]) -> list:
    return list(itertools.chain.from_iterable(list_))


async def get_pages_count(session: aiohttp.ClientSession, url: str) -> int:
    async with session.get(url, ssl=ssl) as r:
        text = await r.text()
        return len(fromstring(text).xpath(".//ul[contains(@class, 'pagination-list')]/li/a/span"))


async def get_ids(session: aiohttp.ClientSession, url: str, pages_count: int) -> list:
    tasks = list()
    for page in range(1, pages_count + 1):
        tasks.append(get_ids_from_page(session, f"{url}&page={page}"))

    results = await asyncio.gather(*tasks)
    return concatenate_lists(results)


async def get_ids_from_page(session: aiohttp.ClientSession, page_url: str) -> list:
    async with session.get(page_url, ssl=ssl) as r:
        # print(r.status, page_url)
        html = await r.text()
        return [a.attrib["id"] for a in fromstring(html).xpath("//article[@id]") if a.attrib["id"].isnumeric()]


async def get_advertisements_data(session: aiohttp.ClientSession, ids: list) -> list:
    tasks = list()
    for id_ in ids:
        tasks.append(get_single_ad_data(session, id_))

    results = await asyncio.gather(*tasks)
    return results


async def get_single_ad_data(session: aiohttp.ClientSession, id_: str) -> dict:
    async with session.get(ad_json_url.format(id_), ssl=ssl) as r:
        # print(r.status, id_)
        json = await r.json()
        return json


async def gather_ads_data(url: str) -> int:
    started_at = time.monotonic()
    async with aiohttp.ClientSession() as session:
        pages_count = await get_pages_count(session, url)
        ids = await get_ids(session, url, pages_count)
        results = await get_advertisements_data(session, ids)
        print(results)
    print(f"Took: {time.monotonic() - started_at}")
    return results
    # return len(results)


# if __name__ == "__main__":
#     asyncio.run(gather_ads_data("https://www.otomoto.pl/osobowe/bmw/i3?search%5Border%5D=created_at_first:desc"))
#     url1 = "https://www.otomoto.pl/osobowe/bmw/i3?search%5Border%5D=created_at_first:desc"
#     url2 = "https://www.otomoto.pl/osobowe/bmw/m2?search%5Border%5D=created_at_first:desc"
# async def hello(request):
#     return web.Response(text="Hello, world")


# async def dupa(request):
#     loop = asyncio.get_event_loop()
#     print(loop)
#     task = await loop.create_task(gather_ads_data("https://www.otomoto.pl/osobowe/bmw/i3?search%5Border%5D=created_at_first:desc"))
#     return web.json_response(task)


async def handle_get(request):
    loop = asyncio.get_event_loop()
    url = f"https://www.otomoto.pl{request.rel_url}"
    print(f"Proceeding {url}")
    data = await loop.create_task(gather_ads_data(url))
    return web.json_response(data)


async def dupa(request):
    pass


app = web.Application()
app.add_routes([web.post("/", dupa), web.get("/osobowe/{brand}/{model}", handle_get)])

web.run_app(app)


# queue = asyncio.Queue(maxsize=1)
# queue.put_nowait(gather_ads_data(url1))


# loop = asyncio.get_event_loop()
# loop.create_future()
# loop.run_until_complete(gather_ads_data(url2))
# f1 = asyncio.run_coroutine_threadsafe(gather_ads_data(url1), loop)
# f2 = asyncio.run_coroutine_threadsafe(gather_ads_data(url2), loop)
# print(f1.result())
# loop.create_task(gather_ads_data(url2), name="url2")
# loop.run_forever()
# loop.run_forever()
# loop = asyncio.get_event_loop()
# loop.create_task(gather_ads_data(url2), name="url2")
# asyncio.run(main())
# asyncio.run_coroutine_threadsafe(gather_ads_data(url1), loop)
# asyncio.run_coroutine_threadsafe(gather_ads_data(url2), loop)
# loop.run_until_complete()
# loop = asyncio.get_event_loop()
# task = asyncio.ensure_future(gather_ads_data(url1))
# task.add_done_callback(done_ome())
# # task = add_success_callback(task, my_callback)
# response = loop.run_until_complete(task)
# print("response:", response)
# loop.close()
