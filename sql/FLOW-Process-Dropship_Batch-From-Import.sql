/* ******************************************* */
/* BUILD DROPSHIP BATCHES                       */
/* ******************************************* */

select vendor,run_id, submitted_datetime, count(*) as skucount
  from FLOW_Item_Single_Sku_Build_Actions with (nolock) 
  group by vendor,run_id, submitted_datetime
   order by submitted_datetime desc

-- delete from FLOW_Item_Single_Sku_Build_Actions where submitted_datetime <= '2023-12-14 09:14:14.750' -- and vendor = 'EOSY'
--convert(datetime,convert(varchar,getdate(),101))
/*
--what is done already
select distinct vendor, run_id, submitted_datetime from [eCatalogDB].[dbo].[FLOW_Item_Single_Sku_Build_Actions]
where sku in (select ipac_sku from[eCatalogDB].[dbo].iPackage ip ) 
*/

/* ******************************************* */
/*  Step 1. CLEAN UP THE DATASET                 */
/* ******************************************* */


declare @run_id varchar(255)
set @run_id = 'C501F940-A906-4A9C-B7BF-20495D015D34'

select Vendor,*  from FLOW_Item_Single_Sku_Build_Actions with (nolock)
 where [run_id] = @run_id  -- and site = 'OTG' 

--update FLOW_Item_Single_Sku_Build_Actions set run_id = 'CATCHUP' where sku in ('93244401','93244425')


/* --fixing up some values when build timeouts
select * from iPackage where ipac_sku = '99180918'
select * from CategoryIpackages where ipac_sku = '40662707'
select * from category where cat_id = 446 cat_title like '%table%' and cat_belongstosite = 'RTG'
insert into CategoryIpackages (cat_id, ipac_sku) values (50,'40662694')
*/

/*
declare @run_id varchar(255)
set @run_id = 'B9831D4A-BAD3-2F3C-A5ED53C03AEEEE7D'
delete from FLOW_Item_Single_Sku_Build_Actions where run_id = @run_id
*/

/*
delete from CategoryIpackages where ipac_sku in (
        select sku from FLOW_Item_Single_Sku_Build_Actions with (nolock)
 where [run_id] = @run_id and category like '%linens%' 
 )
 */
/*

update FLOW_Item_Single_Sku_Build_Actions 
set category = replace(replace(category, 'Adult: Bedding:','Bed Linens :'),'Bedding','Linens')
 where [run_id] = @run_id and category like '%bedding%'
*/

/*
insert into CategoryIpackages (cat_id, ipac_sku) 
select c.cat_id, a.sku
 from dbo.category c
 join FLOW_Item_Single_Sku_Build_Actions a
        on c.cat_long_title = 'Adult : '+ a.Category
 where [run_id] = @run_id and category like '%linens%'

*/


-- delete from  FLOW_Item_Single_Sku_Build_Actions where run_id = '8782CFD3-C6FD-B0FD-EA8369D727C9340F' and vendor = ''

/*
update FLOW_Item_Single_Sku_Build_Actions  set RegionList = 'FL,SE,TX'
 where [run_id] = @run_id 
*/

/*
update FLOW_Item_Single_Sku_Build_Actions  set RegionList = 'FL,SE,TX'
 where [run_id] = @run_id 
--FL, SE, TX
*/


--CLEAN UP FIELDS
update FLOW_Item_Single_Sku_Build_Actions
set    
      [site] = rtrim(ltrim(dbo.fn_RemoveNonASCII([site])))
      ,[RegionList] = rtrim(ltrim(replace(dbo.fn_RemoveNonASCII([RegionList]),' ','')))
      ,[Sku] = rtrim(ltrim(dbo.fn_RemoveNonASCII([Sku])))
      ,[Collection] = rtrim(ltrim(dbo.fn_RemoveNonASCII([Collection])))
      ,[Brand] = rtrim(ltrim(dbo.fn_RemoveNonASCII([Brand])))
      ,[Vendor] = rtrim(ltrim(dbo.fn_RemoveNonASCII([Vendor])))
      ,[VendorDescription] = rtrim(ltrim(dbo.fn_RemoveNonASCII([VendorDescription])))
      ,[Name] = rtrim(ltrim(dbo.fn_RemoveNonASCII([Name])))
      ,[Description] = rtrim(ltrim(dbo.fn_RemoveNonASCII([Description])))
      ,[Image] = rtrim(ltrim(dbo.fn_RemoveNonASCII([Image])))
      ,[Notes] = rtrim(ltrim(dbo.fn_RemoveNonASCII([Notes])))
      ,[Dimensions] = rtrim(ltrim(dbo.fn_RemoveNonASCII([Dimensions])))
      ,[DeliveryType] = rtrim(ltrim(dbo.fn_RemoveNonASCII([DeliveryType])))
      ,[Category] = rtrim(ltrim(dbo.fn_RemoveNonASCII([Category])))
      ,[GenericName] = rtrim(ltrim(dbo.fn_RemoveNonASCII([GenericName])))
      ,[ShippingCode] = rtrim(ltrim(dbo.fn_RemoveNonASCII([ShippingCode])))
      ,[PieceCount] = rtrim(ltrim(dbo.fn_RemoveNonASCII([PieceCount])))
      ,[Size] = rtrim(ltrim(dbo.fn_RemoveNonASCII([Size])))
      ,[Style] = rtrim(ltrim(dbo.fn_RemoveNonASCII([Style])))
      ,[Color] = rtrim(ltrim(dbo.fn_RemoveNonASCII([Color])))
      ,[Finish] = rtrim(ltrim(dbo.fn_RemoveNonASCII([Finish])))
      ,[Decor] = rtrim(ltrim(dbo.fn_RemoveNonASCII([Decor])))
      ,[Fabric] = rtrim(ltrim(dbo.fn_RemoveNonASCII([Fabric])))
      ,[Features] = rtrim(ltrim(dbo.fn_RemoveNonASCII([Features])))
      ,[team] = rtrim(ltrim(dbo.fn_RemoveNonASCII([team])))
      ,[gender] = rtrim(ltrim(dbo.fn_RemoveNonASCII([gender])))
      ,[age] = rtrim(ltrim(dbo.fn_RemoveNonASCII([age])))
      ,[Movement] = rtrim(ltrim(dbo.fn_RemoveNonASCII([Movement])))
    where [run_id] = @run_id 

--Collection should be title Case
update FLOW_Item_Single_Sku_Build_Actions
set   [Collection] = dbo.fn_ProperCase([Collection])
 where [run_id] = @run_id 
 
 --Brand should be title Cased and set to a valid brand
update FLOW_Item_Single_Sku_Build_Actions
set   [Brand] = 
    case    when len([Brand]) = 0 and [site] in ('RTG','KTG') then 'Rooms To Go'
            when len([Brand]) = 0 and [site] in ('OTG') then 'Rooms To Go Outdoor'
            when len([Brand]) > 0 then dbo.fn_ProperCase([Brand])
    end
 where [run_id] = @run_id 

select * from FLOW_Item_Single_Sku_Build_Actions with (nolock)
 where [run_id] = @run_id 




/* ******************************************* */
/*  Step 2. Insert into the Batch build table  */
/* ******************************************* */

declare @run_id varchar(255)
set @run_id = 'B372CE6C-BEBE-4A93-8E08-79428C8FEDE8'

insert into [eCatalogDB].[dbo].[BATCH_items_build_data]
(        [site]
      ,[RegionList]
      ,[Sku]
      ,[Collection]
      ,[Brand]
      ,[Vendor]
      ,[VendorDescription]
      ,[Name]
      ,[Description]
      ,[Image]
      ,[Notes]
      ,[Dimensions]
      ,[DeliveryType]
      ,[Category]
      ,[GenericName]
      ,[ShippingCode]
      ,[PieceCount]
      ,[Size]
      ,[Style]
      ,[Color]
      ,[Finish]
      ,[Decor]
      ,[Fabric]
      ,[Features]
      ,[team]
      ,[gender]
      ,[age]
      ,[Movement]
)
SELECT 
      [site]
      ,[RegionList]
      ,[Sku]
      ,[Collection]
      ,[Brand]
      ,[Vendor]
      ,[VendorDescription]
      ,[Name]
      ,[Description]
      ,[Image]
      ,[Notes]
      ,[Dimensions]
      ,[DeliveryType]
      ,[Category]
      ,[GenericName]
      ,[ShippingCode]
      ,[PieceCount]
      ,[Size]
      ,[Style]
      ,[Color]
      ,[Finish]
      ,[Decor]
      ,[Fabric]
      ,[Features]
      ,[team]
      ,[gender]
      ,[age]
      ,[Movement]
  FROM [eCatalogDB].[dbo].[FLOW_Item_Single_Sku_Build_Actions]
       where [run_id] = @run_id and [action] = 'ADD'
       and [Sku] IS NOT NULL
       order by  [record_id]

/*
select * from 
[eCatalogDB].[dbo].[BATCH_items_build_data]
where  isImageReady = 1 and isQAReady = 1  and  isbuilt = 0
and sku not in (select ipac_sku from iPackage)

update [eCatalogDB].[dbo].[BATCH_items_build_data] 
--set RegionList = 'FL,SE,TX' where regionlist= 'FL,SE.TX'
set DeliveryType = 'O' where DeliveryType = 'Vendor Direct'
*/

/* ******************************************* */
/*  Step 3- IMPORT the skus into ecatalog  */
/* ******************************************* */

declare @run_id varchar(255)
set @run_id = 'B372CE6C-BEBE-4A93-8E08-79428C8FEDE8'



/* Check that the category values line up with ecatalog categories for the site */
/* RTG = Adult */
SELECT DISTINCT site, category FROM  dbo.BATCH_items_build_data WHERE  isBuilt = 0
AND 'Adult : '+ category NOT IN (SELECT cat_long_title FROM category WHERE cat_belongsToSite = 'RTG')
AND site = 'RTG'
and sku in (
        select sku from [eCatalogDB].[dbo].[FLOW_Item_Single_Sku_Build_Actions]
       where [run_id] = @run_id and [action] = 'ADD'
)

/* KTG = Adult */
SELECT DISTINCT site, category FROM  dbo.BATCH_items_build_data WHERE  isBuilt = 0
AND 'Kids : '+ category NOT IN (SELECT cat_long_title FROM category WHERE cat_belongsToSite = 'KTG')
and site= 'KTG'
and sku in (
        select sku from [eCatalogDB].[dbo].[FLOW_Item_Single_Sku_Build_Actions]
       where [run_id] = @run_id and [action] = 'ADD'
)

/* OTG = Adult */
SELECT DISTINCT site, category FROM  dbo.BATCH_items_build_data WHERE  isBuilt = 0
AND 'Outdoor : '+ category NOT IN (SELECT cat_long_title FROM category WHERE cat_belongsToSite = 'OTG')
AND site = 'OTG'
and sku in (
        select sku from [eCatalogDB].[dbo].[FLOW_Item_Single_Sku_Build_Actions]
       where [run_id] = @run_id and [action] = 'ADD'
)


/*  Set the batch as ready to be processed */
UPDATE dbo.BATCH_items_build_data SET isImageReady = 1 , isQAReady = 1  
WHERE  isbuilt = 0 and isClosed = 0 
and sku in (
        select  sku from [eCatalogDB].[dbo].[FLOW_Item_Single_Sku_Build_Actions]
       where [run_id] = @run_id and [action] = 'ADD'
       and sku in (select sku from dbo.BATCH_items_build_data  WHERE  isbuilt = 0 and isClosed = 0 )
       --top 40
)



/* ******************************************* */
/*                                            */
/*                                            */
/* Step 4 -     BUILD THE BATCH               */
/*                                            */
/*                                            */
/* ******************************************* */


/* ********************************************************************* */
/*  Step 5 - Set the batch as build and update the shipping code       */
/* ********************************************************************* */

declare @run_id varchar(255)
set @run_id = 'B372CE6C-BEBE-4A93-8E08-79428C8FEDE8'

UPDATE dbo.BATCH_items_build_data 
SET isbuilt = 1 
WHERE sku in (
        select sku from [eCatalogDB].[dbo].[FLOW_Item_Single_Sku_Build_Actions]
       where [run_id] = @run_id and [action] = 'ADD'
)
and sku in (select ipac_sku from ipackage_region_data)


