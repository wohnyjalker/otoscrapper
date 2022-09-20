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
from typing import Union, Tuple, Optional
from logging import getLogger
from aiohttp import ClientSession
from lxml.html import fromstring
from user_agent import generate_user_agent


PAGE_URL = "https://www.otomoto.pl/osobowe/{}/{}"
AD_JSON_URL = "https://www.otomoto.pl/api/v1/ad/{}/"
SSL = True
logger = getLogger(__name__)


def concatenate_lists(list_: Union[list, tuple]) -> list:
    return list(itertools.chain.from_iterable(list_))


async def scrap_pages_count(session: ClientSession, url: str) -> int:
    async with session.get(url, ssl=SSL) as response:
        text = await response.text()
        pages = fromstring(text).xpath(".//ul[contains(@class, 'pagination-list')]/li/a/span")
        if not pages:
            return 1
        return int(pages[-1].text)


async def scrap_ids(session: ClientSession, url: str, pages_count: int) -> list:
    tasks = [scrap_ids_from_page(session, f"{url}?page={page}") for page in range(1, pages_count+1)]
    return concatenate_lists(await asyncio.gather(*tasks))


async def scrap_ids_from_page(session: ClientSession, page_url: str) -> list:
    async with session.get(page_url, ssl=SSL) as response:
        return [
            a.attrib["id"]
            for a in fromstring(await response.text()).xpath("//article[@id]")
            if a.attrib["id"].isnumeric()
        ]


async def get_advertisements_data(session: ClientSession, ids: Union[list, set]) -> tuple:
    return await asyncio.gather(*[get_single_ad_data(session, idx) for idx in ids])


async def get_single_ad_data(session: ClientSession, id_: str) -> dict:
    async with session.get(AD_JSON_URL.format(id_), ssl=SSL) as response:
        return await response.json()


async def scrap_advertisements_ids(url: str) -> list:
    headers = {"User-Agent": generate_user_agent()}
    logger.info(f"Proceeding {url}")
    async with ClientSession(headers=headers) as session:
        pages_count = await scrap_pages_count(session, url)
        ids = await scrap_ids(session, url, pages_count)
    return ids


async def gather_advertisements_json_data(ids: list) -> Tuple[dict]:
    headers = {"User-Agent": generate_user_agent()}
    async with ClientSession(headers=headers) as session:
        return await get_advertisements_data(session, ids)


# async def gather_ads_data(brand: str, model: str, excluded_ads_ids: list) -> Tuple[dict]:
#     url = PAGE_URL.format(brand, model)
#     started_at = time.monotonic()
#     logger.info(f"Proceeding {url}")
#
#     ids = await scrap_advertisements_ids(url)
#     data = await gather_advertisements_json_data(ids)
#
#     logger.info(f"Took: {time.monotonic() - started_at}")
#     return data

async def gather_advertisements_data(brand: str, model: str, excluded_ids: Optional[list] = None) -> Optional[Tuple[dict]]:
    url = PAGE_URL.format(brand, model)
    headers = {"User-Agent": generate_user_agent()}
    logger.info(f"Proceeding {url}")
    started_at = time.monotonic()
    async with ClientSession(headers=headers) as session:
        pages_count = await scrap_pages_count(session, url)
        ids = await scrap_ids(session, url, pages_count)

        logger.info(f"For {url} collected {len(ids)} ids")
        ids_to_process = set(map(int, ids)) - set(map(int, excluded_ids))
        if not ids_to_process:
            return
        logger.info(f"To process {len(ids_to_process)} items: {ids_to_process}")
        results = await get_advertisements_data(session, ids_to_process)
    logger.info(f"Took: {time.monotonic() - started_at}")
    return results
