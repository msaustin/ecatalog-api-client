--SIZE

--INSERT INTO  eCatalogDB.dbo.AttributeValues
--(attributevalue_attributedefinition_id, attributevalue_value, attributevalue_site, attributevalue_isactive)  
--select 13, 'King Sham', 'RTG', 1

		

DECLARE @newsize VARCHAR(40)
DECLARE @newsizefamily VARCHAR(40)
DECLARE @newattributeid int
DECLARE @site VARCHAR(3)
	

SET @newsize = '9''6 x 14'''
SET @newsizefamily = 'Mansion Size' --'Mansion Size' -- 'Up to 8'' x 11''' --'Up To 4'' x 6''' --'Round Size'--'Up To 6''6 x 10'''
SET @site = 'RTG'


INSERT INTO ecatalogdb.dbo.AttributeValues
(attributevalue_attributedefinition_id, attributevalue_value, attributevalue_site, attributevalue_isactive)  
select 13, @newsize,@site , 1

SET @newattributeid = (SELECT @@IDENTITY) 

--ADD TO THE RIGHT SITE
INSERT INTO  dbo.AttributeValueSites
 ( attributevaluesite_attributevalue_id , attributevaluesite_site )
select @newattributeid, @site

--ADD A SIZE TO A SIZE FAMILY

--add a size to a size family
declare @familysize varchar(40)
declare @productsize varchar(40)

set @familysize = @newsizefamily
set @productsize = @newsize

INSERT into ecatalogdb.dbo.AttributeFamilies
( attributefamily_family_attributevalue_id, attributefamily_member_attributevalue_id, attributefamily_attributedefinition_id )
select (select attributevalue_id from ecatalogdb.dbo.AttributeValues 
where attributevalue_attributedefinition_id = 13 and attributevalue_value = @familysize),
(select attributevalue_id from ecatalogdb.dbo.AttributeValues 
where attributevalue_attributedefinition_id = 13 and attributevalue_value = @productsize),
53


-----------
UPDATE ecatalogdb.dbo.AttributeValues SET attributevalue_value = '40" - 59" Consoles'
WHERE attributevalue_id = 858



select * from ecatalogdb.dbo.AttributeValues where attributevalue_value LIKE '60" - 69" Consoles'
and attributevalue_attributedefinition_id =  13

select * from ecatalogdb.dbo.AttributeValues where attributevalue_value LIKE '%Consoles'

23152

SELECT * FROM dbo.AttributeValueSites WHERE attributevaluesite_attributevalue_id = 23152

 dbo.AttributeValueSites

DELETE from dbo.AttributeValues WHERE attributevaluesite_attributevalue_id = 34052
DELETE from dbo.AttributeValues WHERE attributevalue_id = 25713


SELECT * FROM dbo.AttributeValues WHERE attributevalue_id = 1053
DELETE FROM dbo.AttributeValues WHERE attributevalue_id = 23152
SELECT * FROM dbo.AttributeValueSites WHERE attributevaluesite_attributevalue_id = 34052
DELETE from dbo.AttributeValueSites WHERE attributevaluesite_attributevalue_id = 34052

'2''7 x 10'''

SELECT * FROM dbo.AttributeFamilies WHERE attributefamily_member_attributevalue_id = 625

INSERT into ecatalogdb.dbo.AttributeFamilies
( attributefamily_family_attributevalue_id, attributefamily_member_attributevalue_id, attributefamily_attributedefinition_id )
select (select attributevalue_id from ecatalogdb.dbo.AttributeValues 
where attributevalue_attributedefinition_id = 13 and attributevalue_value =  'Up To 4'' x 6'''),
(select attributevalue_id from ecatalogdb.dbo.AttributeValues 
where attributevalue_attributedefinition_id = 13 and attributevalue_value = '3''3 x 3''7'),
53


INSERT INTO  dbo.AttributeValueSites
 ( attributevaluesite_attributevalue_id , attributevaluesite_site )
select 41923, 'RTG'

	13	7'6 x 9'7

DELETE FROM dbo.AttributeValues WHERE attributevalue_id = 41925
DELETE FROM  dbo.AttributeValueSites where attributevaluesite_attributevalue_id = 41925


update dbo.AttributeValues set attributevalue_value =  '5''3 x 7''' WHERE attributevalue_id = 16121
'5'' x 5'''


'10'' x 13''1'

