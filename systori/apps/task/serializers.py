from rest_framework import serializers
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
    class Meta:
        model = LineItem
        fields = [
            'name', 'order',
            'qty', 'qty_equation',
            'unit',
            'price', 'price_equation',
            'total', 'total_equation',
            'is_flagged',
            'is_hidden',
        ]

    @staticmethod
    def create(validated_data, task=None):
        return LineItem.objects.create(task=task, **validated_data)


class TaskSerializer(serializers.ModelSerializer):
    lineitems = LineItemSerializer(many=True)

    class Meta:
        model = Task
        fields = [
            'group',
            'name', 'description', 'order',
            'qty', 'qty_equation',
            'unit',
            'price', 'price_equation',
            'total', 'total_equation',
            'variant_group', 'variant_serial',
            'is_provisional',
            'lineitems',
        ]

    @staticmethod
    def create(validated_data):
        lineitems = validated_data.pop('lineitems', [])
        task = Task.objects.create(**validated_data)
        for lineitem in lineitems:
            LineItemSerializer.create(lineitem, task=task)
        return task


class GroupSerializer(serializers.ModelSerializer):
    groups = RecursiveField(required=False)
    tasks = TaskSerializer(many=True, required=False)

    class Meta:
        model = Group
        fields = [
            'name', 'description', 'order',
            'groups', 'tasks'
        ]

    @staticmethod
    def create(validated_data, parent=None):
        tasks = validated_data.pop('tasks', [])
        groups = validated_data.pop('groups', [])
        group = Group.objects.create(parent=parent, **validated_data)
        for task in tasks:
            task['group'] = group
            TaskSerializer.create(task)
        for subgroup in groups:
            GroupSerializer.create(subgroup, parent=group)
        return group
