--DELETING ROOMS OUT OF ECATALOGDB
use ecatalogdb

declare @sku varchar(10)
declare @site char(3)
declare @delete bit
declare @deleteimport BIT 
declare @deleteregion bit
declare @region char(2)

/* 
select * from ipackage where ipac_sku = '2201190P'
select * from ipackage_region_data where ipac_sku in ('51518604','50418601','51018604','50618605','5901860P','50218607','50818609') --= '50618605'
5121771P
select ipac_sku, count(*) from ipackage 
where ipac_sku in (select ipac_sku from ipackage_region_data where ipac_isavailable = 1)
group by ipac_sku
having count(*) > 1


*/

set @site = 'RTG'
set @sku =  '1114290P'
set @region = 'FL'
set @delete = 0
set @deleteregion = 0
set @deleteimport = 0

select * from ecatalogdb.dbo.product where pro_sku = @sku
select * from ecatalogdb.dbo.product_region_data where pro_sku = @sku
if @sku like '%P'
	select * from ecatalogdb.dbo.package_product where pkg_sku = @sku
	
select * from ecatalogdb.dbo.ipackage where  ipac_sku = @sku and ipac_belongstosite = @site
select * from ecatalogdb.dbo.ipackage_region_data where  ipac_sku = @sku  and ipac_belongstosite = @site
select * from ecatalogdb.dbo.ipackageproducts where   ipac_sku = @sku  and ipac_belongstosite = @site
select * from ecatalogdb.dbo.categoryipackages where ipac_sku = @sku

select * from ecatalogdb.dbo.rooms where   roo_sku = @sku and roo_belongstosite = @site
select * from ecatalogdb.dbo.rooms_region_data where  roo_sku = @sku and roo_belongstosite = @site
select * from ecatalogdb.dbo.roomipackages where  roo_sku = @sku and roo_belongstosite = @site
select * from ecatalogdb.dbo.container where con_sku = @sku  and con_belongstosite = @site

if @delete =  1
begin
  if @deleteregion = 1 
  begin
  
	    delete from ecatalogdb.dbo.container where con_sku = @sku  and con_belongstosite = @site and con_region = @region
	    delete from ecatalogdb.dbo.roomipackages where  roo_sku = @sku and roo_belongstosite = @site and roo_region = @region
    	delete from ecatalogdb.dbo.rooms_region_data where  roo_sku = @sku and roo_belongstosite = @site and roo_region = @region
  
      delete from ecatalogdb.dbo.ipackageproducts where   ipac_sku = @sku  and ipac_belongstosite = @site and ipac_region = @region
      delete from ecatalogdb.dbo.ipackage_region_data where  ipac_sku = @sku  and ipac_belongstosite = @site and ipac_region = @region

  end
  else
  begin
  
    delete from ecatalogdb.dbo.container where con_sku = @sku  and con_belongstosite = @site
    delete from ecatalogdb.dbo.roomipackages where  roo_sku = @sku and roo_belongstosite = @site 
    delete from ecatalogdb.dbo.rooms_region_data where  roo_sku = @sku and roo_belongstosite = @site 
  	delete  from ecatalogdb.dbo.rooms where   roo_sku = @sku and roo_belongstosite = @site

    delete	from ecatalogdb.dbo.categoryipackages where ipac_sku = @sku
    delete from ecatalogdb.dbo.ipackageproducts where   ipac_sku = @sku  and ipac_belongstosite = @site
    delete from ecatalogdb.dbo.ipackage_region_data where  ipac_sku = @sku  and ipac_belongstosite = @site
    delete from ecatalogdb.dbo.ipackage where  ipac_sku = @sku and ipac_belongstosite = @site
    
  end

	
	if @deleteimport = 1
	begin
	
		  if @deleteregion = 1 
			begin
				delete from ecatalogdb.dbo.package_product where pkg_sku = @sku and pro_region = @region
				delete from ecatalogdb.dbo.product_region_data where pro_sku = @sku and pro_region = @region
			end
		  else
			begin
				if @sku like '%P'
					delete from ecatalogdb.dbo.package_product where pkg_sku = @sku
				
				delete from ecatalogdb.dbo.product_region_data where pro_sku = @sku
				delete from ecatalogdb.dbo.product where pro_sku = @sku
			end
		
		
	end
	
end

