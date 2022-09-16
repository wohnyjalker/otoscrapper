from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator


class Advertisement(Model):
    adv_id = fields.CharField(max_length=255)
    year = fields.IntField()
    mileage = fields.IntField()
    engine_capacity = fields.IntField()
    fuel_type = fields.CharField(max_length=255)
    price = fields.FloatField()
    url = fields.CharField(max_length=255)
    title = fields.CharField(max_length=255)
    brand = fields.CharField(max_length=255)
    model = fields.CharField(max_length=255)


Advertisement_Pydantic = pydantic_model_creator(Advertisement)
