--update schools to gp mapping
update schools_institution set gp_id=4087 where id=10536;

--insert schools_institution
insert into schools_institution (id,name,rural_urban,village,admin0_id,admin1_id,admin2_id,admin3_id,category_id,gender_id,gp_id,institution_type_id,management_id,pincode_id,status_id,dise_id) select max(id)+1,'GLPS SUNNAPPAGUTTA','Rural','SUNNAPPAGUTTA',2,'441','634','9974','13','co-ed','3151','primary',1,'563123','AC',165059 from schools_institution ;
