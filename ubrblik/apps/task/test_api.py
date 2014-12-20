from tastypie.test import ResourceTestCase
from .models import Job, TaskGroup, Task, LineItem
from .test_models import create_data


class ResourceTestCaseBase(ResourceTestCase):

    def setUp(self):
        super(ResourceTestCaseBase, self).setUp()
        create_data(self)
        self.api_client.client.login(username='lex', password='pass')


class JobOrderResourceTest(ResourceTestCaseBase):

    url = '/api/v1/job/'

    def test_get_jobs(self):
        resp = self.api_client.get(self.url, data={})
        self.assertValidJSONResponse(resp)
        objects = self.deserialize(resp)['objects']
        self.assertEqual(len(objects), 1)
        object = objects[0]
        keys = object.keys()
        expected_keys = [
            'id', 'name', 'description', 'order', 'project', 'resource_uri'
        ]
        self.assertEqual(sorted(expected_keys), sorted(keys))

    def test_update_job(self):
        url = self.url+'{}/'.format(Job.objects.first().pk)
        data = {"name": "updated job", "description": "updated desc"}
        resp = self.api_client.put(url, data=data, format='json')
        self.assertHttpAccepted(resp)
        job = Job.objects.get(pk=self.job.id)
        self.assertEqual("updated job", job.name)
        self.assertEqual("updated desc", job.description)

    def test_create_job(self):
        data = {
            "project": "/api/v1/project/{}/".format(self.proj.id),
            "name": "new job",
            "description": "new desc"
        }
        resp = self.api_client.post(self.url, data=data, format='json')
        self.assertHttpCreated(resp)
        job = Job.objects.last()
        self.assertEqual("new job", job.name)
        self.assertEqual("new desc", job.description)


class TaskGroupResourceTest(ResourceTestCaseBase):

    url = '/api/v1/taskgroup/'

    def test_update_task_group(self):
        url = self.url+'{}/'.format(self.group.id)
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
        url = self.url+'{}/'.format(self.group.id)
        resp = self.api_client.delete(url, format='json')
        self.assertHttpAccepted(resp)
        new_count = TaskGroup.objects.count()
        self.assertEqual(start_count-1, new_count)


class TaskResourceTest(ResourceTestCaseBase):

    url = '/api/v1/task/'

    def test_update_task(self):
        url = self.url+'{}/'.format(self.task.id)
        data = {"name": "new name"}
        resp = self.api_client.put(url, data=data, format='json')
        self.assertHttpAccepted(resp)
        task = Task.objects.get(pk=self.task.id)
        self.assertEqual("new name", task.name)

    def test_create_task(self):
        data = {
            "taskgroup": "/api/v1/taskgroup/{}/".format(self.group.id),
            "name": "created task"
        }
        resp = self.api_client.post(self.url, data=data, format='json')
        self.assertHttpCreated(resp)
        task = Task.objects.last()
        self.assertEqual("created task", task.name)
        self.assertEqual(self.group.id, task.taskgroup.id)

    def test_delete_task(self):
        start_count = Task.objects.count()
        url = self.url+'{}/'.format(self.task.id)
        resp = self.api_client.delete(url, format='json')
        self.assertHttpAccepted(resp)
        new_count = Task.objects.count()
        self.assertEqual(start_count-1, new_count)

class LineItemResourceTest(ResourceTestCaseBase):

    url = '/api/v1/lineitem/'

    def test_update_lineitem(self):
        url = self.url+'{}/'.format(self.lineitem.id)
        data = {"name": "new name"}
        resp = self.api_client.put(url, data=data, format='json')
        self.assertHttpAccepted(resp)
        lineitem = LineItem.objects.get(pk=self.task.id)
        self.assertEqual("new name", lineitem.name)

    def test_create_lineitem(self):
        data = {
            "task": "/api/v1/task/{}/".format(self.task.id),
            "name": "created line item",
            "qty": "8",
            "price": "20"
        }
        resp = self.api_client.post(self.url, data=data, format='json')
        self.assertHttpCreated(resp)
        lineitem = LineItem.objects.last()
        self.assertEqual("created line item", lineitem.name)
        self.assertEqual(self.task.id, lineitem.task.id)
        self.assertEqual(160, lineitem.total)

    def test_delete_lineitem(self):
        start_count = LineItem.objects.count()
        url = self.url+'{}/'.format(self.task.id)
        resp = self.api_client.delete(url, format='json')
        self.assertHttpAccepted(resp)
        new_count = LineItem.objects.count()
        self.assertEqual(start_count-1, new_count)