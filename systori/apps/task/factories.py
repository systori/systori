import factory
from factory import fuzzy
from .models import Job, Group, Task, LineItem


class JobFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Job

    name = fuzzy.FuzzyText(length=15)

    @factory.post_generation
    def generate_groups(self: Job, create, extracted, **kwargs):
        if create and extracted:
            parent = self
            next_depth = 1
            while self.project.structure.is_valid_depth(next_depth):
                parent = GroupFactory(parent=parent, depth=next_depth)
                next_depth += 1


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = fuzzy.FuzzyText(length=15)


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    name = fuzzy.FuzzyText(length=15)


class LineItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LineItem

    name = fuzzy.FuzzyText(length=15)
