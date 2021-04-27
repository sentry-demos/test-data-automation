import pytest
import time
import yaml
import random
import sentry_sdk

@pytest.mark.usefixtures("driver")
def test_add_to_cart(driver):
    sentry_sdk.set_tag("test", "test_add_to_cart")
    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['react_endpoints']

    for endpoint in endpoints:
        reported = False
        for i in range(random.randrange(20)):
            driver.get(endpoint)

            # Buttons not be available if tools did not load in time
            try:
                buy_button = driver.find_element_by_css_selector('.item button')
                for i in range(random.randrange(3) + 3):
                    buy_button.click()
                driver.find_element_by_css_selector('.sidebar button').click()
            except Exception as err:
                if reported == False:
                    sentry_sdk.capture_exception(err)
                reported = True

            time.sleep(random.randrange(3) + 3)
