"""
Serializers for apis used by flutter client
"""

from collections import OrderedDict


from django.db import models

from drf_yasg.inspectors import FieldInspector

from rest_framework import serializers
from rest_framework.fields import SkipField

from rest_framework.generics import get_object_or_404
from rest_framework.relations import PKOnlyObject
from rest_framework.validators import UniqueValidator

from rest_framework_recursive.fields import RecursiveField

from systori.apps.main import swagger_field_inspectors

from .models import Group, Job, LineItem, Task


# We want to do a deep merge instead of overriding field schema
# See: https://github.com/axnsan12/drf-yasg/issues/291
FieldInspector.add_manual_fields = swagger_field_inspectors.add_manual_fields


class LineItemSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False)
    token = serializers.IntegerField(
        required=True,
        help_text="This should be unique among all lineitems in a job, "
        "This is used to identify and correctly update lineitems sent by client "
        "that may not already have a pk",
        validators=[
            UniqueValidator(
                queryset=LineItem.objects.all(),
                message="Token already assigned to another lineitem",
            )
        ],
    )

    class Meta:
        ref_name = "LineItem"
        swagger_schema_fields = {
            "properties": {
                "qty": {"x-precision": 3},
                "price": {"x-precision": 2},
                "total": {"x-precision": 2},
            }
        }
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
        ]


class TaskSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=True)
    lineitems = LineItemSerializer(many=True)
    parent = serializers.IntegerField(
        required=False,
        source="group.pk",
        help_text="This can be a group or job pk",
        read_only=True,
    )

    class Meta:
        ref_name = "Task"
        swagger_schema_fields = {
            "properties": {
                "qty": {"x-precision": 3},
                "price": {"x-precision": 2},
                "total": {"x-precision": 2},
            }
        }
        model = Task
        fields = [
            "pk",
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
            "parent",
            "lineitems",
        ]

    def create(self, validated_data):
        lineitems = validated_data.pop("lineitems", [])
        parent = validated_data.pop("group")

        if "pk" in validated_data:
            pk = validated_data.pop("pk")
            if pk:
                raise Exception(
                    "Cannot create task with a predefined pk, try updating instead"
                )

        task = Task.objects.create(**validated_data, job=parent.job, group=parent)

        return self.update(task, {"lineitems": lineitems})

    def update(self, task, validated_data):
        lineitems = validated_data.pop("lineitems", [])

        if validated_data:
            super().update(task, validated_data)

        for lineitem in lineitems:

            pk, instance = lineitem.pop("pk", None), None
            if pk:
                instance = get_object_or_404(LineItem.objects.all(), id=pk)
            serializer = LineItemSerializer(
                instance=instance, data=lineitem, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(task=task)

        return task


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
        ref_name = "Group"
        model = Group
        fields = [
            "pk",
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

        parent = validated_data.pop("parent")

        if "pk" in validated_data:
            pk = validated_data.pop("pk")
            if pk:
                raise Exception(
                    "Cannot create group with a predefined pk, try updating instead"
                )

        if "job" in validated_data:
            validated_data.pop("job")

        job = parent.job

        group = Group.objects.create(**validated_data, job=job, parent=parent)
        return self.update(group, {"tasks": tasks, "groups": groups})

    def update(self, group, validated_data):
        tasks = validated_data.pop("tasks", [])
        groups = validated_data.pop("groups", [])

        if validated_data:
            super().update(group, validated_data)

        for task in tasks:
            pk, instance = task.pop("pk", None), None
            if pk:
                instance = get_object_or_404(Task.objects.all(), id=pk)
            serializer = TaskSerializer(instance=instance, data=task, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(group=group)

        for subgroup in groups:
            pk, instance = subgroup.pop("pk", None), None
            if pk:
                instance = get_object_or_404(Group.objects.all(), id=pk)
            serializer = GroupSerializer(instance=instance, data=subgroup, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(parent=group)

        return group


class JobSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(required=False, many=True)
    tasks = TaskSerializer(required=False, many=True)
    order = serializers.IntegerField(required=False)

    class Meta:
        ref_name = "Job"
        model = Job
        fields = ["pk", "name", "description", "groups", "tasks", "order"]

    def update(self, job, validated_data):

        serializer = GroupSerializer(job, data=validated_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return job

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
        }


class GroupSearchSerializer(serializers.Serializer):
    terms = serializers.CharField(required=True, help_text="Terms to search groups for")
    remaining_depth = serializers.IntegerField(
        required=True,
        help_text="Only groups that are valid for the remaining depth will be returned",
    )

    class Meta:
        ref_name = "GroupSearch"
        fields = ["terms", "remaining_depth"]


class TaskSearchSerializer(serializers.Serializer):
    terms = serializers.CharField(required=True, help_text="Terms to search tasks for")

    class Meta:
        ref_name = "TaskSearch"
        fields = ["terms"]
