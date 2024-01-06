#from tkinter.ttk import INTEGER #tkinter.tix
from flask import Flask, request, Response, jsonify
from decimal import Decimal
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from mftool import Mftool
from yahoo_fin import stock_info
import yfinance as yf
import openai
import json
import requests
from datetime import  datetime ,timedelta
import GChatF
import re


app = Flask(__name__)
my_global_array = []
my_global_user =[]  

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/SparSolutionsWebhook", methods=['POST','GET'])
def SparSolutionsWebhook():    
    ProcessJson(json.dumps(request.json))
    
    return Response(status=200)

def get_price(url):
     
    # getting the request from url
    while True:
        data = requests.get(url)
        if data.status_code >= 200 and data.status_code <= 299:
            break

    # converting the text
    #print(data.text)
    
    pattern = r'var\s+commodityJSON\s*=\s*({.*?});'
    match = re.search(pattern, data.text, re.DOTALL)


    if match:
        commodity_json_data = match.group(1)
        parsed_data = json.loads(commodity_json_data)
        pure_gold_price =parsed_data['allCommodityPrices']['GOLD_RATE']['prices']['PURE']
        print(str(pure_gold_price))
        return str(pure_gold_price)
    else:
        return("Variable 'commodityJSON' not found or data extraction failed.")

def replace_comma_within_quotes(text, from1, to1):
    
    in_quotes = False
    result = ""
    for char in text:
        if char == from1:
            in_quotes = not in_quotes
        if in_quotes and char == str(to1):
            result += ''
        else:
            result += char
    return result

def createuser():
    payload = ""
    payload = "{"
    payload = payload +  chr(ord(chr(34))) +   "reportParameters" +  chr(ord(chr(34))) + ": ["
    payload = payload + "{"
    payload = payload + chr(34) + "reportUri" + chr(34) + ":" + chr(34) + "urn:replicon-tenant:98073d810644455fa6ba949a335590fb:report:5dc92ae3-199d-40a0-8fb9-b978a18aa5eb" + chr(34) + ","
    payload = payload + chr(34) + "filterValues" + chr(34) + ": [],"
    payload = payload + chr(34) + "outputFormatUri"  + chr(34) + ":" + chr(34) + "urn:replicon:report-output-format-option:csv"  + chr(34) 
    payload = payload + "}]}"

    headers = {'content-type': 'application/json','charset':'UTF-8','Authorization':'Bearer uSXfPcCJM0WEPR9YrMJmXQEAOTgwNzNkODEwNjQ0NDU1ZmE2YmE5NDlhMzM1NTkwZmI','X-Replicon-Application':'Sparsolutions1_ReportExtraction_1.0'}

    r=requests.post(url="https://na6.replicon.com/SPARSolutions/services/reportService1.svc/CreateReportGenerationBatch",data=payload,headers=headers)
    data = r.json()
    reporturi=data["d"]

    payload = ""
    payload = "{" + chr(34) + "batchUri" + chr(34) + ":" +  chr(34) + reporturi + chr(34) + "}"
    headers = {'content-type': 'application/json','charset':'UTF-8','Authorization':'Bearer uSXfPcCJM0WEPR9YrMJmXQEAOTgwNzNkODEwNjQ0NDU1ZmE2YmE5NDlhMzM1NTkwZmI','X-Replicon-Application':'Sparsolutions1_ReportExtraction_1.0'}

    r=requests.post(url="https://na6.replicon.com/SPARSolutions/services/reportService1.svc/ExecuteBatchInBackground",data=payload,headers=headers)
    data = r.json()

    while True:
        payload = ""
        payload = "{" + chr(34) + "batchUri" + chr(34) + ":" +  chr(34) + reporturi + chr(34) + "}"
        headers = {'content-type': 'application/json','charset':'UTF-8','Authorization':'Bearer uSXfPcCJM0WEPR9YrMJmXQEAOTgwNzNkODEwNjQ0NDU1ZmE2YmE5NDlhMzM1NTkwZmI','X-Replicon-Application':'Sparsolutions1_ReportExtraction_1.0'}

        r=requests.post(url="https://na6.replicon.com/SPARSolutions/services/reportService1.svc/GetBatchStatus",data=payload,headers=headers)
        data = r.json()

        testdata=data["d"]["executionState"]
        testdata=testdata.split(":")
        
        if testdata[3] != "succeeded":
            continue
        else:
            break

    payload = ""
    payload = "{" + chr(34) + "reportGenerationBatchUri" + chr(34) + ":" +  chr(34) + reporturi + chr(34) + "}"
    headers = {'content-type': 'application/json','charset':'UTF-8','Authorization':'Bearer uSXfPcCJM0WEPR9YrMJmXQEAOTgwNzNkODEwNjQ0NDU1ZmE2YmE5NDlhMzM1NTkwZmI','X-Replicon-Application':'Sparsolutions1_ReportExtraction_1.0'}

    r=requests.post(url="https://na6.replicon.com/SPARSolutions/services/reportService1.svc/GetReportGenerationBatchResults",data=payload,headers=headers)
    data = r.json()
    jdata=""
    jdata=data["d"]["reportGenerationResults"][0]["payload"]
    jdata=jdata.split("\r\n")

    final=''
    for a in jdata:
        final1 = replace_comma_within_quotes(a,'"',',')
        for char in final1:
            if char == '"':
                final = final + ''
            else:
                final = final + str(char)
        row = []
        final=final.split(",")   

        for final1 in final:
            row.append(final1)

        my_global_user.append(row)
        final=''


