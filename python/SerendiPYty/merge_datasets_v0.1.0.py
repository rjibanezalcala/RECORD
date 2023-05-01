# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 15:23:41 2022
Last updated Tue Dec 20 2022
v0.1.0

@author: Raquel Ibáñez Alcalá

Script to import and relate the events in a trial contained in the dataset 
created by the RECORDpy library, the animal tracking dataset created by a
Bonsai workflow, which tracks a rat on the RECORD arena, and the dataset
containing calcium cell traces created by the Inscopix post-processor.

Microcontroller events happen asynchronously from the Bonsai data stream (for
the Inscopix recording system only), thus some fuzzy logic must be implemented
to relate the two datasets. The same is currently true between the cell traces
recorded by Inscopix and the trial events. We want to relate behaviour to
neuronal activity, thus it is importnt that these three datasets are connected.

The output of this script will be the index of the row in the Bonsai dataset
and the cell trace dataset that most closely matches each trial event
timestamp. Two files will be outputted; one corresponding to the connection
between the trial events (dfEvents) and the Bonsai dataset (dfTrack), and
another between the trial events and the Inscopix dataset (dfTrace).
"""

import pandas as pd
import datetime as dt
from datetime import datetime as dtt
import dateutil.parser as dparser
import pytz
import numpy as np
import ast
# Datetime data
import datetime
import pytz
###############################################################################

""" Definition of variables
 To implement fuzzy timestamp comparisons, I need to know what the
 sampling rate is for the Bonsai dataset, this will help in finding
 the Bonsai timestamps that are as close as possible to each event. This can
 found either by subtracting one Bonsai timestamp from the other, which will
 yield the relative sampling rate, or if it is known, by taking the inverse of
 the camera's sampling rate (the FPS) to find the absolute sampling rate since
 Bonsai will only sample once the camera captures a video frame.
"""
# Paths to input files (must be CSV file).
# __TRIAL_PATH = "example_data/heihein L1_Mon-Nov-28-2022_12-48-53_events.csv"
# __BONSA_PATH = "example_data/Bonsai_rat_tracking_2022-11-28T12_51_40.csv"

## Elsa
__TRIAL_PATH = "example_data/InscopixData/Elsa/ElsaL2_Fri-Dec-09-2022_17-36-41_events.csv"
__BONSA_PATH = "example_data/InscopixData/Elsa/Bonsai_rat_tracking_2022-12-09T17_37_10.csv"

__TRACE_PATH = "example_data/InscopixData/Elsa/ElsaL2_MockCellTraces.csv"
__TRAEV_PATH = "example_data/InscopixData/Elsa/ElsaL2_MockEvents.csv"

__METADATA_PATH = "example_data/InscopixData/Elsa/ElsaL2_Fri-Dec-09-2022_17-36-41_metadata.txt"
##

## Bunny
# __TRIAL_PATH = "example_data/InscopixData/Bunny/Bunny2_Fri-Feb-03-2023_14-45-38_events.csv"
# __BONSA_PATH = "example_data/InscopixData/Bunny/Bonsai_rat_tracking_2023-02-03T14_46_32.csv"

# __TRACE_PATH = "example_data/InscopixData/Bunny/bunny 2.3.23 behavior 10 trials.csv"
# __TRAEV_PATH = "example_data/InscopixData/Bunny/bunny 2.3.23 behavior 10 trials events.csv"

# __METADATA_PATH = "example_data/InscopixData/Bunny/Bunny2_Fri-Feb-03-2023_14-45-38_metadata.txt"
##

client_fps = 30              # Camera's FPS setting (set by camera driver).
abs_s_rate = 1/client_fps    # Absolute sampling rate in seconds, dictated by camera's FPS setting.
rel_s_rate_b = 'NaN'         # Relative sampling rate in seconds, dictated by the time delta between two adjacent timestamps.
rel_s_rate_i = 'NaN'
# Relative sampling rate will be calculated after data has been parsed.

# Timezone data is needed to localise timezone-naive timestamps. This is
# because timezone-naive and timezone-aware datetime objects cannot be
# compared.
gmt_tz = pytz.timezone('GMT')
local_tz = pytz.timezone("US/Mountain")
# All the column names containing timestamps are defined here. Could have
# softcoded this too, but for now this serves as a quick reference.
ts_data = [
            # Trial timestamps and information
            "trial_start"     ,
            "trial_end"       ,
            # Events
            "play_tone"       ,
            "first_reset"     ,
            "mcu_timer_start" ,
            "trial_start_cue" ,
            "offer_presented" ,
            "reward_delivery" ,
            "last_reset"      ,
            "mcu_timer_stop"  ,
            "decision_ts"     ,
            # MCU responses and acknowledgements
            "first_reset_ack"      ,
            "mcu_timer_start_ack"  ,
            "trial_start_cue_ack"  ,
            "offer_presented_ack"  ,
            "reward_delivery_ack"  ,
            "last_reset_ack"       ,
            "mcu_timer_stop_ack"   
          ]

###############################################################################

""" Import data 
 Data is imported into pandas dataframes for processing. 
