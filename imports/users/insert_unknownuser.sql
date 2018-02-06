insert into users_user(id, password, email, mobile_no, first_name, last_name, is_active, is_email_verified, is_mobile_verified, opted_email, is_superuser, user_type_id) values(10,'unknown', 'unknown', '0', 'Unknown','User', true, false, false, false, false, 'UK');
insert into users_user_groups select max(ug.id)+1, 10, ag.id from users_user_groups ug, auth_group ag where ag.name='ilp_auth_user' group by ag.id;
insert into users_user_groups select max(ug.id)+1, 10, ag.id from users_user_groups ug, auth_group ag where ag.name='ilp_konnect_user' group by ag.id;
