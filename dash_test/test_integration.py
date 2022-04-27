# 1. imports of dash app
from dash.testing.application_runners import import_app
from selenium.webdriver.common.by import By

#Go to all the pages of the dash app and check if it can be load without errors
def test_multi_page_app_is_running(dash_duo) : 
    app = import_app("dash_test.app")
    dash_duo.start_server(app)
    
    # Go to /QC/zooscan and check is running
    dash_duo.wait_for_page(dash_duo.server_url + '/QC/zooscan', timeout=5)
    assert dash_duo.find_element("h1").text == "Data quality checks"
    assert dash_duo.get_logs() == [], "Browser console contain no error"

    # Go to /QC/zooscan/doc and check is running
    dash_duo.wait_for_page(dash_duo.server_url + '/QC/zooscan/doc', timeout=5)
    assert dash_duo.find_element("h1").text == "Presentation of Data quality checker tool for zooscan projects"
    assert dash_duo.get_logs() == [], "Browser console contain no error"

    return None

#Go to all the pages of the dash app and check if it can be load without errors
def test_links_between_pages(dash_duo) : 
    app = import_app("dash_test.app")
    dash_duo.start_server(app)
    
    # Go from app to doc
    dash_duo.wait_for_page(dash_duo.server_url + '/QC/zooscan', timeout=5)
    dash_duo.driver.find_element(by=By.CSS_SELECTOR, value=".help-btn").click()
    assert dash_duo.find_element("h1").text == "Presentation of Data quality checker tool for zooscan projects"
   
    # Go from doc to app
    dash_duo.wait_for_page(dash_duo.server_url + '/QC/zooscan/doc', timeout=5)
    dash_duo.driver.find_element(by=By.CSS_SELECTOR, value=".go-qc").click()
    assert dash_duo.find_element("h1").text == "Data quality checks"

    return None