"""
print("Importing data...")
### Extract metadata ###
file = open(__METADATA_PATH,'r')
file.seek(0)
data = file.readlines()
file.close()

# Parse metadata into dictionary
metadata = dict()
# Metadata compatibility section 1 for previous versions (pre-pyTrials version 0.3.3)
for line in data:
    substring = line.replace('\n', '').split(":", 1)
    if substring[0] == "created":
        substring[0] = "sessionstart"
    elif substring[0] == "cost_inten":
        substring[0] = "costlevels"
        substring[1] = ast.literal_eval(substring[1])
        substring[1] = str(list(substring[1].values()))
    elif substring[0] == "P_lvls":
        substring[0] = "costprobabilities"
    elif substring[0] == "reward_lvls":
        substring[0] = "rewardlevels"
        substring[1] = ast.literal_eval(substring[1])
        substring[1] = str(list(substring[1].values()))
    elif substring[0] == "P_fdrs":
        substring[0] = "rewardprobabilities"
    elif substring[0] == "T_inter-trial":
        substring[0] = "t_intertrial"
    elif substring[0] == "T_decision":
        substring[0] = "t_decision"
    elif substring[0] == "T_feeding":
        substring[0] = "t_feeding"
    elif substring[0] == "duration":
        substring[0] = "sessionduration"
    elif substring[0] == "subject_name":
        substring[0] = "subjectid"
    elif substring[0] == "avail_fdrs":
        substring[0] = "avail_reward"
# End compatibility section 1
    metadata.update({substring[0]: substring[1]})
# Metadata compatibility section 2 for previous versions (pre-pyTrials version 0.3.3)
metadata.setdefault('subjecthealth', 'Undefined')
metadata.setdefault('subjectweight', 'Undefined')
metadata.setdefault('recordingtype', 'Undefined')
metadata.setdefault('notes', '')
# End compatibility section 1

### Extract events data ###
dfEvents = pd.read_csv(__TRIAL_PATH)

### Extract behaviour tracking data ###
dfTrack = pd.read_csv(__BONSA_PATH)

### Extract cell traces data ###
dfTrace = pd.read_csv(__TRACE_PATH, header=1)
# dfTrace = pd.DataFrame()

### Extract cell event data ###
dfTraev = pd.read_csv(__TRAEV_PATH)
# dfTraev = pd.DataFrame()

### Create new dataframe that will contain all combined data ###
if dfTrace.empty or dfTraev.empty:
    dfTrialsToTrack = pd.DataFrame(columns=ts_data)
else:
    dfTrialsToTrack = pd.DataFrame(columns=ts_data+["trial_index"])
    dfTrialsToTrace = pd.DataFrame(columns=ts_data+["trial_index"])
    dfTrialsToEvent = pd.DataFrame(columns=ts_data+["trial_index"])

###############################################################################

""" Parse timstamp data
 Timestamps in both datasets need to be parsed. It is possible timestamps are
 not timezone aware in one dataframe but are aware in the other, which impedes
 comparisons between the two. In this section, I localise event timestamps
 if they are timezone naive, and parse Bonsai timestamps to convert them from
 having 7 microsecond digits to 6. This will overwrite the two dataframes so
 I can work on them further, but the files will remain intact.
