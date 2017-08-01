--Materialized view for institution aggregates across year
DROP MATERIALIZED VIEW IF EXISTS mvw_institution_aggregations CASCADE;
CREATE MATERIALIZED VIEW mvw_institution_aggregations AS
SELECT format('A%sS%s', stusg.academic_year_id, s.id) as id,
    stusg.academic_year_id AS academic_year_id,
    s.id AS institution_id,
    s.name AS institution_name,
    stu.gender_id AS gender,
    stu.mt_id AS mt,
    stu.religion_id as religion,
    stu.category_id as category,
    count(DISTINCT stu.id) AS num
FROM schools_student stu,
    schools_studentgroup sg,
    schools_studentstudentgrouprelation stusg,
    schools_institution s
WHERE 
    stusg.student_group_id = sg.id
    AND sg.institution_id = s.id
    AND stusg.student_id = stu.id
    AND s.status_id = 'AC'
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
    format('A%sS%s', agg.academic_year_id, agg.institution_id) as id,
    agg.academic_year_id as academic_year_id,
    agg.institution_id as institution_id,
    SUM(CASE agg.gender WHEN 'male' THEN agg.num ELSE 0 END) as num_boys,
    SUM(CASE agg.gender WHEN 'female' THEN agg.num ELSE 0 END) as num_girls
    FROM mvw_institution_aggregations as agg 
    GROUP BY academic_year_id, institution_id;


DROP MATERIALIZED VIEW IF EXISTS mvw_institution_class_year_stucount CASCADE;
CREATE MATERIALIZED VIEW mvw_institution_class_year_stucount AS
SELECT format('A%sS%sC%s', stusg.academic_year_id, sg.institution_id,btrim(sg.name)) as id,
    sg.institution_id AS institution_id,
    btrim(sg.name::text) AS studentgroup,
    count(DISTINCT stu.id) AS num,
    stusg.academic_year_id AS academic_year
   FROM schools_studentstudentgrouprelation stusg,
    schools_studentgroup sg,
    schools_student stu
  WHERE stu.id = stusg.student_id AND stusg.student_group_id = sg.id AND stu.status_id in ('AC','IN') GROUP BY sg.institution_id, btrim(sg.name::text), stusg.academic_year_id;


DROP MATERIALIZED VIEW IF EXISTS mvw_boundary_hierarchy CASCADE;
CREATE materialized VIEW mvw_boundary_hierarchy AS
SELECT b3.id AS admin3_id,
    b3.name as admin3_name,
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
    AND b0.parent_id=1;

