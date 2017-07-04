UPDATE boundary_boundary boundary SET dise_slug = (SELECT B.name from boundary_boundary B WHERE 
boundary.parent_id=B.id)|| '-' || boundary.name WHERE boundary.parent_id IS NOT NULL;