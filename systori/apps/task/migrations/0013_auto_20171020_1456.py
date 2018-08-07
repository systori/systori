# Generated by Django 2.0b1 on 2017-10-20 12:56

from django.db import migrations
from postgres_schema.operations import RunInSchemas


def add_missing_job_accounts(apps, schema_editor):
    from ..models import Job
    from ...accounting.models import Account, create_account_for_job

    for job in Job.objects.filter(account_id__isnull=True).filter(
        project__is_template=False
    ):
        code = 10000 + job.id
        account_qs = Account.objects.filter(code=str(code))
        if account_qs.exists():
            account = account_qs.get()
            # check that it's not assigned to some other job already
            assert Job.objects.filter(account=account).count() == 0
            job.account = account
            print("Job {}: Adding existing account...".format(job.id))
        else:
            job.account = create_account_for_job(job)
            print("Job {}: Creating new account...".format(job.id))
        job.save()


class Migration(migrations.Migration):

    dependencies = [("task", "0012_auto_20170613_1704")]

    operations = [RunInSchemas(migrations.RunPython(add_missing_job_accounts))]
