import asyncio
import logging
import time

import aiohttp.web
from aiohttp import web
from aiohttp.web_response import Response
from tortoise.contrib.aiohttp import register_tortoise

from helpers import dict_to_model, map_query_to_advertisement_queryset
from models import Advertisement, Advertisement_Pydantic
from scrappers.otoscrapper import gather_ads_data


logger = logging.getLogger("server")


async def handle_scrap_url(request) -> Response:
    loop = asyncio.get_event_loop()
    data = await request.json()
    brand, model = data.get("brand"), data.get("model")
    if not brand:
        raise aiohttp.web.HTTPBadRequest(reason="missing brand")
    if not model:
        raise aiohttp.web.HTTPBadRequest(reason="missing model")
    ads_data = await loop.create_task(gather_ads_data(brand, model))
    started_at = time.monotonic()
    jsons_res = await asyncio.gather(*[dict_to_model(a, brand, model) for a in ads_data])
    logger.info(f"Adding to db took: {time.monotonic() - started_at}")
    return web.json_response(jsons_res)


async def handle_get_cars(request) -> Response:
    query_parameters, comparable_parameters = map_query_to_advertisement_queryset(request)
    adverts = await Advertisement.filter(*query_parameters, **comparable_parameters)
    if not adverts:
        return web.json_response({})
    tasks = [Advertisement_Pydantic.from_tortoise_orm(advert) for advert in adverts]
    adverts_pydantic = await asyncio.gather(*tasks)

    logger.info(f"Collected {len(adverts)}")
    return web.json_response([a.dict() for a in adverts_pydantic])


app = web.Application()
logging.basicConfig(level=logging.INFO)
app.add_routes(
    [
        web.post("/scrap", handle_scrap_url),
        web.get("/cars", handle_get_cars),
    ]
)
# register_tortoise(app, db_url="sqlite://db.sqlite3", modules={"models": ["models"]}, generate_schemas=True)
register_tortoise(
   app, db_url="postgres://postgres:postgres@db:5432/postgres", modules={"models": ["models"]}, generate_schemas=True
)

if __name__ == "__main__":
    web.run_app(app)