/*

cat_ID	ipac_sku	created_datetime	modified_datetime	published_datetime
insert into categoryipackages
values (500,	'99054480',	'2018-10-31 12:32:40.603',	NULL,	'2018-10-31 21:15:11.840')

insert into categoryipackages
(cat_ID,	ipac_sku)
values ( '511',	'93770836')

select * from productattributes where productattribute_sku  = '2201190P'

delete from productattributes where productattribute_sku  = '2201190P'

cat_ID	ipac_sku	created_datetime	modified_datetime	published_datetime
500	99054480	2018-10-31 12:32:40.603	NULL	

declare @sku varchar(10)
declare @site char(3)

set @site = 'RTG'
set @sku =  '2205678P'
select * from ecatalogdb.dbo.rooms where   roo_sku = @sku and roo_belongstosite = @site
select * from ecatalogdb.dbo.rooms_region_data where  roo_sku = @sku and roo_belongstosite = @site
select * from ecatalogdb.dbo.roomipackages where  roo_sku = @sku and roo_belongstosite = @site
select * from ecatalogdb.dbo.container where con_sku = @sku  and con_belongstosite = @site

    delete from ecatalogdb.dbo.container where con_sku = @sku  and con_belongstosite = @site
	  delete from ecatalogdb.dbo.roomipackages where  roo_sku = @sku and roo_belongstosite = @site 
    delete from ecatalogdb.dbo.rooms_region_data where  roo_sku = @sku and roo_belongstosite = @site 
  	delete  from ecatalogdb.dbo.rooms where   roo_sku = @sku and roo_belongstosite = @site

SELECT * FROM dbo.package_product  
WHERE pro_sku IN (
'78810136','78910138','78990249','78890247','78940117','78974764','78977657','78986959'
)
AND pkg_sku IN (SELECT ipac_sku FROM ipackage WHERE ipac_belongstosite = 'OTG')

update categoryipackages set modified_datetime = null where ipac_sku = '99054480'

SELECT * FROM dbo.ipackageproducts  
WHERE pro_sku IN (
'78810136','78910138','78990249','78890247','78940117','78974764','78977657','78986959'
)
AND ipac_sku IN (SELECT ipac_sku FROM ipackage WHERE ipac_belongstosite = 'OTG')

--DO THE DAMAGE
delete  FROM dbo.ipackageproducts  
WHERE pro_sku IN (
'78810136','78910138','78990249','78890247','78940117','78974764','78977657','78986959'
)
AND ipac_sku IN (SELECT ipac_sku FROM ipackage WHERE ipac_belongstosite = 'OTG')

delete from dbo.package_product 
where pro_sku in ('22001894','23001895') and 
pkg_sku in 
(
select value from dbo.fn_split('1012419P,1012418P,1012422P,1032419P,1032418P,1032422P,1052419P,1052418P,1052420P,1262418P,1262417P,1262419P,1272418P,1272417P,1272419P,1282418P,1282417P,1282419P,1292418P,1292417P,1292419P,1302418P,1302417P,1302419P,1312418P,1312417P',',')
)
and pro_region = 'FL'


SUFUA.22152538	STOFA.22172023
SUFUA.23052537	STOFA.23072022

delete FROM dbo.package_product  
WHERE pro_sku IN (
'23182962','22182961'
)
AND pkg_sku IN ('1213061P','1213063P','1213060P')
and pro_region in ('TX')


select * from package_product where pkg_sku in ('7501447P','7501446P','7501444P','7501445P','7501448P','7501443P')
update package_product set pro_qty = 4 where pkg_sku in ('7501447P','7501446P','7501444P','7501445P','7501448P','7501443P')
and pro_qty = 7 




select * from ipackageproducts where ipac_sku in ('7501447P','7501446P','7501444P','7501445P','7501448P','7501443P')
update ipackageproducts set ipac_pro_quantity = 4 where ipac_sku in ('7501447P','7501446P','7501444P','7501445P','7501448P','7501443P')
and ipac_pro_quantity = 7 

22128664            2219762P (22197621, 22297623)
23028663            2309762P (23097620, 23197622)

1084745P,1124745P,1134745P

RENRA.22197621	1	6.4811	
RENRA.22297623	1	1.9942	
RENRA.23097620	2	6.5808	
RENRA.23197622	2	4.786	


Torio Brown End Table
JWUAA.74461535	2	13.7893	
JWUAA.74561537	6	37.0792	

--MODULAR ONE 
Sku	Title	Add Qty 1	Change Qty 1	DIV
1044039P	Indigo 5 Pc Power Reclining ModularOne	12440246	13440247	SE TX
1044040P	Midnight 5 Pc Power Reclining ModularOne	12440498	13440499	SE 
1044043P	Merlot 5 Pc Power Reclining ModularOne	12440486	13440487	FL SE TX
1044045P	Beige 5 Pc Power Reclining ModularOne	12440210	13440211	FL SE TX
1044046P	Gray 5 Pc Power Reclining ModularOne	12440222	13440223	FL SE TX
1044048P	Off-White 5 Pc Power Reclining ModularOne	12440284	13440285	FL TX
1044049P	Dark Blue 5 Pc Power Reclining ModularOne	12440309	13440300	FL TX

update package_product set pro_qty = 1 where pkg_sku in ('1044039P') and pro_sku = '13440247' and pro_qty = 2 and pro_region in ('SE','TX');
update package_product set pro_qty = 1 where pkg_sku in ('1044040P') and pro_sku = '13440499' and pro_qty = 2 and pro_region in ('SE');
update package_product set pro_qty = 1 where pkg_sku in ('1044043P') and pro_sku = '13440487' and pro_qty = 2 and pro_region in ('FL','SE','TX');
update package_product set pro_qty = 1 where pkg_sku in ('1044045P') and pro_sku = '13440211' and pro_qty = 2 and pro_region in ('FL','SE','TX');
update package_product set pro_qty = 1 where pkg_sku in ('1044046P') and pro_sku = '13440223' and pro_qty = 2 and pro_region in ('FL','SE','TX');
update package_product set pro_qty = 1 where pkg_sku in ('1044048P') and pro_sku = '13440285' and pro_qty = 2 and pro_region in ('FL','TX');
update package_product set pro_qty = 1 where pkg_sku in ('1044049P') and pro_sku = '13440300' and pro_qty = 2 and pro_region in ('FL','TX');

update ipackageproducts set ipac_pro_quantity = 1 where ipac_sku in ('1044039P') and pro_sku = '13440247' and ipac_pro_quantity = 2 and ipac_region in ('SE','TX');
update ipackageproducts set ipac_pro_quantity = 1 where ipac_sku in ('1044040P') and pro_sku = '13440499' and ipac_pro_quantity = 2 and ipac_region in ('SE');
update ipackageproducts set ipac_pro_quantity = 1 where ipac_sku in ('1044043P') and pro_sku = '13440487' and ipac_pro_quantity = 2 and ipac_region in ('FL','SE','TX');
update ipackageproducts set ipac_pro_quantity = 1 where ipac_sku in ('1044045P') and pro_sku = '13440211' and ipac_pro_quantity = 2 and ipac_region in ('FL','SE','TX');
update ipackageproducts set ipac_pro_quantity = 1 where ipac_sku in ('1044046P') and pro_sku = '13440223' and ipac_pro_quantity = 2 and ipac_region in ('FL','SE','TX');
update ipackageproducts set ipac_pro_quantity = 1 where ipac_sku in ('1044048P') and pro_sku = '13440285' and ipac_pro_quantity = 2 and ipac_region in ('FL','TX');
update ipackageproducts set ipac_pro_quantity = 1 where ipac_sku in ('1044049P') and pro_sku = '13440300' and ipac_pro_quantity = 2 and ipac_region in ('FL','TX');


insert into  package_product ([pro_sku],[pkg_sku],[pro_region],[pro_qty],[pro_price],[pro_ppp])
select '12440246' [pro_sku],[pkg_sku],[pro_region],[pro_qty], 395.00 [pro_price] ,14.5421 [pro_ppp] from package_product where pkg_sku in ('1044039P') and pro_sku = '13440247' and pro_region in ('SE','TX');

insert into  package_product ([pro_sku],[pkg_sku],[pro_region],[pro_qty],[pro_price],[pro_ppp])
select '12440498' [pro_sku],[pkg_sku],[pro_region],[pro_qty], 395.00 [pro_price] ,14.5421 [pro_ppp] from package_product where pkg_sku in ('1044040P') and pro_sku = '13440499' and pro_region in ('SE');

insert into  package_product ([pro_sku],[pkg_sku],[pro_region],[pro_qty],[pro_price],[pro_ppp])
select '12440486' [pro_sku],[pkg_sku],[pro_region],[pro_qty], 395.00 [pro_price] ,14.5421 [pro_ppp] from package_product where pkg_sku in ('1044043P') and pro_sku = '13440487' and pro_region in ('FL','SE','TX');

insert into  package_product ([pro_sku],[pkg_sku],[pro_region],[pro_qty],[pro_price],[pro_ppp])
select '12440210' [pro_sku],[pkg_sku],[pro_region],[pro_qty], 395.00 [pro_price] ,14.5421 [pro_ppp] from package_product where pkg_sku in ('1044045P') and pro_sku = '13440211' and pro_region in ('FL','SE','TX');

insert into  package_product ([pro_sku],[pkg_sku],[pro_region],[pro_qty],[pro_price],[pro_ppp])
select '12440222' [pro_sku],[pkg_sku],[pro_region],[pro_qty], 395.00 [pro_price] ,14.5421 [pro_ppp] from package_product where pkg_sku in ('1044046P') and pro_sku = '13440223' and pro_region in ('FL','SE','TX');

insert into  package_product ([pro_sku],[pkg_sku],[pro_region],[pro_qty],[pro_price],[pro_ppp])
select '12440284' [pro_sku],[pkg_sku],[pro_region],[pro_qty], 395.00 [pro_price] ,14.5421 [pro_ppp] from package_product where pkg_sku in ('1044048P') and pro_sku = '13440285' and pro_region in ('FL','TX');

insert into  package_product ([pro_sku],[pkg_sku],[pro_region],[pro_qty],[pro_price],[pro_ppp])
select '12440309' [pro_sku],[pkg_sku],[pro_region],[pro_qty], 395.00 [pro_price] ,14.5421 [pro_ppp] from package_product where pkg_sku in ('1044049P') and pro_sku = '13440300' and pro_region in ('FL','TX');


insert into ipackageproducts([pro_sku],[ipac_pro_quantity],[ipac_sku],[ipac_region],[ipac_belongstosite])
select '12440246' [pro_sku],[ipac_pro_quantity],[ipac_sku],[ipac_region],[ipac_belongstosite] FROM iPackageProducts where ipac_sku in ('1044039P') and pro_sku = '13440247' and ipac_region in ('SE','TX');

insert into ipackageproducts([pro_sku],[ipac_pro_quantity],[ipac_sku],[ipac_region],[ipac_belongstosite])
select '12440498' [pro_sku],[ipac_pro_quantity],[ipac_sku],[ipac_region],[ipac_belongstosite] FROM iPackageProducts where ipac_sku in ('1044040P') and pro_sku = '13440499' and ipac_region in  ('SE');

insert into ipackageproducts([pro_sku],[ipac_pro_quantity],[ipac_sku],[ipac_region],[ipac_belongstosite])
select '12440486' [pro_sku],[ipac_pro_quantity],[ipac_sku],[ipac_region],[ipac_belongstosite] FROM iPackageProducts where ipac_sku in ('1044043P') and pro_sku = '13440487' and ipac_region in  ('FL','SE','TX');

insert into ipackageproducts([pro_sku],[ipac_pro_quantity],[ipac_sku],[ipac_region],[ipac_belongstosite])
select '12440210' [pro_sku],[ipac_pro_quantity],[ipac_sku],[ipac_region],[ipac_belongstosite] FROM iPackageProducts where ipac_sku in ('1044045P') and pro_sku = '13440211' and ipac_region in  ('FL','SE','TX');

insert into ipackageproducts([pro_sku],[ipac_pro_quantity],[ipac_sku],[ipac_region],[ipac_belongstosite])
select '12440222' [pro_sku],[ipac_pro_quantity],[ipac_sku],[ipac_region],[ipac_belongstosite] FROM iPackageProducts where ipac_sku in ('1044046P') and pro_sku = '13440223' and ipac_region in  ('FL','SE','TX');

insert into ipackageproducts([pro_sku],[ipac_pro_quantity],[ipac_sku],[ipac_region],[ipac_belongstosite])
select '12440284' [pro_sku],[ipac_pro_quantity],[ipac_sku],[ipac_region],[ipac_belongstosite] FROM iPackageProducts where ipac_sku in ('1044048P') and pro_sku = '13440285' and ipac_region in  ('FL','TX');

insert into ipackageproducts([pro_sku],[ipac_pro_quantity],[ipac_sku],[ipac_region],[ipac_belongstosite])
select '12440309' [pro_sku],[ipac_pro_quantity],[ipac_sku],[ipac_region],[ipac_belongstosite] FROM iPackageProducts where ipac_sku in ('1044049P') and pro_sku = '13440300' and ipac_region in  ('FL','TX');


-- --------------------------


select top 10 * from ipackageproducts

select * from package_product where pkg_sku in (
'1117691P','1137691P','1117690P','1137690P'
) and pro_sku = '23060281'

update package_product set pro_qty = 1, pro_ppp = 25.24 where pkg_sku in (
'1382212P'
) and pro_sku = '13822108'

delete FROM dbo.package_product  
WHERE pro_sku IN (
'74461535'
)
AND pkg_sku IN ('7466154P')




 declare @sku varchar(10)
declare @site char(3)

set @site = 'RTG'
set @sku =  '34632972'
	
    delete from ecatalogdb.dbo.container where con_sku = @sku  and con_belongstosite = @site
	  delete from ecatalogdb.dbo.roomipackages where  roo_sku = @sku and roo_belongstosite = @site 
    delete from ecatalogdb.dbo.rooms_region_data where  roo_sku = @sku and roo_belongstosite = @site 
  	delete  from ecatalogdb.dbo.rooms where   roo_sku = @sku and roo_belongstosite = @site

    delete	from ecatalogdb.dbo.categoryipackages where ipac_sku = @sku
    delete from ecatalogdb.dbo.ipackageproducts where   ipac_sku = @sku  and ipac_belongstosite = @site
    delete from ecatalogdb.dbo.ipackage_region_data where  ipac_sku = @sku  and ipac_belongstosite = @site
    delete from ecatalogdb.dbo.ipackage where  ipac_sku = @sku and ipac_belongstosite = @site
    


select * from ecatalogdb.dbo.package_product_deleted
select * from ecatalogdb.dbo.ipackageproducts_deleted
select * from ecatalogdb.dbo.roomipackages_deleted
select * from ecatalogdb.dbo.container_deleted
select * from ecatalogdb.dbo.CategoryIpackages_DELETED


delete from ecatalogdb.dbo.package_product_deleted --where created_datetime >= '2018-04-16 15:57'
delete from ecatalogdb.dbo.ipackageproducts_deleted --where created_datetime >= '2018-04-16 15:57'
delete from ecatalogdb.dbo.roomipackages_deleted --where created_datetime >= '2018-04-16 15:57'
delete from ecatalogdb.dbo.container_deleted --where created_datetime >= '2018-04-16 15:57'
delete from ecatalogdb.dbo.CategoryIpackages_DELETED --where created_datetime >= '2018-04-16 15:57'


7217489P


delete from ecatalogdb.dbo.categoryipackages where vipac_sku = '99183534'

select 
--1090116P and 1090117P
--test a room

sprtggetroominfo 4175, 'RTG', 'TX'

23041104
2215111P

--insert into container
(con_sku,con_ipac_sku,con_region,con_belongstosite)
values( '1392212P','90111762','SE','RTG')

22119970,,90111762,1382212P

update package_product set pro_qty = 1, pro_ppp = 25.24 where pkg_sku in (
'1382212P'
) and pro_sku = '13822108'

--insert into container
(con_sku,con_ipac_sku,con_region,con_belongstosite)
values( '3271623P','3331623P','FL','RTG')



insert into container
(con_sku,con_ipac_sku,con_region,con_belongstosite)
values ('1514764P', '23051117', 'FL', 'RTG)

select value from dbo.fn_split('1232157P,1232158P,1232160P,1242157P,1242158P,1242160P,1232159P,1102757P,1102758P,1112757P,1112758P,1242159P,1122757P,1122758P,1132757P,1132758P',',')



select top 10 * from rooms

insert into container
(con_sku,con_ipac_sku,con_region,con_belongstosite)
values ('1514764P', '23051117', 'FL', 'RTG)

	

8312496p 8372496p Belmar  

1070110P,1100110P

Room – 1272120P
Remove table set - 2200100P
Replace w/ these tables – 22010122, 23010123

OLD                       NEW
2210001P           2210126P
2300126P
PACKAGE


select * from package_product where pkg_sku = '1232160P' and pro_region = 'FL'
order by pro_region, pkg_sku, pro_sku

insert into  package_product
([pro_sku]
      ,[pkg_sku]
      ,[pro_region]
      ,[pro_qty]
      ,[pro_price]
      ,[pro_ppp])
select
[pro_sku]
      ,[pkg_sku]
      ,'TX' [pro_region]
      ,[pro_qty]
      ,[pro_price]
      ,[pro_ppp]
  FROM [eCatalogDB].[dbo].[package_product] where pro_region = 'FL' and pkg_sku = '7217489P' and
   pro_sku not in ('78120006','78320000')


(con_sku,con_ipac_sku,con_region,con_belongstosite)
update container set con_ipac_sku = '2202717P' 
where con_sku in 
(
  select value from dbo.fn_split('1232160P,1112758P,1102758P,1122758P,1242160P,1132758P,1232158P,1112757P,1102757P,1242158P,1132757P,1122757P',',')
) 
and con_ipac_sku = '2209852P' and  con_region = 'FL'

select * from package_product where pkg_sku = '1232160P'
	
select * from package_product where pkg_sku = '7022044P'


  select * from 
  77320403	


update package_product
set pro_qty = 2
where pro_sku = '77320403' and pro_region = 'FL'
and pkg_sku  = '7022044P'

1	7022044P
2	7032049P
1 73020275

insert into container
(con_sku,con_ipac_sku,con_region,con_belongstosite)
select '7062041P','7022044P','FL','OTG'
--select '7062041P','7032049P','FL','OTG'
--select '7062041P','73020275','FL','OTG'


7022044P
7032049P
73020275

select * from container where con_sku = '7062041P'

delete  from container where con_sku = '7062041P' and con_ipac_sku = '77320403' and con_region = 'FL'

select * from ipackageproducts where ipac_sku = '7217489P' 
order by ipac_region, ipac_sku, pro_sku

insert into ipackageproducts
([pro_sku]
      ,[ipac_pro_quantity]
      ,[ipac_sku]
      ,[ipac_region]
      ,[ipac_belongstosite])
select
[pro_sku]
      ,[ipac_pro_quantity]
      ,[ipac_sku]
      ,'TX' [ipac_region]
      ,[ipac_belongstosite]
  FROM [eCatalogDB].[dbo].[iPackageProducts]
  where ipac_region = 'FL' and ipac_sku = '7217489P' and
   pro_sku not in ('78120006','78320000')


old cocktail and end tables
ENDGA.22132928	1	4.765	
ENDGA.23032927	2	6.262

new cocktail table
22001894	1 TSMR	RECT COCKTAIL GLASS	30.00	Y		30.00	Y		30.00	Y	
22101896	1 TSMR	RECT COCKTAIL TBL BSE
new end table
23001895	2 TSMR	END TBL GLASS	30.00	Y		30.00	Y		30.00	Y	
23101897	2 TSMR	END TABLE BASE

select * from package_product where 
pkg_sku in (select value from dbo.fn_split('1012419P,1272418P,1262418P,1032419P,1052419P,1292418P,1312418P,1282418P,1302418P,1012418P,1272417P,1262417P,1052418P,1032418P,1292417P,1312417P,1302417P,1282417P,1012422P,1272419P,1262419P,1052420P,1032422P,1292419P,1312419P,1282419P,1302419P',',')  )  and pro_region = 'FL'
--and pro_sku in ('22132928','23032927')
and pro_region = 'FL'

delete from package_product where 
pkg_sku in (select value from dbo.fn_split('1012419P,1272418P,1262418P,1032419P,1052419P,1292418P,1312418P,1282418P,1302418P,1012418P,1272417P,1262417P,1052418P,1032418P,1292417P,1312417P,1302417P,1282417P,1012422P,1272419P,1262419P,1052420P,1032422P,1292419P,1312419P,1282419P,1302419P',',')  )  and pro_region = 'FL'
and pro_sku in ('22132928','23032927') and pro_region = 'FL'

insert into package_product 
    ([pro_sku]
      ,[pkg_sku]
      ,[pro_region]
      ,[pro_qty]
      ,[pro_price]
      ,[pro_ppp])

select distinct '35414200', pkg_sku, pro_region, 1,99.99,2.9167
from package_product where pkg_sku in (select value 
from  dbo.fn_split('3520184P,3530184P',',') )
/* */

