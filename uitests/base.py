from django.test import SimpleTestCase
from selenium.webdriver.support.select import Select


class BaseTestCase(SimpleTestCase):
    def setUp(self):
        self.do_logout()
        self.do_login()

    def do_logout(self):
        self.driver.get(self.live_server_url + "/logout")

    def do_login(self, username="test@systori.com", password="pass"):
        self.find_id("input_username").send_keys(username)
        self.find_id("input_password").send_keys(password)
        self.find_tag("button").click()

    @property
    def live_server_url(self):
        return "http://%s:%s" % (self.server.host, self.server.port)

    def clear(self):
        self.driver.switch_to.active_element.clear()

    def send_keys(self, keys):
        self.driver.switch_to.active_element.send_keys(keys)

    def find_id(self, element_id):
        return self.driver.find_element_by_id(element_id)

    def find_tag(self, tag_name):
        return self.driver.find_element_by_tag_name(tag_name)

    def find_name(self, element_name):
        return self.driver.find_element_by_name(element_name)

    def find_named_select(self, select_name):
        return Select(self.find_name(select_name))

    def find_class(self, class_name):
        return self.driver.find_element_by_class_name(class_name)

    def find_link(self, link_text):
        return self.driver.find_element_by_link_text(link_text)

    def find_button(self, button_text):
        return self.find_xpath(
            '//button[normalize-space(text())="' + button_text + '"]'
        )

    def find_xpath(self, xpath):
        return self.driver.find_element_by_xpath(xpath)
