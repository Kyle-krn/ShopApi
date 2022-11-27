select *
from product p , (
                    select id
                    from product ,jsonb_to_recordset(product.attributes) as items(name text, value text)
                    where 
                    (items.name = 'Встроенная память' and items.value::integer > 1) 
                    or 
                    (items.name = 'Диагональ' and items.value::float > 3.5) 
                    group by id
                    having count(id) > 1) as p2
where p.id = p2.id