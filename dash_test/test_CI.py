from dash.testing.application_runners import import_app

def test_title(dash_duo):
    app = import_app("dash_test.app")
    dash_duo.start_server(app)
    dash_duo.driver.get('https://www.delrayo.tech')
    assert dash_duo.driver.title == "DelRayo.tech - Delrayo Tech"

def test_title_blog(dash_duo):
    app = import_app("dash_test.app")
    dash_duo.start_server(app)
    dash_duo.driver.get('https://www.delrayo.tech/blog')
    print(dash_duo.driver.title)