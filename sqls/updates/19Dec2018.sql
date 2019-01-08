--update assessments_answergroup_institution
update assessments_answergroup_institution set institution_id=20186 where id in (1313562,1313563,1313564,1313565,1313566,1313567,1313568,1313569,1313570,1313571);
update assessments_answergroup_institution set institution_id=20185 where id in (1313521,1313522,1313523,1313524,1313525,1313526,1313527,1313528,1313529,1313530,1313531,1313532,1313533,1313534,1313535,1313536,1313537,1313538,1313539,1313540,1313541,1313542,1313543,1313544,1313545,1313546,1313547,1313548,1313549,1313550,1313551,1313552,1313553,1313554,1313555,1313556,1313557,1313558,1313559,1313560,1313561);
update assessments_answergroup_institution set institution_id=20181 where id in (1313572,1313573,1313574,1313575,1313576,1313577,1313578,1313579,1313580,1313581,1313582);
update assessments_answergroup_institution set institution_id=20182 where id in (1313583,1313584,1313585,1313586,1313587,1313588,1313589,1313590,1313591,1313592,1313593);
update assessments_answergroup_institution set institution_id=20183 where id in (1313594,1313595,1313596,1313597,1313598,1313599,1313600,1313601,1313602,1313603);
update assessments_answergroup_institution set institution_id=20293 where id in (1319278,1319279,1319280,1319281,1319282);
update assessments_answergroup_institution set institution_id=20276 where id in (1319283);
update assessments_answergroup_institution set institution_id=20283 where id in (1319328,1319329,1319330);
update assessments_answergroup_institution set group_value='Nethravathi' where id in (1282097);
update assessments_answergroup_institution set group_value='Hanumavva' where id in (1282095);
update assessments_answergroup_institution set institution_id=20287 where id in (1282098,1282099,1282100,1282101);
update assessments_answergroup_institution set institution_id=20291 where id in (1282102,1282103,1282104,1282105,1282106,1282107,1282108);
update assessments_answergroup_institution set institution_id=20285 where id in (1288236,1288237,1288238,1288239,1288240,1288241,1288242,1288243,1288244,1288245,1288246,1288247,1288248,1288249,1288250,1288251,1288252,1288253,1288254,1288255);
update assessments_answergroup_institution set institution_id=20291 where id in (1288269,1288270,1288271,1288272,1288273,1288274,1288275,1288276,1288277,1288278,1288279,1288280,1288281);
update assessments_answergroup_institution set institution_id=20285 where id in (1293910,1293911,1293912,1293913,1293914,1293915,1293916,1293917,1293918,1293919,1293920,1293921,1293922,1293923,1293924,1293925,1293926,1293927,1293928,1293929,1293930,1293931,1293932,1293933,1293934,1293935,1293936,1293937,1293938,1293939,1293940,1293941,1293942,1293943,1293944,1293945,1293946,1293947,1293948,1293949,1293950,1293951,1293952,1293953);
update assessments_answergroup_institution set institution_id=20287 where id in (1293954,1293955,1293956,1293957,1293958,1293959,1293960,1293961,1293962,1293963);
update assessments_answergroup_institution set institution_id=30091 where id in (1319359,1319360,1319361,1319362,1319363);
update assessments_answergroup_institution set institution_id=6418 where id in (1321290,1321291);

--update schools_institution
update schools_institution set gp_id=4741 where id=43201;
update schools_institution set gp_id=6203 where id=24213;

--insert school
insert into schools_institution (id,name,rural_urban,village,admin0_id,admin1_id,admin2_id,admin3_id,category_id,gender_id,gp_id,institution_type_id,management_id,pincode_id,status_id,dise_id) values ('213638','GOVERNMENT LOWER PRIMARY SCHOOL KAPPADABANDEHATTI','Rural','SANNAPAPPAYANAHATTI',2,'425','539','1671','13','co-ed','3732','primary',1,'577529','AC',310077);
