CREATE OR REPLACE FUNCTION upsert_students()
RETURNS numeric AS $$
declare cnt numeric;
declare err_context text;
BEGIN

-- Get rid of duplicate entries
    DELETE
    FROM students_staging
    WHERE ctid NOT IN (SELECT min(ctid) FROM students_staging GROUP BY uid);
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE '% duplicates removed', cnt;

    INSERT INTO students
    SELECT uid,
    student_id,
    school_code,
    school_name,
    class_num,
    cluster,
    block,
    district,
    child_name,
    dob,
    sex,
    father_name,
    mother_name,
    now()
    FROM students_staging a
    WHERE NOT EXISTS (
        SELECT * FROM students b
        WHERE b.uid = a.uid );
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE '% rows inserted', cnt;


    update students v2
    set district  =    g.district,
    block   =   g.block,
    cluster  =   g.cluster,
    school_code  = g.school_code,
    school_name  =  g.school_name,
    class_num = g.class_num,
    child_name   = g.child_name,
    sex  = g.sex,
    dob  = g.dob,
    father_name  = g.father_name,
    mother_name = g.mother_name 
    from students_gka g
    where v2.student_id = g.student_id 
    and v2.child_name is null;
    GET DIAGNOSTICS cnt = ROW_COUNT;
    RAISE NOTICE '% rows updated', cnt;
    
    return 0;
    exception
    when others then
        GET STACKED DIAGNOSTICS err_context = PG_EXCEPTION_CONTEXT;
        RAISE INFO 'Error Name:%',SQLERRM;
        RAISE INFO 'Error State:%', SQLSTATE;
        RAISE INFO 'Error Context:%', err_context;
        return -1;




END;
$$ LANGUAGE plpgsql;
