import asyncio
import time
from aiohttp import web

from models import Advertisement, Advertisement_Pydantic
from tortoise.contrib.aiohttp import register_tortoise
from tortoise.queryset import Q

from scrappers.otoscrapper import gather_ads_data


async def dict_to_model(advertisement_dict: dict, brand: str, model: str) -> dict:
    id_ = next(iter(advertisement_dict))
    d = advertisement_dict[id_]
    params = d["params"]
    try:
        advert, crated = await Advertisement.get_or_create(
            adv_id=int(id_),
            year=int(params["year"]["value"]),
            mileage=int(params["mileage"]["value"]),
            engine_capacity=int(params["engine_capacity"]["value"]),
            fuel_type=params["fuel_type"]["value"],
            price=float(params["price"]["price_raw"]),
            url=d["url"],
            title=d["title_full"],
            brand=brand,
            model=model,
        )
        print(f"Previously in db: {not crated} - {advert.title}")
        advert_pydantic = await Advertisement_Pydantic.from_tortoise_orm(advert)
        return advert_pydantic.dict()
    except KeyError:
        return {}


async def handle_scrap_url(request):
    loop = asyncio.get_event_loop()
    url = f"https://www.otomoto.pl{request.path}"
    print(f"Proceeding {url}")
    brand = request.match_info.get("brand")
    model = request.match_info.get("model")

    data = await loop.create_task(gather_ads_data(url))

    started_at = time.monotonic()
    tasks = [dict_to_model(d, brand, model) for d in data]
    jsons = await asyncio.gather(*tasks)
    print(f"Adding to db took: {time.monotonic() - started_at}")
    return web.json_response(jsons)


async def handle_get_cars(request):
    brand = request.rel_url.query.get("brand")
    model = request.rel_url.query.get("model")
    year = request.rel_url.query.get("year")
    price_lte = request.rel_url.query.get("price[lte]")
    price_gte = request.rel_url.query.get("price[gte]")
    comparables = {"price__lte": price_lte, "price__gte": price_gte}
    queries = [Q(brand=brand), Q(model=model), Q(year=year)]

    comparable_parameters = {k: v for k, v in comparables.items() if v}
    query_parameters = [q for q in queries if next(iter(q.filters.values()))]

    adverts = await Advertisement.filter(*query_parameters, **comparable_parameters)
    if not adverts:
        return web.json_response({})
    print(f"Collected {len(adverts)}")
    tasks = [Advertisement_Pydantic.from_tortoise_orm(advert) for advert in adverts]
    adverts_pydantic = await asyncio.gather(*tasks)

    return web.json_response([a.dict() for a in adverts_pydantic])


app = web.Application()
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
