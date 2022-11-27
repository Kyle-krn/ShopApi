create function remove_element(p_value jsonb, p_to_remove jsonb)
 returns jsonb
as
$$
 select coalesce(jsonb_agg(t.element order by t.idx), '[]'::jsonb)
 from jsonb_array_elements(p_value) with ordinality as t(element, idx)
 where not t.element @> p_to_remove;
$$
language sql
immutable;


create function change_value(p_value jsonb, p_what jsonb, p_new jsonb)
  returns jsonb
as
$$
  select jsonb_agg(
         case
           when t.element @> p_what then t.element||p_new
           else t.element
         end order by t.idx)  
  from jsonb_array_elements(p_value) with ordinality as t(element, idx);
$$
language sql
immutable;