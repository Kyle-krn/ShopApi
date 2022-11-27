from typing import List
from fastapi import HTTPException
from tortoise import Tortoise
from app.catalog.models import Category

from app.catalog.schemas import CategoryFilters, QuryProducts
from .utils import GenerateQuerySearchAttr, generate_string_sql_query


async def rowsql_add_attrs_for_all_category(category_attrs: List[CategoryFilters], category_id: int):
    conn = Tortoise.get_connection("default")
    # COALESCE(attributes, '[]'::jsonb)
    string_sql_for_category, string_sql_for_product = await generate_string_sql_query(category_attrs)
    if string_sql_for_category:
        sql = f"""UPDATE product SET attributes = COALESCE(attributes, '[]'::jsonb) || {string_sql_for_product} WHERE category_id={category_id} """
        await conn.execute_query(sql)
        sql = f"""UPDATE category SET filters = COALESCE(filters, '[]'::jsonb) || {string_sql_for_category} WHERE id = {category_id} """
        await conn.execute_query(sql)


async def rowsql_remote_attrs_for_all_category(name: str, category_id: int):
    conn = Tortoise.get_connection("default")
    sql = """UPDATE product SET attributes = remove_element(attributes, '{"name": "%s"}') WHERE category_id = %s""" % (
        name,
        category_id,
    )
    await conn.execute_query(sql)

    sql = """UPDATE category SET filters = remove_element(filters, '{"name": "%s"}') WHERE id = %s""" % (
        name,
        category_id,
    )
    await conn.execute_query(sql)


async def rowsql_update_attr_name(old_name: str, new_name: str, prefix: str, category_id: int):
    conn = Tortoise.get_connection("default")
    json_value_string = '{"name": "%s", "prefix": "%s"}' % (new_name, prefix)
    sql = (
        """UPDATE product SET attributes = change_value(attributes, '{"name": "%s"}', '%s') WHERE category_id = %s"""
        % (old_name, json_value_string, category_id)
    )
    await conn.execute_query(sql)

    # if prefix:
    #     json_new_value_string = json_new_value_string[:-1] + ', "prefix": "%s"}' % prefix

    sql = """UPDATE category SET filters = change_value(filters, '{"name": "%s"}', '%s') WHERE id = %s""" % (
        old_name,
        json_value_string,
        category_id,
    )
    await conn.execute_query(sql)


async def rowsql_append_filepath_photo_product(string_array: str, product_id: str):
    conn = Tortoise.get_connection("default")
    sql = f"""UPDATE product
             SET photo = photo || '{string_array}'::jsonb
             WHERE id = {product_id};"""
    await conn.execute_query(sql)


async def rowsql_remove_photo_product(string_qury: str, product_id: str):
    conn = Tortoise.get_connection("default")
    sql = f"""UPDATE product
             SET photo = photo - {string_qury}
             WHERE id = {product_id};"""
    await conn.execute_query(sql)


async def rowsql_filtering_json_field(category_id: int, query: QuryProducts):
    conn = Tortoise.get_connection("default")
    category = await Category.get(id=category_id)
    x = GenerateQuerySearchAttr(category=category, query=query)
    # print(len(query.attributes))

    sql = f"""select *
        from product p , (
                            select id
                            from product ,jsonb_to_recordset(product.attributes) as items(name text, value text)
                            where 
                            product.category_id = {category_id}
                            {await x.get_sql()}
                            group by id
                            having count(id) = {len(query.attributes)}) as p2
        where p.id = p2.id
        """
    print(sql)
    if query.min_price:
        sql += f""" and {query.min_price} <= p.price"""
    if query.max_price:
        sql += f""" and p.price <= {query.max_price}"""
    x = await conn.execute_query_dict(sql)
    return x


async def rowsql_get_distinct_string_value(category_id: int, attr_name: str):
    conn = Tortoise.get_connection("default")
    sql = f"""select distinct items.value  
             from product ,jsonb_to_recordset(product.attributes) as items(name text, value text)
             where items.name = '{attr_name}' and product.category_id = {category_id} 
          """
    return await conn.execute_query_dict(sql)


async def rowsql_get_distinct_list_value(category_id: int, attr_name: str):
    conn = Tortoise.get_connection("default")
    sql = f"""select distinct jsonb_array_elements(items.value::jsonb) as value
              from product as p ,jsonb_to_recordset(p.attributes) as items(name text, value text)
              where items.name = '{attr_name}' and category_id = {category_id} 
          """
    return await conn.execute_query_dict(sql)


async def rowsql_get_min_max_list_value(category_id: int, attr_name: str):
    conn = Tortoise.get_connection("default")
    sql = f"""select max(items.value::float), min(items.value::float)
              from product ,jsonb_to_recordset(product.attributes) as items(name text, value text)
              where 
              product.category_id = {category_id}
              and 
              (items.name = '{attr_name}')"""
    return await conn.execute_query_dict(sql)


async def rowsql_get_min_max_price_discount(category_id: int):
    conn = Tortoise.get_connection("default")
    sql = f"""select min(price) as min_price, max(price) as max_price, min(discount) as min_discount, max(discount) as max_discount
              from product p 
              where p.category_id = {category_id}"""
    return await conn.execute_query_dict(sql)
