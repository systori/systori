import time
from decimal import Decimal
from selenium.webdriver.common.keys import Keys
from uitests.base import BaseTestCase


class LoginTests(BaseTestCase):

    def test_login(self):
        self.do_login()
        body = self.driver.find_element_by_xpath('//body')
        assert 'Pinnwand' in body.text


class ProjectTests(BaseTestCase):

    def setUp(self):
        super(ProjectTests, self).setUp()
        self.do_login()

    def test_project_create_and_edit_job(self):
        self.driver.get(self.live_server_url+'/create-project')
        self.driver.find_element_by_name('name').send_keys("Test Project")
        self.driver.find_element_by_name('address').send_keys("Pettenkoferstr. 10")
        self.driver.find_element_by_name('city').send_keys("Mannheim")
        self.driver.find_element_by_name('postal_code').send_keys("68169")
        self.driver.find_element_by_name('save_goto_project').click()

        # open first job
        self.driver.find_element_by_xpath('//tbody[@id="job-table"]//a').click()

        # click on task group name field
        self.driver.find_element_by_xpath('//ubr-taskgroup[1]//div[@class="name"][1]').click()

        # edit task group
        self.send_keys("Task Group 1" + Keys.TAB)
        self.send_keys("Group one description." + Keys.SHIFT + Keys.ENTER)

        time.sleep(1)  # give it a second to catchup

        # edit task
        self.send_keys("Task 1" + Keys.TAB)
        self.send_keys("2,5" + Keys.TAB)
        self.send_keys("stk" + Keys.TAB)
        self.send_keys("task description" + Keys.SHIFT + Keys.ENTER)

        time.sleep(2)  # give it two seconds to catchup

        # edit line item
        self.send_keys("Line Item 1" + Keys.TAB)
        self.send_keys("20,0" + Keys.TAB)
        self.send_keys("m" + Keys.TAB)
        self.send_keys("7,50" + Keys.SHIFT + Keys.ENTER)

        time.sleep(1)  # give it a second to catchup

        # check that the editor has calculated the total correctly
        total = self.driver.find_element_by_xpath('//ubr-taskgroup[1]//div[@class="total"][1]').text
        total_cleaned = total.replace(',', '_').replace('.', ',').replace('_', '.')
        self.assertEqual(Decimal(375), Decimal(total_cleaned))

        self.driver.back()
        self.driver.refresh()

        # editor total should be the same as the dashboard total (sans currency symbol)
        job_total = self.driver.find_element_by_xpath('//tbody[@id="job-table"]//td[4]').text
        self.assertEqual(total, job_total.strip()[:-2])