UPDATE dbo.iPackage 
SET ipac_shippingCode = bibd.ShippingCode--, modified_datetime = created_datetime
from [eCatalogDB].[dbo].iPackage ip, 
[eCatalogDB].[dbo].BATCH_items_build_data bibd
where ip.ipac_sku = bibd.sku
and bibd.sku in (
        select sku from [eCatalogDB].[dbo].[FLOW_Item_Single_Sku_Build_Actions]
       where [run_id] = @run_id and [action] = 'ADD'
)

/*
--find ones not built
select bibd.sku, ip.ipac_sku from [eCatalogDB].[dbo].BATCH_items_build_data bibd
left join [eCatalogDB].[dbo].iPackage ip
        on ip.ipac_sku = bibd.sku
where bibd.sku in (
        select sku from [eCatalogDB].[dbo].[FLOW_Item_Single_Sku_Build_Actions]
       where [run_id] = @run_id and [action] = 'ADD'
) and ip.ipac_sku is null
*/




/* ****************************************** */
/*  Step 6 - Validate the attribute values     */
/* ******************************************** */

--PRODUCT COLOR
SELECT site, sku, color FROM 
BATCH_items_build_data bibd
WHERE color NOT IN (
SELECT attributevalue_value 
FROM eCatalogDB.dbo.AttributeValues av 
INNER JOIN eCatalogDB.dbo.AttributeValueSites avs
	ON avs.attributevaluesite_attributevalue_id = av.attributevalue_id AND avs.attributevaluesite_site = bibd.site
WHERE av.attributevalue_attributedefinition_id = 8 AND av.attributevalue_isactive = 1
)
and LEN(ISNULL(bibd.color,'')) > 0
AND isbuilt = 1 AND isclosed = 0

--FINISH
SELECT site, sku, finish FROM 
BATCH_items_build_data bibd
WHERE finish NOT IN (
SELECT attributevalue_value 
FROM  eCatalogDB.dbo.AttributeValues av 
INNER JOIN eCatalogDB.dbo.AttributeValueSites avs
	ON avs.attributevaluesite_attributevalue_id = av.attributevalue_id AND avs.attributevaluesite_site = bibd.site
WHERE av.attributevalue_attributedefinition_id = 3 AND av.attributevalue_isactive = 1
)
and LEN(ISNULL(bibd.finish,'')) > 0
AND isbuilt = 1 AND isclosed = 0

--SIZE
SELECT site, sku, size FROM 
BATCH_items_build_data bibd
WHERE size NOT IN (
SELECT attributevalue_value 
FROM  eCatalogDB.dbo.AttributeValues av 
INNER JOIN eCatalogDB.dbo.AttributeValueSites avs
	ON avs.attributevaluesite_attributevalue_id = av.attributevalue_id AND avs.attributevaluesite_site = bibd.site
WHERE av.attributevalue_attributedefinition_id = 13 AND av.attributevalue_isactive = 1
)
and LEN(ISNULL(bibd.size,'')) > 0
AND isbuilt = 1 AND isclosed = 0

--style
SELECT site, sku, style FROM 
BATCH_items_build_data bibd
WHERE style NOT IN (
SELECT attributevalue_value 
FROM  eCatalogDB.dbo.AttributeValues av 
INNER JOIN eCatalogDB.dbo.AttributeValueSites avs
	ON avs.attributevaluesite_attributevalue_id = av.attributevalue_id AND avs.attributevaluesite_site = bibd.site
WHERE av.attributevalue_attributedefinition_id = 10 AND av.attributevalue_isactive = 1
)
and LEN(ISNULL(bibd.style,'')) > 0
AND isbuilt = 1 AND isclosed = 0

--decor
SELECT site, sku, decor FROM 
BATCH_items_build_data bibd 
WHERE decor NOT IN (
SELECT attributevalue_value 
FROM  eCatalogDB.dbo.AttributeValues av 
INNER JOIN eCatalogDB.dbo.AttributeValueSites avs
	ON avs.attributevaluesite_attributevalue_id = av.attributevalue_id AND avs.attributevaluesite_site = bibd.site
WHERE av.attributevalue_attributedefinition_id = 18 AND av.attributevalue_isactive = 1
)
and LEN(ISNULL(bibd.decor,'')) > 0
AND isbuilt = 1 AND isclosed = 0



--FABRIC
SELECT site, sku, fabric FROM 
BATCH_items_build_data bibd
WHERE fabric NOT IN (
SELECT attributevalue_value 
FROM  eCatalogDB.dbo.AttributeValues av 
INNER JOIN eCatalogDB.dbo.AttributeValueSites avs
	ON avs.attributevaluesite_attributevalue_id = av.attributevalue_id AND avs.attributevaluesite_site = bibd.site
WHERE av.attributevalue_attributedefinition_id = 14 AND av.attributevalue_isactive = 1
)
and LEN(ISNULL(bibd.fabric,'')) > 0
AND isbuilt = 1 AND isclosed = 0

--FEATURES
SELECT site, sku, features FROM 
BATCH_items_build_data bibd
WHERE features NOT IN (
SELECT attributevalue_value 
FROM  eCatalogDB.dbo.AttributeValues av 
INNER JOIN eCatalogDB.dbo.AttributeValueSites avs
	ON avs.attributevaluesite_attributevalue_id = av.attributevalue_id AND avs.attributevaluesite_site = bibd.site
WHERE av.attributevalue_attributedefinition_id = 54 AND av.attributevalue_isactive = 1 
)
and LEN(ISNULL(bibd.features,'')) > 0
AND isbuilt = 1 AND isclosed = 0

--TEAM
SELECT site, sku, team FROM 
BATCH_items_build_data bibd
WHERE team NOT IN (
SELECT attributevalue_value 
FROM  eCatalogDB.dbo.AttributeValues av 
INNER JOIN eCatalogDB.dbo.AttributeValueSites avs
	ON avs.attributevaluesite_attributevalue_id = av.attributevalue_id AND avs.attributevaluesite_site = bibd.site
WHERE av.attributevalue_attributedefinition_id = 39 AND av.attributevalue_isactive = 1 
)
and LEN(ISNULL(bibd.team,'')) > 0
AND isbuilt = 1 AND isclosed = 0

--GENDER
SELECT site, sku, gender FROM 
BATCH_items_build_data bibd
WHERE gender NOT IN (
SELECT attributevalue_value 
FROM  eCatalogDB.dbo.AttributeValues av 
INNER JOIN eCatalogDB.dbo.AttributeValueSites avs
	ON avs.attributevaluesite_attributevalue_id = av.attributevalue_id AND avs.attributevaluesite_site = bibd.site
WHERE av.attributevalue_attributedefinition_id = 11 AND av.attributevalue_isactive = 1
)
and LEN(ISNULL(bibd.gender,'')) > 0
AND isbuilt = 1 AND isclosed = 0

--AGE
SELECT site, sku, age FROM 
BATCH_items_build_data bibd
WHERE age NOT IN (
SELECT attributevalue_value 
FROM  eCatalogDB.dbo.AttributeValues av 
INNER JOIN eCatalogDB.dbo.AttributeValueSites avs
	ON avs.attributevaluesite_attributevalue_id = av.attributevalue_id AND avs.attributevaluesite_site = bibd.site
WHERE av.attributevalue_attributedefinition_id = 7 AND av.attributevalue_isactive = 1 
)
and LEN(ISNULL(bibd.age,'')) > 0
AND isbuilt = 1 AND isclosed = 0

--MOVEMENT
SELECT site, sku, movement FROM 
BATCH_items_build_data bibd
WHERE movement NOT IN (
SELECT attributevalue_value 
FROM  eCatalogDB.dbo.AttributeValues av 
INNER JOIN eCatalogDB.dbo.AttributeValueSites avs
	ON avs.attributevaluesite_attributevalue_id = av.attributevalue_id AND avs.attributevaluesite_site = bibd.site
WHERE av.attributevalue_attributedefinition_id = 55 AND av.attributevalue_isactive = 1 
)
and LEN(ISNULL(bibd.movement,'')) > 0
AND isbuilt = 1 AND isclosed = 0


/* ****************************************** */
/*  Step 7 - Assign the attribute values     */
/* ******************************************** */

IF OBJECT_ID('tempdb.dbo.#singletable', 'U') IS NOT NULL  DROP TABLE #singletable
IF OBJECT_ID('tempdb.dbo.#multitable', 'U') IS NOT NULL  DROP TABLE #multitable


CREATE TABLE #singletable ( [sku] varchar(255),  [site] CHAR(3) , [attribute] varchar(40), [value] varchar(100)  )
CREATE TABLE #multitable ( [sku] varchar(255),  [site] CHAR(3), [attribute] varchar(40), [value] varchar(100)  )


--PRODUCT COLOR
INSERT INTO #singletable
SELECT eip.ipac_sku, eip.ipac_belongstosite, 'Product Color', bibd.color 
FROM eCatalogDB.dbo.BATCH_items_build_data bibd
INNER JOIN eCatalogDB.dbo.iPackage eip ON
	eip.ipac_sku = bibd.Sku AND eip.ipac_belongstosite = bibd.site
WHERE  LEN(ISNULL(bibd.color,'')) > 0 AND bibd.isbuilt =  1 AND bibd.isclosed = 0

---------------

--FINISH
INSERT INTO #singletable
SELECT eip.ipac_sku, eip.ipac_belongstosite, 'Finish', bibd.finish 
FROM eCatalogDB.dbo.BATCH_items_build_data bibd
INNER JOIN eCatalogDB.dbo.iPackage eip ON
	eip.ipac_sku = bibd.Sku AND eip.ipac_belongstosite = bibd.site
WHERE  LEN(ISNULL(bibd.finish,'')) > 0 AND bibd.isbuilt =  1 AND bibd.isclosed = 0

--SIZE
INSERT INTO #singletable
SELECT eip.ipac_sku, eip.ipac_belongstosite, 'Size', bibd.size 
FROM eCatalogDB.dbo.BATCH_items_build_data bibd
INNER JOIN eCatalogDB.dbo.iPackage eip ON
	eip.ipac_sku = bibd.Sku AND eip.ipac_belongstosite = bibd.site
WHERE  LEN(ISNULL(bibd.size,'')) > 0 AND bibd.isbuilt =  1 AND bibd.isclosed = 0

--STYLE
INSERT INTO #singletable
SELECT eip.ipac_sku, eip.ipac_belongstosite, 'Style', bibd.style 
FROM eCatalogDB.dbo.BATCH_items_build_data bibd
INNER JOIN eCatalogDB.dbo.iPackage eip ON
	eip.ipac_sku = bibd.Sku AND eip.ipac_belongstosite = bibd.site
WHERE  LEN(ISNULL(bibd.style,'')) > 0 AND bibd.isbuilt =  1 AND bibd.isclosed = 0


--DECOR
INSERT INTO #singletable
SELECT eip.ipac_sku, eip.ipac_belongstosite, 'Decor', bibd.decor 
FROM eCatalogDB.dbo.BATCH_items_build_data bibd
INNER JOIN eCatalogDB.dbo.iPackage eip ON
	eip.ipac_sku = bibd.Sku AND eip.ipac_belongstosite = bibd.site
WHERE  LEN(ISNULL(bibd.decor,'')) > 0 AND bibd.isbuilt =  1 AND bibd.isclosed = 0


--FABRIC
INSERT INTO #singletable
SELECT eip.ipac_sku, eip.ipac_belongstosite, 'Fabric', bibd.fabric 
FROM eCatalogDB.dbo.BATCH_items_build_data bibd
INNER JOIN eCatalogDB.dbo.iPackage eip ON
	eip.ipac_sku = bibd.Sku AND eip.ipac_belongstosite = bibd.site
WHERE  LEN(ISNULL(bibd.fabric,'')) > 0 AND bibd.isbuilt =  1 AND bibd.isclosed = 0

--FEATURES
INSERT INTO #singletable
SELECT eip.ipac_sku, eip.ipac_belongstosite, 'Features', bibd.features 
FROM eCatalogDB.dbo.BATCH_items_build_data bibd
INNER JOIN eCatalogDB.dbo.iPackage eip ON
	eip.ipac_sku = bibd.Sku AND eip.ipac_belongstosite = bibd.site
