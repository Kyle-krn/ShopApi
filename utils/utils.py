from typing import List
from app.catalog.schemas import CategoryFilters


async def generate_string_sql_query(category_attrs: List[CategoryFilters]):
    value_list_for_product = [] # Когда добавляется атрибут для всей категории в товары всегда улетает {"name": "name": "value": None}
    value_list_for_category = []    # А для категорий {"name": "name": "value": Any, "prefix": "prefix"}
    for attr in category_attrs:        
        if type(attr.value) == list:
            value_string = "["
            for item in attr.value:
                if type(item) == str:
                    value_string += '"' + item + '", '
                elif type(item) == int:
                    value_string += str(item) + ','
            value_string = value_string[:-1] + ']'

        elif type(attr.value) == str:
            value_string = '"' + attr.value + '"'

        elif type(attr.value) in [int, float]:
            value_string = str(attr.value)
        
        elif type(attr.value) == bool:
            if attr.value is True:
                value_string = 'true'
            else:
                value_string = 'false'
        category_attr_sql_string = "'" + '{"name": "%s", "value": %s, "prefix": "%s"}' % (attr.name, value_string, attr.prefix) + "'"
        product_attr_sql_string = "'" + '{"name": "%s", "value": null}' % attr.name + "'"
        value_list_for_category.append(category_attr_sql_string)
        value_list_for_product.append(product_attr_sql_string)
    return " || ".join(value_list_for_category), " || ".join(value_list_for_product)