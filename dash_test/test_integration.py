# 1. imports of dash app
from dash.testing.application_runners import import_app
from selenium.webdriver.common.by import By

#Go to all the pages of the dash app and check if it can be load without errors
def test_multi_page_app_is_running(dash_duo) : 
    app = import_app("dash_test.app")
    dash_duo.start_server(app)
    
    # Go to /QC/zooscan and check is running
    dash_duo.wait_for_page(dash_duo.server_url + '/QC/zooscan', timeout=5)
    assert dash_duo.driver.find_element(by=By.CSS_SELECTOR, value="h1").text == "Zooscan Quality Checks"
    #assert dash_duo.get_logs() == [], "Browser console contain no error"

    # Go to /QC/zooscan/doc and check is running
    dash_duo.wait_for_page(dash_duo.server_url + '/QC/zooscan/doc', timeout=5)
    assert dash_duo.driver.find_element(by=By.CSS_SELECTOR, value="h1").text == "Presentation of Zooscan Quality Checker tool for zooscan projects"
    #assert dash_duo.get_logs() == [], "Browser console contain no error"
    
    # Go from doc to app
    e_go_qc = dash_duo.driver.find_element(by=By.CSS_SELECTOR, value=".go-qc")
    e_go_qc.click()
    dash_duo.wait_for_contains_text("h1", "Zooscan Quality Checks", timeout=5)
    assert dash_duo.driver.find_element(by=By.CSS_SELECTOR, value="h1").text == "Zooscan Quality Checks"

    #Go to all the pages of the dash app and check llinks between pages
    # Go from app to doc
    e = dash_duo.driver.find_element(by=By.CSS_SELECTOR, value=".help-btn")
    e.click()
    dash_duo.wait_for_contains_text("h1", "Presentation of Zooscan Quality Checker tool for zooscan projects", timeout=5)
    assert dash_duo.driver.find_element(by=By.CSS_SELECTOR, value="h1").text == "Presentation of Zooscan Quality Checker tool for zooscan projects"