WHERE  LEN(ISNULL(bibd.features,'')) > 0 AND bibd.isbuilt =  1 AND bibd.isclosed = 0

--TEAM
INSERT INTO #singletable
SELECT eip.ipac_sku, eip.ipac_belongstosite, 'Team', bibd.team 
FROM eCatalogDB.dbo.BATCH_items_build_data bibd
INNER JOIN eCatalogDB.dbo.iPackage eip ON
	eip.ipac_sku = bibd.Sku AND eip.ipac_belongstosite = bibd.site
WHERE  LEN(ISNULL(bibd.team,'')) > 0 AND bibd.isbuilt =  1 AND bibd.isclosed = 0

--Gender
INSERT INTO #singletable
SELECT eip.ipac_sku, eip.ipac_belongstosite, 'Gender', bibd.gender 
FROM eCatalogDB.dbo.BATCH_items_build_data bibd
INNER JOIN eCatalogDB.dbo.iPackage eip ON
	eip.ipac_sku = bibd.Sku AND eip.ipac_belongstosite = bibd.site
WHERE  LEN(ISNULL(bibd.gender,'')) > 0 AND bibd.isbuilt =  1 AND bibd.isclosed = 0

--Age
INSERT INTO #singletable
SELECT eip.ipac_sku, eip.ipac_belongstosite, 'Age', bibd.age 
FROM eCatalogDB.dbo.BATCH_items_build_data bibd
INNER JOIN eCatalogDB.dbo.iPackage eip ON
	eip.ipac_sku = bibd.Sku AND eip.ipac_belongstosite = bibd.site
WHERE  LEN(ISNULL(bibd.age,'')) > 0 AND bibd.isbuilt =  1 AND bibd.isclosed = 0

--Movement
INSERT INTO #singletable
SELECT eip.ipac_sku, eip.ipac_belongstosite, 'Movement', bibd.movement 
FROM eCatalogDB.dbo.BATCH_items_build_data bibd
INNER JOIN eCatalogDB.dbo.iPackage eip ON
	eip.ipac_sku = bibd.Sku AND eip.ipac_belongstosite = bibd.site
WHERE  LEN(ISNULL(bibd.movement,'')) > 0 AND bibd.isbuilt =  1 AND bibd.isclosed = 0


--convert to multiple attributes
--select * from #singletable

DECLARE @single_sku varchar(255)
DECLARE @single_site CHAR(3)
DECLARE @single_attribute varchar(40)
DECLARE @single_value varchar(40) 

DECLARE attribute_cursor CURSOR FOR   
SELECT sku, site, attribute, value
FROM #singletable

OPEN attribute_cursor  

FETCH NEXT FROM attribute_cursor   
INTO @single_sku, @single_site, @single_attribute, @single_value

WHILE @@FETCH_STATUS = 0  
BEGIN  
     
	INSERT INTO #multitable
	SELECT @single_sku, @single_site, @single_attribute, value FROM dbo.fn_split(@single_value,',')

FETCH NEXT FROM attribute_cursor   
	INTO @single_sku, @single_site, @single_attribute, @single_value

END   
CLOSE attribute_cursor
DEALLOCATE attribute_cursor 

SELECT * FROM #multitable 


INSERT INTO eCatalogDB.dbo.ProductAttributes
        ( productattribute_attributevalue_id ,
          productattribute_productType ,
		  productattribute_sku,
		  productattribute_site
        )

SELECT DISTINCT
 av.attributevalue_id, 
 'Item' AS type,
  mt.sku, 
  mt.site
--  mt.attribute,
--  mt.value
FROM #multitable mt
INNER JOIN eCatalogDB.dbo.attributeDefinitions ad ON 
	ad.attributedefinition_name = mt.attribute
INNER JOIN  eCatalogDB.dbo.AttributeValues av ON 
	av.attributevalue_value =  mt.value AND av.attributevalue_attributedefinition_id = ad.attributedefinition_id AND av.attributevalue_isactive = 1
order by mt.sku, av.attributevalue_id
--NEED TO ADD CHECK FOR EXISTENCE




/* ****************************************** */
/*       Step 8. - Close the batch             */
/* ******************************************** */
update eCatalogDB.dbo.BATCH_items_build_data SET isclosed = 1  WHERE  isbuilt = 1 AND isClosed = 0 --and vendor = 'UNIL'

select * from eCatalogDB.dbo.BATCH_items_build_data WHERE  isbuilt = 1 AND isClosed = 0 

select * from eCatalogDB.dbo.BATCH_items_build_data WHERE  isbuilt = 0 

/*
select * from eCatalogDB.dbo.BATCH_items_build_data WHERE sku = '99106378'
select * from eCatalogDB.dbo.iPackage where ipac_sku = '99108310'
select * from eCatalogDB.dbo.iPackage_region_data where ipac_sku = '99108310'
*/

-- ------------------------------- --
--   END: CLOSE THE BATCH			 --
-- ------------------------------- --


   /*

   update dbo.BATCH_items_build_data  set Category = 'Living Room : Cocktail Tables',
GenericName = replace(GenericName,'Outdoor ','')
where sku in ('20010574','20010586')

update dbo.BATCH_items_build_data  set Category = 'Tables : End Tables',
GenericName = replace(GenericName,'Outdoor ','')
where sku in ('20210720')


update BATCH_items_build_data
set fabric = 'Polyester,Linen'
where fabric = 'Polyester, Linen'
and isbuilt = 1 AND isclosed = 0




Boys
Girls

Boy
Girl
Boy,Girl

update BATCH_items_build_data
set gender = 'Girls,Boys'
where gender = 'Girl,Boy'
and isbuilt = 1 AND isclosed = 0


update BATCH_items_build_data
set gender = 'Girls,Boys'
where gender = 'Any'
and isbuilt = 1 AND isclosed = 0

update BATCH_items_build_data
set gender = 'Boys,Girls'
where gender = 'Boy,Girl'
and isbuilt = 1 AND isclosed = 0

update BATCH_items_build_data
set gender = 'Boys,Girls'
where gender = 'Boy, Girl'
and isbuilt = 1 AND isclosed = 0

update BATCH_items_build_data
set gender = 'Boys'
where gender = 'Boy'
and isbuilt = 1 AND isclosed = 0

update BATCH_items_build_data
set gender = 'Girls'
where gender = 'Girl'
and isbuilt = 1 AND isclosed = 0

Boy,Girl
Girl
Boy
--select * from  BATCH_items_build_data

update BATCH_items_build_data
set color = replace(color,', ',',')
where color like '%, %'
and isbuilt = 1 AND isclosed = 0


update BATCH_items_build_data
set fabric = replace(fabric,', ',',')
where fabric like '%, %'
and isbuilt = 1 AND isclosed = 0

update BATCH_items_build_data
set movement = replace(movement,', ',',')
where movement like '%, %'
and isbuilt = 1 AND isclosed = 0

update BATCH_items_build_data
set decor = replace(decor,', ',',')
where decor like '%, %'
and isbuilt = 1 AND isclosed = 0

Cottage/Rustic

update BATCH_items_build_data
set fabric = replace(fabric,', ',',')
where fabric like '%, %'
and isbuilt = 1 AND isclosed = 0

Contemporary, Industrial, Modern


update BATCH_items_build_data
set size = 'Twin,Full'
where size = 'Twin/ Full'
and isbuilt = 1 AND isclosed = 0

update BATCH_items_build_data
set size = ''
where isbuilt = 1 AND isclosed = 0

update BATCH_items_build_data
set size = replace(size,' Runner', '')
where isbuilt = 1 AND isclosed = 0

86880614	2'6 x 8' Runner

2' x 6' Runner
2'7 x 10' Runner
2' x 6'

update BATCH_items_build_data
set size = '18 x 18'
where size = '18x18' and  isbuilt = 1 AND isclosed = 0

update BATCH_items_build_data
set size = '7''10 x 9''8'
where size = '7''10" x 9''8' and  isbuilt = 1 AND isclosed = 0

update BATCH_items_build_data
set size = '5''3 x 7''3'
where size = '5''3" x 7''3' and  isbuilt = 1 AND isclosed = 0

update BATCH_items_build_data
set size = '7''10 x 10''2'
where size = '7''10" x 10''2' and  isbuilt = 1 AND isclosed = 0

update BATCH_items_build_data
set size = '10'' x 14''1'
where size = '10'' x 14''1''' and  isbuilt = 1 AND isclosed = 0





update BATCH_items_build_data
set size = '20 x 20'
where size = '20x20' and  isbuilt = 1 AND isclosed = 0

update BATCH_items_build_data
set size = '7''10 x 10''10'
where size = '7''10x 10''10' and  isbuilt = 1 AND isclosed = 0



update BATCH_items_build_data
set size = 'Full,Queen'
where size = 'Full/Queen'
and isbuilt = 1 AND isclosed = 0

Twin,Twin Extra Long
Twin XL

update BATCH_items_build_data
set size = 'King,California King'
where size = 'King/California King'
and isbuilt = 1 AND isclosed = 0

update BATCH_items_build_data
set size = 'King'
where sku = '84283630'
and isbuilt = 1 AND isclosed = 0

update BATCH_items_build_data
set color = 'Silver'
where sku = '84783577'
and isbuilt = 1 AND isclosed = 0

update BATCH_items_build_data
set finish = 'Silver'
where sku = '84783577'
and isbuilt = 1 AND isclosed = 0
RTG	84783577	King

update ipackage set ipac_name = 'Maness Silver King Headboard' where ipac_sku = '84783577'

84283630	Kind

RTG		Kind

update BATCH_items_build_data
set size = 'Twin XL/Queen'
where size = 'Twin XL/Queen'
and isbuilt = 1 AND isclosed = 0

update BATCH_items_build_data
set color = 'Gold'
where sku in ('89600021')
and isbuilt = 1 AND isclosed = 0

89600021	Golden

85106637	Stone Gray
85106687	Stone Gray

85205839
85205877

update BATCH_items_build_data
set color = 'Black', finish = 'Black'
where sku in ('31100085','31100097','31100112')
and isbuilt = 1 AND isclosed = 0







update BATCH_items_build_data
set color = 'Ivory,Beige'
where color = 'Ivory Beige'
and isbuilt = 1 AND isclosed = 0

Ivory Gray
Ivory Beige

40401286

update BATCH_items_build_data
set size = '7''10 x 9''10'
where sku = '99580221'
and isbuilt = 1 AND isclosed = 0

99488390	5'3 x	--'5''3 x 7''8'
99588405	7'7 x	--'7''7 x 10''10'
99488403	5'3 x	--5'3 x 7'8
99588417	7'7 x	--'7''7 x 10''10'
99488085	5'3 x	--'5''3 x 7''7'
99580219	7'10 x	--'7''10 x 9''10'
99488097	5'3 x	--'5''3 x 7''7'
99580221	7'10 x	7'10 x 9'10

update BATCH_items_build_data
set finish = 'Nickel'
where finish = 'Nickle'
and isbuilt = 1 AND isclosed = 0


update BATCH_items_build_data
set size = 'Bar Height' --, shape = 'Rectangle'
where sku = '76410693'

and isbuilt = 1 AND isclosed = 0

76410693	Bar Height,Round
76410770	Bar Height,Rectangle


99142540	Nickle

 */
