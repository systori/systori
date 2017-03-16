from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from .models import Job, Group, Task, LineItem


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

    class Meta:
        model = LineItem
        fields = [
            'pk', 'token', 'name', 'order',
            'qty', 'qty_equation',
            'unit', 'price', 'price_equation',
            'total', 'total_equation',
            'is_hidden',
        ]

    def create(self, validated_data):
        lineitem, _ = LineItem.objects.update_or_create(
            validated_data,
            job=validated_data['task'].job,
            token=validated_data['token']
        )
        return self.update(lineitem, {})

    def update(self, lineitem, validated_data):
        if validated_data:
            super().update(lineitem, validated_data)
        self._data = {'pk': lineitem.pk, 'token': lineitem.token}
        return self._data


class TaskSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False)
    lineitems = LineItemSerializer(many=True)

    class Meta:
        model = Task
        fields = [
            'pk', 'token',
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
        lineitems = validated_data.pop('lineitems', [])
        task, _ = Task.objects.update_or_create(
            validated_data,
            job=validated_data['group'].job,
            token=validated_data['token']
        )
        return self.update(task, {'lineitems': lineitems})

    def update(self, task, validated_data):
        lineitems = validated_data.pop('lineitems', [])

        if validated_data:
            super().update(task, validated_data)

        data = {'pk': task.pk, 'token': task.token}

        for lineitem in lineitems:
            if 'lineitems' not in data: data['lineitems'] = []
            pk, instance = lineitem.pop('pk', None), None
            if pk: instance = get_object_or_404(LineItem.objects.all(), id=pk)
            serializer = LineItemSerializer(instance=instance, data=lineitem, partial=True)
            serializer.is_valid(raise_exception=True)
            data['lineitems'].append(serializer.save(task=task))

        self._data = data

        return data


class GroupSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False)
    groups = RecursiveField(required=False)
    tasks = TaskSerializer(many=True, required=False)

    class Meta:
        model = Group
        fields = [
            'pk', 'token',
            'name', 'description', 'order',
            'groups', 'tasks'
        ]

    def create(self, validated_data):
        tasks = validated_data.pop('tasks', [])
        groups = validated_data.pop('groups', [])
        group, _ = Group.objects.update_or_create(
            validated_data,
            job=validated_data['parent'].job,
            token=validated_data['token']
        )
        return self.update(group, {'tasks': tasks, 'groups': groups})

    def update(self, group, validated_data):
        tasks = validated_data.pop('tasks', [])
        groups = validated_data.pop('groups', [])

        if validated_data:
            super().update(group, validated_data)

        data = {'pk': group.pk, 'token': group.token}

        for task in tasks:
            if 'tasks' not in data: data['tasks'] = []
            pk, instance = task.pop('pk', None), None
            if pk: instance = get_object_or_404(Task.objects.all(), id=pk)
            serializer = TaskSerializer(instance=instance, data=task, partial=True)
            serializer.is_valid(raise_exception=True)
            data['tasks'].append(serializer.save(group=group))

        for subgroup in groups:
            if 'groups' not in data: data['groups'] = []
            pk, instance = subgroup.pop('pk', None), None
            if pk: instance = get_object_or_404(Group.objects.all(), id=pk)
            serializer = GroupSerializer(instance=instance, data=subgroup, partial=True)
            serializer.is_valid(raise_exception=True)
            data['groups'].append(serializer.save(parent=group))

        self._data = data

        return data


class DeleteSerializer(serializers.Serializer):
    groups = serializers.ListField(child=serializers.IntegerField(), required=False)
    tasks = serializers.ListField(child=serializers.IntegerField(), required=False)
    lineitems = serializers.ListField(child=serializers.IntegerField(), required=False)

    def perform(self):

        groups = self.initial_data.pop('groups', [])
        if groups:
            Group.objects.filter(pk__in=groups).delete()

        tasks = self.initial_data.pop('tasks', [])
        if tasks:
            Task.objects.filter(pk__in=tasks).delete()

        lineitems = self.initial_data.pop('lineitems', [])
        if lineitems:
            LineItem.objects.filter(pk__in=lineitems).delete()


class JobSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, required=False)
    tasks = TaskSerializer(many=True, required=False)
    delete = DeleteSerializer(required=False)

    class Meta:
        model = Job
        fields = ['name', 'description', 'groups', 'tasks', 'delete']

    def update(self, job, validated_data):

        DeleteSerializer(data=validated_data.pop('delete', {})).perform()

        serializer = GroupSerializer(job, data=validated_data, partial=True)
        serializer.is_valid(raise_exception=True)
        self._data = serializer.save()

        return self._data
