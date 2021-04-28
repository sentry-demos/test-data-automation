import pytest
import os
from os import environ
import sentry_sdk
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.remote_connection import RemoteConnection
from dotenv import load_dotenv
load_dotenv()
DSN = os.getenv("DSN")
print("DSN", DSN)

import urllib3
urllib3.disable_warnings()

# TODO try without ENV in .env
sentry_sdk.init(
    dsn= DSN,
    traces_sample_rate=0,
    environment=os.getenv("ENV") or "production"
)
sentry_sdk.set_tag("demo-automation", "test-data-automation")

browsers = [
    {
        "seleniumVersion": '3.4.0',
        "platform": "Windows 10",
        "browserName": "chrome",
        "version": "latest"
    }, {
        "seleniumVersion": '3.4.0',
        "platform": "Windows 10",
        "browserName": "firefox",
        "version": "latest"
    }, {
        "seleniumVersion": '3.4.0',
        "platform": "OS X 10.13",
        "browserName": "safari",
        "version": "latest-1"
    }, {
        "seleniumVersion": '3.4.0',
        "platform": "OS X 10.11",
        "browserName": "chrome",
        "version": "latest",
        "extendedDebugging": True
    }]

def pytest_generate_tests(metafunc):
    if 'driver' in metafunc.fixturenames:
        metafunc.parametrize('browser_config',
                             browsers,
                             ids=_generate_param_ids('broswerConfig', browsers),
                             scope='function')


def _generate_param_ids(name, values):
    return [("<%s:%s>" % (name, value)).replace('.', '_') for value in values]


"""
request.node.name is one of 4 elements from the 'browsers' array defined above
"test_add_to_cart[<broswerConfig:{'seleniumVersion': '3_4_0', 'platform': 'Windows 10', 'browserName': 'chrome', 'version': 'latest'}>]"
"""
@pytest.yield_fixture(scope='function')
def driver(request, browser_config):
    print("00000000")
    print(type(request.node.name))
    platform = ""
    browserName = ""

    if "windows" in request.node.name.lower():
        platform = "Windows"
    else:
        platform = "OSX"

    if "chrome" in request.node.name.lower():
        browserName = "chrome"
    if "firefox" in request.node.name.lower():
        browserName = "firefox"
    if "safari" in request.node.name.lower():
        browserName = "safari"

    print("browserName", browserName)
    print("platform", platform)

    # TODO .'.'.
    # sentry_sdk.set_context("request.node.name", {
    #     "request_node_name": request.node.name
    # })

    sentry_sdk.set_tag("platform", platform)
    sentry_sdk.set_tag("browserName", browserName")
    sentry_sdk.capture_message("Started Pytest")

    # if the assignment below does not make sense to you please read up on object assignments.
    # The point is to make a copy and not mess with the original test spec.
    desired_caps = dict()
    desired_caps.update(browser_config)
    # Represents a specific browser
    test_name = request.node.name
    build_tag = environ.get('BUILD_TAG', None)
    tunnel_id = environ.get('TUNNEL_IDENTIFIER', None)
    username = environ.get('SAUCE_USERNAME', None)
    access_key = environ.get('SAUCE_ACCESS_KEY', None)

    selenium_endpoint = "https://%s:%s@ondemand.saucelabs.com:443/wd/hub" % (username, access_key)
    desired_caps['build'] = build_tag
    # we can move this to the config load or not, also messing with this on a test to test basis is possible :)
    desired_caps['tunnelIdentifier'] = tunnel_id
    desired_caps['name'] = test_name

    executor = RemoteConnection(selenium_endpoint, resolve_ip=False)
    browser = webdriver.Remote(
        command_executor=executor,
        desired_capabilities=desired_caps,
        keep_alive=True
    )
    browser.implicitly_wait(10)

    # This is specifically for SauceLabs plugin.
    # In case test fails after selenium session creation having this here will help track it down.
    # creates one file per test non ideal but xdist is awful
    if browser is not None:
        print("SauceOnDemandSessionID={} job-name={}".format(browser.session_id, test_name))
    else:
        sentry_sdk.capture_message("Never created - case test failed: %s %s" % (browser.session_id, test_name))
        raise WebDriverException("Never created!")

    # TODO this is where the test is run?
    yield browser

    # Teardown starts here
    # report results
    # use the test result to send the pass/fail status to Sauce Labs
    sauce_result = "failed" if request.node.rep_call.failed else "passed"
    if sauce_result == "failed":
        sentry_sdk.set_context("sauce_result", {
            "browser_session_id": browser.session_id,
            "test_name": test_name
        })
        sentry_sdk.capture_message("Sauce Result: %s" % (sauce_result))
    browser.execute_script("sauce:job-result={}".format(sauce_result))
    browser.quit()

    # if the test errors on not finding a button, then will this line execute?
    # sentry_sdk.capture_message("Finished browser.quit()")

@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # this sets the result as a test attribute for Sauce Labs reporting.
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set an report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)

