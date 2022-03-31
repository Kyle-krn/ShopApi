from itertools import product
from ..base.service_base import BaseService
from . import schemas, models

class CategoryService(BaseService):
    model = models.Category
    create_schema = schemas.CreateCategory
    get_schema = schemas.GetCategory


class ProductService(BaseService):
    model = models.Product
    create_schema = schemas.CreateProduct
    get_schema = schemas.GetProduct


category_s = CategoryService()
product_s = ProductService()