/*
update eCatalogDB.dbo.BATCH_items_build_data SET isbuilt = 1,  isclosed = 1  WHERE  sku = '59961017' vendor = 'SURY'

 sku in (
        select value from dbo.fn_split('10618316,10618380,10618378,10618405,10618392,10618188,10618190,10618203',',')
)

select * from eCatalogDB.dbo.BATCH_items_build_data where sku = '90103260'

declare @run_id varchar(255)
set @run_id = '/workflows/5503bc4c0cc64ce08c00d6bc97d8f2f4/runs/08586050109506834480137979286CU37'

update  eCatalogDB.dbo.BATCH_items_build_data set size = replace(size,' in','"')
where isbuilt =  1 AND isclosed = 0
and sku in (

select sku from FLOW_Item_Single_Sku_Build_Actions with (nolock)
 where [run_id] = @run_id --and site = 'RTG'
)
*/
--select * from eCatalogDB.dbo.BATCH_items_build_data  WHERE  isbuilt = 1 AND isClosed = 0 
/*
sku	size
99421148	Under 24 Small
99421162	Under 24 Small
99421198	Under 24 Small
99421225	Under 24 Small

select * from AttributeValues where attributevalue_value like '%Adjustable%'
select * from attributedefinitions

select * from ipackage where ipac_sku in (select value from dbo.fn_split('99162516,99162504,99162528,99162655,99162643,99162631',',') )


INNER JOIN eCatalogDB.dbo.iPackage eip ON
	eip.ipac_sku = bibd.Sku AND eip.ipac_belongstosite = bibd.site
WHERE  LEN(ISNULL(bibd.team,'')) > 0 AND bibd.isbuilt =  1 AND bibd.isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set
--size = '48"+ Extra Large' 
--size = '36" - 48" Large'
size = '24" - 36" Medium'
--size = 'Under 24" Small' 
--where sku in ('99160346')
where
--size = '48" + Extra Large'
--size = '48+ Extra Large'
--size = '48'' + Extra Large'
--size =  '36"-48" Large'  
--size = '24"-36" Medium'
--size = '24"-36" Medium' 
---size = '24'' - 36" Medium'
size = '24" - 36" Mediuim'
--size = 'Small' 
--size = '36"-48" Large'
--size = 'Medium'
--size = 'Large'
--size = 'Extra Large'
AND isbuilt =  1 AND isclosed = 0


RTG	99160699	18"
RTG	99160536	18"
RTG	99160346	18"

RTG	99188065	Extra Large
RTG	99188077	Large
RTG	99188089	Large
RTG	99188091	Extra Large
RTG	99188104	Medium
RTG	99188267	Large
RTG	99188798	Extra Large

update eCatalogDB.dbo.BATCH_items_build_data 
set
--size = '48"+ Extra Large' 
size = '36" - 48" Large'
--size = '24" - 36" Medium'
--size = 'Under 24" Small' 
--where sku in ('99101633')
where
---size = 'Small' 
---size = 'Medium'
size = 'Large'
AND isbuilt =  1 AND isclosed = 0

99101633	Large
select * from category where cat_title like '%dining%' and cat_belongstosite = 'RTG'
select * from category where cat_title like '%lighting%'
select * from category where cat_id = 493

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Dining Tables'
where category = 'Diningroom : Diningtables'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Dining Tables'
where category = 'Diningroom : Dining Tabbles'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Dining Tables'
where category = 'Diningroom : Dining Table'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Dining : Bar Tables'
where category = 'Dining: Bar Tables'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Dining : Dining Chairs'
where category = 'Dining: Dining Chairs'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Dining : Dining Tables'
where category = 'Dining: Dining Tables'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Dining : Dining Tables'
where category = 'Outdoor : Dining : Dining Tables'




update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Dining : Bar Tables'
where category = 'Seating : Bar Tables'
where category = 'Seating: Bar Tables'

select * from category where cat_title like '%mattress%' and cat_belongstosite = 'RTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedding : Twin XL Mattress Only'
where category = 'Bedding: Twin XL Mattress Only'





update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedding : Twin Mattress Only'
where category = 'Bedding: Twin Mattress Only'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedding : Full Mattress Only'
where category = 'Bedding: Full Mattress Only'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedding : Queen Mattress Only'
where category = 'Bedding: Queen Mattress Only'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedding : King Mattress Only'
where category = 'Bedding: King Mattress Only'


Bedding: Full Mattress Only


Adult : 

Outdoor : 


Fire: Fire Pits


Outdoor : Dining : Bar Tables
Outdoor : Dining : Dining Chairs
Outdoor : Dining : Dining Tables
Outdoor : Seating : Benches
Outdoor : Seating : Chairs
Outdoor : Seating : Coffee Tables


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Fire : Fire Pits'
where category = 'Fire: Fire Pits'




Outdoor : Seating : Coffee Tables
select * from category where cat_title like '%coffee%'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Coffee Tables'
where category = 'Outdoor : Seating : Coffee Tables' and site = 'OTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : End Tables'
where category = 'Outdoor : Seating : End Tables' and site = 'OTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Loveseats'
where category = 'Outdoor : Seating : Loveseats' and site = 'OTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Sofas'
where category = 'Outdoor : Seating : Sofas' and site = 'OTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Sofas'
where category = 'Seating : Sofa' and site = 'OTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Sectionals'
where category = 'Seating : Sectional' and site = 'OTG'

Seating : Sectional


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Dining : Bar Tables'
where category = 'Outdoor : Dining : Bar Tables' and site = 'OTG'



Outdoor : Dining : Bistro Tables

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Buffet Servers'
where category = 'Dining Room : Buffet Servers' and site = 'OTG'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Buffet Servers'
where category = 'Diningroom : Bufet Servers' 

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Buffet Servers'
where category = 'Diningroom : Buffert Servers' 




Adult : 
Dining Room : Buffet Servers



Living Room : Cocktail Table

Dining Room : Buffett Servers

select * from category where cat_title like '%buff%' --cat_id = 211 order by created_datetime desc

update eCatalogDB.dbo.BATCH_items_build_data 
set
style = '',
size = '36" - 48" Large'
where
sku = '21225467'
AND isbuilt =  1 AND isclosed = 0




update eCatalogDB.dbo.BATCH_items_build_data 
set  size = '7''6 x 9''6'
where sku = '99151486'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set  size = '5''3 x 7''7'
where sku = '99488782'
AND isbuilt =  1 AND isclosed = 0

RTG	99488782	5'3 x

	7'6' x 9'6

			
99150573	5'2			 
	

update eCatalogDB.dbo.BATCH_items_build_data 
set size = 'Twin'
where sku in ('30052524','30052625')
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set size = '8'' x 8'''
where size = '8'''
AND isbuilt =  1 AND isclosed = 0


update eCatalogDB.dbo.BATCH_items_build_data 
set size = '5''3 x 5''3'
where size = '5''3 Square'
AND isbuilt =  1 AND isclosed = 0

5'3 Square	5'3 x 5'3

update eCatalogDB.dbo.BATCH_items_build_data 
set size = '6''7 x 6''7'
where size = '6''7 Square'
AND isbuilt =  1 AND isclosed = 0

6'7 Square	6'7 x 6'7

update eCatalogDB.dbo.BATCH_items_build_data 
set size = '7''10 x 7''10'
where size = '7''10 Square'
AND isbuilt =  1 AND isclosed = 0

7'10 Square	7'10 x 7'10

update eCatalogDB.dbo.BATCH_items_build_data 
set size = '6''7 x 9'''
where size = '6''7 x 9'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set size = '5''3 x 7''6'
where size = '5''3 x7''6'
AND isbuilt =  1 AND isclosed = 0




6'7 x 9	6'7 x 9'

update eCatalogDB.dbo.BATCH_items_build_data 
set size = '7'' x 7'''
where size = '7'' Square'
AND isbuilt =  1 AND isclosed = 0

7' Square

8' Square	8' x 8'


select * from attributevalues where attributevalue_value like '%54%' and attributevalue_attributedefinition_id = 13

select * from attributedefinitions where attributedefinition_id = 13


update eCatalogDB.dbo.BATCH_items_build_data 
set finish = 'Blush' where sku in ('30068173','30068159','30268153')


update eCatalogDB.dbo.BATCH_items_build_data 
set size = replace(size,' in.','"')
where size like '%in.%'
AND isbuilt =  1 AND isclosed = 0

63 in.
55 in.
73 in.
70 in.
47 in.
54 in.

RTG	Dining Room : Barstools
RTG	Dinning Room : Side Chairs

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Lighting/Lanterns'
where category = 'Accessories : Floor Lamps' and site = 'OTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Carts'
where category = 'Accessories:Carts' and site = 'OTG'



select * from category where cat_title like '%linen%'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Buffet Servers'
where category = 'Dining Room : Buffett Servers'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bed Linens : Queen Linens'
where category = 'Bed Linens Queen Linens'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bed Linens : Queen Linens'
where category = 'Bed Linens: Queen Linens'


Bed Linens: Queen Linens
update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bed Linens : Twin Linens'
where category = 'Kids: Bed Linens: Twin Linens' and site = 'KTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bed Linens : Full Linens'
where category = 'Bed Linens: Full Linens' and site = 'KTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bed Linens : Twin Linens'
where category = 'Bed Linens: Twin Linens' and site = 'KTG'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bed Linens : Full Linens'
where category = 'Bed Linens: Queen Linens' and site = 'KTG'



select * from category where cat_title like '%queen%' and  cat_belongstosite = 'KTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bed Linens : Full Linens'
where category = 'Bed Linens: Full Linens' and site = 'RTG'

Bed Linens: Full Linens
Adult : Bed Linens : Full Linens

Bed Linens: Full Linens

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bed Linens : King Linens'
where category = 'Bed Linens: King Linens'

Bed Linens: King Linens

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bed Linens : King Linens'
where category = 'Bed  Linens: King Linens'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bed Linens : Queen Linens'
where category = 'Adult: Bed Linens: Queen Linens'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedding : California King Bedding'
where category = 'Adult: Bedding: California King Bedding'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedding : Full Bedding'
where category = 'Adult: Bedding: Full Bedding'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedding : King Bedding'
where category = 'Adult: Bedding: King Bedding'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedding : Queen Bedding'
where category = 'Adult: Bedding: Queen Bedding'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedding : Twin Bedding'
where category = 'Adult: Bedding: Twin Bedding'






Adult : Diningroom : Buffet Servers


Patio : Sectional Sets
Outdoor : Seating : Sectionals


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Wall Decor'
where category = 'Accessories: Wall Decor' 

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Wall Decor'
where category = 'Accessories : Wall Dcor' 


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Wall Decor'
where category = 'Accessories : Wall Dcor' 




update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories: Pillows/throws'
where category = 'Kids : Accessories : Pillows/Throws' 
and site = 'KTG'

Kids : Accessories : Pillows/throws

Kids : Accessories: Pillows/throws

select * from category where cat_title like '%/%'

Kids : Accessories : Pillows/Throws


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories: Pillows/throws'
where category = 'Accessories : Pillows/Throws' 
and site = 'KTG'





update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories: Pillows/throws'
where category = 'Accessories : Pillows/Throws' 
and site = 'KTG'



Accessories: Pillows/throws
Accessories : Pillows/Throws

Outdoor : Accessories : Pillows

select * from category where cat_title like '%pill%' and cat_belongstosite = 'KTG'

Diningroom : Arm Chairs


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Side Chairs'
where category = 'Diningroom : Dining Chair' 



Livingroom : End Tables



Acessories: Accent Pillows
Adult : Accessories : Accent Pillows

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Accent Pillows'
where category = 'Decor : Accent Pillows' 


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Accent Pillows'
where category = 'Accessories: Accent Pillows' 

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Pillows'
where category = 'Accessories :  Accent Pillows'  and site = 'OTG'

Accessories :  Accent Pillows -> 'Accessories : Pillows'
Accessories : Poufs

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Accent Pillows'
where category = 'Accessories : Pillows'  and site = 'RTG'





update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Accent Chairs'
where category = 'Livingroom : Accents Chairs'  and site = 'RTG'

select * from ipackage where ipac_sku in (select ipac_sku from categoryipackages where cat_id = 190)

Livingroom : Accents Chairs
Livingroom : Accents Chairs


Decor : Accent Pillows
Acessories: Accent Pillows

Kids : Bedding : Full Bedding
Kids : Bedding : Twin Bedding

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedding : Twin Bedding'
where category = 'Kids : Bedding : Twin Bedding' 

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedding : Twin Bedding'
where category = 'Kids:Bedding:Twin Bedding' 





update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedding : Full Bedding'
where category = 'Kids : Bedding : Full Bedding' 

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedding : California King Bedding'
where category = 'Bedding: California King Bedding' 

Adult: Bedding: California King Bedding

Bedding: California King Bedding

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedding : Full Bedding'
where category = 'Bedding: Full Bedding' 

Bedding: Full Bedding


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedding : King Bedding'
where category = 'Bedding: King Bedding' 

Bedding: King Bedding

Bedding: King Bedding

Adult: Bedding: Queen Bedding


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedding : Queen Bedding'
where category = 'Adult: Bedding: Queen Bedding' 

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedding : Queen Bedding'
where category = 'Bedding: Queen Bedding' 

Bedding: Queen Bedding

Adult: Bedding: Twin Bedding

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedding : Twin Bedding'
where category = 'Adult: Bedding: Twin Bedding' 


Adult : Livingroom : Ottomans

select * from category where cat_title like '%otto%' and cat_belongstosite = 'RTG'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Ottomans'
where category = 'Living Rooms : Ottomans' 

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Ottomans'
where category = 'Livingrom : Ottomans' 


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Ottomans'
where category = 'Adult: Livingroom : Ottomans' 



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Poufs'
where category = 'Accessories : Poufs and Ottomans' and site = 'RTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Poufs'
where category =' Accessories : Poufs' and site = 'RTG'

select * from category where cat_title like '%otto%' and cat_belongstosite = 'RTG'

select Outdoor : Seating : Ottomans


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Ottomans'
where category ='Accessories :  Poufs' and site = 'OTG'

Accessories :  Poufs



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Ottomans'
where category = 'Decor : Ottomans' 

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Ottomans'
where category = 'Decor : Ottomans' 

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Ottomans'
where category = 'Adult : Livingroom : Ottomans' 




Kids: Accessories: Wall Dcor


Living Rooms : Ottomans

Adult : Livingroom : Ottomans

Accessories: Wall Decor
Kids : Accessories : Wall Decor

Accessories : Wall Dcor
Accessories :  Wall Dcor
Kids: Accessories: Wall Dcor

Outdoor : Accessories : Lighting/Lanterns


Accessories : Floor Lamps
Accessories : Table Lamps

Adult : Diningroom : Barstools

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Dining : Bar Stools'
where category = 'Dining : Bar Stool'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Barstools'
where category = 'Adult : Diningroom : Barstools'
and site = 'RTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Barstools'
where category = 'Diningroom : Barstool'
and site = 'RTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Barstools'
where category = 'Adult : Diningroom : Barstool'
and site = 'RTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Barstools'
where category = 'Diningroom :  Barstools'
and site = 'RTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Silk Florals'
where category = 'Adult : Accessories : Silk Florals'






Diningroom :  Barstools


Outdoor : Dining : Barstools


select * from category where cat_belongstosite = 'OTG' -- '%barstool%'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Dining : Bar Stools'
where category = 'Outdoor : Dining : Barstools'
and site = 'OTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Dining : Bar Stools'
where category = 'Dining Bar Stools'
and site = 'OTG'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Dining : Bar Stools'
where category = 'Dining : Barstools'
and site = 'OTG'

Outdoor : Dining : Barstools


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Barstools'
where category = 'Adult : Diningroom : Barstools'
and site = 'RTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Chairs'
where category = 'Seating: Chairs'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Chaise/Lounges'
where category = 'Seating: Chaise/Lounges'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Coffee Tables'
where category = 'Seating: Coffee Tables'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : End Tables'
where category = 'Seating: End Tables'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Ottomans'
where category = 'Seating: Ottomans'
Kids : Seating : Ottomans


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Benches'
where category = 'Outdoor : Seating : Benches'
and site = 'OTG'


select * from category where cat_title like '%bench%'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Dining : Bar Stools'
where category = 'Outdoor : Dining : Bar Stools'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Dining : Dining Chairs'
where category = 'Outdoor : Dining : Dining Chairs'



Outdoor : Dining : Dining Chairs

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Side Chairs'
where category = 'Diningroom: Side Chairs'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Side Chairs'
where category = 'Adult: Diningroom: Side Chairs'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Side Chairs'
where category = 'Diningroom : Side Charis'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Side Chairs'
where category = 'Diningroom : Side Chair'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Dining Tables'
where category = 'Dining Room : Dining Tables'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Dining Tables'
where category = 'Dining Room : Tables'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Chairs'
where category = 'Seating :Chairs'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Desks and Chairs : Desk Chairs'
where category = 'Desks and Chairs : Chairs'
and site = 'KTG'

Desks  & Chairs : Desks

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Desks and Chairs : Desks'
where category = 'Desks  & Chairs : Desks'
and site = 'KTG'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Umbrellas/Canopies : Umbrellas'
where category = 'Umbrellas : Umbrellas'
Umbrellas : Umbrellas


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Umbrellas : Bases/Stands'
where category = 'Umbrellas :Bases/Stands'


Outdoor : Umbrellas : Bases/Stands

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Beds'
where category = 'Bedding : Beds'
and site = 'KTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Beds'
where category = 'Adult: Bedroom : Beds'





select * from category where cat_title like '%desk%'
and cat_belongstosite = 'KTG'

select * from categoryipackages where cat_id = 483

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Umbrellas : Bases/Stands'
where category = 'Umbrellas :Bases/Stands'





Dining Room : Dining Tables

Dining Room : Dining Tables

Dining Tables
Adult : Diningroom : Dining Tables

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Dining Tables'
where category = 'Adult : Diningroom : Dining Tables'

Adult : Diningroom : Dining Tables


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Sconces'
where category = 'Accessories : Scones'

Accessories : Chandeleirs
Accessories : Scones


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Ottomans'
where category = 'Living Room : Ottomans'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Ottomans'
where category = 'Lingingroom : Ottomans'




Living room : Ottomans

Living Room : Ottomans
Livingroom: Ottomans

Living Room : Ottomans


RTG	Living Room : Ottomans


Living Rooms : Ottomans

Living Rooms : Ottomans

Living Rooms : Ottomans

RTG	Living Room : Ottomans

Adult : Diningroom : Side Chairs

RTG	Accessories : Floor Lamp
RTG	Accessories : Table Lamp
RTG	Dining Room : Side Chairs

RTG	Living Room : Accent Chairs
RTG	Living Room : Ottomans

RTG	Living Room : Ottomans

Accessories : Chaneliers
Accessories : Floor Lamp
Accessories : Wall Dcor

Lighting/Lanterns

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Home Office Furniture : Desks'
where category = 'Home Office Furniture : Desk'



select * from category where cat_title like '%chair%' and cat_belongstosite = 'RTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Desks and Chairs : Desks'
where category = 'Home Office Furniture : Desks' and site = 'KTG'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Desks and Chairs : Desks'
where category = 'Kids : Desks and Chairs : Desks' and site = 'KTG'




update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Home Office Furniture : Office Chairs'
where category = 'Home Office Furniture : Desk Chairs' and site = 'RTG'



select * from  eCatalogDB.dbo.BATCH_items_build_data 
where category = 'Home Office Furniture:  Office Chairs'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Home Office Furniture : Office Chairs'
where category = 'Home Office Furniture:  Office Chairs'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Home Office Furniture : Office Chairs'
where category = 'Home Office Furniture:  Office Chairs' and site = 'RTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Home Office Furniture : Office Chairs'
where category = 'Home Office : Furniture : Office Chairs' and site = 'RTG'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Home Office Furniture : Office Chairs'
where category = 'Home Office Furniture : Office Chair'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Home Office Furniture : Office Chairs'
where category = 'Adult : Home Office Furniture : Office Chairs'



Adult : Home Office Furniture : Office Chairs


select * from category where cat_title like '%rugs%'


Kids: Accent Furniture: Rugs

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Lighting/Lanterns'
where category = 'Accessories : Chandeliers' and site = 'OTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Lighting/Lanterns'
where category = 'Accessories : Sconces' and site = 'OTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Chandeliers'
where category = 'Accessories: Pendants'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Wall Decor'
where category = 'Kids: Accessories: Wall Dcor'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Wall Decor'
where category = 'Kids:Accessories:Wall Dcor'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Wall Decor'
where category = 'Accessories: Wall Dcor'


Accessories: Wall Dcor
Kids : Accessories : Wall Decor

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Wall Decor'
where category = 'Accessories : Wall Dcor'



Kids : Accessories : Wall Decor


select * from category where cat_title like '%end%'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Side Chairs'
where category = 'Dining Room : Side Chairs'

Dining Room : Side Chairs

---
update eCatalogDB.dbo.BATCH_items_build_data 
set category = replace(category,'Outdoor : ','')
where category like 'Outdoor : %'

OTG	Outdoor : Dining : Bar Stool
OTG	Outdoor : Dining : Dining Chairs
OTG	Outdoor : Dining : Dining Tables
OTG	Outdoor : Seating : Chairs
OTG	Outdoor : Seating : End Tables

Accessories : Mirrors
Accessories : Wall Dcor
Bedrooms : Bedding

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Decorative Accents'
where category = 'Accesssories : Decorative Accents'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Decorative Accents'
where category = 'Accessoires : Decorative Accents'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Decorative Accents'
where category = 'Accessories: Decorative Accents'

	Accessories: Decorative Accents

Outdoor : Accessories : Decorative Accents

select * from category where cat_title like '%Accents%'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Decorative Accents'
where category = 'Adult: Accessories: Decorative Accents'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Decorative Accents'
where category = 'Adult : Accessories : Decorative Accents'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Decorative Accents'
where category = 'Outdoor : Accessories : Decorative Accents'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Decorative Mirrors'
where category = 'Adult : Accessories : Decorative Mirror'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Decorative Mirrors'
where category = 'Accessories : Mirrors'

Accessories : Mirrors

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Decorative Mirrors'
where category = 'Adult : Accessories : Decorative Mirrors'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Decorative Mirrors'
where category = 'Accessoires : Decorative Mirrors'

select * from category where cat_title like '%decorative%'

Adult : Accessories : Decorative Mirror



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Headboards'
where category = 'Bedroom: Headboards'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Headboards'
where category = 'Adult : Bedroom: Headboards'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Headboards'
where category = 'Bedrooms : Headboards'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Headboards'
where category = 'Adult : Bedroom : Headboards'


Bedroom: Padded Headboards

select * from category where cat_title like '%headboard%'

Bedrooms : Headboards

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Padded Headboards'
where category = 'Bedroom: Padded Headboards' and site = 'KTG'


select * from category where cat_title like '%chairs%' and cat_belongstosite = 'RTG'

Kids : Bedding : Full Bedding


Accessories: Decorative Accents

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Wall Decor'
where category = 'Accessories : Wall Dcor'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Tables : Sofa Tables'
where category = 'Tables: Sofa Tables'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Tables : Sofa Tables'
where category = 'Tables: Sofa Table'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Tables : Sofa Tables'
where category = 'Living Room : Sofa Tables'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Tables : Sofa Tables'
where category = 'Adult : Tables : Sofa Tables'




Living Room : Sofa Tables

Tables: Sofa Tables

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Accent Tables'
where category = 'Accessories :  Accent Tables'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Accent Tables'
where category = 'Accessoreis : Accent Tables'



Accessories :  Accent Tables

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Accent Benches'
where category = 'Accessories: Accent Benches'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Accent Benches'
where category = 'Accessories : Acccent Benches'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Accent Benches'
where category = 'Accessories : Accents Benches'

Accessories : Accents Benches
Accessories : Accents Benches

Accessories : Accents Benches

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Accent Benches'
where category = 'Adult : Accessories : Accent Bench'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Side Chairs'
where category = 'Adult : Diningroom : Side Chairs'



Adult : Diningroom : Side Chairs



Accessories : Accent Bench

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Accent Benches'
where category = 'Accessories : Accent Bench'


Accessories: Accent Benches	

Accecories : Accent Bench
Accecories : Table Lamp
Accessories : Floor Lamp


18511445	Manual

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Wall Decor'
where category = 'Adult : Accessories : Wall Decor'

update eCatalogDB.dbo.BATCH_items_build_data 
set features = 'With Electric Fireplace'
where features = 'Electric Fireplace'

update eCatalogDB.dbo.BATCH_items_build_data 
set features = 'With Electric Fireplace'
where features = 'Fireplace'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Tables : End Tables'
where category = 'Seating : End Tables'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Tables : End Tables'
where category = 'Seating : End Table'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Tables : End Tables'
where category = 'Livingroom : End Tables'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Tables : End Tables'
where category = 'Tables : End Table'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Tables : End Tables'
where category = 'Adult : Tables: End Tables'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Tables : End Tables'
where category = 'Tables: End Tables'

Tables : End Table

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Tables : End Tables'
where category = 'Tables: End Tables'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Tables : End Tables'
where category = 'Tables : End Table'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Tables : End Tables'
where category = 'Tables:End Tables'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Accent Tables'
where category = 'Seating : Coffee Tables' and isbuilt = 0 and site = 'RTG'




update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : End Tables'
where category = 'Seating : Coffee Tables' and isbuilt = 0 and site = 'OTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Accent Tables'
where category = 'Accessories : Decorative Accents' and isbuilt = 0 and site = 'OTG'


Outdoor : Accessories : Decorative Accents


select * from eCatalogDB.dbo.category where cat_title like '%accent%'  and cat_belongstosite = 'OTG'

Living Room : Accent Chairs
Living Room : Chaises


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Chaises'
where category = 'Living Room : Chaises'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Chaises'
where category = 'Livingrom : Chaises'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Chaises'
where category = 'Adult : Livingroom : Chaises'




update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Accent Chairs'
where category = 'Living Room : Accent Chairs'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Accent Chairs'
where category = 'Livingrom : Accent Chairs'


Living Room : Accent Chairs

Adult : Livingroom : Accent Chairs


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Dressers'
where category = 'Bedroom: Dressers'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Dressers'
where category = 'Bedroom : Dresser'



Bedroom: Dressers
Home Office Furniture: Desk

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Home Office Furniture : Bookcases'
where category = 'Home Office Furniture: Bookcases'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Home Office Furniture : Bookcases'
where category = 'Home Office Furiture : Bookcases'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Home Office Furniture : Bookcases'
where category = 'Adult : Home Office Furniture : Bookcases'


Home Office Furniture: Bookcases

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Home Office Furniture : Desks'
where category = 'Home Office Furniture: Desks'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Home Office Furniture : Desks'
where category = 'Adult : Home Office Furniture : Desks'




update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Home Office Furniture : Desks'
where category = 'Home Office Furniture: Desk'


Home Office Furniture: Desk




Kids : Bedroom : Beds

Kids : Bedroom : Beds
Kids : Bedroom : Dressers

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Barstools'
where category = 'Dining Room : Barstools'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Barstools'
where category = 'Dining Room : Barstools'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Barstools'
where category = 'Diningroom : Barstool'

Adult: Diningroom: Barstools

Dining Room : Barstools


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Benches'
where category = 'Dining Room : Benches'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Benches'
where category = 'Diningroom : Dining Benches'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Benches'
where category = 'Adult : Diningroom : Benches'



RTG	
Adult : 
select * from eCatalogDB.dbo.BATCH_items_build_data where category = 'Dining Room : Dining Chairs'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Side Chairs'
where category = 'Dining Room : Dining Chairs'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Side Chairs'
where category = 'Dining Room : Side Chairs'

Dining Room : Side Chairs


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Arm Chairs'
where category = 'Dining Room : ArmChairs'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Arm Chairs'
where category = 'Dining Room : Arm Chairs'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Dining : Arm Chairs'
where category = 'Diningroom : Arm Chairs' and site = 'OTG'




update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Arm Chairs'
where category = 'Diningrom : Arm Chairs'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Arm Chairs'
where category = 'Diningroom : Arm Chair'



Dining Room : ArmChairs

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Dining Tables'
where category = 'Dining Room : Dining Tables'




Outdoor : Seating : End Tables

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Beds'
where category = 'Bedrooms : Beds'

Bedroom : Bed

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Beds'
where category = 'Bedroom: Beds'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Beds'
where category = 'Adult : Bedroom : Beds'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Beds'
where category = 'Adult : Bedroom: Beds'

Adult : Bedroom: Beds

RTG	Adult : Bedroom: Headboards


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Beds'
where category = 'Bedroom : Bed'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Daybeds'
where category = 'Bedroom: Daybeds'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Daybeds'
where category = 'Bedroom : Daybed'

Bedroom : Daybed

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Daybeds'
where category = 'Adult : Bedroom : Daybeds'




update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Trundle Beds'
where category = 'Bedroom: Trundle Beds'


update ipackage set ipac_name = replace(ipac_name,'Kind','King') where ipac_sku = '84283630'

Kids : Bedroom : Bed Add-Ons
Kids : Bedroom : Dressers
Kids : Bedroom : Nightstands
Kids : Bedrooms : Beds


select * from eCatalogDB.dbo.BATCH_items_build_data  where sku = '21248340'

select * from dbo.attributevalues where 

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Wall Decor'
where category = 'Accessories : Wall Dcor'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Accent Chairs'
where category = 'Livingroom: Accent Chairs'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Accent Chairs'
where category = 'Livingroom: Accent Chair'

Livingroom: Accent Chair

Livingroom: Accent Chairs


Living Room : Accent Chairs

Living Room : Accent Chairs

RTG	Living Room : Accent Chairs

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Chairs'
where category = 'Seating : Chairs/ Chaises'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Chairs/Chaises'
where category = 'Seating : Chairs' and site = 'KTG'


Living Room : Accent Chairs
Living Room : Chaises

select * from category where cat_title like '%seating%' and cat_belongstosite = 'KTG'
select ipac_sku from categoryipackages where cat_id = 220
intersect
select ipac_sku from ipackage_region_data where ipac_isavailable = 1
intersect
select ipac_sku from ipackage where ipac_name like '%crib%'

Baby Furniture: Crib Beds

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Chairs/Chaises'
where category = 'Kids : Seating : Chairs/Chaises' and site = 'KTG'
Kids : Seating : Chairs/Chaises

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Chairs/Chaises'
where category = 'Seating:Chairs/Chaises' and site = 'KTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Chairs/Chaises'
where category = 'Kids : Seating : Chairs' and site = 'KTG'

Seating : Chaises/Lounges

Seating:Chairs/Chaises



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Beds'
where category = 'Baby Furniture: Crib Beds' and site = 'KTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Beds'
where category = 'Kids : Bedroom : Beds' and site = 'KTG'



Kids : Bedroom : Beds

Seating: Chairs/Chaises
Adult : Livingroom : Chairs

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Chairs'
where category = 'Adult : Livingroom : Chairs'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Sconces'
where category = 'Accessories: Sconces'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Floor Lamps'
where category = 'Accessories: Floor Lamps'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Floor Lamps'
where category = 'Accessories : Floor Lamp'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Floor Lamps'
where category = 'Accessories: Floor Lamp'

site	category
RTG	Accessories: Floor Lamp
RTG	Bedroom: Accent Pieces
RTG	Diningroom: Barstools
RTG	Livingroom: Accent Chair

Adult : Bedroom : Accent Pieces

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Accent Pieces'
where category = 'Bedrooom : Accent Pieces'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Accent Pieces'
where category = 'Adult : Bedroom: Accent Pieces'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Accent Pieces'
where category = 'Bedroom: Accent Pieces'

Bedroom: Accent Pieces

Bedrooom : Accent Pieces

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Accent Pieces'
where category = 'Adult : Bedroom : Accent Pieces'


Accessories : Floor Lamp

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Table Lamps'
where category = 'Accessories : Table Lamp'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Wall Decor'
where category = 'Accessories : Wall Dcor'


Accecories : Table Lamp
Accessories : Floor Lamp

Accessories : Table Lamp
Accessories : Wall Dcor

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Chandeliers'
where category = 'Accessories: Chandeliers'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Chandeliers'
where category = 'Accessories : Chaneliers'

Accessories : Floor Lamp
Accessories : Table Lamp
Home Office Furniture : Desk

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Wall Decor'
where category = 'Accessories : Wall Dcor'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Floor Lamps'
where category = 'Accessories : Floor Lamp'
Accessories : Table Lamp

RTG	Accessories : Table Lamp


Accessories: Chandeliers
Accessories: Floor Lamps
Accessories: Sconces
Accessories: Table Lamps

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Chandeliers'
where category = 'Accessories: Chandeliers'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Sconces'
where category = 'Accessories: Sconces'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Barstools'
where category = 'Diningroom: Barstools'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Barstools'
where category = 'Diningroom: Barstool'

s

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Side Chairs'
where category = 'Diningroom : Side Cairs'

Diningroom : Side Cairs

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Side Chairs'
where category = 'Diningroom : Side Chair'


Accent Benches	Adult : Accessories : Accent Benches


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Dining Tables'
where category = 'Diningroom: Dining Tables'




Diningroom : Dinng Tables






update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Barstools'
where category = 'Diningroom : Barstool'

select * from category where cat_title like '%accent%' and cat_belongstosite = 'RTG'

select * from categoryipackages where cat_id = 366
order by created_datetime desc

Accent Furniture : TV Console

Outdoor : Accessories : Rugs

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Rugs'
where category = 'Outdoor : Accessories : Rugs'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accent Furniture : Rugs'
where category = 'Accessories : Rugs' and site = 'KTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accent Furniture : Rugs'
where category = 'Kids : Accessories : Rugs' and site = 'KTG'




Accessories : Rugs

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accent Furniture : Rugs'
where category = 'Kids : Accent Furniture : Rugs'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Rugs'
where category = 'Accessories: Rugs'
 and site = 'RTG'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Rugs'
where category = 'Accessories:Rugs'
 and site = 'RTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Rugs'
where category = 'Accessories :Rugs'
 and site = 'RTG'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Rugs'
where category = 'Accessories: Rug'
 and site = 'RTG'


 


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Rugs'
where category = 'Accesseories : Rugs'

Accesseories : Rugs


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Rugs'
where category = 'Decor : Rugs'
 and site = 'RTG'



select * from category where cat_long_title like '%rugs%'

Accessories: Rugs
Adult : Accessories : Rugs

Kids : Accent Furniture : Rugs

select * from category where cat_title like '%rugs%'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Chairs'
where category = 'Outdoor : Seating : Chairs'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Ottomans'
where category = 'Outdoor : Seating : Ottomans'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Chairs'
where category = 'Outdoor : Seating : Chairs'

Outdoor : Seating : Chairs



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accent Furniture : TV Consoles'
where category = 'Accent Furniture: TV Consoles'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accent Furniture : TV Consoles'
where category = 'Accent Furniture : TV Console'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accent Furniture : TV Consoles'
where category = 'Accent Funiture: TV Consoles'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accent Furniture : TV Consoles'
where category = 'Adult : Accent Furniture : TV Consoles'





update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accent Furniture : TV Consoles'
where category = 'Accent Furnitire : TV Consoles'

Accent Furnitire : TV Consoles

Accent Furnitire : TV Consoles

Accent Furniture : Tv Console

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accent Furniture : Accent Cabinets'
where category = 'Accent Furniture: Accent Cabinets'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accent Furniture : Accent Cabinets'
where category = 'Accent Furniture : Accents Cabinets'
Living Room : Accent Chairs

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accent Furniture : Accent Cabinets'
where category = 'Accent Funiture: Accent Cabinets'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accent Furniture : Accent Cabinets'
where category = 'Accent Furniture : Accent Cabinet'




update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accent Furniture : Accent Cabinets'
where category = 'Accent Furnitur e: Accent Cabinets'

select * from category where cat_title like '%chests%' and cat_belongstosite = 'RTG'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Chests'
where category = 'Bedroom: Chests'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Chests'
where category = 'Bedroom: Chest'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Chests'
where category = 'Adult : Bedroom: Chests'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Chests'
where category = 'Adult : Bedroom : Chests'



Adult : Bedroom : Chests

Accent Furniture: Accent Cabinets

Accent Furniture: Accent Cabinets

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accent Furniture : Accent Cabinets'
where category = 'Accent Furniture : Accent Cabinet'



Livingroom : Cocktail Tables
Adult : Accent Furniture : TV Consoles

Accessories: Chandeliers
Accessories: Floor Lamps
Accessories: Sconces
Accessories: Table Lamps

RTG	Accessories: Chandeliers
RTG	Accessories: Floor Lamp
RTG	Accessories: Pendants
RTG	Accessories: Sconces
RTG	Accessories: Table Lamp

Livingroom : Cocktail Tables

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Lamps/Lanterns'
where category = 'Accessories : Table Lamps' and site = 'OTG'

Adult : Accessories : Lamps/Lanterns

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Lamps/Lanterns'
where category = 'Outdoor : Accessories : Lamps/Lanterns' and site = 'OTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Lamps'
where category = 'Adult : Accessories : Lamps/Lanterns' and site = 'RTG'




Lamps/Lanterns

select * from category where cat_title like '%pend%' and cat_belongstosite = 'RTG'

Tables : Table Set
Tables : Table Sets

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Tables : Table Sets'
where category = 'Tables : Table Set'


Accessories :  Accent Tables

Adult : Accessories : Accent Tables

select * from category where cat_title like '%accent%' and cat_belongstosite = 'RTG'


Livingroom : Cocktail Tables
Living Room : Cocktail Tables


366	Accent Pieces	Adult : Bedroom : Accent Pieces	RTG	1	getItemResults	NULL	0	1	NULL	1
381	Accent Chairs	Adult : Livingroom : Accent Chairs	RTG	17	getItemResults	NULL	0	1	NULL	1
4	Accent Furniture	Adult : Accent Furniture	RTG	61	getItemResults	Icon_Accent.jpg	8	1	NULL	1
176	Decorative Accents	Adult : Accessories : Decorative Accents	RTG	173	getItemResults	Accessories_DecorativeItems.jpg	0	1	NULL	1
190	Accent Pillows	Adult : Accessories : Accent Pillows	RTG	173	getItemResults	Accessories_AccentPillows.jpg	0	1	NULL	1
66	Accent Cabinets	Adult : Accent Furniture : Accent Cabinets	RTG	173	getItemResults	accents.gif	0	1	NULL	1
325	Accent Tables	Adult : Accessories : Accent Tables	RTG	173	getItemResults	NULL	0	1	NULL	1
326	Accent Benches	Adult : Accessories : Accent Benches	RTG	173	getItemResults	NULL	0	1	NULL	1
361	iSOFA Accent Pillows	Adult : iSOFA Furniture : iSOFA Accent Pillows	RTG	347	getItemResults	NULL	0	1	NULL	0

Acccessories : Accent Tables

RTG	Accessories : Floor Lamp
RTG	Accessories : Table Lamp
RTG	Livingroom : Cocktail Tables

RTG	Accessories: Chandeliers
RTG	Accessories: Floor Lamps
RTG	Accessories: Sconces
RTG	Accessories: Table Lamps

RTG	Diningroom : Table Sets
RTG	Livingroom : Cocktail Tables

Adult : Living Room : Cocktail Tables
Accent Furniture : Accent Cabinet

RTG	Diningroom : Dining Table
RTG	Livingrooms : Accent Chairs

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Living Room : Cocktail Tables'
where category = 'Living Room :  Cocktail Table'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Living Room : Cocktail Tables'
where category = 'Adult : Living Room : Cocktail Tables'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Living Room : Cocktail Tables'
where category = 'Living Room : Cocktail Table'





update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Living Room : Cocktail Tables'
where category = 'Adult : Livingroom : Cocktail Tables'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Tables : End Tables'
where category = 'Adult : Tables : End Tables'
and site = 'RTG'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Barstools'
where category = 'Adult :Diningroom : Barstools'
and site = 'RTG'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Sectionals'
where category = 'Livingroomm : Sectionals'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Living Room : Cocktail Tables'
where category = 'Livingroom : Cocktail Tables'

Livingroomm : Sectionals

Livingroom : Cocktail Tables

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Coffee Tables'
where category = 'Living Room : Cocktail Tables'
and site = 'OTG'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Seating : Chaise/Lounges'
where category = 'Seating : Chaises/Lounges'
and site = 'OTG'


 
Living Room :  Cocktail Table

Livingroom: Cocktail Tables

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accent Furniture : Lamps'
where category = 'Kids : Accent Furniture : Lamps'






RTG	Diningroom : Buffer Servers
RTG	Diningroom : Dining Table
RTG	Livingroom : Cocktail Tables


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Home Office Furniture : Desks'
where category = 'Home Office Furniture : Desk'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Home Office Furniture : Desks'
where category = 'Home Office : Furniture : Desks'



Home Office Furniture : Desk
Adult : Home Office Furniture : Desks

select * from category where cat_title like '%table%' and cat_belongstosite = 'OTG'

Living Room : Cocktail Tables

Accent Furnitire : TV Consoles
Livingroom : Cocktail Tables

Livingroom : Cocktail Tables

Adult : Bedroom : Nightstands

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Nightstands'
where category = 'Bedroon : Nightstand'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Nightstands'
where category = 'Bedroom: Nightstands'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Bedroom : Nightstands'
where category = 'Adult : Bedroom : Nightstands'



RTG	Livingroom : Cocktail Tables

Livingroom : Cocktail Tables

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Living Room : Cocktail Tables'
where category = 'Livingroom : Cocktail Tables'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Living Room : Cocktail Tables'
where category = 'Livingroom: Cocktail Tables'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Living Room : Cocktail Tables'
where category = 'Livingroom : Cocktail Table'




Livingroom : Cocktail Tables

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Living Room : Cocktail Tables'
where category = 'Livingroom: Cocktail Table'

Livingroom: Cocktail Table

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Living Room : Cocktail Tables'
where category = 'Living Rooms : Cocktail Tables'



Livingroom : Cocktail Tables
update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Accent Chairs'
where category = 'Livingroom: Accent Chair'

Livingroom: Accent Chair

Accent Furniture : Accent Cabinet
Livingroom : Cocktail Tables

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Dining Tables'
where category = 'Dining Room : Dining Tables'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Buffet Servers'
where category = 'DiningroomL Buffet Servers'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Buffet Servers'
where category = 'Diningroom: Buffet Servers'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Buffet Servers'
where category = 'Adult : Diningroom : Buffet Servers'

Adult : Diningroom : Buffet Servers



DiningroomL Buffet Servers


Livingroom : Cocktail Tables
Livingroom: Loveseats
Livingrooms : Cocktail Tables

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Loveseats'
where category = 'Livingroom: Loveseats'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Loveseats'
where category = 'Livingroom : Loveseat'


Adult : Livingroom : Loveseats

select * from category where cat_title like '%night%'

Accessories : Accent Tabels
Adult : Accessories : Accent Tables

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Accent Tables'
where category = 'Accessories : Accent Tbles'



update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Accent Tables'
where category = 'Adult : Accessories : Accent Tables'



Accessories :  Accent Tables


Livingroom : Accent Chiars


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Accent Chairs'
where category = 'Living Room : Accent Chairs'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Accent Chairs'
where category = 'Adult : Livingroom : Accent Chairs'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Recliners'
where category = 'Adult : Livingroom : Recliners'



Adult : Livingroom : Accent Chairs


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Livingroom : Accent Chairs'
where category = 'Adult : Livingroom : Accent Chairs'





RTG	Living Room : Accent Chairs





Livingrooms : Accent Chairs

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Diningroom : Dining Tables'
where category = 'Diningroom : Dining Table'


update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accent Furniture : Accent Cabinets'
where category = 'Accent Furniture : Accent Cabinet'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accent Furniture : Accent Cabinets'
where category = 'Adult : Accent Furniture : Accent Cabinets'




RTG	Home Decor : Accent Benches
RTG	Living Room : Accent Chairs
RTG	Living Room : Ottomans

Kids: Accent Furniture: Lamps

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Floor Lamps'
where category = 'Accessories : Floor Lamp'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Table Lamps'
where category = 'Accessories : Table Lamp'

update eCatalogDB.dbo.BATCH_items_build_data 
set category = 'Accessories : Table Lamps'
where category = 'Accessories: Table Lamps'



Accessories : Floor Lamp


update eCatalogDB.dbo.BATCH_items_build_data 
set color = 'Glass'
where color = 'Crystal'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set Finish = 'Brown'
where Finish = 'Brrown'
and sku = '87014329'
AND isbuilt =  1 AND isclosed = 0

	Finish	Brrown

update eCatalogDB.dbo.BATCH_items_build_data 
set color = 'Brown'
where color = 'More'
AND isbuilt =  1 AND isclosed = 0


99114363	Product Color	

update eCatalogDB.dbo.BATCH_items_build_data 
set color = 'Ivory'
where color = 'Torric'
AND isbuilt =  1 AND isclosed = 0

Torric

update eCatalogDB.dbo.BATCH_items_build_data 
set color = 'Dark Brown'
where sku = '21003544'
AND isbuilt =  1 AND isclosed = 0

	


update eCatalogDB.dbo.BATCH_items_build_data 
set fabric = 'Vinyl,Polyester,Steel'
where fabric = 'Vinyl,Polyester,Steeel'
AND isbuilt =  1 AND isclosed = 0




update eCatalogDB.dbo.BATCH_items_build_data 
set fabric = 'Polyurethane'
where fabric = 'Polyutherane'
AND isbuilt =  1 AND isclosed = 0




update eCatalogDB.dbo.BATCH_items_build_data 
set fabric = 'Polyester'
where fabric = 'Polyester Blend'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set style = 'Square,Rectangle'
where style = 'Square, Rectangle'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set style = 'Upholstered'
where style = 'Upholstred'
AND isbuilt =  1 AND isclosed = 0
where sku = '82044098'

82044098
	Style	

update eCatalogDB.dbo.BATCH_items_build_data 
set style = 'Rectangle'
where style = 'Rectngle'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set style = 'Floor'
where sku = '93283782'
AND isbuilt =  1 AND isclosed = 0

93279846
93283782

Outdoor Table Lamp
Outdoor Floor Lamp


update eCatalogDB.dbo.BATCH_items_build_data 
set decor = 'Transitional'
where decor = 'Transitonal'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set decor = 'Transitional'
where decor = 'Transtitional'
AND isbuilt =  1 AND isclosed = 0


update eCatalogDB.dbo.BATCH_items_build_data 
set decor = 'Traditional'
where decor = 'Tradititional'
AND isbuilt =  1 AND isclosed = 0



update eCatalogDB.dbo.BATCH_items_build_data 
set decor = 'Contemporary'
where decor = 'Contemporay'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set decor = replace(decor,'Comtemporary','Contemporary')
where decor like '%Comtemporary%'
AND isbuilt =  1 AND isclosed = 0

Comtemporary

update eCatalogDB.dbo.BATCH_items_build_data 
set decor = 'Boho,Contemporary'
where decor = 'Boho - Contemporary'
AND isbuilt =  1 AND isclosed = 0



update eCatalogDB.dbo.BATCH_items_build_data 
set decor = 'Contemporary'
where decor = 'Conteporary'
AND isbuilt =  1 AND isclosed = 0



update eCatalogDB.dbo.BATCH_items_build_data 
set color = 'Light Blue'
where color = 'Ligth Blue'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set color = 'Navy'
where color = 'Navy Blue'
AND isbuilt =  1 AND isclosed = 0



update eCatalogDB.dbo.BATCH_items_build_data 
set finish = 'Pink'
where finish = 'Pink Rose'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set size = 'Counter Height'
where size = 'Counter Stool'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set size = 'Counter Height'
where size = 'Counter'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set size = 'Bar Height'
where size = 'Bar'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set size = 'Bar Height', Style = ''
where Style = 'Bar'
AND isbuilt =  1 AND isclosed = 0 and sku = '41321009'

Bar Height

color
41400336	
finish
40400373	Pink Rose
size
41400348	Conter Height

RTG	20110259	Grey
RTG	20210251	Grey


update eCatalogDB.dbo.BATCH_items_build_data 
set finish = 'Stone Wash'
where finish = 'Stonewash'
AND isbuilt =  1 AND isclosed = 0

Stone Wash

update eCatalogDB.dbo.BATCH_items_build_data 
set finish = 'Beige'
where finish = 'Biege'
AND isbuilt =  1 AND isclosed = 0


update eCatalogDB.dbo.BATCH_items_build_data 
set color = 'Emerald'
where color = 'Emerald Green'
AND isbuilt =  1 AND isclosed = 0
and sku = '40600391'

	Castolon

update eCatalogDB.dbo.BATCH_items_build_data 
set color = 'Pink'
where sku = '96677677'


update eCatalogDB.dbo.BATCH_items_build_data 
set color = 'Cobalt'
where color = 'Colbalt'
AND isbuilt =  1 AND isclosed = 0
and sku = '18358641'

update eCatalogDB.dbo.BATCH_items_build_data 
set color = 'Yellow'
where color = 'Yelow'
AND isbuilt =  1 AND isclosed = 0


update eCatalogDB.dbo.BATCH_items_build_data 
set finish = 'Yellow'
where finish = 'Yelow'
AND isbuilt =  1 AND isclosed = 0


40600391	Emerald Green

20040349	Biege

Conteporary


sku                         fabric
10402852            Faux Fur Should be Synthetic

update eCatalogDB.dbo.BATCH_items_build_data 
set fabric = 'Synthetic'
where fabric = 'Faux Fur'
AND isbuilt =  1 AND isclosed = 0

sku                         finish
21202421            Light Silver Should just be Silver

update eCatalogDB.dbo.BATCH_items_build_data 
set finish = 'Silver'
where finish = 'Light Silver'
AND isbuilt =  1 AND isclosed = 0


update eCatalogDB.dbo.BATCH_items_build_data 
set finish = 'Brown'
where finish = 'Borwn'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set finish = '', color='Sage'
where finish = 'Sage'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set color = 'Turquoise'
where color = 'Turquiose'
AND isbuilt =  1 AND isclosed = 0




update eCatalogDB.dbo.BATCH_items_build_data 
set  color='Gray'
where color = 'Grey'
AND isbuilt =  1 AND isclosed = 0
and sku in ('30000107','30200098','30300141','30400131','30400155','30000222','30200264','30300317','30400422','30400458','30000397','30200389','30300456','30400674','30400686')

update eCatalogDB.dbo.BATCH_items_build_data 
set finish = 'Brushed Nickel'
where finish = 'Nickel'
AND isbuilt =  1 AND isclosed = 0


update eCatalogDB.dbo.BATCH_items_build_data 
set decor = 'Rustic'
where decor = 'Rustivc'
AND isbuilt =  1 AND isclosed = 0


update eCatalogDB.dbo.BATCH_items_build_data 
set decor = 'Rustic'
where decor = 'Rucstic'
AND isbuilt =  1 AND isclosed = 0


update eCatalogDB.dbo.BATCH_items_build_data 
set decor = 'Rustic'
where decor = 'Rucstic'
AND isbuilt =  1 AND isclosed = 0


update eCatalogDB.dbo.BATCH_items_build_data 
set decor = 'Mid Century Modern'
where decor = 'Mid-Century'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set decor = 'Mid Century Modern'
where decor = 'Midcentury Modern'

update eCatalogDB.dbo.BATCH_items_build_data 
set decor = 'Mid-Century Modern'
where decor = 'Mid Century'
AND isbuilt =  1 AND isclosed = 0
Mid Century


Accesssories : Decorative Accents

02E37810-2830-4DED-A813-9C2DDB917B34


update eCatalogDB.dbo.BATCH_items_build_data 
set decor = 'Mid Century Modern'
where decor = 'Mid-century modern'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set decor = 'Mid Century Modern'
where decor = 'Mid-Centruy Modern'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set decor = 'Boho,Mid Century Modern'
where decor = 'Boho,Mid Century'
AND isbuilt =  1 AND isclosed = 0


update eCatalogDB.dbo.BATCH_items_build_data 
set decor = 'Traditional'
where decor = 'Traditonal'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set decor = replace(decor,'Mid Century Modern,','Mid-Century Modern,')
where decor like '%Mid Century Modern%'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set decor = replace(decor,'Mid Century Modern,','Mid-Century Modern,')
where decor like '%Mid Century Modern%'
AND isbuilt =  1 AND isclosed = 0

Mid Century Modern,Glam
85775747

update eCatalogDB.dbo.BATCH_items_build_data 
set decor = replace(decor,'Mid Century,','Mid Century Modern,')
where decor like '%,Mid Century'
AND isbuilt =  1 AND isclosed = 0

Boho,Mid Century

Contemporary,glam

Mid-Century Modern, Industrial

update eCatalogDB.dbo.BATCH_items_build_data 
set decor = 'Mid Century Modern'
where decor = 'Mid Century'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set decor = 'Mid-Century Modern'
where decor = 'Mid Century'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set decor = 'Coastal'
where decor = 'Costal'
AND isbuilt =  1 AND isclosed = 0



Costal
Mid Century


update eCatalogDB.dbo.BATCH_items_build_data 
set color = 'White'
where sku = '41401112'
AND isbuilt =  1 AND isclosed = 0

RTG	41400677	Height
RTG	41401112	Height


RTG	99431961	Nickel


update eCatalogDB.dbo.BATCH_items_build_data 
set size = '', style='Chandelier'
where size = 'Pendant'
AND isbuilt =  1 AND isclosed = 0


update eCatalogDB.dbo.BATCH_items_build_data 
set  style='Floor'
where sku = '90286381'

AND isbuilt =  1 AND isclosed = 0
90179411	LAMP	Table
90184234	LAMP	Table
90283816	LAMP	Floor
90283866	LAMP	Floor
90286381	LAMP	Floor

size
Floor
Table
Chandelier
Pendant

update eCatalogDB.dbo.BATCH_items_build_data 
set size = 'Standard Height'
where size = 'Standard'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set size = 'Standard Height'
where sku = '82043969'
AND isbuilt =  1 AND isclosed = 0

82043969	Size	Standard

	Size	Standard

RTG	21658767	25" - 58"
RTG	40127222	Standard
RTG	21652246	52"
RTG	21670321	70'

update eCatalogDB.dbo.BATCH_items_build_data 
set size = '70"'
where sku = '21670321'

update eCatalogDB.dbo.BATCH_items_build_data 
set size = '5''3 x 7'''
where size = '5''3x7'''


RTG	21638157	55"
update eCatalogDB.dbo.BATCH_items_build_data 
set style='',size = '55"'
where sku = '21638171'

21638169	55"
21638183	55"
21638171	55"

update eCatalogDB.dbo.BATCH_items_build_data 
set size = ''
where sku = '99161045'

99161259
99161146
99161045

update eCatalogDB.dbo.BATCH_items_build_data 
set finish = 'Metal', style = '', fabric=''
where sku = '30202523'
where size = 'Standard'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set movement = 'Non-Power Reclining'
where  movement = 'Reclining'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set movement = 'Stationary', style = ''
where sku  = '21142574'
AND isbuilt =  1 AND isclosed = 0



10189911	Reclining

update eCatalogDB.dbo.BATCH_items_build_data 
set features = 'With Electric Fireplace'
where features = 'Electric Fireplace'
AND isbuilt =  1 AND isclosed = 0


update eCatalogDB.dbo.BATCH_items_build_data 
set finish = 'Chrome'
where sku = '41417026'

41417026	Chorme

update eCatalogDB.dbo.BATCH_items_build_data 
set size = 'Standard Height'
where sku = '40110037'

40110037

update eCatalogDB.dbo.BATCH_items_build_data 
set style = ''
where sku = '18312265'



update eCatalogDB.dbo.BATCH_items_build_data 
set size = '6''7 Round'
where size = '6''7 X 6''7 Round'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set size = '6''7 x 6''7'
where size = '6''7 x 6''7 Square'
AND isbuilt =  1 AND isclosed = 0




update eCatalogDB.dbo.BATCH_items_build_data 
set style = 'Round'
where style = 'Circle'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set size = '8'' Square'
where size = '8'''
AND isbuilt =  1 AND isclosed = 0
and name like '%8'' Square%'

update eCatalogDB.dbo.BATCH_items_build_data
set size = '5'' Square'
where size = '5'''
AND isbuilt =  1 AND isclosed = 0
and name like '%5'' Square%'

6'
4'
5'


RTG	18312265	Navy

update eCatalogDB.dbo.BATCH_items_build_data 
set style = 'Floor'
where style = 'Floor Lamp'
AND isbuilt =  1 AND isclosed = 0


update eCatalogDB.dbo.BATCH_items_build_data 
set style = 'Floor'
where style = 'Floor Lamp'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set style = 'Rectangle', size = null
where size = 'Rectangle'
and sku = '20012100'

AND isbuilt =  1 AND isclosed = 0
site	sku	size
RTG	20012100		Rectangle


update eCatalogDB.dbo.BATCH_items_build_data 
set color = 'Brass'
where sku = '90632196'
AND isbuilt =  1 AND isclosed = 0


update eCatalogDB.dbo.BATCH_items_build_data 
set color = 'Dark Blue'
where sku = '18505062'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set finish = 'Dark Gray'
where finish = 'Drak Gray'
AND isbuilt =  1 AND isclosed = 0


Dark Blue

RTG	18503638	Light
RTG	18505062	Dark


update eCatalogDB.dbo.BATCH_items_build_data 
set finish = 'Light Oak'
where sku = '21210795'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set finish = 'Black'
where finish = 'Balck'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set finish = 'Orange'
where finish = 'Orangge'
AND isbuilt =  1 AND isclosed = 0




update eCatalogDB.dbo.BATCH_items_build_data 
set color = 'Terracotta'
where color = 'Terracota'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set finish = 'Natural'
where finish = 'Natural Wood'
AND isbuilt =  1 AND isclosed = 0



update eCatalogDB.dbo.BATCH_items_build_data 
set color = 'White'
where sku = '41420112'
AND isbuilt =  1 AND isclosed = 0

41420112	Whire

90115532	Smoked
90235752	Mercury

update eCatalogDB.dbo.BATCH_items_build_data 
set movement = 'Rocker'
where movement = 'Rocking'
AND isbuilt =  1 AND isclosed = 0
c

update eCatalogDB.dbo.BATCH_items_build_data 
set color = 'Off-White'
where color = 'Off-Whtie'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set color = 'Off-White'
where color = 'Off White'
AND isbuilt =  1 AND isclosed = 0



update eCatalogDB.dbo.BATCH_items_build_data 
set finish = 'Off-White'
where finish = 'Off'
AND isbuilt =  1 AND isclosed = 0

Off-white



18134611	Rocking
18134623	Rocking

update eCatalogDB.dbo.BATCH_items_build_data 
set size = 'Standard Height'
where size = 'Standard'
AND isbuilt =  1 AND isclosed = 0

40160006	Standard
40160018	Standard

update eCatalogDB.dbo.BATCH_items_build_data 
set size = 'Bar Height'
where size = 'Bar Hieght'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set size = 'Counter Height'
where sku = '40110847'
AND isbuilt =  1 AND isclosed = 0


update eCatalogDB.dbo.BATCH_items_build_data 
set size = '5''2 x 7'
where size = '5''2x7'
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set size = '8'' x 10'
where size = '8x10'
AND isbuilt =  1 AND isclosed = 0
	
update eCatalogDB.dbo.BATCH_items_build_data 
set size = '3''11 x 5''11'
where size = '3''11x5''11'
AND isbuilt =  1 AND isclosed = 0
	
update eCatalogDB.dbo.BATCH_items_build_data 
set size = '4'' x 6'
where size = '4''X6'''
AND isbuilt =  1 AND isclosed = 0

update eCatalogDB.dbo.BATCH_items_build_data 
set size = '6''6 x 9''9'
where size = '6''6X9''9'
AND isbuilt =  1 AND isclosed = 0	

update eCatalogDB.dbo.BATCH_items_build_data 
set size = '2'' x 8'''
where size = '2X8'
AND isbuilt =  1 AND isclosed = 0
	
3'11x5'11
5'2x7
8x10


update eCatalogDB.dbo.BATCH_items_build_data 
set fabric = 'Leather'
where sku = '18519186'
AND isbuilt =  1 AND isclosed = 0


RTG	18519186	Genuine Leather


update eCatalogDB.dbo.BATCH_items_build_data 
set movement = 'Adjustable Height'
where movement = 'Adjustable'
AND isbuilt =  1 AND isclosed = 0

41404447	Adjustable



update eCatalogDB.dbo.BATCH_items_build_data 
set movement = 'Adjustable Height'
where sku = '41610785'
AND isbuilt =  1 AND isclosed = 0

	

update eCatalogDB.dbo.BATCH_items_build_data 
set style = 'Canopy'
where sku = '30310724'
AND isbuilt =  1 AND isclosed = 0
30210823	Canpoy
30310724	Canpoy


select * from ecatalogdb.dbo.category where cat_title like '%accent%' and cat_belongstosite = 'RTG'

Accent Furniture : Accent Cabinet

*/