from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from .models import Job, TaskGroup, Task, TaskInstance, LineItem
from .test_models import create_task_data


class ResourceTestCaseBase(ResourceTestCaseMixin, TestCase):
    def setUp(self):
        super(ResourceTestCaseBase, self).setUp()
        create_task_data(self)
        self.api_client.client.login(username=self.user.email, password='open sesame')


class JobOrderResourceTest(ResourceTestCaseBase):
    url = '/api/v1/job/'

    def test_get_jobs(self):
        resp = self.api_client.get(self.url, data={})
        self.assertValidJSONResponse(resp)
        objects = self.deserialize(resp)['objects']
        self.assertEqual(len(objects), 2)
        object = objects[0]
        keys = object.keys()
        expected_keys = [
            'id', 'job_code', 'name', 'description', 'project', 'billing_method', 'status', 'taskgroup_offset',
            'resource_uri', 'is_revenue_recognized'
        ]
        self.assertEqual(sorted(expected_keys), sorted(keys))

    def test_update_job(self):
        url = self.url + '{}/'.format(Job.objects.first().pk)
        data = {"name": "updated job", "description": "updated desc"}
        resp = self.api_client.put(url, data=data, format='json')
        self.assertHttpAccepted(resp)
        job = Job.objects.get(pk=self.job.id)
        self.assertEqual("updated job", job.name)
        self.assertEqual("updated desc", job.description)

    def test_create_job(self):
        data = {
            "project": "/api/v1/project/{}/".format(self.project.id),
            "name": "new job",
            "description": "new desc",
            "job_code": 99
        }
        resp = self.api_client.post(self.url, data=data, format='json')
        self.assertHttpCreated(resp)
        job = Job.objects.order_by('id').last()
        self.assertEqual("new job", job.name)
        self.assertEqual("new desc", job.description)


class TaskGroupResourceTest(ResourceTestCaseBase):
    url = '/api/v1/taskgroup/'

    def test_update_task_group(self):
        url = self.url + '{}/'.format(self.group.id)
        data = {"name": "new name"}
        resp = self.api_client.put(url, data=data, format='json')
        self.assertHttpAccepted(resp)
        group = TaskGroup.objects.get(pk=self.group.id)
        self.assertEqual("new name", group.name)

    def test_create_task_group(self):
        data = {
            "job": "/api/v1/job/{}/".format(self.job.id),
            "name": "created group"
        }
        resp = self.api_client.post(self.url, data=data, format='json')
        self.assertHttpCreated(resp)
        group = TaskGroup.objects.last()
        self.assertEqual("created group", group.name)
        self.assertEqual(self.job.id, group.job.id)

    def test_delete_task_group(self):
        start_count = TaskGroup.objects.count()
        url = self.url + '{}/'.format(self.group.id)
        resp = self.api_client.delete(url, format='json')
        self.assertHttpAccepted(resp)
        new_count = TaskGroup.objects.count()
        self.assertEqual(start_count - 1, new_count)

    def test_autocomplete_no_matches(self):
        url = self.url + 'autocomplete/'
        resp = self.api_client.get(url, data={"query": "green"}, format='json')
        self.assertHttpOK(resp)
        self.assertEqual(b'', resp.content.strip())

    def test_autocomplete_has_matches(self):
        url = self.url + 'autocomplete/'
        resp = self.api_client.get(url, data={"query": "group"}, format='json')
        self.assertHttpOK(resp)
        self.assertEqual(2, str(resp.content).count('group'))