WRLWA.35414200	1	2.9167

/*
select '22101896', value pkg_sku, 'FL', 1,79.99,3.2596
from dbo.fn_split('1012419P,1272418P,1262418P,1032419P,1052419P,1292418P,1312418P,1282418P,1302418P,1012418P,1272417P,1262417P,1052418P,1032418P,1292417P,1312417P,1302417P,1282417P,1012422P,1272419P,1262419P,1052420P,1032422P,1292419P,1312419P,1282419P,1302419P',',')  
*/
/*
select '23001895', value pkg_sku, 'FL', 1,30.00,1.8319
from dbo.fn_split('1012419P,1272418P,1262418P,1032419P,1052419P,1292418P,1312418P,1282418P,1302418P,1012418P,1272417P,1262417P,1052418P,1032418P,1292417P,1312417P,1302417P,1282417P,1012422P,1272419P,1262419P,1052420P,1032422P,1292419P,1312419P,1282419P,1302419P',',')  

update package_product 
set pro_qty = 2 
where pkg_sku in (select value from dbo.fn_split('1012419P,1272418P,1262418P,1032419P,1052419P,1292418P,1312418P,1282418P,1302418P,1012418P,1272417P,1262417P,1052418P,1032418P,1292417P,1312417P,1302417P,1282417P,1012422P,1272419P,1262419P,1052420P,1032422P,1292419P,1312419P,1282419P,1302419P',',')  )  and pro_region = 'FL'
and pro_sku in ('23001895') and pro_region = 'FL'
*/

