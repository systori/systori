import os
import django
django.setup()

from systori.apps.company.models import *
from systori.apps.project.factories import ProjectFactory
from systori.apps.task.factories import JobFactory, GroupFactory, TaskFactory, LineItemFactory

desc = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

Company.objects.get(schema="mehr-handwerk").activate()

project = ProjectFactory(name="Test Project", structure_format="1.01.01.01.001.0001")
job = JobFactory(name="Gated Community", project=project)

entrance_group = GroupFactory(name="Entrance", parent=job, description=desc)
security_group = GroupFactory(name="Security Checkpoint", parent=entrance_group, description=desc)
GroupFactory(name="Boom Gate", parent=GroupFactory(name='', parent=security_group), description=desc)
booth_group = GroupFactory(name="Booth", parent=GroupFactory(name='', parent=security_group), description=desc)
level_task = TaskFactory(name="Level Area", group=booth_group, qty=1, description=desc)
LineItemFactory(name="Remove brush", unit="hr", qty=8, price=12, task=level_task)
LineItemFactory(name="Level", unit="hr", qty=4, price=26, task=level_task)
LineItemFactory(name="Compact", unit="hr", qty=4, price=20, task=level_task)
concrete_task = TaskFactory(name="Pour Concrete Pad", group=booth_group, qty=1, description=desc)
LineItemFactory(name="Forms", unit="ft", qty=500, price=3, task=concrete_task)
LineItemFactory(name="Setup Forms", unit="hr", qty=8, price=20, task=concrete_task)
LineItemFactory(name="Concrete", unit="cu ft", qty=200, price=5, task=concrete_task)
LineItemFactory(name="risk", unit="%", qty=10, price_equation="C!:", price=2660, task=concrete_task)
LineItemFactory(name="Screed", unit="hr", qty=2, price=20, task=concrete_task)
LineItemFactory(name="Remove Forms", unit="hr", qty=4, price=20, task=concrete_task)
LineItemFactory(name="risk", qty=10, unit="%", price_equation="C!]&", price=120, task=concrete_task)
LineItemFactory(name="discount", qty=-10, unit="%", price_equation="C!:", price=3058, task=concrete_task)
booth_task = TaskFactory(name="Install Booth", group=booth_group, qty=1, description=desc)
LineItemFactory(name="Manufacturer suggested installation cost", unit="", qty=1, price=5000, task=booth_task, is_hidden=True)
LineItemFactory(name="Place ontop concrete pad", unit="hr", qty=2, price=50, task=booth_task)

housing_group = GroupFactory(name="Housing", parent=job)
site_group = GroupFactory(name="House Site #1", parent=housing_group)
house_group = GroupFactory(name="House", parent=site_group)
foundation_group = GroupFactory(name="Foundation", parent=house_group)
excavate_task = TaskFactory(name="Excavate", group=foundation_group, qty=1)
LineItemFactory(name="", unit="hr", qty=24, price=40, task=excavate_task)
foundation_task = TaskFactory(name="Walls", group=foundation_group, qty=1)
LineItemFactory(name="Forms", unit="ft", qty=500, price=3, task=foundation_task)
LineItemFactory(name="Setup Forms", unit="hr", qty=8, price=20, task=foundation_task)
LineItemFactory(name="Concrete", unit="cu ft", qty=200, price=5, task=foundation_task)
LineItemFactory(name="Remove Forms", unit="hr", qty=4, price=20, task=foundation_task)
GroupFactory(name="Walls", parent=house_group)
GroupFactory(name="Roof", parent=house_group)
GroupFactory(name="Landscaping", parent=site_group)
