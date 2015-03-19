from tastypie.test import ResourceTestCase
from .models import Project
from ..task.test_models import create_task_data


class ResourceTestCaseBase(ResourceTestCase):

    def setUp(self):
        super(ResourceTestCaseBase, self).setUp()
        create_task_data(self)
        self.api_client.client.login(username='lex', password='pass')


class ProjectResourceTest(ResourceTestCaseBase):

    url = '/api/v1/project/'

    def test_get_projects(self):
        resp = self.api_client.get(self.url, data={})
        self.assertValidJSONResponse(resp)
        objects = self.deserialize(resp)['objects']
        self.assertEqual(len(objects), 2)
        object = objects[0]
        keys = object.keys()
        expected_keys = [
            'id', 'name', 'description', 'job_zfill', 'taskgroup_zfill', 'task_zfill', 'job_offset', 'resource_uri',
            'address', 'city', 'country', 'postal_code', 'latitude', 'longitude'
        ]
        self.assertEqual(sorted(expected_keys), sorted(keys))

    def test_update_project(self):
        url = self.url+'{}/'.format(Project.objects.first().pk)
        data = {"name": "updated proj", "description": "updated desc"}
        resp = self.api_client.put(url, data=data, format='json')
        self.assertHttpAccepted(resp)
        proj = Project.objects.get(pk=self.project.id)
        self.assertEqual("updated proj", proj.name)
        self.assertEqual("updated desc", proj.description)

    def test_create_project(self):
        data = {
            "name": "new proj",
            "description": "new desc"
        }
        resp = self.api_client.post(self.url, data=data, format='json')
        self.assertHttpCreated(resp)
        proj = Project.objects.order_by('id').last()
        self.assertEqual("new proj", proj.name)
        self.assertEqual("new desc", proj.description)

