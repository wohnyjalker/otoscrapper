# from aiohttp import web

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
import sre_parse


# from requests import get
#
#
# r = get("https://www.otomoto.pl/osobowe/bmw/m2?search%5Border%5D=created_at_first%3Adesc&page=1")
# if r.status_code != 200:
#     print(f"{r.status_code} != 200")
#     exit(1)
# tree = fromstring(r.text)
# pages_count = len(tree.xpath(".//ul[contains(@class, 'pagination-list')]/li/a/span"))
# print(pages_count)

import asyncio
import aiohttp
from datetime import datetime
import itertools
from lxml.html import fromstring
from typing import Union


# url = "https://www.otomoto.pl/osobowe/bmw/m2?search%5Border%5D=created_at_first%3Adesc&page=1"
url_with_query = "https://www.otomoto.pl/osobowe/bmw/m2?search%5Border%5D=created_at_first:desc"
ad_json_url = "https://www.otomoto.pl/api/v1/ad/{}/"
db = dict()
ssl = True


def concatenate_lists(l: Union[list, tuple]) -> list:
    return list(itertools.chain.from_iterable(l))


def time_now() -> str:
    return datetime.strftime(datetime.utcnow(), "%H:%M:%S")


async def get_pages_count(url: str) -> int:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=ssl) as r:
            print(r.status)
            text = await r.text()
            return len(fromstring(text).xpath(".//ul[contains(@class, 'pagination-list')]/li/a/span"))


async def get_ids(url: str, pages_count: int) -> list:
    tasks = list()
    async with aiohttp.ClientSession() as session:
        for page in range(1, pages_count + 1):
            tasks.append(get_ids_from_page(session, f"{url}&page={page}"))

        results = await asyncio.gather(*tasks)
        return concatenate_lists(results)


async def get_ids_from_page(session: aiohttp.ClientSession, page_url: str) -> list:
    async with session.get(page_url, ssl=ssl) as r:
        print(r.status, page_url)
        html = await r.text()
        return [a.attrib["id"] for a in fromstring(html).xpath("//article[@id]") if a.attrib["id"].isnumeric()]


async def get_advertisements_data(ids: list) -> list:
    tasks = list()
    async with aiohttp.ClientSession() as session:
        for id_ in ids:
            tasks.append(get_single_ad_data(session, id_))

        results = await asyncio.gather(*tasks)
        return results


async def get_single_ad_data(session: aiohttp.ClientSession, id_: str) -> dict:
    async with session.get(ad_json_url.format(id_), ssl=ssl) as r:
        print(r.status, id_)
        json = await r.json()
        return json


async def main():
    started_at = time_now()
    pages = await get_pages_count(url_with_query)
    ids = await get_ids(url_with_query, pages)
    print(ids)
    results = await get_advertisements_data(ids)
    print(results)
    print(f'started ad started at {started_at} finished at {time_now()}')
    print(len(results))


if __name__ == "__main__":
    asyncio.run(main())
