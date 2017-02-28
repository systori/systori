import os
import re
import types
import string
import django; django.setup()
from decimal import Decimal as D
from django.template import Context, Template
from django.test.client import Client
from django.test.utils import setup_databases, teardown_databases
from django.urls import reverse
from django.utils.translation import activate
from django.conf import settings
from systori.apps.company.factories import CompanyFactory
from systori.apps.project.factories import ProjectFactory
from systori.apps.task.factories import JobFactory, GroupFactory, TaskFactory, LineItemFactory
from systori.apps.user.factories import UserFactory
from systori.apps.accounting.models import Entry, create_account_for_job
from systori.apps.document.forms import PaymentRowForm
from systori.apps.accounting.workflow import debit_jobs, create_chart_of_accounts
from systori.apps.accounting.constants import TAX_RATE
from systori.lib.accounting.tools import Amount as A


DART_APP_ROOT = os.path.dirname(os.path.dirname(__file__))

CSRFINPUT = re.compile(rb"(<input type='hidden' name='csrfmiddlewaretoken' value=')[0-9A-Za-z]+(' />)")


def write_test_html(path, name, html):
    file_path = os.path.join(DART_APP_ROOT, 'test', path, name+'_test.html')
    html = CSRFINPUT.sub(rb'\1abc\2', html)
    with open(file_path, 'wb') as test_file:
        test_file.write(html)
        test_file.write(b'<link rel="x-dart-test" href="'+name.encode()+b'_test.dart">\n')
        test_file.write(b'<script src="packages/test/dart.js"></script>\n')
        test_file.write(b'<!--\n')
        test_file.write(b'<script type="application/dart" src="'+name.encode()+b'_test.dart"></script>\n')
        test_file.write(b'-->\n')


def create_data():
    data = types.SimpleNamespace()
    data.company = CompanyFactory(name="ACME Industries")
    create_chart_of_accounts()
    data.user = UserFactory(first_name="Ben", last_name="Zimmermann", email='test@systori.com', company=data.company)
    data.project = ProjectFactory(name="Test Project", structure="0.00.00.000")

    data.job1 = JobFactory(name="Test Job", project=data.project)
    data.job1.account = create_account_for_job(data.job1)
    data.job1.save()
    group1 = GroupFactory(name='Group 1', parent=data.job1)
    group2 = GroupFactory(name='Group 2', parent=group1)
    task = TaskFactory(name='Fence', group=group2, qty=200, qty_equation='200', unit='m²', price=74.98, total=14996)
    LineItemFactory(name='Labor', task=task, qty=0.1, qty_equation='0.1', unit='hr', price=19.8, price_equation='18*1.1', total=1.98)
    LineItemFactory(name='Equipment Rental', task=task, qty=0.1, qty_equation='!', unit='hr', price=50, price_equation='50', total=5)
    LineItemFactory(name='Materials', task=task, qty=4, qty_equation='4', unit='m', price=17, price_equation='17', total=68)

    data.job2 = JobFactory(name="Test Job", project=data.project)
    data.job2.account = create_account_for_job(data.job2)
    data.job2.save()

    debit_jobs([
        (data.job1, A(D(388.8), D(91.2)), Entry.WORK_DEBIT),
        (data.job2, A(D(100), D(19)), Entry.WORK_DEBIT)
    ])

    data.big_project = ProjectFactory(name="Big Project", structure="0.00.00.00.00.000")
    data.big_job = JobFactory(name="Big Job", project=data.big_project)
    data.big_job.account = create_account_for_job(data.big_job)
    data.big_job.save()

    def add_task(group):
        task = TaskFactory(name='Fence', group=group, qty=200, qty_equation='200', unit='m²', price=74.98, total=14996)
        LineItemFactory(name='Labor', task=task, qty=0.1, qty_equation='0.1', unit='hr', price=19.8, price_equation='18*1.1', total=1.98)
        LineItemFactory(name='Equipment Rental', task=task, qty=0.1, qty_equation='!', unit='hr', price=50, price_equation='50', total=5)
        LineItemFactory(name='Materials', task=task, qty=4, qty_equation='4', unit='m', price=17, price_equation='17', total=68)

    for groupset in range(3):
        groupset = string.ascii_uppercase[groupset]
        group = GroupFactory(name='Main Group {}1'.format(groupset), parent=data.big_job)
        groups = []
        for depth in range(2, 5):
            groups = [
                GroupFactory(name='Group {}{}.1'.format(groupset, depth), parent=group),
                GroupFactory(name='Group {}{}.2'.format(groupset, depth), parent=group),
            ]
            group = groups[1]
        if groupset == 'B':
            for g in groups:
                add_task(g)
                add_task(g)
        else:
            add_task(group)

    return data


def generate_amount_test_html(data):
    form = PaymentRowForm(initial={
        'jobs': [data.job1],
        'job': data.job1,
        'split': A(D('4800'), D('912'))
    })
    form.pre_txn = types.SimpleNamespace()
    form.calculate_accounting_state(form.pre_txn)
    form.calculate_initial_values()
    template = Template("""{% load amount %}
    <div id="scaffold">
    <table><tr>
    {% amount_view "test-amount-view" form1 "balance" %}
    {% amount_input "test-amount-input" form1 "split" %}
    {% amount_stateful "test-amount-stateful" form1 "discount" %}
    </tr></table></div>""")
    return template.render(Context({'TAX_RATE': TAX_RATE, 'form1': form})).encode()


def generate_pages():
    data = create_data()
    host = data.company.schema+settings.SESSION_COOKIE_DOMAIN
    client = Client()
    client.login(username=data.user.email, password='open sesame')

    job_editor = client.get(reverse('job.editor', args=[data.project.id, data.job1.id]), HTTP_HOST=host)
    write_test_html('editor', 'editor', job_editor.content)

    #proposal_create = client.get(reverse('proposal.create', args=[data.project.id]), HTTP_HOST=host)
    #write_test_html('apps', 'proposal_editor', proposal_create.content)

    payment_create = client.get(reverse('payment.create', args=[data.project.id]), HTTP_HOST=host)
    write_test_html('apps', 'payment_editor', payment_create.content)

    adjustment_create = client.get(reverse('adjustment.create', args=[data.project.id]), HTTP_HOST=host)
    write_test_html('apps', 'adjustment_editor', adjustment_create.content)

    refund_create = client.get(reverse('refund.create', args=[data.project.id]), HTTP_HOST=host)
    write_test_html('apps', 'refund_editor', refund_create.content)

    sticky_header = client.get(reverse('job.editor', args=[data.big_project.id, data.big_job.id]), HTTP_HOST=host)
    write_test_html('editor', 'sticky_header', sticky_header.content)

    activate('de')
    write_test_html('inputs', 'amount', generate_amount_test_html(data))


if __name__ == "__main__":
    class DisableMigrations:
        def __contains__(self, item):
            return True
        def __getitem__(self, item):
            return None
    settings.MIGRATION_MODULES = DisableMigrations()
    print('Creating test database.')
    config = setup_databases(verbosity=0, interactive=False)
    print('Generating scaffolds.')
    generate_pages()
    print('Done.')
    teardown_databases(config, verbosity=0)
