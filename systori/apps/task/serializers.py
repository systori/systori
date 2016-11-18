from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from .models import Group, Task, LineItem


class RecursiveField(serializers.Field):

    PROXIED_ATTRS = (
        # methods
        'get_value',
        'get_initial',
        'run_validation',
        'get_attribute',
        'to_representation',

        # attributes
        'field_name',
        'source',
        'read_only',
        'default',
        'source_attrs',
        'write_only',
    )

    def __init__(self, **kwargs):
        self._proxied = None
        super().__init__(**kwargs)

    def bind(self, field_name, parent):
        self.bind_args = (field_name, parent)

    @property
    def proxied(self):
        if not self._proxied:
            if self.bind_args:
                field_name, parent = self.bind_args
                if hasattr(parent, 'child') and parent.child is self:
                    # RecursiveField nested inside of a ListField
                    parent_class = parent.parent.__class__
                else:
                    # RecursiveField directly inside a Serializer
                    parent_class = parent.__class__
                proxied = parent_class(many=True, required=False)
                proxied.bind(field_name, parent)
                self._proxied = proxied
        return self._proxied

    def __getattribute__(self, name):
        if name in RecursiveField.PROXIED_ATTRS:
            try:
                proxied = object.__getattribute__(self, 'proxied')
                return getattr(proxied, name)
            except AttributeError:
                pass

        return object.__getattribute__(self, name)


class LineItemSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False)
    token = serializers.IntegerField(required=False)

    class Meta:
        model = LineItem
        fields = [
            'token', 'pk', 'name', 'order',
            'qty', 'qty_equation',
            'unit',
            'price', 'price_equation',
            'total', 'total_equation',
            'is_flagged',
            'is_hidden',
        ]

    @staticmethod
    def create_or_update_many(lineitems, task):
        data = []
        for lineitem_data in lineitems:
            if 'token' in lineitem_data:
                token = lineitem_data.pop('token')
                lineitem = LineItem.objects.create(task=task, **lineitem_data)
                data.append({'pk': lineitem.pk, 'token': token})
            elif 'pk' in lineitem_data:
                lineitem = get_object_or_404(
                    LineItem.objects.all(),
                    id=lineitem_data.pop('pk')
                )
                for attr, val in lineitem_data.items():
                    setattr(lineitem, attr, val)
                lineitem.save()
                data.append({'pk': lineitem.pk})
        return data


class TaskSerializer(serializers.ModelSerializer):
    lineitems = LineItemSerializer(many=True)
    token = serializers.IntegerField(required=False)

    class Meta:
        model = Task
        fields = [
            'token', 'group',
            'name', 'description', 'order',
            'qty', 'qty_equation',
            'unit',
            'price', 'price_equation',
            'total', 'total_equation',
            'variant_group', 'variant_serial',
            'is_provisional',
            'lineitems',
        ]

    def create(self, validated_data):
        token = validated_data.pop('token')
        lineitems = validated_data.pop('lineitems', [])
        task = Task.objects.create(**validated_data)
        self._data = {
            'pk': task.pk,
            'token': token,
        }
        changed_lineitems = LineItemSerializer.create_or_update_many(lineitems, task)
        if changed_lineitems: self._data['lineitems'] = changed_lineitems
        return self._data

    def update(self, task, validated_data):
        lineitems = validated_data.pop('lineitems', [])
        super().update(task, validated_data)
        self._data = {'pk': task.pk}
        changed_lineitems = LineItemSerializer.create_or_update_many(lineitems, task)
        if changed_lineitems: self._data['lineitems'] = changed_lineitems
        return self._data


class GroupSerializer(serializers.ModelSerializer):
    groups = RecursiveField(required=False)
    tasks = TaskSerializer(many=True, required=False)
    token = serializers.IntegerField(required=False)

    class Meta:
        model = Group
        fields = [
            'token', 'name', 'description', 'order',
            'groups', 'tasks'
        ]

    def create(self, validated_data, parent=None):
        token = validated_data.pop('token')
        tasks = validated_data.pop('tasks', [])
        groups = validated_data.pop('groups', [])
        group = Group.objects.create(parent=parent, **validated_data)
        data = {'pk': group.pk, 'token': token}
        for task in tasks:
            if 'tasks' not in data: data['tasks'] = []
            task['group'] = group
            data['tasks'].append(TaskSerializer.create(task))
        for subgroup in groups:
            if 'groups' not in data: data['groups'] = []
            data['groups'].append(GroupSerializer().create(subgroup, parent=group))
        self._data = data
        return data

    def update(self, group, validated_data):
        super().update(group, validated_data)
        self._data = {'pk': group.pk}
        return self._data
