--1. BRCNO , BRC Nodal Officer (ka) ==> BRC, Block Resource Coordinator
--2. BRC (od) ==> BRCC
insert into common_respondenttype(char_id, name,state_code_id,active_id) values('BRCC','Block Resource Coordinator','od','AC');
update users_user set user_type_id ='BRCC' where user_type_id='BRC';
update common_respondenttype set state_code_id='ka' where char_id='BRC' and state_code_id='od';
update users_user set user_type_id='BRC' where user_type_id='BRCNO';
delete from common_respondenttype where char_id='BRCNO';

--3. DDPI ,DDPI (ka) ==> DDPI,  `DDPI/DyPc/ECO'
update common_respondenttype set name ='DDPI/DyPc/ECO' where char_id='DDPI';
--4. ECO (ka) ==> Make it inactive
update common_respondenttype set active_id='IA' where char_id='ECO'; 
--5. DIET (ka) ==> Make it inactive
update common_respondenttype set active_id='IA' where char_id='DIET'; 
--6. There is no DIE Nodal Officer in DB (so no changes)
--7. Elected Representative ==> Make it inactive
update common_respondenttype set active_id='IA' where char_id='ER'; 
--8. Government Official ==> Make it inactive
update common_respondenttype set active_id='IA' where char_id='GO'; 
--9. Educational Officer ==> Make it inactive
update common_respondenttype set active_id='IA' where char_id='EO'; 
--10. Add entry for GP Member
insert into common_respondenttype(char_id, name,active_id) values('GP','GP Members','AC');
--11. Add entry for NGO
insert into common_respondenttype(char_id, name,active_id) values('NGO','Non Government Organization','AC');
--12. Remove entry for children (Make it inactive)
update common_respondenttype set active_id='IA' where char_id='CH'; 
--13. Remove entry for CBO Member (Make it inactive)
update common_respondenttype set active_id='IA' where char_id='CM'; 
--14. Remove entry for Local leader (Make it inactive)
update common_respondenttype set active_id='IA' where char_id='LL'; 
--15. Remove entry for Educated Youth (Make it inactive)
update common_respondenttype set active_id='IA' where char_id='EY'; 

