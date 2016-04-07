from .models import Project
from ..task.test_api import ResourceTestCaseBase


class ProjectResourceTest(ResourceTestCaseBase):
    url = '/api/v1/project/'

    def test_get_projects(self):
        resp = self.client_get(self.url, data={})
        self.assertValidJSONResponse(resp)
        objects = self.deserialize(resp)['objects']
        self.assertEqual(len(objects), 2)
        object = objects[0]
        keys = object.keys()
        expected_keys = [
            'id', 'name', 'description', 'job_zfill', 'taskgroup_zfill', 'task_zfill', 'resource_uri',
            'state', 'phase'
        ]
        self.assertEqual(sorted(expected_keys), sorted(keys))

    def test_update_project(self):
        url = self.url + '{}/'.format(self.project.id)
        data = {"name": "updated proj", "description": "updated desc"}
        resp = self.client_put(url, data=data, format='json')
        self.assertHttpAccepted(resp)
        proj = Project.objects.get(pk=self.project.id)
        self.assertEqual("updated proj", proj.name)
        self.assertEqual("updated desc", proj.description)

    def test_create_project(self):
        data = {
            "name": "new proj",
            "description": "new desc"
        }
        resp = self.client_post(self.url, data=data, format='json')
        self.assertHttpCreated(resp)
        proj = Project.objects.order_by('id').last()
        self.assertEqual("new proj", proj.name)
        self.assertEqual("new desc", proj.description)