select '23101897', value pkg_sku, 'FL', 2,79.99,4.1609
from dbo.fn_split('1012419P,1272418P,1262418P,1032419P,1052419P,1292418P,1312418P,1282418P,1302418P,1012418P,1272417P,1262417P,1052418P,1032418P,1292417P,1312417P,1302417P,1282417P,1012422P,1272419P,1262419P,1052420P,1032422P,1292419P,1312419P,1282419P,1302419P',',')  


TSMRA.22001894	1	1.6926	30.00	
TSMRA.22101896	1	3.2596	 79.99
TSMRA.23001895	2	1.8319	30.00	
TSMRA.23101897	2	4.1609   79.99


Old tables                            New table set
22010122, 23010123                    2200100P
select * from container where con_sku = '1622120P'
delete from container where con_id in (381256,381257)

update package_product
set pro_sku = '22010122' where pro_sku = '2200100P' and
 pkg_sku = '1622120P' and 
pro_sku = '9999A.2200100P*0'

select * from ipackageproducts where ipac_sku = '1622120P' and 

insert into container
(con_sku,con_ipac_sku,con_region,con_belongstosite)
select con_sku,'2300126P',con_region,con_belongstosite 
from container where con_sku in (
'1764184P'
) and con_ipac_sku = '2210126P' and con_region = 'FL'