def GetLinkID(Stremail): 
    count=0
    while count <= len(GChatF.Gchat)-1:
            
        if str(GChatF.Gchat[count][0]).lower()==Stremail.lower():
            #return 'https://chat.googleapis.com/v1/spaces/gcKgBEAAAAE/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=bqUUjMLSBefiDkPXHqpHnSqKtRCOZpjs2mcbGr4_pnY%3D','Alaa Alkhafaji'
            return str(GChatF.Gchat[count][1]),str(GChatF.Gchat[count][3])
            break
        count=count+1
    return '',''
    #return link, df2['Id']



def createproject():
    payload = ""
    payload = "{"
    payload = payload +  chr(ord(chr(34))) +   "reportParameters" +  chr(ord(chr(34))) + ": ["
    payload = payload + "{"
    payload = payload + chr(34) + "reportUri" + chr(34) + ":" + chr(34) + "urn:replicon-tenant:98073d810644455fa6ba949a335590fb:report:f6b2c381-1273-4cb6-8a89-5737f1721756" + chr(34) + ","
    payload = payload + chr(34) + "filterValues" + chr(34) + ": [],"
    payload = payload + chr(34) + "outputFormatUri"  + chr(34) + ":" + chr(34) + "urn:replicon:report-output-format-option:csv"  + chr(34) 
    payload = payload + "}]}"

    headers = {'content-type': 'application/json','charset':'UTF-8','Authorization':'Bearer uSXfPcCJM0WEPR9YrMJmXQEAOTgwNzNkODEwNjQ0NDU1ZmE2YmE5NDlhMzM1NTkwZmI','X-Replicon-Application':'Sparsolutions1_ReportExtraction_1.0'}

    r=requests.post(url="https://na6.replicon.com/SPARSolutions/services/reportService1.svc/CreateReportGenerationBatch",data=payload,headers=headers)
    data = r.json()
    reporturi=data["d"]

    payload = ""
    payload = "{" + chr(34) + "batchUri" + chr(34) + ":" +  chr(34) + reporturi + chr(34) + "}"
    headers = {'content-type': 'application/json','charset':'UTF-8','Authorization':'Bearer uSXfPcCJM0WEPR9YrMJmXQEAOTgwNzNkODEwNjQ0NDU1ZmE2YmE5NDlhMzM1NTkwZmI','X-Replicon-Application':'Sparsolutions1_ReportExtraction_1.0'}

    r=requests.post(url="https://na6.replicon.com/SPARSolutions/services/reportService1.svc/ExecuteBatchInBackground",data=payload,headers=headers)
    data = r.json()

    while True:
        payload = ""
        payload = "{" + chr(34) + "batchUri" + chr(34) + ":" +  chr(34) + reporturi + chr(34) + "}"
        headers = {'content-type': 'application/json','charset':'UTF-8','Authorization':'Bearer uSXfPcCJM0WEPR9YrMJmXQEAOTgwNzNkODEwNjQ0NDU1ZmE2YmE5NDlhMzM1NTkwZmI','X-Replicon-Application':'Sparsolutions1_ReportExtraction_1.0'}

        r=requests.post(url="https://na6.replicon.com/SPARSolutions/services/reportService1.svc/GetBatchStatus",data=payload,headers=headers)
        data = r.json()

        testdata=data["d"]["executionState"]
        testdata=testdata.split(":")
        
        if testdata[3] != "succeeded":
            continue
        else:
            break

    payload = ""
    payload = "{" + chr(34) + "reportGenerationBatchUri" + chr(34) + ":" +  chr(34) + reporturi + chr(34) + "}"
    headers = {'content-type': 'application/json','charset':'UTF-8','Authorization':'Bearer uSXfPcCJM0WEPR9YrMJmXQEAOTgwNzNkODEwNjQ0NDU1ZmE2YmE5NDlhMzM1NTkwZmI','X-Replicon-Application':'Sparsolutions1_ReportExtraction_1.0'}

    r=requests.post(url="https://na6.replicon.com/SPARSolutions/services/reportService1.svc/GetReportGenerationBatchResults",data=payload,headers=headers)
    data = r.json()
    jdata=""
    jdata=data["d"]["reportGenerationResults"][0]["payload"]
    jdata=jdata.split("\r\n")

    final=''
    for a in jdata:
        final1 = replace_comma_within_quotes(a,'"',',')
        for char in final1:
            if char == '"':
                final = final + ''
            else:
                final = final + str(char)
        row = []
        final=final.split(",")   

        for final1 in final:
            row.append(final1)

        my_global_array.append(row)
        final=''