"""
print("\n\nParsing timstamp data in trial event dataset, please wait...")
# Check if trial event timestamps are in the old format
old_format = True
test_str = dfEvents["trial_start"].loc[dfEvents["trial_start"].index[0]]
try:
    old_format = bool(dtt.strptime(test_str, "%d-%B-%Y %H:%M:%S.%f"))
except ValueError:
    old_format = False
# Localise event timestamps to make them timezone-aware
if old_format:
    for key in ts_data:
        dfEvents[key] = pd.to_datetime(dfEvents[key], format="%d-%B-%Y %H:%M:%S.%f").dt.tz_localize(local_tz)
else:
    for key in ts_data:
        dfEvents[key] = pd.to_datetime(dfEvents[key], format="%Y-%m-%dT%H:%M:%S.%f%z")

print("\n\nParsing timstamp data in Bonsai spatial dataset, please wait...")
# Parse Bonsai timestamps since it'll likely have 7 microsecond digits instead of 6.
for value in dfTrack[["Timestamp"]].itertuples():
    dfTrack.at[value[0],"Timestamp"] = dparser.parse(str(value[1]), fuzzy=True)
dfTrack["Timestamp"] = pd.to_datetime(dfTrack["Timestamp"], format="%Y-%m-%dT%H:%M:%S.%f%z")

print("\n\nParsing timstamp data in Inscopix dataset, please wait...")
# Convert Unix timestamps to timezone-aware datetime objects
for value in dfTrace[["Time(s)/Cell Status"]].itertuples():
    # For some reason, when converting the timestamp to datetime, the local
    # timezone is automatically applied, or seems to be. I circumvent this by
    # specifying the offset for the GMT timezone upon conversion, then
    # replacing the timezone information on that timestamp with the local one.
    new_timestamp = dtt.fromtimestamp(dfTrace.at[value[0],"Time(s)/Cell Status"], tz=gmt_tz)\
        .replace(tzinfo=local_tz)
    dfTrace.at[value[0],"Time(s)/Cell Status"] = new_timestamp
    
###############################################################################

""" Calculate relative sampling rate
 Take the average time delta between all adjacent datapoints. I prefer using
 the relative sampling rate to find events because this is the actual rate
 in the data, using this might make the results more exact, though it is
 possible that is makes no difference as both this value and the absolute rate
 end up being very similar.
"""
print("\n\nCalculating relative sampling rate of track data...: ", end='')
deltas = list()
for i in range (0,len(dfTrack)-1):
    deltas.append(dfTrack["Timestamp"].loc[dfTrack["Timestamp"].index[i+1]]\
                  - dfTrack["Timestamp"].loc[dfTrack["Timestamp"].index[i]])

avg_delta_b = np.mean(deltas)
rel_s_rate_b = avg_delta_b.microseconds/1000000 # Divide to convert microseconds to seconds.
print(rel_s_rate_b)

print("\n\nCalculating relative sampling rate of cell trace data...: ", end='')
deltas = list()
for i in range (0,len(dfTrace)-1):
    deltas.append(dfTrace["Time(s)/Cell Status"].loc[dfTrace["Time(s)/Cell Status"].index[i+1]]\
                  - dfTrace["Time(s)/Cell Status"].loc[dfTrace["Time(s)/Cell Status"].index[i]])

avg_delta_i = np.mean(deltas)
rel_s_rate_i = avg_delta_i.microseconds/1000000 # Divide to convert microseconds to seconds.
print(rel_s_rate_i)

###############################################################################

# """ Divide Bonsai data into trials
#  This is where some fuzzy logic is implemented. I first extract the timestamp
#  at which a trial started from the 'trial_start' column in the events dataframe
#  and the time at which the trial stops from the 'trial_end' column. Then I look
#  for timestamps in the Bonsai dataframe that are greater than the start
#  timestamp minus C times the sampling rate (absolute), and lesser than the end
#  timestamp plus C times the sampling rate.
# """
# print("\r\n\nDividing track data into trials...")
# # Find start and end of trial in Bonsai data
# for n in range(0,len(dfEvents)):
#     x0 = dfEvents["trial_start"].loc[dfEvents["trial_start"].index[n]] # Start
#     x1 = dfEvents["trial_end"].loc[dfEvents["trial_end"].index[n]]     # End
#     print("\r\n\nTrial", n+1, "start:", x0, "\r\nTrial",n+1, "end  :", x1)
#     # Copy this data block into a new dataframe
#     trial1 = dfTrack.loc[(dfTrack["Timestamp"] >= x0-(avg_delta*2))\
#                          & (dfTrack["Timestamp"] <= x1+(avg_delta*2))]
    
