import requests
import os
import json
from dotenv import load_dotenv
from webexteamssdk import WebexTeamsAPI

"Getting environmental variables"
load_dotenv()
BOTEMAIL = os.getenv("TEAMS_BOT_EMAIL")
TEAMSTOKEN = os.getenv("WEBEX_TEAMS_ACCESS_TOKEN")
TETOKEN = os.getenv("TETOKEN")
BOTAPPNAME = os.getenv("TEAMS_BOT_APP_NAME")
TEwebexRoodId = os.getenv("TE_WEBEX_ROOM_ID")
base_url = "https://api.thousandeyes.com/v6/"


"Initializing API objects"
apiWebex = WebexTeamsAPI(access_token=TEAMSTOKEN)

TE_headers = {
        "Authorization": "Bearer" + TETOKEN,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

"Seting messages to sent to Webex room"
coreMessage = '''
Alert ID = {0}
Test Name = {1}
URL = {2}
Alert Rule = {3}
Start Date = {4}
Severity = {5}
'''
agentMessage = '''           
    AgentName = {0}
    MetricAtStart = {1}
    AgentStatus = {2}
'''

"Getting a dictionari with alertID:TestID via API call"
def TEalerts():
    res = requests.get(url=base_url+"alerts", headers=TE_headers)
    data = json.loads(res.text)
    IDlist = {}
    MultipleID = []

    for alert in data["alert"]:
        IDlist[str(alert["alertId"])] = str(alert["testId"])
        MultipleID.append(IDlist)

    return MultipleID


"Getting information from the alerts/alertID API"
def alertDetail(alertID):
    
    res = requests.get(url=base_url+"alerts/"+alertID , headers=TE_headers)
    data = json.loads(res.text)
    info = {}
    agentInfoarray=[]
    agentInfo={}
    for alert in data["alert"]:
        info["startDate"] = alert["dateStart"]
        info["severity"] = alert["severity"]
        for agent in alert["agents"]:
            agentInfo["name"] = agent["agentName"]
            agentInfo["metric"] = agent["metricsAtStart"]
            if agent["active"] == 1:
                agentInfo["status"] = "Active"
            else:
                agentInfo["status"] = "Cleared"
            agentInfoarray.append(agentInfo)
            agentInfo = {}
            
        info["agent"] = agentInfoarray
    
    return info

def testDetail(testId):
    #print(str(testId) + "  Test detail")
    res = requests.get(url=base_url+"tests/"+testId, headers=TE_headers)
    data = json.loads(res.text)
    info = {}
    alertrules=[]
    for element in data["test"]:
        info["testName"] = element["testName"]
        info["url"] = element["url"]
        for element2 in element["alertRules"]:
            alertrules.append(element2["ruleName"])
            
        info["ruleName"]=alertrules
        
    
    return info

# # # # # # # # # # # # # # # # # # # # # # # # #

def getWebexInfo(element):
    
    message = ""
    ruleName = []

    AlertID  = element[0]
    TestID = element[1]
    testInfo =testDetail(TestID)
    testName = testInfo["testName"]
    testUrl = testInfo["url"]
    if len(testInfo["ruleName"]) == 1:
        testAlertRule=testInfo["ruleName"]
    else:
        for element in testInfo["ruleName"]:
            ruleName.append(element)
        testAlertRule = ruleName
    alertInfo = alertDetail(AlertID)
    alertStartDate = alertInfo["startDate"]
    alertSeverity= alertInfo["severity"]
    for agent in alertInfo["agent"]:
        message += agentMessage.format(agent["name"], agent["metric"], agent["status"]) 
    coreInfo = coreMessage.format(AlertID, testName, testUrl, testAlertRule, alertStartDate, alertSeverity)+"Impacted Agents:"+ message 
    
    

    return coreInfo

    
def sendMessage(element):
    message = getWebexInfo(element)
    apiWebex.messages.create(roomId=TEwebexRoodId, text=message)

if __name__ == "__main__":
    #print(alertDetail("197245574"))
    
    getWebexInfo(TEalerts()[-1])
    
    