/*

Can you please add 33” and 45” to the Size attribute menu in Ecat?  I have a few fireplaces that fit those measurements.
 


This size attribute family for this will be 70”-89” Consoles.
Please let me know if you need anything else.
Thanks!
 
DI 
 
Daniela Pacheco Ibraim 
Wed 5/29/2019 2:45 PM 
Good Afternoon Tara and Mike, 
Is there a chance to add to e-cat tv console size under SIZE : 75”
We do not have a 75” option and my console is 75” wide

8' x 12' to the rug size family named Mansion Size?

42"
42" - 59" Consoles

Standard Sham
King Sham

'6''7' Round 

SELECT * FROM dbo.AttributeFamilies af1 WHERE af1.attributefamily_family_attributevalue_id = 753 
and attributefamily_member_attributevalue_id = 29985


SELECT * FROM dbo.AttributeFamilies af1 WHERE af1.attributefamily_member_attributevalue_id = 13577



AND EXISTS (SELECT * FROM  dbo.AttributeFamilies af2 WHERE af1.attributefamily_family_attributevalue_id = 753
	AND af2.attributefamily_member_attributevalue_id = af1.attributefamily_member_attributevalue_id)

SELECT * FROM dbo.AttributeFamilies af1 WHERE af1.attributefamily_family_attributevalue_id = 753
DELETE FROM dbo.AttributeFamilies WHERE attributefamily_id = 1075


UPDATE dbo.AttributeFamilies SET attributefamily_family_attributevalue_id = 753 
WHERE attributefamily_family_attributevalue_id = 751

 
SELECT * FROM ecatalogdb.dbo.AttributeValues WHERE attributevalue_id =  755
UPDATE ecatalogdb.dbo.AttributeValues SET attributevalue_value = 'Up to 4'' x 6''' WHERE attributevalue_id =  755

SELECT * FROM ecatalogdb.dbo.AttributeValues WHERE attributevalue_id =  750
UPDATE ecatalogdb.dbo.AttributeValues SET attributevalue_value = 'Up to 8'' x 11''' WHERE attributevalue_id =  750

SELECT * FROM ecatalogdb.dbo.AttributeValues WHERE attributevalue_id =  753
UPDATE ecatalogdb.dbo.AttributeValues SET attributevalue_value =  'Up to 6''6 x 10''' WHERE attributevalue_id =  753

*/
select * from ecatalogdb.dbo.attributedefinitions

select * from ecatalogdb.dbo.AttributeValues where attributevalue_attributedefinition_id =  13

select * from ecatalogdb.dbo.AttributeValues where attributevalue_value like '9''6 x 14'''
and attributevalue_attributedefinition_id =  13

-----------------






'Up To 4'' x 6'''
'Up To 6''6 x 10'''
'Up to 8'' x 11'''
'Mansion Size'
'Runner Size'
'Round Size'

'7''11 x 10''11'

'6'' Square'

7'10 x 12'2

'7''9  x 9''9'
'5''5 x 7''7'
'2''5 x 8''' 'Up To 4'' x 6'''
'5 x 7''5'	'Up To 6''6 x 10'''
'2''5 x 8' 'Runner Size'



3'10 x 6'






2'7 x 10'

'Up to 8'' x 11'''

'2''5 x 8''' 'Up To 4'' x 6'''
'5 x 7''5'	'Up To 6''6 x 10'''
'2''5 x 8' 'Runner Size'

Up to 8' x 11'
Up to 6'6 x 10'
Up to 4' x 6'

select * from ecatalogdb.dbo.AttributeValues where attributevalue_value IN
(
'3''11 x 6''2','3''11 x 5''11','5''2 x 7''','18 x 18','15 x 12','15 x 15'
)
AND attributevalue_attributedefinition_id =  13

select * from ecatalogdb.dbo.AttributeValues where attributevalue_value LIKE '%size%'
and attributevalue_attributedefinition_id =  13
'47.5"'
Please expand the (TV) console size family from 46” – 59” Consoles to 44” – 59” Consoles.
Also, please add 44” as a new size attribute in the edesk drop-down menu.

select * from ecatalogdb.dbo.AttributeValues where attributevalue_value LIKE '%Up to%'
and attributevalue_attributedefinition_id =  13

SELECT * FROM ecatalogdb.dbo.AttributeFamilies WHERE attributefamily_member_attributevalue_id = 904

UPDATE ecatalogdb.dbo.AttributeFamilies SET attributefamily_family_attributevalue_id = 1053 WHERE attributefamily_id = 745

