import pytest
import time
import yaml
import random
import sentry_sdk

# If you print 'driver', it's not an object, it's "<selenium.webdriver.remote.webdriver.WebDriver (session="3955e7dab66c4172ad3d4a8808c0a67c")>"
@pytest.mark.usefixtures("driver")
def test_add_to_cart(driver):

    sentry_sdk.set_tag("py_test", "test_add_to_cart")
    with open('endpoints1.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['react_endpoints']

    for endpoint in endpoints:
        sentry_sdk.set_tag("endpoint", endpoint)
        reported = False
        clickedButtons = 0
        missedButtons = 0

        # TODO each of these rand20 has to be for a different endpoint
        for i in range(random.randrange(20)):
            # TODO - Driver was loaded/running already (Selenium), now is pulling the web app in, which is served by the endpoint?
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

    
