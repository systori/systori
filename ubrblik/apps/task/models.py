from django.db import models, connections
from django.db.models import Sum, F
from django.db.models.manager import BaseManager
from django.db.models.sql import Query
from django.db.models.sql.constants import JoinInfo
from django.db.models.sql.compiler import SQLCompiler
from django.utils.translation import ugettext_lazy as _

import copy

# TODO:
# - Test what happens when OrderedManager is used with either select_related or prefetch_related
# - Test with more complex examples of converting a Query -> Update/Insert/Delete Queries

class OrderedSQLCompiler(SQLCompiler):
    def as_sql(self, with_limits=True, with_col_aliases=False):
        sql, params = super(OrderedSQLCompiler, self).as_sql(with_limits, with_col_aliases)
        meta = self.query.get_meta()
        sql = """
        with recursive {virtual_table} as
        (
          select 1 as sequence_number, * from {table} where previous_id is null
          union all 
          select {virtual_table}.sequence_number+1 as sequence_number, {table}.* from {table} join {virtual_table} on ({virtual_table}.id={table}.previous_id)
        )
        {sql}
        """.format(table=meta.original_db_table, virtual_table=meta.db_table, sql=sql)
        return sql, params


class OrderedQuery(Query):

    _view_meta = None
    def get_meta(self):
        if self._view_meta:
            return self._view_meta
        meta = copy.copy(self.model._meta)
        meta.original_db_table = meta.db_table
        meta.db_table += '_ordered'
        self._view_meta = meta
        return meta

    def get_compiler(self, using=None, connection=None):
        if using: connection = connections[using]
        return OrderedSQLCompiler(self, connection, using)

    def clone(self, klass=None, memo=None, **kwargs):
        clone = super(OrderedQuery, self).clone(klass, memo, **kwargs)
        if klass is OrderedQuery or not klass:
          return clone

        # Since the OrderedQuery uses a virtual table
        # and often times regular Query's are converted
        # into Insert/Update/Delete Queries we need to
        # fix up the cloned query and any reference
        # to virtual table needs to be replaced with the
        # original table name.

        meta = self.get_meta()

        # the first table in clone.tables is used as the update/insert/delete table
        clone.tables[clone.tables.index(meta.db_table)] = meta.original_db_table

        # rewrite where clause to use table instead of view
        for where in clone.where.children:
            if where.lhs.alias == meta.db_table:
              where.lhs.alias = meta.original_db_table

        return clone


class OrderedQuerySet(models.QuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None):
        super(OrderedQuerySet, self).__init__(model, query or OrderedQuery(model), using, hints)


class OrderedManager(BaseManager.from_queryset(OrderedQuerySet)):
    use_for_related_fields = True
    def get_queryset(self):
        queryset = super(OrderedManager, self).get_queryset()
        meta = queryset.query.get_meta()
        return queryset.extra(select={'sequence_number': '{}.sequence_number'.format(meta.db_table)})


class TaskGroup(models.Model):

    name = models.CharField(_("Name"), max_length=128)
    description = models.TextField()
    trade = models.ForeignKey("project.Trade", related_name="taskgroups")

    previous = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)
    # sequence_number is automatically added

    objects = OrderedManager()

    class Meta:
        verbose_name = _("Task Group")
        verbose_name_plural = _("Task Groups")
        
    @property
    def code(self):
        return self.id

    @property
    def total(self):
        # TODO: slow implementation, convert to aggregate
        t = 0
        for task in self.tasks.all():
            t += task.total
        return t

class Task(models.Model):

    name = models.CharField(_("Name"), max_length=128)
    description = models.TextField()
    taskgroup = models.ForeignKey(TaskGroup, related_name="tasks")

    previous = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)

    objects = OrderedManager()

    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")

    @property
    def code(self):
        return "{}.{}".format(self.taskgroup_id, self.id)

    @property
    def total(self):
        price = self.lineitems.aggregate(total=Sum('price', field='price*qty'))
        return price['total'] or 0


class LineItem(models.Model):

    task = models.ForeignKey("Task", related_name="lineitems")
    name = models.CharField(_("Name"), max_length=128)
    qty = models.DecimalField(_("Quantity"), max_digits=12, decimal_places=2)
    unit = models.CharField(_("Unit"), max_length=64)
    price = models.DecimalField(_("Price"), max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = _("Line Item")
        verbose_name_plural = _("Line Items")
        ordering = ['id']

    @property
    def total(self):
        return self.price * self.qty