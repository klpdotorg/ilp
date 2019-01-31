delete from assessments_surveytaginstitutionmapping where tag_id='gka' and academic_year_id in ('1617', '1718');
delete from assessments_surveytaginstitutionmapping where tag_id='gka' and academic_year_id='1819' and institution_id in (select id from schools_institution where admin0_id=2);
