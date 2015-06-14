insert into company_company values ('mehr_handwerk', 'Mehr Handwerk', true);
insert into company_access (is_enabled, is_employee, is_accountant, company_id, user_id) select true, true, false, 'mehr_handwerk', id from user_user;
