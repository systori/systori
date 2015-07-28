import time
from decimal import Decimal
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
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
        self.driver.find_element_by_xpath('//li[2]').click()
        self.driver.find_element_by_xpath('//p[1]/a').click()
        #self.driver.get(self.live_server_url+'/create-project')
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
        time.sleep(0.5)
        self.send_keys("20,0" + Keys.TAB)
        time.sleep(0.5)
        self.send_keys("m" + Keys.TAB)
        time.sleep(0.5)
        self.send_keys("7,50" + Keys.SHIFT + Keys.ENTER)

        time.sleep(1.5)

        self.send_keys("Line Item 2" + Keys.TAB)
        time.sleep(0.5)
        self.send_keys("10,0" + Keys.TAB)
        time.sleep(0.5)
        self.send_keys("kg" + Keys.TAB)
        time.sleep(0.5)
        self.send_keys("15" + Keys.SHIFT + Keys.ENTER)

        time.sleep(1)  # give it a second to catchup

        for i in range(3):
            self.send_keys(Keys.SHIFT + Keys.ENTER)
            time.sleep(0.5)

        # edit task group
        self.send_keys("Task Group 2" + Keys.TAB)
        self.send_keys("Group one description." + Keys.SHIFT + Keys.ENTER)

        time.sleep(1)  # give it a second to catchup

        # edit task
        self.send_keys("Task 2" + Keys.TAB)
        self.send_keys("1" + Keys.TAB)
        self.send_keys("m²" + Keys.TAB)
        self.send_keys("task description" + Keys.SHIFT + Keys.ENTER)

        time.sleep(1)  # give it two seconds to catchup

        # edit line item
        self.send_keys("Line Item 1" + Keys.TAB)
        time.sleep(0.5)
        self.send_keys("20,0" + Keys.TAB)
        time.sleep(0.5)
        self.send_keys("m" + Keys.TAB)
        time.sleep(0.5)
        self.send_keys("7,50" + Keys.SHIFT + Keys.ENTER)

        time.sleep(1)

        self.send_keys("Line Item 2" + Keys.TAB)
        time.sleep(0.5)
        self.send_keys("10,0" + Keys.TAB)
        time.sleep(0.5)
        self.send_keys("m³" + Keys.TAB)
        time.sleep(0.5)
        self.send_keys("10" + Keys.SHIFT + Keys.ENTER)

        time.sleep(2)

        # check that the editor has calculated the total correctly
        total = self.driver.find_element_by_xpath('//ubr-taskgroup[1]//div[@class="total"][1]').text
        total_cleaned = total.replace(',', '_').replace('.', ',').replace('_', '.')
        self.assertEqual(Decimal(750), Decimal(total_cleaned))

        time.sleep(0.5)
        # click on project link to get to detail page
        self.driver.find_element_by_xpath('//li[4]').click()
        time.sleep(0.5)
        self.driver.find_element_by_xpath('//li[3]').click()
        self.driver.refresh()
        time.sleep(1)

        # editor total should be the same as the dashboard total (sans currency symbol)
        job_total = self.driver.find_element_by_xpath('//tbody[@id="job-table"]//td[3]').text
        self.assertEqual(total, job_total.strip()[:-2])

        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/a[2]').click()
        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/a').click()
        self.driver.find_element_by_xpath('//*[@id="id_is_billable"]').click()
        self.driver.find_element_by_xpath('//*[@id="id_business"]').send_keys("Company")
        self.driver.find_element_by_xpath('//*[@id="id_salutation"]').send_keys("Mr.")
        self.driver.find_element_by_xpath('//*[@id="id_first_name"]').send_keys("Max")
        self.driver.find_element_by_xpath('//*[@id="id_last_name"]').send_keys("Mustermann")
        self.driver.find_element_by_xpath('//*[@id="id_phone"]').send_keys("0123 456789")
        self.driver.find_element_by_xpath('//*[@id="id_email"]').send_keys("max.mustermann@trash-mail.com")
        self.driver.find_element_by_xpath('//*[@id="id_website"]').send_keys("http://www.mustermann.de")
        self.driver.find_element_by_xpath('//*[@id="id_address"]').send_keys("Eintrachtstraße 24")
        self.driver.find_element_by_xpath('//*[@id="id_postal_code"]').send_keys("68169")
        self.driver.find_element_by_xpath('//*[@id="id_city"]').send_keys("Mannheim")
        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/form/div[14]/div/textarea').send_keys("This is a Note on a Contact")

        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/form/div[15]/button').click()

        time.sleep(0.5)
        self.assertEqual('Max Mustermann',
                         self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[4]/tbody/tr/td[2]/a').text)
        self.assertEqual('Ja',
                         self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[4]/tbody/tr/td[4]').text)

        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/a[2]').click()
        time.sleep(0.5)

        self.driver.find_element_by_xpath('//*[@id="id_document_date"]').send_keys('07/23/2015')
        self.driver.find_element_by_xpath('//*[@id="id_header"]').send_keys('Dear Sir or Madam,\n this is a Test:')
        self.driver.find_element_by_xpath('//*[@id="id_footer"]').send_keys('We hope you pay us for something.')
        jobs = Select(self.driver.find_element_by_xpath('//*[@id="id_jobs"]'))
        jobs.select_by_visible_text('Default')
        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/form/div[8]/button').click()
        time.sleep(1)

        self.assertEqual('750,00 €',
                         self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[2]/tbody/tr/td[4]').text)

        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[2]/tbody/tr/td[7]/div/button[2]').click()
        #self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[2]/tbody/tr/td[7]/div/ul/li[1]/a').click()

        self.assertEqual('Neu',
                         self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[2]/tbody/tr/td[2]').text)
        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[2]/tbody/tr/td[8]/a[1]').click()
        self.assertEqual('Gesendet',
                         self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[2]/tbody/tr/td[2]').text)
        #self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[2]/tbody/tr/td[8]/a[1]').click()
        #self.assertEqual('Beauftragt',
        #                 self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[2]/tbody/tr/td[2]').text)
        time.sleep(0.5)

        self.driver.get(self.live_server_url+'/field/project-2')
        self.driver.find_element_by_xpath('/html/body/div/div[3]/a[2]').click()
        self.driver.find_element_by_xpath('/html/body/form/div/div[2]/div[2]/label[1]/input').click()
        self.driver.find_element_by_xpath('/html/body/form/div/div[2]/div[3]/div/button').click()
        self.driver.find_element_by_xpath('/html/body/div/div[2]/ul/a').click()
        self.driver.find_element_by_xpath('/html/body/div/div[2]/div[3]/div/a').click()
        self.driver.find_element_by_xpath('/html/body/div/div[2]/ul/a').click()
        self.driver.find_element_by_xpath('/html/body/div/form/div/div[2]/div[1]/input').send_keys("2.5")
        self.driver.find_element_by_xpath('/html/body/div/form/div/div[2]/textarea').send_keys("Some Report billable_amount")
        self.driver.find_element_by_xpath('/html/body/div/form/div/div[3]/div/input[2]').click()
        self.driver.find_element_by_xpath('/html/body/div/div[1]/div[1]/a').click()
        self.driver.find_element_by_xpath('/html/body/div/div[1]/div/div/div[1]/div[1]/a').click()
        self.driver.get(self.live_server_url+'/project-2')
        time.sleep(0.5)

        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[3]/tbody/tr[2]/td[1]/a[1]').click()
        self.driver.find_element_by_xpath('//*[@id="id_document_date"]').send_keys('07/27/2015')
        self.driver.find_element_by_xpath('//*[@id="id_invoice_no"]').send_keys('1234/04|ä@1"2!')
        self.driver.find_element_by_xpath('//*[@id="id_header"]').send_keys('So much, very much Money.')
        self.driver.find_element_by_xpath('//*[@id="id_footer"]').send_keys('So much, very much Money.')
        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/form/div[10]/button').click()

        invoice_total = self.driver.find_element_by_class_name('add-total-amount').text[:-2]
        invoice_total_cleaned = invoice_total.replace(',', '_').replace('.', ',').replace('_', '.')
        self.assertEqual(float(invoice_total_cleaned), float(total_cleaned)*1.19)
        time.sleep(0.5)

        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[3]/tbody/tr[4]/td[1]/a[2]').click()
        account = Select(self.driver.find_element_by_xpath('//*[@id="id_bank_account"]'))
        account.select_by_visible_text('1200 - ')
        self.driver.find_element_by_xpath('//*[@id="id_amount"]').send_keys('400')
        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/form/div[5]/button').click()
        time.sleep(0.5)

        self.driver.get(self.live_server_url+'/field/project-2')
        self.driver.find_element_by_xpath('/html/body/div/div[4]/div[2]/a[4]').click()
        self.driver.find_element_by_xpath('/html/body/div/form/div/div[2]/div[1]/input').clear()
        self.driver.find_element_by_xpath('/html/body/div/form/div/div[2]/div[1]/input').send_keys("4.5")
        self.driver.find_element_by_xpath('/html/body/div/form/div/div[2]/textarea').send_keys("Additional Report billable_amount")
        self.driver.find_element_by_xpath('/html/body/div/form/div/div[3]/div/input[2]').click()
        self.driver.get(self.live_server_url+'/project-2')
        time.sleep(0.5)

        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[3]/tbody/tr[5]/td[1]/a[1]').click()
        self.driver.find_element_by_xpath('//*[@id="id_document_date"]').send_keys('07/28/2015')
        self.driver.find_element_by_xpath('//*[@id="id_invoice_no"]').send_keys('1235/07|ä@1"2!')
        self.driver.find_element_by_xpath('//*[@id="id_header"]').send_keys('So much, very much Money.')
        self.driver.find_element_by_xpath('//*[@id="id_footer"]').send_keys('So much, very much Money.')
        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/form/div[10]/button').click()

        invoice_total = self.driver.find_elements_by_class_name('invoice-amount')[1].text[:-2]
        invoice_total = float(invoice_total.replace('.', '').replace('_', '.'))
        self.assertEqual(invoice_total, 1206.50)
        time.sleep(0.5)

        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[3]/tbody/tr[7]/td[1]/a[2]').click()
        account2 = Select(self.driver.find_element_by_xpath('//*[@id="id_bank_account"]'))
        account2.select_by_visible_text('1200 - ')
        self.driver.find_element_by_xpath('//*[@id="id_amount"]').send_keys('250.25')
        self.driver.find_element_by_xpath('//*[@id="id_received_on"]').clear()
        self.driver.find_element_by_xpath('//*[@id="id_received_on"]').send_keys('2015-07-29')
        discount = Select(self.driver.find_element_by_xpath('//*[@id="id_discount"]'))
        discount.select_by_visible_text('3%')
        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/form/div[5]/button').click()
        time.sleep(0.5)

        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[3]/tbody/tr[9]/td[1]/a[1]').click()
        self.driver.find_element_by_xpath('//*[@id="id_is_final"]').click()
        self.driver.find_element_by_xpath('//*[@id="id_document_date"]').send_keys('07/30/2015')
        self.driver.find_element_by_xpath('//*[@id="id_invoice_no"]').send_keys('1236/07|ä@1"2!')
        self.driver.find_element_by_xpath('//*[@id="id_title"]').clear()
        self.driver.find_element_by_xpath('//*[@id="id_title"]').send_keys('Final Invoice')
        self.driver.find_element_by_xpath('//*[@id="id_header"]').send_keys('So much, very much Money. Final')
        self.driver.find_element_by_xpath('//*[@id="id_footer"]').send_keys('So much, very much Money. Final')
        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/form/div[10]/button').click()
        time.sleep(0.5)

        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[3]/tbody/tr[11]/td[1]/a').click()
        account3 = Select(self.driver.find_element_by_xpath('//*[@id="id_bank_account"]'))
        account3.select_by_visible_text('1200 - ')
        self.driver.find_element_by_xpath('//*[@id="id_amount"]').send_keys('948.51')
        self.driver.find_element_by_xpath('//*[@id="id_received_on"]').clear()
        self.driver.find_element_by_xpath('//*[@id="id_received_on"]').send_keys('2015-07-31')
        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/form/div[5]/button').click()
        time.sleep(0.5)

        self.driver.get(self.live_server_url+'/projects')
        self.driver.find_element_by_xpath('//*[@id="id_search_term"]').send_keys('project')
        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/div/div[1]/form/div[3]/button').click()
