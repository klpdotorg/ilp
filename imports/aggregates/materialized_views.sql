--Materialized view for institution aggregates across year
DROP MATERIALIZED VIEW IF EXISTS mvw_institution_aggregations CASCADE;
CREATE MATERIALIZED VIEW mvw_institution_aggregations AS
SELECT format('A%sS%s', stusg.academic_year_id, s.id) AS id,
    stusg.academic_year_id AS academic_year_id,
    s.id AS institution_id,
    s.name AS institution_name,
    stu.gender_id AS gender,
    stu.mt_id AS mt,
    stu.religion_id AS religion,
    stu.category_id AS category,
    count(DISTINCT stu.id) AS num
FROM schools_student stu,
    schools_studentgroup sg,
    schools_studentstudentgrouprelation stusg,
    schools_institution s
WHERE 
    stusg.student_group_id = sg.id
    AND sg.institution_id = s.id
    AND stusg.student_id = stu.id
    AND stusg.status_id != 'DL'
    AND s.status_id != 'DL'
GROUP BY academic_year_id,
    s.id,
    gender,
    mt,
    religion,
    category;


---Materialized view for getting gender count per school per year
DROP MATERIALIZED VIEW IF EXISTS mvw_institution_stu_gender_count CASCADE;
CREATE MATERIALIZED VIEW mvw_institution_stu_gender_count AS
SELECT
    format('A%sS%s', agg.academic_year_id, agg.institution_id) AS id,
    agg.academic_year_id AS academic_year_id,
    agg.institution_id AS institution_id,
    SUM(CASE agg.gender WHEN 'male' THEN agg.num ELSE 0 END) AS num_boys,
    SUM(CASE agg.gender WHEN 'female' THEN agg.num ELSE 0 END) AS num_girls
FROM mvw_institution_aggregations AS agg 
GROUP BY academic_year_id, institution_id;


DROP MATERIALIZED VIEW IF EXISTS mvw_institution_class_year_stucount CASCADE;
CREATE MATERIALIZED VIEW mvw_institution_class_year_stucount AS
SELECT format('A%sS%sC%s', stusg.academic_year_id, sg.institution_id,btrim(sg.name)) AS id,
    sg.institution_id AS institution_id,
    btrim(sg.name::text) AS studentgroup,
    count(DISTINCT stu.id) AS num,
    stusg.academic_year_id AS academic_year
FROM schools_studentstudentgrouprelation stusg,
    schools_studentgroup sg,
    schools_student stu
WHERE stu.id = stusg.student_id AND stusg.student_group_id = sg.id AND stu.status_id != 'DL' 
    AND stusg.status_id != 'DL'
GROUP BY sg.institution_id, btrim(sg.name::text), stusg.academic_year_id;


DROP MATERIALIZED VIEW IF EXISTS mvw_boundary_hierarchy CASCADE;
CREATE materialized VIEW mvw_boundary_hierarchy AS
SELECT format('A%s_%s_%s', b3.id, b2.id, b1.id) AS id,
    b3.id AS admin3_id,
    b3.name AS admin3_name,
    b2.id AS admin2_id,
    b2.name AS admin2_name,
    b1.id AS admin1_id,
    b1.name AS admin1_name,
    b0.id AS admin0_id,
    b0.name AS admin0_name,
    b1.type_id AS type_id
FROM boundary_boundary b1,
     boundary_boundary b2,
     boundary_boundary b3,
     boundary_boundary b0
WHERE b3.parent_id = b2.id
    AND b2.parent_id = b1.id
    AND b1.parent_id = b0.id
    AND b0.parent_id = 1;


DROP MATERIALIZED VIEW IF EXISTS mvw_boundary_basic_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_boundary_basic_agg AS
SELECT distinct format('A%s_%s', stusg.academic_year_id, b.id) AS id,
    stusg.academic_year_id AS year,
    b.id AS boundary_id,
    count(distinct s.id) AS num_schools,
    count(distinct stu.id) AS num_students,
    sum(case(stu.gender_id) when 'male' then 1 else 0 end) AS num_boys,
    sum(case(stu.gender_id) when 'female' then 1 else 0 end) AS num_girls
FROM schools_student stu, 
     schools_institution s, 
     boundary_boundary b,
     schools_studentstudentgrouprelation stusg
