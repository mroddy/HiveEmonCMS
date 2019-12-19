# HiveEmonCMS

A python script to monitor the Hive thermostat and upload data to emoncms.org for analysis mainly as the standard web interface lacks much in the way of historical data
Addtional functions to manage the boost setting and precent it being set too high or too long

To use edit config.json with the following details....
username - Your Hive username,
password - Your Hive password,
apikey - Your write API key for emoncms.org,
node - The node name for the Hive device on emoncms.org,
emonURL - The upload URL for emoncms.org (should not need changing),
hiveURL - The URL for accessing the Hive API (should not need changing)

The following settings are optional and to enable the abilty to limit the heat ruse and duration of the boost function....
diffBoost - Set this to the maximum increase in temperature a boost should achieve,
timeBoost - Set this to the maximum time a boost should run,
tempCut - Set how quickly the boost templerature is cut - a smaller number takes longer to cut but less likely to cut too low,
timeCut - Set hom quickly the boost duration is cut - again smaller number means longer to cut - I'd suggest setting to the same as the maximum boost duration
