#!/usr/bin/python3

# Hive API v6 Status Script
# Uploads to Econ CMS
# Dan Chaplin

import requests
import json
import sys

#Define Output File
uploaddata = {}

# Open config file
#json_data=open('/home/dan/hive/config.json')
json_data=open(sys.path[0]+'/config.json')
config = json.load(json_data)
json_data.close()
# Read Info
config = config["config"]
username = config[0]["username"]
password = config[1]["password"]
apikey = config[2]["apikey"]
node = config[3]["node"]
emonurl = config[4]["emonURL"]
hiveurl = config[5]["hiveURL"]
maxboostdif = config[6]["difBoost"]
maxboosttime = config[7]["timeBoost"]
boosttempcut = config[8]["tempCut"]
boosttimecut = config[9]["timeCut"]


#Login to Hive API
url = hiveurl+"/auth/sessions"
payload = {
  "sessions": [{
    "username":username,
    "password":password,
    "caller": "WEB"
  }]
}
headers = {'Content-Type': 'application/vnd.alertme.zoo-6.1+json','Accept': 'application/vnd.alertme.zoo-6.1+json','X-Omnia-Client': 'Hive Web Dashboard'}
r = requests.post(url, data=json.dumps(payload), headers=headers).json()

#Get Session ID
SessID = r['sessions'][0]['sessionId']
SessID = str(SessID)

#Get Node Data
url = hiveurl+"/nodes"
headers = {'Content-Type': 'application/vnd.alertme.zoo-6.1+json','Accept': 'application/vnd.alertme.zoo-6.1+json','X-Omnia-Client': 'Hive Web Dashboard','X-Omnia-Access-Token': '%s' % SessID}

r = requests.get(url, headers=headers).json()

#Extract Relevant Data
for index in range(len(r)):
        devtype = r['nodes'][index]['name']
        if devtype.startswith("Thermostat"):
                hwcheck = r['nodes'][index]['attributes']['supportsHotWater']['reportedValue']
                if hwcheck:
                        hwstatus = r['nodes'][index]['attributes']['stateHotWaterRelay']['reportedValue']
                        if hwstatus.startswith("OFF"):
                                uploaddata["hwStatus"] = 0
                        else:
                                uploaddata["hwStatus"] = 1
                        hwbooststat = r['nodes'][index]['attributes']['activeHeatCoolMode']['reportedValue']
                        if hwbooststat.startswith("BOOST"):
                                uploaddata["hwBoost"] = 1
                        else:
                                uploaddata["hwBoost"] = 0
                else:
                        heatstatus = r['nodes'][index]['attributes']['stateHeatingRelay']['reportedValue']
                        if heatstatus.startswith("OFF"):
                                uploaddata["heatStatus"] = 0
                        else:
                                uploaddata["heatStatus"] = 1
                        heattarget = r['nodes'][index]['attributes']['targetHeatTemperature']['reportedValue']
                        uploaddata["tempTarget"] = heattarget
                        heatnow = r['nodes'][index]['attributes']['temperature']['reportedValue']
                        uploaddata["tempNow"] = heatnow
                        heatbooststat = r['nodes'][index]['attributes']['activeHeatCoolMode']['reportedValue']
                        if heatbooststat.startswith("BOOST"):
                                uploaddata["heatBoost"] = 1
                                #If BOOST active check is it set too high
                                if heattarget - maxboostdif > heatnow:
                                    newtarget = heattarget - boosttempcut
                                    url = r['nodes'][index]['href']
                                    mypayloaddata = {"nodes": [{
                                        "attributes": {
                                            "targetHeatTemperature": {
                                                "targetValue": newtarget
                                            }
                                        }
                                    }]}
                                    #Set new BOOST target
                                    r = requests.put(url, headers=headers, data=json.dumps(mypayloaddata))
                                else:
                                    newtarget = heattarget
                                #If BOOST active check not too long
                                boostlength = r['nodes'][index]['attributes']['scheduleLockDuration']['reportedValue']
                                if boostlength > maxboosttime:
                                    newboostlength = boostlength - boosttimecut
                                    url = r['nodes'][index]['href']
                                    mypayloaddata = {"nodes": [{
                                        "attributes": {
                                            "activeHeatCoolMode": {
                                                "targetValue": "BOOST"
                                            },
                                            "targetHeatTemperature": {
                                                "targetValue": newtarget
                                            },
                                            "scheduleLockDuration": {
                                                "targetValue": newboostlength
                                            }                                          
                                        }
                                    }]}
                                    #Set new BOOST duration
                                    r = requests.put(url, headers=headers, data=json.dumps(mypayloaddata))
                        else:
                                uploaddata["heatBoost"] = 0

#Convert to JSON
upload_json = json.dumps(uploaddata)

#Upload Data
url = emonurl+node+'&fulljson='+upload_json+'&apikey='+apikey
print(url)
#requests.post(url)
