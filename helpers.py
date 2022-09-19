import time
from logging import getLogger
import aiohttp
from tortoise.queryset import Q
from models import Advertisement, Advertisement_Pydantic


AdvertisementQuerySet = tuple[list, dict]
logger = getLogger(__name__)


def map_query_to_advertisement_queryset(request: aiohttp.request) -> AdvertisementQuerySet:
    brand = request.rel_url.query.get("brand")
    model = request.rel_url.query.get("model")
    year = request.rel_url.query.get("year")
    price_lte = request.rel_url.query.get("price[lte]")
    price_gte = request.rel_url.query.get("price[gte]")
    comparables = {"price__lte": price_lte, "price__gte": price_gte}
    queries = [Q(brand=brand), Q(model=model), Q(year=year)]

    comparable_parameters = {k: v for k, v in comparables.items() if v}
    query_parameters = [q for q in queries if next(iter(q.filters.values()))]
    return query_parameters, comparable_parameters


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
        logger.info(f"Previously in db: {not crated} - {advert.adv_id} {advert.title}")
        advert_pydantic = await Advertisement_Pydantic.from_tortoise_orm(advert)
        return advert_pydantic.dict()
    except KeyError:
        return {}


def log_execution_time(func):
    async def wrapper(*args, **kwargs):
        started_at = time.monotonic()
        f = await func(*args, **kwargs)
        logger.info(f"{func.__name__} took {time.monotonic() - started_at}")
        return f
    return wrapper
