import pytest
import time
import yaml
import random
import sentry_sdk

# If you print 'driver', it's not an object, it's "<selenium.webdriver.remote.webdriver.WebDriver (session="3955e7dab66c4172ad3d4a8808c0a67c")>"
@pytest.mark.usefixtures("driver")
def test_add_to_cart_2(driver):

    sentry_sdk.set_tag("py_test", "test_add_to_cart_2")
    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['react_endpoints']

    for endpoint in endpoints:
        sentry_sdk.set_tag("endpoint", endpoint)
        reported = False
        clickedButtons = 0
        missedButtons = 0

        for i in range(random.randrange(20)):
            # Loads the homepage
            driver.get(endpoint)

            # Buttons not be available if tools did not load in time
            try:
                buy_button = driver.find_element_by_css_selector('.item button')
                for i in range(random.randrange(3) + 3):
                    buy_button.click()
                driver.find_element_by_css_selector('.sidebar button').click()
                clickedButtons = clickedButtons + 1
            except Exception as err:
                missedButtons = missedButtons + 1
                if reported == False:
                    sentry_sdk.capture_exception(err)
                reported = True
            time.sleep(random.randrange(3) + 3)

        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("clickedButtons", clickedButtons)
            scope.set_tag("missedButtons", missedButtons)
            msg = ""
            if 'platform' in scope._tags:
                msg = msg + scope._tags['platform']
            if 'browserName' in scope._tags:
                msg = msg + " - " + scope._tags['browserName']
            if msg == "":
                msg = "Finished Endpoint"
            else:
                msg = "Finished Endpoint: %s" % (msg)
        sentry_sdk.capture_message(msg)
        
        if missedButtons > 0:
            raise 'unable to click button somewhere in this test'

    