def getEmail(Projname,Usermail):
    row=0
    finalo=''
    
    final =''
    final1=replace_comma_within_quotes(Projname,'"',',')
    for char in final1:
        if char == '"':
            final = final + ''
        else:
            final = final + str(char)
    Projname=final
    
    while row <= len(my_global_array)-1:
        if str(my_global_array[row][0]).lower() == Projname.lower():
            finalo= my_global_array[row][2]
            break
        row=row+1

    if finalo=='':
        row=0
        while row <= len(my_global_user)-1:
            if str(my_global_user[row][0]).lower()==Usermail.lower():
                finalo= my_global_user[row][1]
                break
            row=row+1
    
    return finalo


def format_row(row):
    pname, email, hrs = row
    text = f"{pname:<60} | {hrs:^5}"
    return text

def ProcessJson(jsonload):
    json_load=json.loads(jsonload)
    tsstatus=json_load['approvalStatusUri']
    tsstatus=tsstatus.split(':')[-1]
    if tsstatus=='waiting':
        payload = ""
        print(str(json_load['timesheet']['uri']))
        payload = "{" + chr(34) + "timesheetUri" + chr(34) + ":" +  chr(34) + str(json_load['timesheet']['uri']) + chr(34) + "}"
        headers = {'content-type': 'application/json','charset':'UTF-8','Authorization':'Bearer uSXfPcCJM0WEPR9YrMJmXQEAOTgwNzNkODEwNjQ0NDU1ZmE2YmE5NDlhMzM1NTkwZmI','X-Replicon-Application':'Sparsolutions1_ReportExtraction_1.0'}

        r=requests.post(url="https://na6.replicon.com/sparsolutions/services/timesheetService1.svc/GetTimesheetDetails",data=payload,headers=headers)
        data = r.json()
        startDate_d = data['d']['dateRange']['startDate']['day']
        startDate_m = data['d']['dateRange']['startDate']['month']
        startDate_y = data['d']['dateRange']['startDate']['year']
        sdate=datetime(int(startDate_y), int(startDate_m), int(startDate_d))
        sd= str(startDate_d) + "-" + sdate.strftime('%b') + "-" + str(startDate_y)

        EndDate_d = data['d']['dateRange']['endDate']['day']
        EndDate_m = data['d']['dateRange']['endDate']['month']
        EndDate_y = data['d']['dateRange']['endDate']['year']
        edate=datetime(int(EndDate_y), int(EndDate_m), int(EndDate_d))
        ed = str(EndDate_d) + "-" + edate.strftime('%b') + "-" + str(EndDate_y)
        
        Owner = ""
        Owner = data['d']['owner']['displayText']
        loginname = data['d']['owner']['loginName']
        TimeSheetPeriod = sd + ' - ' + ed

        payload = ""
        payload = "{" + chr(34) + "timesheetUri" + chr(34) + ":" +  chr(34) + str(json_load['timesheet']['uri']) + chr(34) + "}"
        headers = {'content-type': 'application/json','charset':'UTF-8','Authorization':'Bearer uSXfPcCJM0WEPR9YrMJmXQEAOTgwNzNkODEwNjQ0NDU1ZmE2YmE5NDlhMzM1NTkwZmI','X-Replicon-Application':'Sparsolutions1_ReportExtraction_1.0'}

        r=requests.post(url="https://na6.replicon.com/sparsolutions/services/timesheetService1.svc/GetTimesheetSummary",data=payload,headers=headers)
        data = r.json()
        final_data=[]
        for projdata in data['d']['actualsByProject']:
            row1=[]
            #print(projdata['project']['displayText'])
            if len(my_global_array)==0:
                createproject()
            if len(my_global_user)==0:
                createuser()
            row1.append(projdata['project']['displayText'])
            row1.append(getEmail(str(projdata['project']['displayText']),loginname))
            row1.append(projdata['totalTimeDuration']['hours'] + (projdata['totalTimeDuration']['minutes'])/60)
            #print(str(projdata['totalTimeDuration']['hours'] + (projdata['totalTimeDuration']['minutes'])/60))
            #row1.append('1')
            final_data.append(row1)
        
        unique_values = {row[1] for row in final_data}        
        #for row in final_data:           
            #unique_values.append({row[1]})

            
        for value in unique_values:
            matching_rows=[]
            messagetosend=''
            messagetosendc=''
            for row in final_data:
                if row[1]==value:
                    #matching_rows.append(row)
                    messagetosendc = messagetosendc + format_row(row) + '\n'
            
            link=''
            id=''
            link,id=(GetLinkID(value))

            messagetosend = "Hey " + id + ", " + Owner + ' has submited a TimeSheet' + '\n'
            messagetosend = messagetosend + 'For the period ' + TimeSheetPeriod  + '\n'
            messagetosend1 = f"{'Project Name':<60} | {'Hours':^5}" + '\n'
            messagetosend1 = messagetosend1 + ("-" * 73) + '\n'
            finalm = messagetosend + '\n' + messagetosend1 + messagetosendc
            finalm = '```' + finalm + '```'
            data={"text":finalm}                  
            
            data=json.dumps(data)        
            headers = {'content-type': 'application/json','charset':'UTF-8'}
            if link!="":
                r=requests.post(url=link,data=data,headers=headers)

            
            #print(finalm)
            #matching_rows=[row for row in final_data if row[1] == value]

        
        final_data=[]
        