class TaskResourceTest(ResourceTestCaseBase):
    url = '/api/v1/task/'

    def setUp(self):
        super(TaskResourceTest, self).setUp()
        self.task3 = Task.objects.create(name="my task three green", qty=0, taskgroup=self.group)
        self.task4 = Task.objects.create(name="my task four green", qty=0, taskgroup=self.group)

    def test_update_task(self):
        url = self.url + '{}/'.format(self.task.id)
        data = {"name": "new name"}
        resp = self.api_client.put(url, data=data, format='json')
        self.assertHttpAccepted(resp)
        task = Task.objects.get(pk=self.task.id)
        self.assertEqual("new name", task.name)

    def test_create_task(self):
        data = {
            "taskgroup": "/api/v1/taskgroup/{}/".format(self.group.id),
            "name": "created task",
            "qty": 5
        }
        resp = self.api_client.post(self.url, data=data, format='json')
        self.assertHttpCreated(resp)
        task = Task.objects.last()
        self.assertEqual("created task", task.name)
        self.assertEqual(self.group.id, task.taskgroup.id)
        self.assertEqual(5, task.qty)

    def test_delete_task(self):
        start_count = Task.objects.count()
        url = self.url + '{}/'.format(self.task.id)
        resp = self.api_client.delete(url, format='json')
        self.assertHttpAccepted(resp)
        new_count = Task.objects.count()
        self.assertEqual(start_count - 1, new_count)

    def test_clone_task(self):
        url = self.url + '{}/clone/'.format(self.task.id)
        data = {
            "target": "/api/v1/taskgroup/{}/".format(self.group.id),
            "pos": 1
        }
        self.assertEqual(2, Task.objects.filter(name=self.task.name).count())
        response = self.api_client.post(url, data=data, format='json')
        self.assertEqual(3, Task.objects.filter(name=self.task.name).count())
        new_task = Task.objects.get(taskgroup=self.group.id, order=1)
        self.assertContains(response, '<ubr-task data-pk="{0}">'.format(new_task.id), 1, 201)


class TaskInstanceResourceTest(ResourceTestCaseBase):
    url = '/api/v1/taskinstance/'

    def test_update_taskinstance(self):
        url = self.url + '{}/'.format(self.task.instance.id)
        data = {"name": "new name"}
        resp = self.api_client.put(url, data=data, format='json')
        self.assertHttpAccepted(resp)
        task = TaskInstance.objects.get(pk=self.task.instance.id)
        self.assertEqual("new name", task.name)

    def test_create_taskinstance(self):
        data = {
            "task": "/api/v1/task/{}/".format(self.task.id),
            "name": "created task instance"
        }
        resp = self.api_client.post(self.url, data=data, format='json')
        self.assertHttpCreated(resp)
        task = TaskInstance.objects.last()
        self.assertEqual("created task instance", task.name)
        self.assertEqual(self.task.id, task.task.id)

    def test_delete_taskinstance(self):
        start_count = TaskInstance.objects.count()
        url = self.url + '{}/'.format(self.task.instance.id)
        resp = self.api_client.delete(url, format='json')
        self.assertHttpAccepted(resp)
        new_count = TaskInstance.objects.count()
        self.assertEqual(start_count - 1, new_count)


class LineItemResourceTest(ResourceTestCaseBase):
    url = '/api/v1/lineitem/'

    def test_update_lineitem(self):
        url = self.url + '{}/'.format(self.lineitem.id)
        data = {"name": "new name"}
        resp = self.api_client.put(url, data=data, format='json')
        self.assertHttpAccepted(resp)
        lineitem = LineItem.objects.get(pk=self.lineitem.id)
        self.assertEqual("new name", lineitem.name)

    def test_create_lineitem(self):
        data = {
            "taskinstance": "/api/v1/taskinstance/{}/".format(self.task.instance.id),
            "name": "created line item",
            "unit_qty": "8",
            "price": "20"
        }
        resp = self.api_client.post(self.url, data=data, format='json')
        self.assertHttpCreated(resp)
        lineitem = LineItem.objects.last()
        self.assertEqual("created line item", lineitem.name)
        self.assertEqual(self.task.instance.id, lineitem.taskinstance.id)
        self.assertEqual(160, lineitem.price_per_task_unit)

    def test_delete_lineitem(self):
        start_count = LineItem.objects.count()
        url = self.url + '{}/'.format(self.lineitem.id)
        resp = self.api_client.delete(url, format='json')
        self.assertHttpAccepted(resp)
        new_count = LineItem.objects.count()
        self.assertEqual(start_count - 1, new_count)
