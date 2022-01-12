# coding: utf-8

import httplib2
import webbrowser
import pandas
import requests
import json
from pandas.io.json import json_normalize
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from apiclient.discovery import build

# -----> Authorization GWT <-----
scope = 'https://www.googleapis.com/auth/webmasters.readonly'

flow = flow_from_clientsecrets('D:\\Work\\Python Scripts\\client_secrets.json', scope, redirect_uri = 'http://localhost')
storage = Storage('D:\\Work\\Python Scripts\\webmasters_credentials.dat')
credentials = storage.get()
if not credentials or credentials.invalid:
  auth_uri = flow.step1_get_authorize_url()
  webbrowser.open(auth_uri)
  auth_code = input('Enter the auth code: ')
  credentials = flow.step2_exchange(auth_code)
  storage.put(credentials)

# Getting GWT service
http = httplib2.Http()
http = credentials.authorize(http)
service = build('webmasters', 'v3', http = http)

# Requests to GWT
request_current = {
    'startDate' : '2018-12-01',
    'endDate' : '2019-02-28',
    'dimensions' : ['page'], # ['page','query']
    'aggregationType': 'byPage', # experimental
    'rowLimit' : 25000
}

request_previous = {
    'startDate' : '2017-12-01',
    'endDate' : '2018-02-28',
    'dimensions' : ['page'], # ['page','query']
    'aggregationType': 'byPage', # experimental
    'rowLimit' : 25000
}

properties = ['https://blog.selectel.ru/', 'https://selectel.ru/']
requests = [request_current, request_previous]

# Query loop to GWT with property
'''
for i in properties:
  for j in requests:
    response = service.searchanalytics().query(siteUrl = i, body = j).execute()
    data_frame = pandas.DataFrame(data = response['rows'])
    data_frame.to_csv('D:\\Work\\Python Scripts\\Result\\webmasters_' + str(properties.index(i)) + '_' + str(requests.index(j)) + '.csv')
    print(response['rows'])
    print(data_frame)
#'''

# -----> Authorization GA <-----
scope = 'https://www.googleapis.com/auth/analytics.readonly'

flow = flow_from_clientsecrets('D:\\Work\\Python Scripts\\client_secrets.json', scope, redirect_uri = 'http://localhost')
storage = Storage('D:\\Work\\Python Scripts\\analytics_credentials.dat')
credentials = storage.get()
if not credentials or credentials.invalid:
  auth_uri = flow.step1_get_authorize_url()
  webbrowser.open(auth_uri)
  auth_code = input('Enter the auth code: ')
  credentials = flow.step2_exchange(auth_code)
  storage.put(credentials)
  
# Getting GA service
http = httplib2.Http()
http = credentials.authorize(http)
service = build('analytics', 'v4', http = http, discoveryServiceUrl = ('https://analyticsreporting.googleapis.com/$discovery/rest'))

# Request parameters to GA LP
'''
request = {
    'reportRequests': [
    {
      'viewId': 'integer',
      'pageSize': '20001',
      'dateRanges': [{'startDate':'2018-12-01', 'endDate':'2019-02-28'}, {'startDate':'2017-12-01', 'endDate':'2018-02-28'}],
      'metrics': [{'expression':'ga:sessions'}],
      'orderBys': [{'fieldName': 'ga:sessions', 'sortOrder': 'DESCENDING'}],
      'dimensions': [{'name':'ga:landingPagePath'}],
      #'dimensionFilterClauses': [{'filters': [{'dimensionName': 'ga:landingPagePath', 'operator': 'REGEXP', 'expressions': ['^(blog\.|kb\.)*selectel.ru']}]}]
                      }
    ]
}
#'''