select * from container where con_sku in ('3264223P','3254223P','3324223P','3314223P')
and con_ipac_sku = '33542235'

delete from container where con_sku in ('3264223P','3254223P','3324223P','3314223P')
and con_ipac_sku = '33542235'


select * from container where con_sku in ('3254221P','3324221P','3314221P','3264221P')
and con_ipac_sku = '33542211'

delete from container where con_sku in ('3254221P','3324221P','3314221P','3264221P')
and con_ipac_sku = '33542211'

8004221P


delete from container where con_id in (371565,371566)
select * from container where con_id in (371565,371566)


3264223P,3254223P,3324223P,3314223P

8004223P

33542235	

	QUANTITY	PERCENT	SAME

	

update package_product 
set pro_sku = '32542234' where pkg_sku in 
('3264223P','3254223P','3324223P','3314223P')
and  pro_sku = '8004223P'

select * from package_product 
where pkg_sku in
 ('3264223P','3254223P','3324223P','3314223P') and 
 pro_sku = '8004223P'

select * from package_product where pkg_sku in 
 ('3254221P','3324221P','3314221P','3264221P')
and  pro_sku = '8004221P'

update package_product 
set pro_sku = '32542210' where pkg_sku in 
 ('3254221P','3324221P','3314221P','3264221P')
