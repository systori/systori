import os
import types
import django
from decimal import Decimal as D
from django.db import transaction
from django.template import Context, Template
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.test.runner import setup_databases
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings.travis")

from systori.apps.company.factories import CompanyFactory
from systori.apps.project.factories import ProjectFactory
from systori.apps.task.factories import JobFactory
from systori.apps.user.factories import UserFactory
from systori.apps.accounting.models import Entry, create_account_for_job
from systori.apps.accounting.forms import PaymentRowForm
from systori.apps.accounting.workflow import debit_jobs, create_chart_of_accounts
from systori.lib.accounting.tools import Amount as A


DART_APP_ROOT = os.path.dirname(os.path.dirname(__file__))


def write_test_html(name, html):
    file_path = os.path.join(DART_APP_ROOT, 'test', name+'_test.html')
    with open(file_path, 'wb') as test_file:
        test_file.write(html)
        test_file.write(b'<link rel="x-dart-test" href="'+name.encode()+b'_test.dart">\n')
        test_file.write(b'<script src="packages/test/dart.js"></script>\n')


def create_data():
    data = types.SimpleNamespace()
    data.company = CompanyFactory()
    create_chart_of_accounts()
    data.user = UserFactory(email='lex@damoti.com', password='open sesame', company=data.company)
    data.project = ProjectFactory(name="Test Project")

    data.job1 = JobFactory(name="Test Job", project=data.project)
    data.job1.account = create_account_for_job(data.job1)
    data.job1.save()

    data.job2 = JobFactory(name="Test Job", project=data.project)
    data.job2.account = create_account_for_job(data.job2)
    data.job2.save()

    debit_jobs([
        (data.job1, A(D(388.8), D(91.2)), Entry.WORK_DEBIT),
        (data.job2, A(D(100), D(19)), Entry.WORK_DEBIT)
    ])
    return data


def generate_amount_test_html(data):
    template = Template("""{% load amount %}
    <table><tr>
    {% amount_view "test-amount-view" form1 "balance" %}
    {% amount_input "test-amount-input" form1 "payment" %}
    {% amount_stateful "test-amount-stateful" form1 "discount" %}
    </tr></table>""")
    context = Context({
        'TAX_RATE': '0.19',
        'form1': PaymentRowForm(initial={
            'job': data.job1,
            'payment_net': '4800',
            'payment_tax': '912',
        })
    })
    return template.render(context).encode()


def generate_pages():
    data = create_data()
    client = Client()
    client.login(username=data.user.email, password='open sesame')

    editor = client.get(reverse('tasks', args=[data.project.id, data.job1.id]))
    write_test_html('proposal_editor', editor.content)

    payment_create = client.get(reverse('payment.create', args=[data.project.id]))
    write_test_html('payment_editor', payment_create.content)

    adjustment_create = client.get(reverse('adjustment.create', args=[data.project.id]))
    write_test_html('adjustment_editor', adjustment_create.content)

    write_test_html('amount', generate_amount_test_html(data))


if __name__ == "__main__":
    django.setup()
    setup_databases(verbosity=1, interactive=False, keepdb=True)

    # Start Transaction
    atom = transaction.atomic()
    atom.__enter__()

    generate_pages()

    # Rollback Transaction
    transaction.set_rollback(True)
    atom.__exit__(None, None, None)
