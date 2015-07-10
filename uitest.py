import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings.testing")
import django
django.setup()

import sys
import unittest
from django.test import SimpleTestCase
from django.test.testcases import LiveServerThread, _StaticFilesHandler
from selenium import webdriver
from sauceclient import SauceClient


TRAVIS_JOB_NUMBER = os.environ.get('TRAVIS_JOB_NUMBER', 1)
TRAVIS_BUILD_NUMBER = os.environ.get('TRAVIS_BUILD_NUMBER', 1)


CHROME_VERSION = "43.0"
SAUCE_BROWSERS = [

    #("OS X 10.10", "safari", "8.0"), BROKEN FOR NOW
    ("OS X 10.10", "chrome", CHROME_VERSION),

    ("Windows 7",  "internet explorer", "11.0"),
    ("Windows 7",  "chrome", CHROME_VERSION),

]


class BaseTestCase(SimpleTestCase):

    @property
    def live_server_url(self):
        return 'http://%s:%s' % (
            self.server.host, self.server.port)

    def setUp(self):
        self.driver.implicitly_wait(30)

class LoginTests(BaseTestCase):

    def test_login(self):
        self.driver.get(self.live_server_url)
        assert "systori" in self.driver.title
#        comments = self.driver.find_element_by_id('comments')
#        comments.send_keys('Hello! I am some example comments.'
#                           ' I should be in the page after submitting the form')
#        self.driver.find_element_by_id('submit').click()
#
#        commented = self.driver.find_element_by_id('your_comments')
#        assert ('Your comments: Hello! I am some example comments.'
#                ' I should be in the page after submitting the form'
#                in commented.text)
#        body = self.driver.find_element_by_xpath('//body')
#        assert 'I am some other page content' not in body.text
#        self.driver.find_elements_by_link_text('i am a link')[0].click()
#        body = self.driver.find_element_by_xpath('//body')
#        assert 'I am some other page content' in body.text


def make_suite(driver, server, sauce=None):
    suite = unittest.findTestCases(sys.modules[__name__])
    suite.sauce = sauce
    suite.driver = driver
    for subsuite in suite:
        for test in subsuite:
            test.driver = driver
            test.server = server
    return suite


def sauce_update(suite, result):
    build_num = TRAVIS_BUILD_NUMBER
    if result.wasSuccessful():
        suite.sauce.jobs.update_job(suite.driver.session_id,
            passed=True, build_num=build_num, public="share")
    else:
        suite.sauce.jobs.update_job(suite.driver.session_id,
            passed=False, build_num=build_num, public="share")


def run_tests(runner, suite, cleanup, keep_open):

    name = '{platform} {browserName} {version}'.format(**suite.driver.desired_capabilities)
    print("Starting: {}".format(name))

    result = runner.run(suite)

    if cleanup:
        cleanup(suite, result)

    if not keep_open:
        suite.driver.quit()

    if result.wasSuccessful():
        print("Passed: {}".format(name))

    else:
        print("Failed: {}".format(name))


def start_django():
    server = LiveServerThread('localhost', range(8100, 8200), _StaticFilesHandler)
    server.daemon = True
    server.start()
    return server


def main(driver_names, keep_open, not_parallel):

    server = start_django()

    # while django is starting we setup the webdrivers...
    drivers = []
    suites = []

    if 'chrome' in driver_names:
        chrome = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
        drivers.append(chrome)
        suites.append((make_suite(chrome, server), None))

    if 'firefox' in driver_names:
        firefox = webdriver.Firefox()
        drivers.append(firefox)
        suites.append((make_suite(firefox, server), None))

    if 'saucelabs' in driver_names:
        username = os.environ.get('SAUCE_USERNAME', "systori_ci")
        access_key = os.environ.get('SAUCE_ACCESS_KEY', "1c7a1f7b-9890-46ef-89d0-93e435df146a")
        sauce = SauceClient(username, access_key)
        sauce_url = "http://%s:%s@ondemand.saucelabs.com:80/wd/hub" % (username, access_key)
        for platform, browser, version in SAUCE_BROWSERS:
            saucelabs = webdriver.Remote(
                desired_capabilities={
                    "name": "systori ui tests",
                    "platform": platform,
                    "browserName": browser,
                    "version": version,
                    "tunnel-identifier": TRAVIS_JOB_NUMBER,
                    "build": TRAVIS_BUILD_NUMBER
                },
                command_executor=sauce_url
            )
            drivers.append(saucelabs)
            suites.append((make_suite(saucelabs, server, sauce), sauce_update))

    # if django is still not ready, then we wait...
    server.is_ready.wait()

    # if django couldn't start, quit() the webdrivers and raise error
    if server.error:
        for driver in drivers:
            driver.quit()
        raise server.error

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as executor:
        for suite, cleanup in suites:
            runner = unittest.TextTestRunner()
            if not_parallel:
                run_tests(runner, suite, cleanup, keep_open)
            else:
                executor.submit(run_tests, runner, suite, cleanup, keep_open)

    # all done, stop django
    server.terminate()
    server.join()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Test Systori UI using Selenium.')
    parser.add_argument('--not-parallel', action='store_true',
                        help='Do not run tests in parallel.')
    parser.add_argument('--keep-open', action='store_true',
                        help='Keep local browser open after running tests.')
    parser.add_argument('drivers', nargs='+',
                        choices=['saucelabs', 'chrome', 'firefox'],
                        help='Run on Sauce Labs and/or on local browser.')
    args = parser.parse_args()
    main(args.drivers, args.keep_open, args.not_parallel)
