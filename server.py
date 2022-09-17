import asyncio
import logging
import time

from aiohttp import web
from aiohttp.web_response import Response
from tortoise.contrib.aiohttp import register_tortoise

from helpers import dict_to_model, map_query_to_advertisement_queryset
from models import Advertisement, Advertisement_Pydantic
from scrappers.otoscrapper import gather_ads_data


logger = logging.getLogger()


async def handle_scrap_url(request) -> Response:
    loop = asyncio.get_event_loop()
    url = f"https://www.otomoto.pl{request.path}"
    logger.info(f"Proceeding {url}")
    brand = request.match_info.get("brand")
    model = request.match_info.get("model")

    data = await loop.create_task(gather_ads_data(url))
    started_at = time.monotonic()
    tasks = [dict_to_model(d, brand, model) for d in data]
    jsons = await asyncio.gather(*tasks)
    logger.info(f"Adding to db took: {time.monotonic() - started_at}")
    return web.json_response(jsons)


async def handle_get_cars(request) -> Response:
    query_parameters, comparable_parameters = map_query_to_advertisement_queryset(request)
    adverts = await Advertisement.filter(*query_parameters, **comparable_parameters)
    if not adverts:
        return web.json_response({})
    logger.info(f"Collected {len(adverts)}")
    tasks = [Advertisement_Pydantic.from_tortoise_orm(advert) for advert in adverts]
    adverts_pydantic = await asyncio.gather(*tasks)

    return web.json_response([a.dict() for a in adverts_pydantic])


app = web.Application()
logging.basicConfig(level=logging.INFO)
app.add_routes(
    [
        web.get("/osobowe/{brand}/{model}", handle_scrap_url),
        web.get("/cars", handle_get_cars),
    ]
)
# register_tortoise(app, db_url="sqlite://db.sqlite3", modules={"models": ["models"]}, generate_schemas=True)
register_tortoise(
    app, db_url="postgres://postgres:postgres@db:5432/postgres", modules={"models": ["models"]}, generate_schemas=True
)

if __name__ == "__main__":
    web.run_app(app)
