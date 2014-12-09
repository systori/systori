from tastypie.test import ResourceTestCase
from .models import TaskGroup, Task
from .test_models import create_data


class ResourceTestCaseBase(ResourceTestCase):

    def setUp(self):
        super(ResourceTestCaseBase, self).setUp()
        create_data(self)
        self.api_client.client.login(username='lex', password='pass')


class TaskGroupResourceTest(ResourceTestCaseBase):

    url = '/api/v1/group/'

    def test_update_task_group(self):
        url = self.url+'{}/'.format(self.group.id)
        data = {"name": "new name"}
        resp = self.api_client.put(url, data=data, format='json')
        self.assertHttpAccepted(resp)
        group = TaskGroup.objects.get(pk=self.group.id)
        self.assertEqual("new name", group.name)

    def test_create_task_group(self):
        data = {
            "project": "/api/v1/project/{}/".format(self.proj.id),
            "name": "created group"
        }
        resp = self.api_client.post(self.url, data=data, format='json')
        self.assertHttpCreated(resp)
        group = TaskGroup.objects.last()
        self.assertEqual("created group", group.name)
        self.assertEqual(self.proj.id, group.project.id)

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
            "group": "/api/v1/group/{}/".format(self.group.id),
            "name": "created task"
        }
        resp = self.api_client.post(self.url, data=data, format='json')
        self.assertHttpCreated(resp)
        task = Task.objects.last()
        self.assertEqual("created task", task.name)
        self.assertEqual(self.group.id, task.group.id)