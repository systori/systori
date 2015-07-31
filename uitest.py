#!/usr/bin/env python
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "systori.settings")
import django
django.setup()

import unittest
from django.test.testcases import LiveServerThread, _StaticFilesHandler
from django.test.runner import setup_databases
from selenium import webdriver
from sauceclient import SauceClient
from systori.apps.accounting.skr03 import create_chart_of_accounts

TRAVIS_JOB_NUMBER = os.environ.get('TRAVIS_JOB_NUMBER', 1)
TRAVIS_BUILD_NUMBER = os.environ.get('TRAVIS_BUILD_NUMBER', 1)

CHROME_VERSION = "43.0"
SAUCE_BROWSERS = [

    #("OS X 10.10", "safari", "8.0"),
    #("OS X 10.10", "chrome", CHROME_VERSION),

    #("Windows 7",  "internet explorer", "11.0"),
    ("Windows 7",  "chrome", CHROME_VERSION),

]

SELENIUM_WAIT_TIME = 15 # max seconds to wait for page to load before failing

SAUCE_PORTS = [8003, 8031, 8765]
# per: https://docs.saucelabs.com/reference/sauce-connect/#can-i-access-applications-on-localhost-


def make_suite(driver, server, sauce=None):
    main_suite = unittest.defaultTestLoader.discover('uitests')
    main_suite.sauce = sauce
    main_suite.driver = driver
    for suite in main_suite:
        for sub_suite in suite:
            for test in sub_suite:
                test.driver = driver
                test.server = server
    return main_suite


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
    server = LiveServerThread('localhost', SAUCE_PORTS, _StaticFilesHandler)
    server.daemon = True
    server.start()
    return server


def setup_test_data():
    from systori.apps.company.models import Company, Access
    from systori.apps.user.models import User
    from systori.apps.project.models import Project
    company = Company.objects.create(schema="test", name="Test")
    company.activate()
    user = User.objects.create_user('test@systori.com', 'pass', first_name="Standard", last_name="Worker")
    Access.objects.create(user=user, company=company, is_staff=True)
    user = User.objects.create_user('test2@systori.com', 'pass', first_name="Standard2", last_name="Worker2")
    Access.objects.create(user=user, company=company, is_staff=True)
    create_chart_of_accounts()
    Project.objects.create(name="Template Project", is_template=True)


def main(driver_names, keep_open, not_parallel):

    setup_databases(verbosity=True, interactive=False, keepdb=False)

    setup_test_data()

    server = start_django()

    # while django is starting we setup the webdrivers...
    suites = []

    if 'chrome' in driver_names:
        chrome = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
        chrome.implicitly_wait(SELENIUM_WAIT_TIME)
        suites.append((make_suite(chrome, server), None))

    if 'firefox' in driver_names:
        firefox = webdriver.Firefox()
        firefox.implicitly_wait(SELENIUM_WAIT_TIME)
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
            saucelabs.implicitly_wait(SELENIUM_WAIT_TIME)
            suites.append((make_suite(saucelabs, server, sauce), sauce_update))

    # if django is still not ready, then we wait...
    server.is_ready.wait()

    # if django couldn't start, quit() the webdrivers and raise error
    if server.error:
        for suite, cleanup in suites:
            suite.driver.quit()
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
