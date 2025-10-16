select * from dbo.workrequest_queue --where status = 'FAILED'
where status = 'PENDING'

update dbo.workrequest_queue
set 
status = 'PENDING', error_message = null 
where status = 'FAILED' 

--delete from dbo.workrequest_queue where id <= 417
--delete from dbo.workrequest_queue where status = 'FAILED'

--update dbo.workrequest_queue set status = 'PENDING', error_message = null where id = 402
--update dbo.workrequest_queue set status = 'PENDING', error_message = null where id = 364 

                query = query.replace("Livingroom : Cocktail Tables", 'Living Room : Cocktail Tables') #fix format on Cocktail Tables category
                query = query.replace("Mid Century Modern", 'Mid-Century Modern') #swap new spelling on Mid-Century Modern


Kids: Bedroom : Chests
Kids: Bedroom : Nightstands

declare @sku as varchar(10) = '85500102'
declare @workrequest_id int = null
select @workrequest_id = id from dbo.workrequest_queue where workrequest_json like '%' + @sku + '%'
print convert(varchar,@workrequest_id)

update dbo.workrequest_queue
set 
workrequest_json = replace(workrequest_json,'Kids: Bedroom : Nightstands','Kids : Bedroom : Nightstands'),
-- workrequest_json = replace(workrequest_json,'Adult : Livingroom : Cocktail Tables','Adult : Living Room : Cocktail Tables'),
status = 'PENDING', error_message = null 
where status = 'FAILED' 
and charindex('Kids: Bedroom : Nightstands', workrequest_json) >0

update dbo.workrequest_queue
set 
--workrequest_json = replace(workrequest_json,'Kids: Bedroom : Nightstands','Kids : Bedroom : Nightstands'),
-- workrequest_json = replace(workrequest_json,'Adult : Livingroom : Cocktail Tables','Adult : Living Room : Cocktail Tables'),
status = 'PENDING', error_message = null 
where status = 'FAILED' 
and charindex('Sage', workrequest_json) >0

where id =  @workrequest_id


"[Prevalidation] FAILED for SKU 85610004. Missing attribute values: {'Decor': ['Mid Century Modern']}"

/*
        SELECT TOP 1 av.attributevalue_id 
        FROM AttributeValues av 
        JOIN AttributeDefinitions ad ON ad.attributedefinition_id = av.attributevalue_attributedefinition_id
        JOIN AttributeValueSites avs ON avs.attributevaluesite_attributevalue_id = av.attributevalue_id AND avs.attributevaluesite_site = 'KTG'
        WHERE av.attributevalue_value = 'Transitional' --AND av.attributevalue_isactive = 1
        AND ad.attributedefinition_name = 'Decor'

        select * from AttributeValueSites where attributevaluesite_attributevalue_id = 550

          SELECT * --av.attributevalue_id 
        FROM AttributeValues av 
        JOIN AttributeDefinitions ad ON ad.attributedefinition_id = av.attributevalue_attributedefinition_id
        JOIN AttributeValueSites avs ON avs.attributevaluesite_attributevalue_id = av.attributevalue_id --AND avs.attributevaluesite_site = 'KTG'
        WHERE av.attributevalue_value like '%Transitional%'

        update ProductAttributes 
        set productattribute_attributevalue_id = 550 
        where productattribute_attributevalue_id = 40642

delete from AttributeValues where attributevalue_id = 40642
delete from AttributeValueSites where attributevaluesite_attributevalue_id = 40642
        40642
    */

    select attributevalue_value, len(attributevalue_value), ltrim(attributevalue_value), len(ltrim(attributevalue_value)) 
    from AttributeValues 
    where  attributevalue_value like ' %'

select * from AttributeValues where attributevalue_value like '%stitch%'

/* need to either fix or delete these and move any things assigned to proper values */
/* 
 Stitch TN3.1	13	Stitch TN3.1	12
 Stitch TN5.1	13	Stitch TN5.1	12
 Stitch TN7.1	13	Stitch TN7.1	12
 Stitch TN9.1	13	Stitch TN9.1	12
 6' x 5'	8	6' x 5'	7
 */

