from django.test import SimpleTestCase


class BaseTestCase(SimpleTestCase):

    @property
    def live_server_url(self):
        return 'http://%s:%s' % (
            self.server.host, self.server.port)

    def send_keys(self, keys):
        self.driver.switch_to.active_element.send_keys(keys)

    def do_login(self, username='test@systori.com', password='pass'):
        self.driver.find_element_by_id('input_username').send_keys(username)
        self.driver.find_element_by_id('input_password').send_keys(password)
        self.driver.find_element_by_tag_name('button').click()

    def setUp(self):
        self.driver.get(self.live_server_url+'/logout')
