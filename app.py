import dash
import ecotaxa_py_client
from ecotaxa_py_client.api import authentification_api
from ecotaxa_py_client.model.http_validation_error import HTTPValidationError
from ecotaxa_py_client.model.login_req import LoginReq

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title="Quality checks"
app._favicon = ("favicon.png")
server = app.server

######--- Connect to ecotaxa api (will be deleted) ---######
app.configuration = ecotaxa_py_client.Configuration(
    host = "https://ecotaxa.obs-vlfr.fr/api"
)

print("************Get token in************")
with ecotaxa_py_client.ApiClient(app.configuration) as api_client:
    # Create an instance of the API class
    api_instance = authentification_api.AuthentificationApi(api_client)
    login_req = LoginReq(
        password="test!",
        username="ecotaxa.api.user@gmail.com",
    ) # LoginReq | 

    # example passing only required values which don't have defaults set
    try:
        # Login
        api_response = api_instance.login(login_req)
        app.configuration.access_token = api_response
    except ecotaxa_py_client.ApiException as e:
        print("Exception when calling AuthentificationApi->login_login_post: %s\n" % e)
