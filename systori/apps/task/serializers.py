from collections import OrderedDict


from django.db import models

from rest_framework import serializers
from rest_framework.fields import SkipField

from rest_framework.generics import get_object_or_404
from rest_framework.relations import PKOnlyObject

from rest_framework_recursive.fields import RecursiveField

from .models import Group, Job, LineItem, Task


class LineItemSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False)
    job = serializers.IntegerField(required=False, source="job.pk", read_only=True)
    task = serializers.IntegerField(required=False, source="task.pk", read_only=True)

    class Meta:
        model = LineItem
        fields = [
            "pk",
            "token",
            "name",
            "order",
            "qty",
            "qty_equation",
            "unit",
            "price",
            "price_equation",
            "total",
            "total_equation",
            "is_hidden",
            "lineitem_type",
            "task",
            "job",
        ]

    def create(self, validated_data):
        lineitem, _ = LineItem.objects.update_or_create(
            validated_data,
            job=validated_data["task"].job,
            token=validated_data["token"],
        )
        return self.update(lineitem, {})

    def update(self, lineitem, validated_data):
        if validated_data:
            super().update(lineitem, validated_data)

        # This forcefully sets the json returned by this, but we use [to_representation]
        # self._data = {"pk": lineitem.pk, "token": lineitem.token}
        return self.to_representation(lineitem)


class TaskSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False)
    lineitems = LineItemSerializer(many=True)
    job = serializers.IntegerField(required=False, source="job.pk", read_only=True)
    group = serializers.IntegerField(required=False, source="group.pk", read_only=True)

    class Meta:
        model = Task
        fields = [
            "pk",
            "token",
            "name",
            "description",
            "order",
            "qty",
            "qty_equation",
            "unit",
            "price",
            "price_equation",
            "total",
            "total_equation",
            "variant_group",
            "variant_serial",
            "is_provisional",
            # "status",
            "job",
            "group",
            "lineitems",
        ]

    def create(self, validated_data):
        lineitems = validated_data.pop("lineitems", [])
        task, _ = Task.objects.update_or_create(
            validated_data,
            job=validated_data["group"].job,
            token=validated_data["token"],
        )
        return self.update(task, {"lineitems": lineitems})

    def update(self, task, validated_data):
        lineitems = validated_data.pop("lineitems", [])

        if validated_data:
            super().update(task, validated_data)

        data = {"pk": task.pk, "token": task.token}

        for lineitem in lineitems:
            if "lineitems" not in data:
                data["lineitems"] = []
            pk, instance = lineitem.pop("pk", None), None
            if pk:
                instance = get_object_or_404(LineItem.objects.all(), id=pk)
            serializer = LineItemSerializer(
                instance=instance, data=lineitem, partial=True
            )
            serializer.is_valid(raise_exception=True)
            data["lineitems"].append(serializer.save(task=task))

        # This forcefully sets the json returned by this to [data], but we use [to_representation]
        # self._data = data

        return self.to_representation(task)


class GroupSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False)
    job = serializers.IntegerField(
        required=False, source="job.pk", allow_null=True, read_only=True
    )
    parent = serializers.IntegerField(
        required=False, source="parent.pk", allow_null=True, read_only=True
    )
    groups = serializers.ListField(child=RecursiveField(), required=False)
    tasks = TaskSerializer(many=True, required=False)

    class Meta:
        model = Group
        fields = [
            "pk",
            "token",
            "name",
            "description",
            "order",
            "groups",
            "tasks",
            "parent",
            "job",
        ]

    def to_representation(self, instance):
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            # We skip `to_representation` for `None` values so that fields do
            # not have to explicitly deal with that case.
            #
            # For related fields with `use_pk_only_optimization` we need to
            # resolve the pk value.
            check_for_none = (
                attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            )
            if check_for_none is None:
                ret[field.field_name] = None
            elif field.field_name == "groups":
                # If it's a single object
                if isinstance(attribute, Group):
                    ret[field.field_name] = [self.to_representation(attribute)]
                # If it's already iterable (e.g. result from a QuerySet)
                elif hasattr(attribute, "__iter__"):
                    ret[field.field_name] = [
                        self.to_representation(item) for item in attribute
                    ]
                # If it's a manager or QuerySet
                elif isinstance(attribute, models.Manager) or isinstance(
                    attribute, models.QuerySet
                ):
                    ret[field.field_name] = [
                        self.to_representation(item) for item in attribute.all()
                    ]
                # If it can be made iterable (RelatedManager)
                elif hasattr(attribute, "all"):
                    iterator = attribute.all()
                    if not hasattr(iterator, "__iter__"):
                        raise Exception(f"Expected an iterator, got ${iterator}")
                    ret[field.field_name] = [
                        self.to_representation(item) for item in iterator
                    ]
                else:
                    raise Exception(f"Invalid groups value: ${attribute}")
            elif field.field_name == "tasks":
                ret[field.field_name] = field.to_representation(attribute.all())
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret

    def create(self, validated_data):
        tasks = validated_data.pop("tasks", [])
        groups = validated_data.pop("groups", [])
        group, _ = Group.objects.update_or_create(
            validated_data,
            job=validated_data["parent"].job,
            token=validated_data["token"],
        )
        return self.update(group, {"tasks": tasks, "groups": groups})

    def update(self, group, validated_data):
        tasks = validated_data.pop("tasks", [])
        groups = validated_data.pop("groups", [])

        if validated_data:
            super().update(group, validated_data)

        data = {"pk": group.pk, "token": group.token}

        for task in tasks:
            if "tasks" not in data:
                data["tasks"] = []
            pk, instance = task.pop("pk", None), None
            if pk:
                instance = get_object_or_404(Task.objects.all(), id=pk)
            serializer = TaskSerializer(instance=instance, data=task, partial=True)
            serializer.is_valid(raise_exception=True)
            data["tasks"].append(serializer.save(group=group))

        for subgroup in groups:
            if "groups" not in data:
                data["groups"] = []
            pk, instance = subgroup.pop("pk", None), None
            if pk:
                instance = get_object_or_404(Group.objects.all(), id=pk)
            serializer = GroupSerializer(instance=instance, data=subgroup, partial=True)
            serializer.is_valid(raise_exception=True)
            data["groups"].append(serializer.save(parent=group))

        # This forcefully sets the json returned by this to [data], but we use [to_representation]
        # self._data = data

        return self.to_representation(group)


class DeleteSerializer(serializers.Serializer):
    groups = serializers.ListField(child=serializers.IntegerField(), required=False)
    tasks = serializers.ListField(child=serializers.IntegerField(), required=False)
    lineitems = serializers.ListField(child=serializers.IntegerField(), required=False)

    def perform(self):

        groups = self.initial_data.pop("groups", [])
        if groups:
            Group.objects.filter(pk__in=groups).delete()

        tasks = self.initial_data.pop("tasks", [])
        if tasks:
            Task.objects.filter(pk__in=tasks).delete()

        lineitems = self.initial_data.pop("lineitems", [])
        if lineitems:
            LineItem.objects.filter(pk__in=lineitems).delete()


class JobSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(required=False, many=True)
    tasks = TaskSerializer(required=False, many=True)
    delete = DeleteSerializer(required=False)
    order = serializers.IntegerField(required=False)

    class Meta:
        model = Job
        fields = ["pk", "name", "description", "groups", "tasks", "order", "delete"]

    def update(self, job, validated_data):

        DeleteSerializer(data=validated_data.pop("delete", {})).perform()

        # This is requried because, nested fields [groups] and [tasks] need to be updated as well
        # The process is same as that of [GroupSerializer.update]
        # Downside of this is that the returned json for [job] would conform to whatever
        # [GroupSerialzier.to_representation] produces
        # This currently produces additional "token", "parent" & "job" fields
        # The web editor does expect "token" field, which is not included in JobSerializer
        serializer = GroupSerializer(job, data=validated_data, partial=True)
        serializer.is_valid(raise_exception=True)
        self._data = serializer.save()

        return self._data

    def to_representation(self, instance):
        return {
            "pk": instance.pk,
            "name": instance.name,
            "description": instance.description,
            "groups": [
                GroupSerializer(instance=group).data for group in instance.groups.all()
            ],
            "tasks": [
                TaskSerializer(instance=task).data for task in instance.tasks.all()
            ],
            "order": instance.order,
            "delete": {},
        }
