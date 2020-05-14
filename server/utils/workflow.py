from django.conf import settings
import time
import requests
import hashlib
import traceback
import json

class WorkFlowAPiRequest(object):
    def __init__(self,token=settings.WORKFLOW_TOKEN, appname=settings.WORKFLOW_APP, username='admin', workflowurl=settings.WORKFLOW_URL):
        self.token = token
        self.appname = appname
        self.username = username
        self.workflowurl = workflowurl
    
    def getrequestheader(self):
        timestamp = str(time.time())[:10]
        ori_str = timestamp + self.token
        signature = hashlib.md5(ori_str.encode(encoding='utf-8')).hexdigest()
        headers = dict(signature=signature, timestamp=timestamp, appname=self.appname, username=self.username)
        return headers

    def getdata(self,parameters=dict(),method='get',url='/api/v1.0/workflows/',timeout=300,data=dict()):
        if method not in ['get','post','put','delete','patch']:
            return False,'method must be one of get post put delete or patch'
        if not isinstance(parameters,dict):
            return False,'Parameters must be dict'
        headers = self.getrequestheader()
        try:
            r = getattr(requests,method)('{0}{1}'.format(self.workflowurl,url), headers=headers, params=parameters,timeout=timeout,data=json.dumps(data))
            result = r.json()
            return True,result
        except:
            return False,traceback.format_exc()

# ins = WorkFlowAPiRequest()
# print (ins.getdata(parameters=dict(username='admin', per_page=20, name=''),method='get',url='/api/v1.0/workflows'))