WHERE stu.institution_id = s.id AND 
    stu.id = stusg.student_id AND 
    (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    AND stu.status_id != 'DL'
    AND stusg.status_id != 'DL'
GROUP BY stusg.academic_year_id, b.id;


DROP MATERIALIZED VIEW IF EXISTS mvw_boundary_school_gender_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_boundary_school_gender_agg AS
SELECT distinct format('A%s_%s_%s', stusg.academic_year_id,b.id, instgender.name) AS id,
    stusg.academic_year_id AS year,
    b.id AS boundary_id,
    instgender.name AS gender,
    count(distinct s.id) AS num_schools,
    count(distinct stu.id) AS num_students,
    sum(case(stu.gender_id) when 'male' then 1 else 0 end) AS num_boys,
    sum(case(stu.gender_id) when 'female' then 1 else 0 end) AS num_girls
FROM schools_student stu, 
     schools_institution s, 
     boundary_boundary b, common_institutiongender instgender,
     schools_studentstudentgrouprelation stusg
WHERE stu.institution_id = s.id AND s.gender_id =  instgender.char_id AND 
    stu.id = stusg.student_id AND 
    (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    AND stu.status_id != 'DL'
    AND stusg.status_id != 'DL'
GROUP BY stusg.academic_year_id, b.id, instgender.name;

DROP MATERIALIZED VIEW IF EXISTS mvw_boundary_school_category_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_boundary_school_category_agg AS
SELECT distinct format('A%s_%s_%s', stusg.academic_year_id,b.id, category.name) AS id,
    stusg.academic_year_id AS year,
     b.id AS boundary_id,
    category.institution_type_id AS institution_type,
    category.name AS category,
    count(distinct s.id) AS num_schools,
    count(distinct stu.id) AS num_students,
    sum(case(stu.gender_id) when 'male' then 1 else 0 end) AS num_boys,
    sum(case(stu.gender_id) when 'female' then 1 else 0 end) AS num_girls
FROM schools_student stu, 
     schools_institution s, 
     schools_institutioncategory category,
     boundary_boundary b,
     schools_studentstudentgrouprelation stusg 
WHERE stu.institution_id = s.id AND s.category_id =  category.id 
    AND stu.id = stusg.student_id 
    AND (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    AND stu.status_id != 'DL' 
    AND stusg.status_id != 'DL'
GROUP BY stusg.academic_year_id, b.id, category.name, category.institution_type_id;

DROP MATERIALIZED VIEW IF EXISTS mvw_boundary_school_mgmt_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_boundary_school_mgmt_agg AS
SELECT distinct format('A%s_%s_%s', stusg.academic_year_id,b.id, management.name) AS id,
    stusg.academic_year_id AS year,
    b.id AS boundary_id,
    management.name AS management,
    count(distinct s.id) AS num_schools,
    count(distinct stu.id) AS num_students,
    sum(case(stu.gender_id) when 'male' then 1 else 0 end) AS num_boys,
    sum(case(stu.gender_id) when 'female' then 1 else 0 end) AS num_girls
FROM schools_student stu, 
    schools_institution s, 
    schools_management management,
    boundary_boundary b,
    schools_studentstudentgrouprelation stusg 
WHERE stu.institution_id = s.id 
    AND stu.id = stusg.student_id 
    AND s.management_id = management.id
    AND (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    AND stu.status_id != 'DL' 
    AND stusg.status_id != 'DL'
GROUP BY stusg.academic_year_id, b.id, management.name;


DROP MATERIALIZED VIEW IF EXISTS mvw_boundary_student_mt_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_boundary_student_mt_agg AS
SELECT distinct format('A%s_%s_%s', stusg.academic_year_id,b.id, mt.name) AS id,
    stusg.academic_year_id AS year,
    b.id AS boundary_id,
    mt.name AS mt,
    count(distinct s.id) AS num_schools,
    count(distinct stu.id) AS num_students,
    sum(case(stu.gender_id) when 'male' then 1 else 0 end) AS num_boys,
    sum(case(stu.gender_id) when 'female' then 1 else 0 end) AS num_girls
FROM schools_student stu, 
     schools_institution s, 
     common_language mt,
     boundary_boundary b,
     schools_studentstudentgrouprelation stusg 
WHERE stu.institution_id = s.id
    AND stu.mt_id = mt.char_id 
    AND stu.id = stusg.student_id 
    AND (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    AND stu.status_id != 'DL'
    AND stusg.status_id != 'DL' 
GROUP BY stusg.academic_year_id, b.id, mt.name;


DROP MATERIALIZED VIEW IF EXISTS mvw_boundary_school_moi_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_boundary_school_moi_agg AS
SELECT distinct format('A%s_%s_%s', stusg.academic_year_id,b.id, moi.name) AS id,
    stusg.academic_year_id AS year,
    b.id AS boundary_id,
    moi.name AS moi,
    count(distinct s.id) AS num_schools,
    count(distinct stu.id) AS num_students,
    sum(case(stu.gender_id) when 'male' then 1 else 0 end) AS num_boys,
    sum(case(stu.gender_id) when 'female' then 1 else 0 end) AS num_girls
FROM schools_student stu, 
     schools_institution s, 
     schools_institutionlanguage instlang,
     common_language moi,
     boundary_boundary b,
     schools_studentstudentgrouprelation stusg 
WHERE stu.institution_id = s.id 
    AND stu.id = stusg.student_id
    AND s.id = instlang.institution_id
    AND instlang.moi_id = moi.char_id
    AND (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    AND stu.status_id != 'DL' 
    AND stusg.status_id != 'DL'
GROUP BY stusg.academic_year_id, b.id, moi.name;
