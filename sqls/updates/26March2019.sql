--insert schools_institution
insert into schools_institution (id,name,rural_urban,village,admin0_id,admin1_id,admin2_id,admin3_id,category_id,gender_id,gp_id,institution_type_id,management_id,pincode_id,status_id,dise_id) select max(id)+1,'GLPS ANNEHAL','Rural','ANNEHAL',2,'425','534','1603','13','co-ed','730','primary',1,'577555','AC',247459 from schools_institution ;

--update schools to gp mapping
update schools_institution set gp_id=5152 where id=24934;