SELECT * FROM dbo.ProductAttributes WHERE productattribute_attributevalue_id = 13417
1053

SELECT 
--update ecatalogdb.dbo.AttributeValues set attributevalue_value =  '44" - 59" Consoles' where attributevalue_id = 858

--update ecatalogdb.dbo.AttributeValues set attributevalue_site = null where  attributevalue_id = 904
/*
Estate Size
Family Room Size
Mansion Size
Room Size
Round Size
Studio Size
*/

'Up to 6''6 x 10'''
'Up to 4'' x 6'''

--add a size to a size family
declare @familysize varchar(40)
declare @productsize varchar(40)

set @familysize = 'Up to 8'' x 11'''
set @productsize = '7'' Square'
insert into ecatalogdb.dbo.AttributeFamilies
( attributefamily_family_attributevalue_id, attributefamily_member_attributevalue_id, attributefamily_attributedefinition_id )
select (select attributevalue_id from ecatalogdb.dbo.AttributeValues 
where attributevalue_attributedefinition_id = 13 and attributevalue_value = @familysize),
(select attributevalue_id from ecatalogdb.dbo.AttributeValues 
where attributevalue_attributedefinition_id = 13 and attributevalue_value = @productsize),
53

DELETE FROM ecatalogdb.dbo.AttributeFamilies WHERE attributefamily_id = 823
SELECT * FROM ecatalogdb.dbo.AttributeFamilies WHERE attributefamily_member_attributevalue_id = 904
SELECT * FROM ecatalogdb.dbo.Attributevalues WHERE attributevalue_id IN (34052)

--add a size to a size family - based on lists
declare @familysize varchar(40)
declare @productsizelist varchar(1000)
declare @familyid int

set @familysize = 'Estate Size'
set @productsizelist = ',,,,,,,,'

set @familyid =(select attributevalue_id from ecatalogdb.dbo.AttributeValues 
where attributevalue_attributedefinition_id = 13 and attributevalue_value = @familysize)

insert into ecatalogdb.dbo.AttributeFamilies
( attributefamily_family_attributevalue_id, attributefamily_member_attributevalue_id, attributefamily_attributedefinition_id )
select @familyid, attributevalue_id,53 from ecatalogdb.dbo.AttributeValues 
where attributevalue_attributedefinition_id = 13 and attributevalue_value in (select value from dbo.fn_split(@productsizelist,',') )



SELECT * FROM ecatalogdb.dbo.attributevalues where attributevalue_value like '%size'

attributevalue_id	attributevalue_attributedefinition_id	attributevalue_value	attributevalue_site	attributevalue_isactive
750	13	Estate Size	RTG	1
751	13	Family Room Size	RTG	1
752	13	Mansion Size	RTG	1
753	13	Room Size	RTG	1
754	13	Round Size	RTG	1
755	13	Studio Size	RTG	1
1053	13	Runner Size	RTG	1


select productsize, COUNT(*) 
from (
select *,
 family.attributevalue_value as SIZEFAMILY,
 size.attributevalue_value as PRODUCTSIZE
 from   ecatalogdb.dbo.AttributeValues size
 inner join  ecatalogdb.dbo.AttributeFamilies af on size.attributevalue_id = af.attributefamily_member_attributevalue_id
 inner join   ecatalogdb.dbo.AttributeValues family on af.attributefamily_family_attributevalue_id = family.attributevalue_id
 where size.attributevalue_attributedefinition_id = 13 and family.attributevalue_value = 'Room Size'
 order by family.attributevalue_value,size.attributevalue_value
 ) as sizemappings 
 group by productsize having COUNT(*) > 1
 


 978
 SELECT * FROM ecatalogdb.dbo.attributevalues where attributevalue_id = 978
 DELETE FROM ecatalogdb.dbo.attributevalues where attributevalue_id = 34052

 SELECT * FROM ecatalogdb.dbo.AttributeFamilies WHERE attributefamily_member_attributevalue_id = 979
--delete  FROM ecatalogdb.dbo.AttributeFamilies WHERE attributefamily_member_attributevalue_id = 980

SELECT * FROM ecatalogdb.dbo.AttributeFamilies WHERE attributefamily_member_attributevalue_id = 979



--5'3 x 7'6
select '7''10 x 11'
select '7''10 C 10''10'
select '27 X 8''10
7''6 x 9''6
5''3 x 7''4 








