--inert new gp
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6271,'','Bailur (uk)','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6272,'','Bailooru (chmngr)','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6273,'','Nagenahalli (chkmlr)','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6274,'','Hosahalli (dvg)','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6275,'','Hosahalli (bgrural)','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6276,'','Hosahalli (tkrmgr)','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6277,'','Hosahalli (shmg)','GP','2','AC');

--update boundary_electionboundary
update boundary_electionboundary set const_ward_name='Bailur (bgv)' where id=939;
update boundary_electionboundary set const_ward_name='Hosahalli (mdy)' where id=2785;
update boundary_electionboundary set const_ward_name='Hosahalli (bly)' where id=2784;
update boundary_electionboundary set const_ward_name='Hosahalli (gdg)' where id=3110;

--update answergroup
update assessments_answergroup_institution set institution_id=20320 where id=1304458;
update assessments_answergroup_institution set institution_id=20320 where id=1304459;
update assessments_answergroup_institution set institution_id=20320 where id=1304460;
update assessments_answergroup_institution set institution_id=20320 where id=1304461;
update assessments_answergroup_institution set institution_id=20320 where id=1308625;
update assessments_answergroup_institution set institution_id=20320 where id=1308626;
update assessments_answergroup_institution set institution_id=20320 where id=1308627;
update assessments_answergroup_institution set institution_id=20320 where id=1308628;

-update schools_institution
update schools_institution set gp_id=2332 where id=5059;
update schools_institution set gp_id=6271 where id in (61741,61731,61739,61733,61734,61738,61737,61736,61732,61735,61730,61740);
update schools_institution set gp_id=6272 where id in (7027,7032,43397,7036,7037,43398,7030);
update schools_institution set gp_id=6273 where id in (43583,43585,43579,43581);
update schools_institution set gp_id=3110 where id in (47873,47904,47903);
update schools_institution set gp_id=6274 where id in (47290,47196,47195,47197,47194);
update schools_institution set gp_id=6275 where id in (11320,42714,42837,42838,42839,42840,42841,42842,42843,42844,42845,42846,42847,42848,42849,42850,42851);
update schools_institution set gp_id=6276 where id in (60554,60555,60556,60557,60636,60641,60642,60643,60819);
update schools_institution set gp_id=6277 where id in (56873,56874,56875,56876,56882,57101,57483,57489,57490,57491,57492,57587);

--update boundary_boundary
update boundary_boundary set name='Jammukashmir' where id=4;

--update assessment_question
update assessments_question set question_text='Are you satisfied with the Mid Day Meal served in your child''s school?' where id=591;

--delete invalid answers
delete from assessments_answerinstitution where answergroup_id in (1306742,1306743,1306744,1306745,1306746,1306747,1306748,1306749,1306750,1306751,1306752,1306753,1306754,1306755,1306756,1306757,1311066,1311067,1311068,1311069,1311070,1311071,1311072,1311073,1311074,1311075,1311076,1311077,1311078,1311079,1311080,1311081,1315361,1315362,1315363,1315364,1315365,1315366,1315367,1315368,1315369,1315370,1315371,1315372,1315373,1315374,1315375,1315376,1315377,1315378,1315379,1315380,1315381);
delete from assessments_answergroup_institution where id in (1306742,1306743,1306744,1306745,1306746,1306747,1306748,1306749,1306750,1306751,1306752,1306753,1306754,1306755,1306756,1306757,1311066,1311067,1311068,1311069,1311070,1311071,1311072,1311073,1311074,1311075,1311076,1311077,1311078,1311079,1311080,1311081,1315361,1315362,1315363,1315364,1315365,1315366,1315367,1315368,1315369,1315370,1315371,1315372,1315373,1315374,1315375,1315376,1315377,1315378,1315379,1315380,1315381);