#     print("\r\n\n", trial1)

###############################################################################

""" Find trial events in Bonsai dataframe 
  Here I iterate through each trial in the events dataframe, then for each key
  that I know contains timestamp data, I try to find the three Bonsai/Inscopix
  datapoints that mostly closely match with each event's timestamp. Here I
  sharpen my search from 2 times the relative sampling rate to only 1 times
  that rate.
"""
print("\n\nFinding trial events in both databases...")
# Start identifying where each event is in the Bonsai data
i = 1
# For every row (as a named tuple) in the dfEvents dataframe...
for row in dfEvents.itertuples():
    # Convert row to dictionary.
    dict_row = row._asdict()
    print("\n\n### Trial", i, "###")
    # Then, for every key in that dictionary...
    for key, value in dict_row.items():
        # If the key-value pair is a timestamp...
        if isinstance(value, dt.date):
            # Find all timestamps in Bonsai data that fall between the event
            # timestamp plus/minus one times the timedelta. Record the rows
            # where these timestamps are located.
            ind_b = dfTrack.loc[(dfTrack["Timestamp"] >= value-(avg_delta_b))\
                                & (dfTrack["Timestamp"] <= value+(avg_delta_b))]
            ind_i = dfTrace.loc[(dfTrace["Time(s)/Cell Status"] >= value-(avg_delta_i))\
                                & (dfTrace["Time(s)/Cell Status"] <= value+(avg_delta_i))]
            print("Found instances for key", key, ":", end=" ")
            # The result is a short dataframe containing only the found rows.
            # The actual indices need to be extracted from this, so extract all
            # the indices in this dataframe and convert them to a list.
            print(list(ind_b["Timestamp"].index[0:len(ind_b)]), "in track",\
                  list(ind_i["Time(s)/Cell Status"].index[0:len(ind_i)]), "in trace.")
            # Update the new dataframe that will be exported later with this
            # list
            dfTrialsToTrack.loc[i, key] = list(ind_b["Timestamp"].index[0:len(ind_b)])
            dfTrialsToTrack.loc[i,"trial_index"] = i
            dfTrialsToTrace.loc[i, key] = list(ind_i["Time(s)/Cell Status"].index[0:len(ind_i)])
            dfTrialsToTrace.loc[i,"trial_index"] = i
        else:
            # If the key-value pair is not a timestamp, just skip.
            pass
    # Then move on to the next row.
    i += 1

# The final result is a new dataframe where each column is an event, each row
# is a trial, and each cell is the list of indices where that event was found
# in the Bonsai data!
#print("\r\n\n", dfTrialsToTrack)

###############################################################################

""" Export CSV files
This section just exports the generated dataframes into CSV files, but first
I add the trial_index column from the events dataframe so that there is some
context in the new files.
"""
timezone = pytz.timezone('US/Mountain')
now = timezone.localize(datetime.datetime.now())
subjectname = metadata.get("subjectid", "Rat")
path = "example_data/InscopixData/"+subjectname+"/"
# Export the produced dataframes into CSV files.
dfTrialsToTrack.to_csv(path+subjectname+"_TrialToBonsai_"+now.strftime('%a-%b-%d-%Y_%H-%M-%S_%z')+".csv", index=False)
dfTrialsToTrace.to_csv(path+subjectname+"_TrialToInscopix_"+now.strftime('%a-%b-%d-%Y_%H-%M-%S_%z')+".csv", index=False)

###############################################################################


# #bonsaiTs = dfTrack[["Timestamp"]].apply(pd.to_datetime, format="%Y-%m-%dT%H:%M:%S.%f%z")
# bonsaiTs = dfTrack[["Timestamp"]]
# trialStart = dfEvents[["trial_start"]]

# x = trialStart["trial_start"].loc[trialStart.index[3]]
# y = bonsaiTs["Timestamp"].loc[bonsaiTs.index[2145]]



# print(x, isinstance(x, dt.date))
# print(y, isinstance(y, dt.date))

# print(x > y)
# print(x < y)
# print(x == y)





###############################################################################
# # Localise event timestamps
# tz = timezone("US/Mountain")
# for value in dfEvents[["trial_start"]].itertuples():
#     trialStart.at[value[0],"trial_start"] = tz.localize(trialStart.at[value[0],"trial_start"])
