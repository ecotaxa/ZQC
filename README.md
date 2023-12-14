[![CI](https://github.com/ecotaxa/AQC/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/ecotaxa/AQC/actions/workflows/main.yml)
# AQC
*TODO* : context and credits
## Technologies
The quality checker is a Dash based application. Here you can find more information about it https://dash.plotly.com/introduction.
## Features
*TODO* : context
For more details here is tool specifications : https://docs.google.com/document/d/1zyayKITTeReZ2u3fev85HJ_2rgs-Ceb18n6CXRlTVfA/edit
### Available
*TODO*
### Comming soon
*TODO*

## On local dev env
### Setup
requirement : python3.8

```shell
git clone https://github.com/juliecoust/AQC.git
cd AQC/
python3 -m venv "venvQC"  
source venvQC/bin/activate
pip3 install -r requirements.txt
```
### Run the app
```shell
cd AQC/
source venvQC/bin/activate
DASH_ENV=DEV python index.py
```
Local Url to zooscan QC app : http://127.0.0.1:8050/QC/zooscan
Local Url to zooscan QC doc : http://127.0.0.1:8050/QC/zooscan/doc

## On COMPLEX server
### Setup
```shell
git clone https://github.com/juliecoust/AQC.git
cd AQC/
python3 -m venv venvQC
source venvQC/bin/activate
pip3 install -r requirements.txt
```

### Run the app
```shell
cd AQC/
source venvQC/bin/activate
nohup DASH_ENV=PROD python index.py
```

Local Url to zooscan QC app : http://complex.imev-mer.fr:8050/QC/zooscan
Local Url to zooscan QC doc : http://complex.imev-mer.fr:8050/QC/zooscan/doc



## Architecture
*TODO* : define classes/architecture and argue about choices for maintenance, reusability and scalability.
-  *Logs :*
    The logs are saved in the /logs folder. The log files are created automatically and have the name format ***YYYY-MM.log***. 
    If log files become to big we will easily be able to change this to YYYY-MM-***DD***.log or more by adding an incremental number N : YYYY-MM-DD-***N***.log
## Tests :
- https://dash.plotly.com/testing
  UNIT : *TODO*
  FEATURES : *TODO*
  INTEGRATION : used tutorials : https://python.plainenglish.io/test-your-dash-app-in-python-6eb7229d40b8 https://community.plotly.com/t/how-you-can-integration-test-your-app-by-dash-testing/25002/3 *TODO*
  PERF  : *TODO*
