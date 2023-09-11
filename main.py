import os
from dotenv import load_dotenv
from webexteamssdk import WebexTeamsAPI
import time
from funtions import *

"Getting environmental variables"
load_dotenv()
TEwebexRoodId = os.getenv("TE_WEBEX_ROOM_ID")
apiWebex = WebexTeamsAPI(access_token=TEAMSTOKEN)

"""
This Script Analize mutiple TE alerts
It analize a current list and provide information of new entries
"""
def trackChanges():
    current_list=[]
    while True:
        try: "Handles exception since the Current list is original empty and generate DICT exception"
            time.sleep(30)
            new_list=TEalerts()
            new_alerts = [item for item in new_list if item not in current_list] "Return a list of elements if there are new alerts"
            clear_alerts = [item for item in current_list if item not in new_list]"Return a list of elements if there are new clear alerts"
            
            if new_alerts:
                for alert in new_alerts[0].items(): "each element is a tuple"

                    apiWebex.messages.create(roomId=TEwebexRoodId, markdown= "New triggered alert")
                    sendMessage(alert)
                
            if clear_alerts:
                for alert in clear_alerts[0].items():"each element is a tuple"
                    apiWebex.messages.create(roomId=TEwebexRoodId, markdown= "Bellow alert is clear")
                    sendMessage(alert)
                
            current_list = new_list
        except:
            pass
trackChanges()
