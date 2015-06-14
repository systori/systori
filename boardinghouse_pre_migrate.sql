create schema mehr_handwerk;

alter table public.accounting_account set schema mehr_handwerk;
alter table public.accounting_entry set schema mehr_handwerk;
alter table public.accounting_transaction set schema mehr_handwerk;
alter table public.directory_contact set schema mehr_handwerk;
alter table public.directory_projectcontact set schema mehr_handwerk;
alter table public.document_documenttemplate set schema mehr_handwerk;
alter table public.document_invoice set schema mehr_handwerk;
alter table public.document_proposal set schema mehr_handwerk;
alter table public.document_proposal_jobs set schema mehr_handwerk;
alter table public.equipment_equipment set schema mehr_handwerk;
alter table public.project_dailyplan set schema mehr_handwerk;
alter table public.project_dailyplan_equipment set schema mehr_handwerk;
alter table public.project_dailyplan_tasks set schema mehr_handwerk;
alter table public.project_jobsite set schema mehr_handwerk;
alter table public.project_project set schema mehr_handwerk;
alter table public.project_teammember set schema mehr_handwerk;
alter table public.task_job set schema mehr_handwerk;
alter table public.task_lineitem set schema mehr_handwerk;
alter table public.task_progressattachment set schema mehr_handwerk;
alter table public.task_progressreport set schema mehr_handwerk;
alter table public.task_task set schema mehr_handwerk;
alter table public.task_taskgroup set schema mehr_handwerk;
alter table public.task_taskinstance set schema mehr_handwerk;

delete from django_migrations where app in ('accounting','directory','document','equipment','project','task');