@app.route("/sms", methods=['POST','GET'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Fetch the message
    msg = request.form.get('Body')
    #fromnum = request.form.get('from_')
    fromnum = request.values.get('From_', None)

    # Create reply
    resp = MessagingResponse()
    resp.message("You said: {} and from the number:{}".format(msg,fromnum))

    return str(resp)

@app.route("/whatsapp", methods=['POST','GET'])
def SendWhatsapp():
    #account_sid = os.environ['TWILIO_ACCOUNT_SID']
    #auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client('AC4eadcaab15de04fd55b492882d9b66a8', '904e9db1587ece5b595545cc865c1972')
    to = request.args.get('to')
    msg = request.args.get('msg')
    #print(to)
    #print(msg)
    message = client.messages.create(
                              body=msg, #'Hello there!',
                              from_='whatsapp:+14155238886',
                              to='whatsapp:+' + to
                          )
    return message.sid
    #print(message.sid)

@app.route("/OpenAI", methods=['POST','GET'])
def OpenAIAsk():
    openai.api_key = "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"
    model_engine = "text-davinci-003"
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=request.args.get('ask'),
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    response = completion.choices[0].text
    return response

@app.route("/Test")
def Test():
    return "Hello, Debashish!"

@app.route("/Gold", methods=['POST','GET'])
def Gold():
    api_key = "goldapi-1125c016lmdvcm6p-io"
    symbol = "XAU"
    curr = "INR"
    date = ""

    url = f"https://www.goldapi.io/api/{symbol}/{curr}{date}"
    url= "https://api.metalpriceapi.com/v1/latest?api_key=5d263475ae0b57c0c4d33619b92ee545&base=INR&&currencies=XAU"
    
    headers = {
        "x-access-token": api_key,
        "Content-Type": "application/json"
    }    
    """ 
        Below working but using https://www.bankbazaar.com
        response = requests.get(url)
        response.raise_for_status()
        key_to_extract = "rates"
        result = response.text

        parsed_data =json.loads(result, parse_float=Decimal)

        a = 1/Decimal(parsed_data['rates']['XAU'])
        print(str(a))
        a = a / Decimal(31.1034768)
        #if a < 0:
   """
    url = "https://www.bankbazaar.com/gold-rate-maharashtra.html"
    a=get_price(url)
    return str(a)        

    
@app.route("/MF/<code>",methods=['POST','GET'])
def MF(code):
    mf = Mftool()
    q = mf.get_scheme_quote(str(code))
    return q['nav']

@app.route("/Stock/<code>",methods=['POST','GET'])
def Stock(code):
    #price = stock_info.get_live_price(code)
    #return str(price)
    tickerData = yf.Ticker(code)
    hist = tickerData.history(period="max")
    hist=hist['Close'].iloc[-1]
    return str(hist)

if __name__ == "__main__":
    my_global_array = []
    my_global_user =[]    
    app.run(debug=True)