and  pro_sku = '8004221P'


insert into container
(con_sku,con_ipac_sku,con_region,con_belongstosite)
select '1272120P', 23010123, 'TX', 'RTG'
	
  OLD                        NEW
2201580P            (NO 3 PC TO REPLACE WITH)
22115807            22215621
23015806            23015628
 
insert into container
(con_sku,con_ipac_sku,con_region,con_belongstosite)
select con_sku, '90173229', con_region, con_belongstosite
 from container where con_sku in ('1039674P')
 and con_region = 'SE' and con_ipac_sku = '90173229'
 

22153338 -co tbl


insert into container
(con_sku,con_ipac_sku,con_region,con_belongstosite)
select con_sku, '23053337', con_region, con_belongstosite
 from container where con_sku in ('1883413P','1883414P','1883415P')
 and con_region = 'SE' and con_ipac_sku = '22153338'


select *
from container where con_sku = '1260372P' and con_ipac_sku = '23022281' and con_region = 'TX'

select * from container where con_sku in (
'1514764P','1514765P','1547615P','1547616P','1547617P','1547618P','1547619P','1547621P'
) 
and con_ipac_sku = '23041104'

delete from container where con_sku in (
'1514764P','1514765P','1547615P','1547616P','1547617P','1547618P','1547619P','1547621P'
) 
and con_ipac_sku = '23041104'



2300091P

1569274P','1569273P','1579273P','1579274P','1599273P','1589273P','1589274P','1599274P','


select idx pkg_idx, value pkg_sku from dbo.fn_split('7064005P,7064004P,7064006P,7064003P',',') 


insert into container
(con_sku,con_ipac_sku,con_region,con_belongstosite)
select '1660008P', 23198523, 'TX', 'RTG'

insert into container
(con_sku,con_ipac_sku,con_region,con_belongstosite)
 select '3271597P','32115974','SE','RTG'

 insert into container
(con_sku,con_ipac_sku,con_region,con_belongstosite)
 select '3281597P','32115974','SE','RTG'
 
 ,



1260372P
23022281  


1660007P
1660008P


delete 1 pillow
Package
7064005P
Remove pillow 78940312

delete from package_product where pkg_sku = '7064005P' and pro_sku = '78943012'


Package
7064003P
7064006P
Remove pillow 78915304

delete  from package_product where pkg_sku = '7064006P' and pro_sku = '78915304'

 
Package
7064004P
Remove 78916104

delete from package_product where pkg_sku = '7064004P' and pro_sku = '78916104'


7215483P

select * from roomipackages where roo_sku = '8372496P'
delete from ecatalogdb.dbo.container where con_id  IN
(
364719,
364720
)

7310149P
32514970          32524971

PACKAGE
7310149P

select * from  ecatalogdb.dbo.container where con_sku in ('1239685P','1229685P')  and con_region = 'SE'   and con_ipac_sku in ('22154001')





insert into container
(con_sku,con_ipac_sku,con_region,con_belongstosite)
select con_sku, '23142261', con_region, con_belongstosite
from container where con_sku in ('1239685P','1229685P') and con_ipac_sku = '22042268' and con_region = 'SE' 


2217013P           22170132
                                23070131
 
Packages:
1583512P
1502512P

--add in an end table
insert into container
(con_sku,con_ipac_sku,con_region,con_belongstosite)
select con_sku, '23070131', con_region, con_belongstosite
from container where con_sku in ('1583512P','1502512P') and con_ipac_sku = '22170132' and con_region = 'FL' 



OLD:                      NEW:
22229327           2212932P
23029324
 
 '1796053P','1016054P','1026054P'

select con_id 
from container where con_sku in ( '1796053P','1016054P','1026054P') and con_ipac_sku = '23029324' and con_region = 'SE' 

delete from container where con_id in (385123,385124,385131,385132,385116,385117)

9999A.2212932P*0	
--on move to 3pc table set the package sku is getting put into package product (incorrectly)
--the package should not be altered
select * from package_product where pkg_sku  = '1796053P' and pro_region = 'SE'
--put the cocktail table back in (overwrite)
update package_product set pro_sku = '22229327' where pkg_sku in ( '1796053P','1016054P','1026054P') and 
pro_sku = '2212932P' and pro_region = 'SE'


--rooms don't include contents of packages in ipackageproducts
select * from ipackageproducts where ipac_sku = '1796053P'


OLD                        NEW
22042268             2201226P
23042269
 
PKGS
'1850023P','1100024P,'1880022P'

select * from container where con_sku in ('1850023P','1100024P','1880022P')
and con_ipac_sku = '23042269' and con_region = 'SE'

delete from container where con_id in (341222, 341223, 341194, 341195, 341214, 341215)

