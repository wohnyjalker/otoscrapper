import asyncio
import logging
import os
import time

from aiohttp import web
from aiohttp.web_response import Response
from tortoise.contrib.aiohttp import register_tortoise
from tortoise.queryset import Q

from helpers import map_query_to_advertisement_queryset, add_to_db, log_execution_time
from models import Advertisement, Advertisement_Pydantic
from scrappers.otoscrapper import gather_advertisements_data


logger = logging.getLogger("server")
TimeMonotonic = float


def response_dict(message: str, started_at: TimeMonotonic) -> dict:
    return {"message": message, "operation_time": time.monotonic() - started_at}


@log_execution_time
async def handle_scrap_url(request) -> Response:
    started_at = time.monotonic()
    request_json = await request.json()
    brand, model = request_json.get("brand"), request_json.get("model")

    if not brand:
        raise web.HTTPBadRequest(reason="missing brand")
    if not model:
        raise web.HTTPBadRequest(reason="missing model")

    ids_in_db = [a.get("adv_id") for a in await Advertisement.filter(Q(brand=brand), Q(model=model)).values("adv_id")]
    gathered_advertisements_data = await gather_advertisements_data(brand, model, excluded_ids=ids_in_db)

    if not gathered_advertisements_data:
        return web.json_response(
            response_dict(f"No new entries for {brand} {model}, nothing to scrap", started_at)
        )

    to_bulk_add = await asyncio.gather(*[add_to_db(a, brand, model) for a in gathered_advertisements_data])
    added_count = len(await Advertisement.bulk_create(to_bulk_add))

    return web.json_response(
        response_dict(f"Added {added_count} new entries for {brand} {model}", started_at)
    )


@log_execution_time
async def handle_get_cars(request) -> Response:
    query_parameters, comparable_parameters = map_query_to_advertisement_queryset(request)
    adverts = await Advertisement.filter(*query_parameters, **comparable_parameters)

    if not adverts:
        return web.json_response({})
    adverts_pydantic = await asyncio.gather(*map(Advertisement_Pydantic.from_tortoise_orm, adverts))

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
register_tortoise(
    app, db_url=os.getenv("DATABASE_URL", "sqlite://db.sqlite3"), modules={"models": ["models"]}, generate_schemas=True
)

if __name__ == "__main__":
    web.run_app(app)
