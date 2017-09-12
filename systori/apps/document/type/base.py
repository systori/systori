from datetime import date

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import money, ubrdecimal


def parse_date(str_date):
    return date_format(date(*map(int, str_date.split('-'))), use_l10n=True) if str_date else None


class BaseRowIterator:

    def __init__(self, render, document):
        self.render = render
        self.document = document

    def __iter__(self):
        for job in self.document['jobs']:
            yield from self.iterate_job(job)
        for job in self.document['jobs']:
            yield from self.subtotal_job(job)

    def iterate_job(self, job):
        yield from self.iterate_group(job, 0)

    def iterate_group(self, group, depth):
        yield self.render.group_html, self.get_group_context(group, depth)
        yield from self.iterate_tasks(group)
        for subgroup in group.get('groups', []):
            yield from self.iterate_group(subgroup, depth+1)
        if not group.get('groups', []) and group.get('tasks', []):
            yield self.render.subtotal_html, self.get_subtotal_context(group, offset=True)

    def iterate_tasks(self, group):
        for task in group.get('tasks', []):
            task_context = self.get_task_context(task)
            yield self.render.group_html, task_context
            if task_context['qty'] is not None:
                yield self.render.lineitem_html, {
                    'name': '',
                    'qty': task_context['qty'],
                    'unit': task['unit'],
                    'price': money(task['price']),
                    'total': task_context['total'],
                }
            else:
                for lineitem in task['lineitems']:
                    yield self.render.lineitem_html, \
                          self.get_lineitem_context(lineitem)

    def subtotal_job(self, job):
        for group in job.get('groups', []):
            yield self.render.subtotal_html, self.get_subtotal_context(group, offset=False)

    def get_group_context(self, group, depth, **kwargs):
        kwargs.update({
            'code': group['code'],
            'name': group['name'],
            'bold_name': depth <= 2,
            'description': group['description'],
            'show_description': depth <= 2,
        })
        return kwargs

    def get_task_context(self, task, **kwargs):
        kwargs.update({
            'code': task['code'],
            'name': task['name'],
            'bold_name': False,
            'description': task['description'],
        })
        if task.get('variant_group'):
            if task['variant_serial'] == 0:
                kwargs['name'] = _('Variant {}.0: {}').format(task['variant_group'], task['name'])
            else:
                kwargs['name'] = _('Variant {}.{}: {} - Alternative for Variant {}.0').format(
                    task['variant_group'], task['variant_serial'], task['name'], task['variant_group']
                )
        return kwargs

    def get_lineitem_context(self, lineitem, **kwargs):
        kwargs.update({
            'name': lineitem['name'],
            'unit': lineitem['unit'],
            'price': money(lineitem['price']),
        })
        return kwargs

    def get_subtotal_context(self, group, **kwargs):
        kwargs.update({
            'code': group['code'],
            'name': group['name'],
        })
        return kwargs