select * from ecatalogdb.dbo.package_product where pkg_sku = '7310149P' and pro_sku in ('32514970')
update ecatalogdb.dbo.package_product set pro_sku = '32524971' where pkg_sku = '7310149P' and pro_sku in ('32514970') and pro_region = 'TX'


select pp.* 
into #fixrecords 
from ecatalogdb.dbo.package_product pp
join (
  select * from 
  (
    select idx pkg_idx, value pkg_sku from dbo.fn_split('7064005P,7064004P,7064006P,7064003P',',') 
  ) pkg
  join (
    select idx pro_idx, value pro_sku from dbo.fn_split(' 77340049,77340037,77340051,77340025',',') 
  ) pro
  on pkg.pkg_idx = pro.pro_idx
) skus
on skus.pkg_sku = pp.pkg_sku and skus.pro_sku = pp.pro_sku 

select * from #fixrecords

update package_product
set pro_qty = 2
from package_product pp 
join #fixrecords f
  on f.pkg_sku = pp.pkg_sku and f.pro_sku = pp.pro_sku and f.pro_region = pp.pro_region and pp.pro_qty = 5


           23041180
 
Packages
1332045P
1342044P
1352045P

23054000



HOUSA.32514970	1	20	

4218017P should have quantity of 4 for 4248017P
4228017P should have quantity of 6 for 4248017P


update roomipackages set modified_datetime = null, published_datetime = getdate() where roo_sku = '8210598P'

update container set con_ipac_sku = '28003250' where con_id = 90257
delete from container where con_id in (263006)

1046735P 


	    delete from ecatalogdb.dbo.container where con_sku = '7211018P'  and con_belongstosite = 7211018P and con_region = @region
	    delete from ecatalogdb.dbo.roomipackages where  roo_sku = '7211018P' and roo_belongstosite = @site and roo_region = @region
    	delete from ecatalogdb.dbo.rooms_region_data where  roo_sku = '7211018P' and roo_belongstosite = @site and roo_region = @region
  delete from ecatalogdb.dbo.rooms where  roo_sku = '7211018P'
  
--------
 2204473P… not sure if you need this) – PLEASE DELETE
 
PACKAGE
1153273P

These were built with the individual tables instead of the 3 pc table set. Can you please fix for us?
 
Packages:
1721362P
1741362P
1711363P
 
Built with:           Should be:
22115807             2201580P
23015806


 - end table


delete from ecatalogdb.dbo.container 
where con_sku in ('1721362P','1741362P','1711363P') and con_ipac_sku = '23015806' and con_region = 'SE'

select * from ecatalogdb.dbo.container 
where con_sku in ('1517797P','1517796P','1517799P','1517798P','1517800P','1517801P') and con_ipac_sku = '2301011P'

delete from ecatalogdb.dbo.container 
where con_sku in ('1517797P','1517796P','1517799P','1517798P','1517800P','1517801P') and con_ipac_sku = '2301011P'

update ecatalogdb.dbo.container 
set con_ipac_sku = '2201580P'
where con_sku in ('1721362P','1741362P','1711363P') and con_ipac_sku = '22115807' and con_region = 'SE'

delete from ecatalogdb.dbo.container 
where con_sku in ('1018134P','1048135P','1058135P') and con_ipac_sku = '23103346' and con_region = 'SE'

22103345,23103346	2210334P
 	 
   select * from ipackageproducts where pro_sku = '9999A.2210334P*0'

   select * from package_product where pkg_sku in ('1018134P','1048135P','1058135P')

update package_product set pro_sku = '22103345' 
where pkg_sku in ('1018134P','1048135P','1058135P')
and pro_sku = '2210334P'

   select top 1 * from ipackage_products
   9999A.2210334P*0	

 select * from ecatalogdb.dbo.container 
where con_sku in ('1018134P','1048135P','1058135P') 

Packages	 

select * from ecatalogdb.dbo.container 

update ecatalogdb.dbo.container set con_ipac_sku = '22170233'
where con_sku in ('1546499P','1546498P') and con_ipac_sku = '2217019P' and con_region = 'SE'



insert into ecatalogdb.dbo.container
(con_sku,con_ipac_sku,con_region,con_belongstosite)

select con_sku,'23070232' con_ipac_sku,con_region,con_belongstosite 
from ecatalogdb.dbo.container
where con_sku in ('1506497P','1516497P','1546499P','1546498P','1506496P','1516496P') and con_ipac_sku = '22170233' and con_region = 'SE'


22170233	



delete from ecatalogdb.dbo.container 
where con_sku in ('1213061P','1213063P','1213060P') and con_ipac_sku = '2318296P' and con_region = 'TX'

22082969, 22182961 (& remove 2208296P)                         22124957
23082960, 23182962 (& remove 2318296P)                         23024956

insert into ecatalogdb.dbo.container
(con_sku,con_ipac_sku,con_region,con_belongstosite)
values ('1111670P','2302021P','SE','RTG')
 
insert into ecatalogdb.dbo.container
(con_sku,con_ipac_sku,con_region,con_belongstosite)
select con_sku, con_ipac_sku, con_region, con_belongstosite
from container
where con_sku = '8055308P' and con_ipac_sku = '32553085'

insert into ecatalogdb.dbo.container
(con_sku,con_ipac_sku,con_region,con_belongstosite)
select con_sku, con_ipac_sku, con_region, con_belongstosite
from container
where con_sku = '4242386P' and con_ipac_sku = '42623860' and con_region = 'FL'

42623860
select * from package_product where pkg_sku = '8055308P' and pro_sku = '32553085'


insert into ecatalogdb.dbo.container
(con_sku,con_ipac_sku,con_region,con_belongstosite)
select con_sku, '2300091P', con_region, con_belongstosite
from container
where con_sku in ( '1569274P','1569273P','1579273P','1579274P','1599273P','1589273P','1589274P','1599274P' ) and con_ipac_sku = '2210091P' and con_region = 'FL'



