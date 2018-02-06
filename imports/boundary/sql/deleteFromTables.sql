DELETE from boundary_boundaryneighbours;
DELETE from boundary_boundary where id not in (1,2,3);
DELETE from boundary_electionneighbours;
DELETE from boundary_electionboundary;
