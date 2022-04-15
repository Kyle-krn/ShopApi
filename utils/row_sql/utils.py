from ctypes import Union
import random
import string
from typing import List
import logging
from fastapi import HTTPException
from app.catalog.models import Category

from app.catalog.schemas import CategoryFilters, QuryProducts


async def generate_string_sql_query(category_attrs: List[CategoryFilters]):
    value_list_for_product = [] # Когда добавляется атрибут для всей категории в товары всегда улетает {"name": "name": "value": None}
    value_list_for_category = []    # А для категорий {"name": "name": "value": Any, "prefix": "prefix"}
    for attr in category_attrs:        
        if type(attr.value) == list:
            value_string = "[]"

        elif type(attr.value) == str:
            value_string = '"' + attr.value + '"'

        elif type(attr.value) in [int, float]:
            print(attr.value)
            value_string = str(attr.value)
        
        elif type(attr.value) == bool:
            if attr.value is True:
                value_string = 'true'
            else:
                value_string = 'false'
        category_attr_sql_string = "'" + '{"name": "%s", "value": %s, "prefix": "%s"}' % (attr.name, value_string, attr.prefix) + "'"
        product_attr_sql_string = "'" + '{"name": "%s", "value": null, "prefix": "%s"}' % (attr.name, attr.prefix) + "'"
        value_list_for_category.append(category_attr_sql_string)
        value_list_for_product.append(product_attr_sql_string)
    return " || ".join(value_list_for_category), " || ".join(value_list_for_product)


class GenerateQuerySearchAttr:
    def  __init__(self, category: Category, query: QuryProducts) -> None:
        self.query = query
        self.category = category

    async def get_sql(self) -> str:
        # category = await Category.get(id=category_id)
        attrs_sql = []
        for item in self.query.attributes:
            filter = [i for i in self.category.filters if i['name'] == item['name']]
            if len(filter) == 0:
                continue
            if type(filter[0]['value']) in [int, float]:
                digit_str_sql = await self.digit_attr(item['min'], item['max'], item['name'])
                attrs_sql.append(digit_str_sql)
            if type(filter[0]['value']) == str:
                attrs_sql.append(await self.str_attr(item))
            if type(filter[0]['value']) == list:
                attrs_sql.append(await self.list_attr(item))
            if type(filter[0]['value']) == bool:
                attrs_sql.append(await self.bool_attr(item))
        # if len(attrs_sql) == 1:
        return ' and ' + " or ".join(attrs_sql)
        # elif len(attrs_sql) > 1:
        #     return 

    async def digit_attr(self, min, max, name: str) -> str:
        if name and min and max:
            return f'''(items.name = '{name}' and (items.value::float >={min} and items.value::float <= {max}))'''
        elif name and min:
            return f'''(items.name = '{name}' and items.value::float >={min})'''
        elif name and max:
            return f'''(items.name = '{name}' and items.value::float <={min})'''
        elif name:
            return f'''(items.name = '{name}')'''
# '''(items.name = 'Процессор' and (items.value::text = 'Apple A8' or items.value::text = 'Apple A10'))'''
    
    async def str_attr(self, item: dict):
        if item['value']:
            return f"(items.name = '{item['name']}' and " +  \
                        "(" + " or ".join([f"items.value::text = '{i}'"  for i in item['value']]) + "))"
        else:
            return f" (items.name = '{item['name']}')"

    async def list_attr(self, item: dict):
        if item['value']:
            return f"(items.name = '{item['name']}' and " +  \
                        "(" + " or ".join([f"items.value::text like '%{i}%'"  for i in item['value']]) + "))"
        else:
            return f" (items.name = '{item['name']}')"

    async def bool_attr(self, item: dict):
        if item['value'] is True:
            item['value'] = 'true'
        elif item['value'] is False:
            item['value'] = 'false'
        return f"(items.name = '{item['name']}' and (items.value::bool = {item['value']}))"


# like '%пластик%'