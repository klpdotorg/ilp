update boundary_electionboundary set const_ward_name = subquery.name from (select id, regexp_replace(const_ward_name,'(.*)\(.*\)','\1') as name from boundary_electionboundary where const_ward_name like '%(%' and const_ward_type_id='GP') as subquery where boundary_electionboundary.id=subquery.id;
