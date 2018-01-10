insert into auth_group(id,name) values(10, 'Unknown');
insert into users_user(id, password, email, mobile_no, first_name, last_name, is_active, is_email_verified, is_mobile_verified, opted_email, is_superuser) values(10,'unknown', 'unknown', '0', 'Unknown','User', true, false, false, false, false);
insert into users_user_groups select max(id)+1, 10, 10 from users_user_groups;
