import random
import string
from typing import List
from app.catalog.schemas import CategoryFilters


async def generate_random_string(n: int):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))


# async def generate_query_filtering_product_for_sql(category_id: int, query: QuryProducts):
#
# sql = f'''select *
# from product p , (
# select id
# from product ,jsonb_to_recordset(product.attributes) as items(name text, value text)
# where
# (items.name = 'Встроенная память' and items.value::integer > 1)
# or
# (items.name = 'Диагональ' and items.value::float > 3.5)
# group by id
# having count(id) > 1) as p2
# where p.id = p2.id
# '''
# and
# 33000 <=p.price
# and
# p.price <= 50000
# if query.min_price:
# sql += f''' and {query.min_price} <= p.price'''
# if query.max_price:
# sql += f''' and p.price <= {query.max_price}'''
# return sql
