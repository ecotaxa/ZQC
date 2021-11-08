
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
# dynamicaly expose checks

######--- Return an object containing all availables quallity checks ---######
def listChecks():
    return [{
       "title" : "Before scan",
       "id" : "before_scan",
       "blocs" :[{
               "title":"Sample quality checks",
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
       "blocs" : [{
               "title":"Sample quality checks",
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
               "checks":[{
                  "id":"motoda_is_coherent",
                  "title":"Motoda is coherent",
                  "description":"Checks that motoda frac is coherent."
               }]
            },
            {
               "title":"Processing quality checks",
               "checks":[{
                  "id":"scans_are_processed",
                  "title":"_raw has img, meta, and log",
                  "description":"Checks the number of zip/tif images, meta files and log files in the _raw directory"
               }]
            }]      
    }]