OLD                        NEW
22122129            2212210P
23022128
 
PACKAGES
1100788P
1100789P
1040788P
1040789P

delete from ecatalogdb.dbo.container where con_sku in ('1100788P','1100789P','1040788P','1040789P') and con_ipac_sku = '23022128' and con_region = 'TX'


1517797P


1111670P


delete from ecatalogdb.dbo.package_product where pkg_sku = '1153273P' and pro_region = 'SE' and pro_sku in ('22044705','22144707')
HLSDA.22044705	1	6.34	
HLSDA.22144707	1	7.14	

--------

select * from ecatalogdb.dbo.package_product_deleted
select * from ecatalogdb.dbo.ipackageproducts_deleted
select * from ecatalogdb.dbo.roomipackages_deleted
select * from ecatalogdb.dbo.container_deleted 
select * from ecatalogdb.dbo.categoryipackages_deleted

delete from ecatalogdb.dbo.package_product_deleted
delete  from ecatalogdb.dbo.ipackageproducts_deleted
delete from ecatalogdb.dbo.roomipackages_deleted
delete  from ecatalogdb.dbo.container_deleted
delete from ecatalogdb.dbo.categoryipackages_deleted

--reset a room that needs to be re-created
declare @sku varchar(10)
declare @site char(3)

set @site = 'RTG'
set @sku =  '3328818P'
	
update ecatalogdb.dbo.ipackage set modified_datetime = created_datetime, published_datetime = null where  ipac_sku = @sku and ipac_belongstosite = @site
update ecatalogdb.dbo.ipackage_region_data set modified_datetime = created_datetime, published_datetime = null where  ipac_sku = @sku  and ipac_belongstosite = @site
update ecatalogdb.dbo.ipackageproducts set modified_datetime = created_datetime, published_datetime = null where   ipac_sku = @sku  and ipac_belongstosite = @site

update ecatalogdb.dbo.rooms set modified_datetime = created_datetime, published_datetime = null where  roo_sku = @sku and roo_belongstosite = @site
update ecatalogdb.dbo.rooms_region_data set modified_datetime = created_datetime, published_datetime = null where  roo_sku = @sku and roo_belongstosite = @site
update ecatalogdb.dbo.roomipackages set modified_datetime = created_datetime, published_datetime = null where  roo_sku = @sku and roo_belongstosite = @site
update ecatalogdb.dbo.container set modified_datetime = created_datetime, published_datetime = null where con_sku = @sku  and con_belongstosite = @site

--reset a room that needs to be re-created in a region
declare @sku varchar(10)
declare @site char(3)
declare @region char(2)

set @site = 'RTG'
set @sku =  '4322302P'
set @region = 'SE'
	
update ecatalogdb.dbo.ipackage_region_data set modified_datetime = created_datetime, published_datetime = null where  ipac_sku = @sku  and ipac_belongstosite = @site and ipac_region = @region
update ecatalogdb.dbo.ipackageproducts set modified_datetime = created_datetime, published_datetime = null where   ipac_sku = @sku  and ipac_belongstosite = @site  and ipac_region = @region

update ecatalogdb.dbo.rooms_region_data set modified_datetime = created_datetime, published_datetime = null where  roo_sku = @sku and roo_belongstosite = @site and roo_region = @region
update ecatalogdb.dbo.roomipackages set modified_datetime = created_datetime, published_datetime = null where  roo_sku = @sku and roo_belongstosite = @site and roo_region = @region
update ecatalogdb.dbo.container set modified_datetime = created_datetime, published_datetime = null where con_sku = @sku  and con_belongstosite = @site and con_region = @region

--

8800417P
8802417P
8801417P

declare @sku varchar(10)
declare @site char(3)


set @site = 'RTG'
set @sku =  '18584157'


update  ecatalogdb.dbo.product set modified_datetime = created_datetime, published_datetime = null where pro_sku = @sku

update  ecatalogdb.dbo.product_region_data  set modified_datetime = created_datetime, published_datetime = null where pro_sku = @sku
and pro_region = 'FL'
	
update  ecatalogdb.dbo.product set modified_datetime = created_datetime, published_datetime = null where pro_sku = @sku
update  ecatalogdb.dbo.product_region_data  set modified_datetime = created_datetime, published_datetime = null where pro_sku = @sku
if charindex('P',@sku) > 0
	update  ecatalogdb.dbo.package_product set modified_datetime = created_datetime, published_datetime = null where pkg_sku = @sku
else
	update  ecatalogdb.dbo.package_product set modified_datetime = created_datetime, published_datetime = null where pro_sku = @sku
update  ecatalogdb.dbo.ipackageproducts set modified_datetime = created_datetime, published_datetime = null where pro_sku = @sku


--delete from  Container_DELETED where con_sku in ('3270554P','3370554P','3380554P')

select * from container where con_sku = '7033219P' and con_ipac_sku = '7033215P'
order by con_region, con_ipac_sku,con_id

--delete from Container where con_id in (380395,
380398,380396,
380399,380397,
380400)

--delete from container where con_id in (139294,139295,139296,139297)
--delete from container where con_id in (139303,139304,139305,139306)
   -- delete from ecatalogdb.dbo.rooms_region_data where  roo_sku = '1288861P' and roo_belongstosite = @site 
  --	delete  from ecatalogdb.dbo.rooms where   roo_sku =  '1288861P' and roo_belongstosite = @site
  	
--update  ecatalogdb.dbo.package_product set modified_datetime = created_datetime, published_datetime = null where pkg_sku = '4311438P' and pro_sku = '42114380'
--update  ecatalogdb.dbo.package_product set modified_datetime = created_datetime, published_datetime = null where pkg_sku = '4211438P' and pro_sku = '42414386'

*/



