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
import itertools
import time
from typing import Union, Tuple
from aiohttp import ClientSession, web
from lxml.html import fromstring


AD_JSON_URL = "https://www.otomoto.pl/api/v1/ad/{}/"
SSL = True


def concatenate_lists(list_: Union[list, tuple]) -> list:
    return list(itertools.chain.from_iterable(list_))


async def get_pages_count(session: ClientSession, url: str) -> int:
    async with session.get(url, ssl=SSL) as response:
        text = await response.text()
        return int(fromstring(text).xpath(
            ".//ul[contains(@class, 'pagination-list')]/li/a/span")[-1].text)


async def get_ids(session: ClientSession, url: str, pages_count: int) -> list:
    tasks = list()
    for page in range(1, pages_count + 1):
        tasks.append(get_ids_from_page(session, f"{url}&page={page}"))

    results = await asyncio.gather(*tasks)
    return concatenate_lists(results)


async def get_ids_from_page(session: ClientSession, page_url: str) -> list:
    async with session.get(page_url, ssl=SSL) as response:
        # print(r.status, page_url)
        html = await response.text()
        return [a.attrib["id"] for a in fromstring(html).xpath(
            "//article[@id]") if a.attrib["id"].isnumeric()]


async def get_advertisements_data(session: ClientSession, ids: list) -> tuple:
    tasks = list()
    for id_ in ids:
        tasks.append(get_single_ad_data(session, id_))

    results = await asyncio.gather(*tasks)
    return results


async def get_single_ad_data(session: ClientSession, id_: str) -> dict:
    async with session.get(AD_JSON_URL.format(id_), ssl=SSL) as response:
        # print(r.status, id_)
        json = await response.json()
        return json


async def gather_ads_data(url: str) -> Tuple[dict]:
    started_at = time.monotonic()
    async with ClientSession() as session:
        pages_count = await get_pages_count(session, url)
        ids = await get_ids(session, url, pages_count)
        print(f"For {url} collected {len(ids)} ids")
        results = await get_advertisements_data(session, ids)
    print(f"Took: {time.monotonic() - started_at}")
    return results


async def handle_get(request):
    loop = asyncio.get_event_loop()
    # url = f"https://www.otomoto.pl{request.rel_url}"
    url = f"https://www.otomoto.pl{request.path}"
    print(f"Proceeding {url}")
    data = await loop.create_task(gather_ads_data(url))
    return web.json_response(data)


if __name__ == "__main__":
    app = web.Application()
    app.add_routes([web.get("/osobowe/{brand}/{model}", handle_get)])
    web.run_app(app)
