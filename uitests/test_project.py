import time
from selenium.webdriver.common.keys import Keys
from uitests.base import BaseTestCase
import datetime


TODAY = datetime.date.today()


def following_day(days):
    return TODAY + datetime.timedelta(days)


class ProjectTests(BaseTestCase):

    def test_common_workflow(self):

        self.find_link('Projects').click()
        self.find_link('Create').click()
        self.complete_project_form()

        # open first job
        self.find_xpath('//*[@id="jobs-table"]//a').click()

        # click on task group name field
        self.find_xpath('//ubr-taskgroup[1]//div[@class="name"][1]').click()

        # edit task group
        self.send_keys("Task Group 1" + Keys.TAB)
        self.send_keys("Group one description." + Keys.SHIFT + Keys.ENTER)

        time.sleep(1)

        # create task
        self.send_keys("Task 1" + Keys.TAB)
        self.send_keys("2.5" + Keys.TAB)
        self.send_keys("stk" + Keys.TAB)
        self.send_keys("task description" + Keys.SHIFT + Keys.ENTER)

        time.sleep(2)

        # create line item
        self.send_keys("Line Item 1" + Keys.TAB)
        self.send_keys("20.0" + Keys.TAB)
        self.send_keys("m" + Keys.TAB)
        self.send_keys("5" + Keys.SHIFT + Keys.ENTER)

        time.sleep(1)

        # create another line item
        self.send_keys("Line Item 2" + Keys.TAB)
        self.send_keys("10.0" + Keys.TAB)
        self.send_keys("kg" + Keys.TAB)
        self.send_keys("10" + Keys.SHIFT + Keys.ENTER)

        time.sleep(1)

        # go back out to start a new task group
        for i in range(3):
            self.send_keys(Keys.SHIFT + Keys.ENTER)
            time.sleep(0.5)

        # autocomplete a new task group
        self.send_keys("Ta")
        time.sleep(1)
        # select the first option from the autocomplete
        self.send_keys(Keys.ARROW_DOWN)
        self.send_keys(Keys.ENTER)
        time.sleep(2)

        # edit the qty for the first task
        self.send_keys(Keys.ARROW_DOWN)
        self.send_keys(Keys.TAB)
        self.clear()
        self.send_keys("3.0")
        # leave input to trigger a save
        self.send_keys(Keys.ARROW_UP)
        time.sleep(1)

        # make sure everything was saved
        self.driver.refresh()

        # check that the editor has calculated the total correctly
        taskgroup_total = self.find_xpath('//ubr-taskgroup[2]//div[@class="total"][1]').text.strip()
        self.assertEqual('600.00', taskgroup_total)

        # check project details page for correct job total
        self.find_link('Test Project').click()

        job_total = self.find_xpath('//*[@id="jobs-table"]//td[3]').text.strip()
        self.assertEqual('$1,100.00', job_total)

        # Create Contact
        self.find_link('Add Contact').click()
        self.find_link('Create').click()
        self.complete_contact_form()

        time.sleep(0.5)
        row = self.find_xpath('//*[@id="contacts-table"]/tbody/tr')
        self.assertEqual('Max Mustermann', row.find_element_by_xpath('./td[2]/a').text)
        self.assertEqual('yes', row.find_element_by_xpath('./td[5]').text)

        # Create Proposal
        self.find_link('Create Proposal').click()
        self.complete_proposal_form()

        row = self.find_xpath('//*[@id="proposals-table"]/tbody/tr')
        self.assertEqual('New', row.find_element_by_xpath('./td[2]').text.strip())
        self.assertEqual('$1,309.00', row.find_element_by_xpath('./td[4]').text.strip())
        time.sleep(0.5)

        # report some billable amounts
        self.driver.get(self.live_server_url+'/field/project-2/')
        self.driver.find_element_by_xpath('/html/body/div/div[3]/a[1]').click()
        self.driver.find_element_by_css_selector('a[href="/field/project-2/{}?copy_source_date="]'.format(following_day(1).strftime('%Y-%m-%d'))).click()

        self.driver.find_element_by_xpath('/html/body/div/div[3]/a[2]').click()
        self.driver.find_element_by_xpath('/html/body/form/div/div[2]/div[2]/label[1]/input').click()
        self.driver.find_element_by_xpath('/html/body/form/div/div[2]/div[3]/div/button').click()
        self.driver.find_element_by_xpath('/html/body/div/div[2]/ul/a').click()
        self.driver.find_element_by_xpath('/html/body/div/div[2]/div[3]/div/a').click()
        self.driver.find_element_by_xpath('/html/body/div/div[2]/ul/a[2]').click()
        self.driver.find_element_by_xpath('/html/body/div/div[2]/div[3]/div/a').click()

        self.driver.find_element_by_xpath('/html/body/div/div[2]/ul/a').click()
        self.driver.find_element_by_xpath('/html/body/div/form/div/div[2]/div[1]/input').send_keys("2.5")
        self.driver.find_element_by_xpath('/html/body/div/form/div/div[2]/textarea').send_keys("Some Report billable_amount")
        self.driver.find_element_by_xpath('/html/body/div/form/div/div[3]/div/input[2]').click()

        self.driver.find_element_by_xpath('/html/body/div/div[1]/div[1]/a').click()
        self.driver.find_element_by_xpath('/html/body/div/div[1]/div/div/div[1]/div[1]/a').click()
        self.driver.get(self.live_server_url+'/project-2')
        time.sleep(0.2)
        self.assertEqual('500,00',
                         self.driver.find_element_by_xpath('//*[@id="job-table"]/tr/td[5]').text[:-2])

        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[3]/tbody/tr[2]/td[1]/a[1]').click()
        self.driver.find_element_by_xpath('//*[@id="id_document_date"]').send_keys(following_day(2).strftime('%m-%d-%Y'))
        self.driver.find_element_by_xpath('//*[@id="id_invoice_no"]').send_keys('1234/04|ä@1"2!')
        self.driver.find_element_by_xpath('//*[@id="id_header"]').send_keys('So much, very much Money.')
        self.driver.find_element_by_xpath('//*[@id="id_footer"]').send_keys('So much, very much Money.')
        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/form/div[10]/button').click()

        self.assertEqual('595,00',
                         self.driver.find_element_by_class_name('add-total-amount').text[:-2])
        time.sleep(0.5)

        # receive first payment
        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[3]/tbody/tr[4]/td[1]/a[2]').click()
        account = Select(self.driver.find_element_by_xpath('//*[@id="id_bank_account"]'))
        account.select_by_visible_text('1200 - ')
        self.driver.find_element_by_xpath('//*[@id="id_amount"]').send_keys('595')
        self.driver.find_element_by_xpath('//*[@id="id_received_on"]').clear()
        self.driver.find_element_by_xpath('//*[@id="id_received_on"]').send_keys(following_day(3).strftime('%Y-%m-%d'))
        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/form/div[5]/button').click()
        time.sleep(0.5)

        # second amount report
        self.driver.get(self.live_server_url+'/field/project-2')
        self.driver.find_element_by_xpath('/html/body/div/div[3]/a[1]').click()
        self.driver.find_element_by_css_selector('a[href="/field/project-2/{}?copy_source_date="]'.format(following_day(2).strftime('%Y-%m-%d'))).click()
        self.driver.find_element_by_xpath('/html/body/div/a[2]').click()
        self.driver.find_element_by_xpath('/html/body/div/div[4]/div[2]/a[4]').click()
        self.driver.find_element_by_xpath('/html/body/div/form/div/div[2]/div[1]/input').send_keys("2.5")
        self.driver.find_element_by_xpath('/html/body/div/form/div/div[2]/textarea').send_keys("Some another Report billable_amount")
        self.driver.find_element_by_xpath('/html/body/div/form/div/div[3]/div/input[2]').click()
        self.driver.get(self.live_server_url+'/project-2')
        time.sleep(0.5)

        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[3]/tbody/tr[5]/td[1]/a[1]').click()
        self.driver.find_element_by_xpath('//*[@id="id_is_final"]').click()
        self.driver.find_element_by_xpath('//*[@id="id_document_date"]').send_keys(following_day(4).strftime('%m-%d-%Y'))
        self.driver.find_element_by_xpath('//*[@id="id_invoice_no"]').send_keys('1235/07|ä@1"2!')
        self.driver.find_element_by_xpath('//*[@id="id_title"]').clear()
        self.driver.find_element_by_xpath('//*[@id="id_title"]').send_keys('Final Invoice')
        self.driver.find_element_by_xpath('//*[@id="id_header"]').send_keys('So much, very much Money.')
        self.driver.find_element_by_xpath('//*[@id="id_footer"]').send_keys('So much, very much Money.')
        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/form/div[10]/button').click()
        time.sleep(0.5)

        # receive second payment
        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[3]/tbody/tr[7]/td[1]/a[2]').click()
        account2 = Select(self.driver.find_element_by_xpath('//*[@id="id_bank_account"]'))
        account2.select_by_visible_text('1200 - ')
        self.driver.find_element_by_xpath('//*[@id="id_amount"]').send_keys('577.15')
        self.driver.find_element_by_xpath('//*[@id="id_received_on"]').clear()
        self.driver.find_element_by_xpath('//*[@id="id_received_on"]').send_keys(following_day(5).strftime('%Y-%m-%d'))
        discount = Select(self.driver.find_element_by_xpath('//*[@id="id_discount"]'))
        discount.select_by_visible_text('3%')
        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/form/div[5]/button').click()
        time.sleep(0.5)

        # test project filter
        self.driver.get(self.live_server_url+'/projects')
        self.driver.find_element_by_xpath('//*[@id="id_search_term"]').send_keys('project')
        self.driver.find_element_by_xpath('/html/body/div/div/div[2]/div/div[1]/form/div[3]/button').click()
        self.driver.find_element_by_xpath('//*[@id="table"]/tbody/tr[2]/td[2]/a').click()

        #check accounts
        self.driver.get(self.live_server_url+'/accounts')
        self.assertEqual('1.172,15 €',
                         self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[1]/tbody/tr/td[3]').text)
        self.assertEqual('187,15 €',
                         self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[2]/tbody/tr[3]/td[4]').text)
        self.assertEqual('1.000,00 €',
                         self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[2]/tbody/tr[4]/td[4]').text)
        self.assertEqual('-15,00 €',
                         self.driver.find_element_by_xpath('/html/body/div/div/div[2]/table[2]/tbody/tr[5]/td[4]').text)

    def complete_project_form(self):
        self.find_name('name').send_keys("Test Project")
        self.find_name('address').send_keys("Pettenkoferstr. 10")
        self.find_name('city').send_keys("Mannheim")
        self.find_name('postal_code').send_keys("68169")
        self.find_name('save_goto_project').click()

    def complete_contact_form(self):
        self.find_name('is_billable').click()
        self.find_name('business').send_keys("Company")
        self.find_name('salutation').send_keys("Mr.")
        self.find_name('first_name').send_keys("Max")
        self.find_name('last_name').send_keys("Mustermann")
        self.find_name('phone').send_keys("0123 456789")
        self.find_name('email').send_keys("max.mustermann@trash-mail.com")
        self.find_name('website').send_keys("http://www.mustermann.de")
        self.find_name('address').send_keys("Eintrachtstraße 24")
        self.find_name('postal_code').send_keys("68169")
        self.find_name('city').send_keys("Mannheim")
        self.find_name('notes').send_keys("This is a Note on a Contact")
        self.find_button('Create').click()

    def complete_proposal_form(self):
        self.find_name('document_date').send_keys(TODAY.strftime('%m-%d-%Y'))
        self.find_name('header').send_keys('Dear Sir or Madam,\n this is a Test:')
        self.find_name('footer').send_keys('We hope you pay us for something.')
        self.find_named_select('jobs').select_by_visible_text('Default')
        self.find_button('Save').click()

