"""
Serializers for apis used by flutter client
"""

from collections import OrderedDict
from decimal import Decimal


from django.db import models

from drf_yasg.inspectors import FieldInspector

from rest_framework import serializers
from rest_framework.fields import SkipField

from rest_framework.generics import get_object_or_404
from rest_framework.relations import PKOnlyObject

from rest_framework_recursive.fields import RecursiveField

from systori.apps.main import swagger_field_inspectors

from .models import Group, Job, LineItem, Task


# We want to do a deep merge instead of overriding field schema
# See: https://github.com/axnsan12/drf-yasg/issues/291
FieldInspector.add_manual_fields = swagger_field_inspectors.add_manual_fields


class LineItemSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False)
    token = serializers.IntegerField(
        required=False,
        help_text="This should be unique among all lineitems in a job, "
        "This is used to identify and correctly update lineitems sent by client "
        "that may not already have a pk",
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

    def validate(self, data):
        for field in ["qty", "price", "total"]:
            if not field in data or not data[field]:
                raise serializers.ValidationError({field: "This field is required"})
            decimal = Decimal(data[field])
            if decimal.is_nan():
                raise serializers.ValidationError({field: "Invalid decimal value"})

        qty = Decimal(data["qty"])
        has_percent = "unit" in data and "%" in data["unit"]

        if has_percent and not qty.is_zero():
            qty = qty / Decimal("100.00")

        total = Decimal(data["total"])
        price = Decimal(data["price"])
        if total != qty * price:
            raise serializers.ValidationError(
                {"total": "Total is not equal to qty*price"}
            )

        has_pk = self.instance or data.get("pk", False)
        has_token = data.get("token", False)

        if has_token and not has_pk:
            token = self.fields["token"].to_internal_value(data["token"])
            is_dup_token = LineItem.objects.filter(token=token).count() > 0
            if is_dup_token:
                raise serializers.ValidationError(
                    {"token": "Token already assigned to another lineitem"}
                )

        if not (has_pk or has_token):
            raise serializers.ValidationError(
                {
                    "pk": "`pk` is required for updating lineitem",
                    "token": "`token` is required for creating lineitem",
                }
            )

        return data

    def create(self, validated_data):
        lineitem, _ = LineItem.objects.update_or_create(
            validated_data,
            job=validated_data["task"].job,
            token=validated_data["token"],
        )

        return lineitem

    def update(self, lineitem, validated_data):
        # Do not update token
        validated_data.pop("token")
        return super().update(lineitem, validated_data)


class TaskSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(required=False, read_only=True)
    lineitems = LineItemSerializer(many=True, required=True)
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

    def validate(self, data):
        for field in ["qty", "price", "total"]:
            if not field in data:
                raise serializers.ValidationError({field: "This field is required"})
            # qty can be empty in case of t&m tasks
            if not data[field] and field != "qty":
                raise serializers.ValidationError({field: "Invalid value"})
            decimal = Decimal(data[field])
            if decimal.is_nan():
                raise serializers.ValidationError({field: "Invalid decimal value"})

        qty = Decimal(data["qty"]) if data["qty"] else None
        total = Decimal(data["total"])
        price = Decimal(data["price"])

        has_percent = "unit" in data and "%" in data["unit"]

        if has_percent and qty and not qty.is_zero():
            qty = qty / Decimal("100.00")

        if qty and total != qty * price:
            raise serializers.ValidationError(
                {"total": "Total is not equal to qty*price"}
            )

        if not qty and total != price:
            raise serializers.ValidationError(
                {"total": "Total is not equal to price for t&m task"}
            )

        # Validate that all lineitems have unique tokens
        # UniqueValidator only checks if the token in a lineitem exists in db only once or it does not exist at all
        # if it exists, then it is an update request.
        # But if multiple lineitems are to be created, they all must have unique tokens

        li_tokens = []
        for i in data["lineitems"]:
            has_token = i.get("token", False)
            has_pk = i.get("pk", False)
            if not (has_pk or has_token):
                raise serializers.ValidationError(
                    {"lineitems": "All lineitems must have a token"}
                )
            if has_token:
                li_tokens.append(i["token"])

        if len(set(li_tokens)) != len(li_tokens):
            raise serializers.ValidationError(
                {"lineitems": "Multiple lineitems have same token"}
            )

        # Valid tasks have their price equal to the total of all lineitems
        lineitems_total = Decimal()
        for lineitem in data["lineitems"]:
            lineitems_total += Decimal(lineitem["total"])

        if price != lineitems_total:
            raise serializers.ValidationError(
                {"price": "Task price does not match lineitems total"}
            )
        return data

    def create(self, validated_data):
        lineitems = validated_data.pop("lineitems", [])
        parent = validated_data.pop("group")

        for i in lineitems:
            has_pk = i.get("pk", False)
            if has_pk:
                raise serializers.ValidationError(
                    "Cannot create task with lineitem with a predefined pk, try updating instead"
                )

        if "pk" in validated_data:
            pk = validated_data.pop("pk")
            if pk:
                raise serializers.ValidationError(
                    "Cannot create task with a predefined pk, try updating instead"
                )
        task = Task.objects.create(**validated_data, job=parent.job, group=parent)

        return self.update(task, {"lineitems": lineitems})

    def update(self, task, validated_data):
        lineitems = validated_data.pop("lineitems", [])

        # First we update the lineitems, if there are any lineitems
        # They should have already been validated at this point, since lineitem serializer runs before task serializer
        # The only thing that could fail is if an invalid pk was supplied

        # List of validated lineitem serializers
        li_serializers = []
        for lineitem in lineitems:
            pk, instance = lineitem.pop("pk", None), None
            if pk:
                instance = get_object_or_404(
                    LineItem.objects, id=pk, task=task, job=task.job
                )

            serializer = LineItemSerializer(
                instance=instance, data=lineitem, partial=True
            )
            serializer.is_valid(raise_exception=True)
            li_serializers.append(serializer)

        # At this point all lineitems are safe to be created/updated
        for serializer in li_serializers:
            serializer.save(task=task, job=task.job)

        # If lineitems successfully updated, update the task
        if validated_data:
            super().update(task, validated_data)

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
                raise serializers.ValidationError(
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


class CloneHeirarchySerializer(serializers.Serializer):
    source = serializers.IntegerField(
        required=True, help_text="PK of the model that should be cloned"
    )
    target = serializers.IntegerField(
        required=True, help_text="PK of the model where [source] should be cloned to"
    )
    position = serializers.IntegerField(
        required=True, help_text="Position where [source] shoulb be cloned to"
    )

    class Meta:
        ref_name = "CloneHeirarchy"
        fields = ["source", "target", "position"]


class GroupSearchSerializer(serializers.Serializer):
    terms = serializers.CharField(required=True, help_text="Terms to search groups for")
    remaining_depth = serializers.IntegerField(
        required=True,
        help_text="Only groups that are valid for the remaining depth will be returned",
    )

    class Meta:
        ref_name = "GroupSearch"
        fields = ["terms", "remaining_depth"]


class GroupSearchResultSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField(help_text="Number of tasks in this group")
    groups = serializers.SerializerMethodField(
        help_text="Number of groups in this group"
    )

    class Meta:
        ref_name = "GroupSearchResult"
        model = Group
        fields = ["pk", "name", "description", "groups", "tasks"]

    def get_tasks(self, group) -> int:
        if group and group.pk:
            return group.tasks.count()
        return 0

    def get_groups(self, group) -> int:
        if group and group.pk:
            return group.groups.count()
        return 0


class TaskSearchSerializer(serializers.Serializer):
    terms = serializers.CharField(required=True, help_text="Terms to search tasks for")

    class Meta:
        ref_name = "TaskSearch"
        fields = ["terms"]


class TaskSearchResultSerializer(serializers.ModelSerializer):
    lineitems = serializers.SerializerMethodField(
        help_text="Number of lineitems in this task"
    )

    class Meta:
        ref_name = "TaskSearchResult"
        model = Task
        fields = ["pk", "name", "description", "total", "lineitems"]

    def get_lineitems(self, task) -> int:
        if task and task.pk:
            return task.lineitems.count()
        return 0
