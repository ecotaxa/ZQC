
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
# dynamicaly expose checks

######--- Return an object containing all availables quallity checks ---######
def listChecks():
    return [{
       "title" : "Before scan",
       "id" : "before_scan",
       "blocks" :[{
               "title":"Sample quality checks",
               "description" : "This quality check gives an overview of the quality of the data related to the acquisition of the sample.",
               "checks":[{
                     "id":"gps_points_are_coherent",
                     "title":"GPS points are coherent",
                     "description":"Checks that GPS points are coherent."
                  },{
                     "id":"dates_are_coherent",
                     "title":"Dates are coherent",
                     "description":"Checks that dates are coherent."
                  }]
         }]
    },
    {
       "title" : "During analysis",
       "id" : "during_analysis",
       "blocks" : [{
               "title":"Sample quality checks",
               "description" : "This quality check gives an overview of the quality of the data related to the acquisition of the sample.",
               "checks":[{
                  "id":"gps_points_are_coherent",
                  "title":"GPS points are coherent",
                  "description":"Checks that GPS points are coherent."
               },{
                  "id":"dates_are_coherent",
                  "title":"Dates are coherent",
                  "description":"Checks that dates are coherent."
               }]
            },{
               "title":"Acquisition quality checks",
               "description" : "This quality check gives an overview of the quality of the data related to the acquisition of the scan on the Zooscan.",
               "checks":[{
                  "id":"motoda_is_coherent",
                  "title":"Motoda is coherent",
                  "description":"Checks that motoda frac is coherent."
               }]
            },
            {
               "title":"Processing quality checks",
               "description" : "This quality check gives an overview and notes the quality of the steps performed by the sample during its acquisition (SCAN) at the Zooscan and its processing (PROCESS) via the Zooprocess application.",
               "checks":[{
                  "id":"scans_are_processed",
                  "title":"_raw has img, meta, and log",
                  "description":"Checks the number of zip/tif images, meta files and log files in the _raw directory"
               }]
            }]      
    }]