# Request parameters to GA PV
'''
request = {
    'reportRequests': [
    {
      'viewId': 'integer',
      'pageSize': '50001',
      'dateRanges': [{'startDate':'2018-12-01', 'endDate':'2019-02-28'}, {'startDate':'2017-12-01', 'endDate':'2018-02-28'}],
      'metrics': [{'expression':'ga:uniquePageviews'},{'expression':'ga:entranceRate'},{'expression':'ga:exitRate'}],
      'orderBys': [{'fieldName': 'ga:uniquePageviews', 'sortOrder': 'DESCENDING'}],
      'dimensions': [{'name':'ga:pagePath'}],
      #'dimensionFilterClauses': [{'filters': [{'dimensionName': 'ga:pagePath', 'operator': 'REGEXP', 'expressions': ['^(blog\.|kb\.)*selectel.ru']}]}]
                      }
    ]
}
#'''

# Request parameters to GA previous PV
'''
request = {
    'reportRequests': [
    {
      'viewId': 'integer',
      'pageSize': '50001',
      'dateRanges': [{'startDate':'2018-12-01', 'endDate':'2019-02-28'}],
      'metrics': [{'expression':'ga:pageviews'}],
      'orderBys': [{'fieldName': 'ga:pageviews', 'sortOrder': 'DESCENDING'}],
      'dimensions': [{'name':'ga:pagePath'},{'name':'ga:previousPagePath'}],
      #'dimensionFilterClauses': [{'filters': [{'dimensionName': 'ga:pagePath', 'operator': 'REGEXP', 'expressions': ['^(blog\.|kb\.)*selectel.ru']}]}]
                      }
    ]
}
#'''

# Query to GA with property
'''
response = service.reports().batchGet(body = request).execute()
data_frame = pandas.DataFrame(data = response['reports'][0]['data']['rows'])
data_frame.to_csv('D:\\Work\\Python Scripts\\Result\\analytics.csv')
print(response['reports'][0]['data']['rows'])
print(data_frame)
#'''

# -----> Yandex API Query <-----
# ID: string
# Пароль: string
# Callback URL: http://localhost
# Авторизация: https://oauth.yandex.ru/authorize?response_type=token&client_id=string
# Токены: #access_token=string&token_type=bearer&expires_in=15552000

# Query attributes
'''
ym:s:startURLPathFull
ym:s:<attribution>SearchPhrase
ym:s:<attribution>SearchEngine
ym:s:<attribution>TrafficSource
ym:s:visits
'''

# Request query scheme
'''
https://api-metrika.yandex.ru/stat/v1/data.csv ?
metrics=<string> {metrics=ym:s:visits}
& dimensions=<string> {dimensions=ym:s:<attribution>SearchEngine,ym:s:startURLPathFull,ym:s:<attribution>SearchPhrase}
& date1=<string> {date1=2015-01-01}
& date2=<string> {date2=2015-01-01}
& limit=<integer> {limit=10000}
& filters=<string> {filters=ym:s:<attribution>TrafficSource=='organic'}
& offset=<integer> 
& ids=<int,int,...> {ids=2138128}
'''

# Request parameters to YM
'''
request = {
  'id': 'id=integer',
  'preset': 'preset=sources_search_phrases',
  'dimensions': 'dimensions=ym:s:<attribution>SearchEngine,ym:s:startURLPathFull,ym:s:<attribution>SearchPhrase',
  'metrics': 'metrics=ym:s:visits',
  'filters': 'filters=ym:s:TrafficSource==\'organic\'',
  'date1': 'date1=2018-01-01',
  'date2': 'date2=2019-02-20',
  'limit': 'limit=10000',
}
#'''

# Query to YM with property
'''
headers = {'Authorization': 'OAuth String'}
url = ['https://api-metrika.yandex.ru/stat/v1/data?' + '&' +
  request['id'] + '&' +
  request['preset'] + '&' +
  #request['dimensions'] + '&' +
  request['metrics'] + '&' +
  request['filters'] + '&' +
  request['date1'] + '&' +
  request['date2'] + '&' +
  request['limit']
]

response = requests.request('GET', url = url[0], headers = headers)
response.encoding = 'utf-8'
response.text
data = json.loads(response.text)
data_frame = json_normalize(data['data'])
data_frame.to_csv('D:\\Google API\\Result\\metrika.csv')
print(data_frame)
#'''
