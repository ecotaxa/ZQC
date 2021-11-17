from ecotaxa_py_client import api
from app import app

import time
import ecotaxa_py_client
from ecotaxa_py_client.model.http_validation_error import HTTPValidationError
from ecotaxa_py_client.api import files_api
from ecotaxa_py_client.model.directory_model import DirectoryModel

from libQC_classes import Mode

def getDrives():
    print("************Get drives in************")
    return getDir("")

def getProjects(drive):
    print("************Get projects in************")
    return getDir(drive)

def getDir(subpath) :
    print("************Get dir in************")
    # create a context with an instance of the API client
    with ecotaxa_py_client.ApiClient(app.configuration) as api_client:
        # Create an instance of the API class
        api_instance = files_api.FilesApi(api_client)
        path = "/local_plankton/zooscan/"+subpath # str | 
        try:
            # List Common Files
            api_response = api_instance.list_common_files(path).entries
            dirs = [x for x in api_response if x.type=='D' and x.name.lower().startswith("zooscan")]
            dirs.sort(key=lambda x: x.name)
        except ecotaxa_py_client.ApiException as e:
            print("Exception when calling FilesApi->list_common_files_common_files_get: %s\n" % e)
    return dirs

def getFiles(subpath):
    print("************Get files in************")
    # create a context with an instance of the API client
    with ecotaxa_py_client.ApiClient(app.configuration) as api_client:
        # Create an instance of the API class
        api_instance = files_api.FilesApi(api_client)
        path = "/local_plankton/zooscan/"+subpath+"/Zooscan_scan/_raw/" # str | 
        try:
            # List Common Files
            api_response = api_instance.list_common_files_common_files_get(path).entries
            files = [x for x in api_response if x.type=='F']
            files.sort(key=lambda x: x.name)

        except ecotaxa_py_client.ApiException as e:
            print("Exception when calling FilesApi->list_common_files_common_files_get: %s\n" % e)
    return files

def getdata(mode, subpath) :
    print("*******************"+subpath)
    
    if mode==Mode.TSV :
        a=0
    elif mode==Mode.HEADER :
        a=0