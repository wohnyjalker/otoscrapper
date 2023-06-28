from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator


class Advertisement(Model):
    adv_id = fields.CharField(max_length=255)
    year = fields.IntField(null=True)
    mileage = fields.IntField(null=True)
    engine_capacity = fields.IntField(null=True)
    fuel_type = fields.CharField(max_length=255, null=True)
    price = fields.FloatField(null=True)
    url = fields.CharField(max_length=255)
    title = fields.CharField(max_length=255)
    brand = fields.CharField(max_length=255)
    model = fields.CharField(max_length=255)


Advertisement_Pydantic = pydantic_model_creator(Advertisement)
