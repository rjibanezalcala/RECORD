# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 14:47:47 2023
Last updated Tue Jan 25 2022
v0.0.0

@author: Raquel
"""

# Data wrangling
import pandas as pd
import numpy as np
# Error handling
from pandas.core.groupby.groupby import DataError
# Timestamp processing
import datetime as dt
from datetime import datetime as dtt
import dateutil.parser as dparser
import pytz


class Dlink:
    def __init__(self, client_fps=30, local_tz="US/Mountain"):
        # client_fps: Camera's FPS setting (set by camera driver).
        self.abs_s_rate = 1/client_fps  # Absolute sampling rate in seconds, dictated by camera's FPS setting.
        self.rel_s_rate_b = None        # Relative sampling rate in seconds, dictated by the time delta between two adjacent timestamps.
        # Relative sampling rate will be calculated after data has been parsed.
        
        # Timezone data is needed to localise timezone-naive timestamps. This is
        # because timezone-naive and timezone-aware datetime objects cannot be
        # compared and it is preferred to have timezone information to avoid
        # data insconsistencies.
        self.gmt_tz = pytz.timezone('GMT')
        self.local_tz = pytz.timezone(local_tz)
        
        # All the column names containing timestamps are defined here. Could have
        # softcoded this too, but for now this serves as a quick reference.
        self.ts_data = [
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
                    "extsys_on"       ,
                    "extsys_off"      ,
                    # MCU responses and acknowledgements
                    "first_reset_ack"      ,
                    "mcu_timer_start_ack"  ,
                    "trial_start_cue_ack"  ,
                    "offer_presented_ack"  ,
                    "reward_delivery_ack"  ,
                    "last_reset_ack"       ,
                    "mcu_timer_stop_ack"   ,
                    "extsys_on_ack"        ,
                    "extsys_off_ack"
                  ]
        
    def find_time_data(self, dataframe):
        result = list()
        
        # For every row (as a named tuple) in the dataframe...
        for row in dataframe.itertuples():
            # Convert row to dictionary.
            dict_row = row._asdict()
            # Then, for every key in that dictionary...
            for key, value in dict_row.items():
                # If the key-value pair is a timestamp...
                if isinstance(value, dt.date):
                    if key not in result:
                        # Record the key name into list
                        result.append(key)
        return result
        
    def localize_timestamp(self, dataframe, ts_columns, ts_format="%d-%B-%Y %H:%M:%S.%f"):
        print("\nParsing timstamp data in dataset, please wait...")
        # Localise event timestamps to make them timezone-aware
        try:
            for key in ts_columns:
                try:
                    dataframe[key] = pd.to_datetime(dataframe[key], format=ts_format).dt.tz_localize(self.local_tz)
                except:
                    dataframe[key].replace(
                            to_replace=['Null', 'null', 'None', 'none'], 
                            value=pd.NaT,
                            inplace=True, 
                            limit=None, 
                            regex=False, 
                            method='pad')
                    dataframe[key] = pd.to_datetime(dataframe[key], format=ts_format).dt.tz_localize(self.local_tz)
            
            return True
        
        except DataError as error:
            print(error)
            
            return False
        
    def tsstrings_to_timestamp(self, dataframe, ts_columns, ts_format="%Y-%m-%dT%H:%M:%S.%f%z"):
        try:
            for key in ts_columns:
                if key in self.ts_data:
                    if "null" in map(str.lower, dataframe[key].to_list()):
                        dataframe[key].replace(
                                to_replace=['Null', 'null', 'None', 'none'], 
                                value=pd.NaT,
                                inplace=True, 
                                limit=None, 
                                regex=False)
                    dataframe[key] = pd.to_datetime(dataframe[key], format=ts_format)
                else:
                    pass
            
            return True
        except Exception as error:
            print(error)
            
            return False
        
    def parse_timestamps(self, dataframe, ts_column="Timestamp", ts_format="%Y-%m-%dT%H:%M:%S.%f%z"):
        # Parse timestamps to known format.
        try:
            for value in dataframe[[ts_column]].itertuples():
                dataframe.at[value[0],ts_column] = dparser.parse(str(value[1]), fuzzy=True)
            
            dataframe[ts_column] = pd.to_datetime(dataframe[ts_column], format=ts_format)
            
            return True
        
        except Exception as error:
            print(error)
            
            return False
        
    def tsunix_to_timestamp(self, dataframe, ts_column="Time(s)/Cell Status", ts_format="%Y-%m-%dT%H:%M:%S.%f%z"):
        # Convert Unix timestamps to timezone-aware datetime objects
        try:
            for value in dataframe[[ts_column]].itertuples():
                # For some reason, when converting the timestamp to datetime, the local
                # timezone is automatically applied, or seems to be. I circumvent this by
                # specifying the offset for the GMT timezone upon conversion, then
                # replacing the timezone information on that timestamp with the local one.
                # new_timestamp = dtt.fromtimestamp(dataframe.at[value[0],ts_column], tz=self.gmt_tz)\
                #     .replace(tzinfo=self.local_tz)
                new_timestamp = dtt.utcfromtimestamp(dataframe.at[value[0],ts_column])
                new_timestamp = self.local_tz.localize(new_timestamp)
                dataframe.at[value[0],ts_column] = new_timestamp
                
            return True
            
        except DataError as error:
            print(error)
            
            return False
    
    def get_timedelta(self, dataframe, column):
        deltas = list()
        for i in range (0,len(dataframe)-1):
            deltas.append(dataframe[column].loc[dataframe[column].index[i+1]]\
                          - dataframe[column].loc[dataframe[column].index[i]])

        avg_delta = np.mean(deltas)
        rel_s_rate = avg_delta.microseconds/1000000 # Divide to convert microseconds to seconds.
        
        return avg_delta, rel_s_rate
    
    def divide_to_events(self, dfEvents, dfTarget, delta, dfResult,
                         ts_column="Timestamp", print_results=True):
        # Start identifying where each event is in the Bonsai data
        i = 1
        # For every row (as a named tuple) in the dfEvents dataframe...
        for row in dfEvents.itertuples():
            # Convert row to dictionary.
            dict_row = row._asdict()
            if print_results:
                print("\r\n### Trial", i, "###")
            # Then, for every key in that dictionary...
            for key, value in dict_row.items():
                # If the key-value pair is a timestamp...
                if isinstance(value, dt.date):
                    # Find all timestamps in Bonsai data that fall between the event
                    # timestamp plus/minus one times the timedelta. Record the rows
                    # where these timestamps are located.
                    ind = dfTarget.loc[(dfTarget[ts_column] >= value-(delta))\
                                        & (dfTarget[ts_column] <= value+(delta))]
                    if print_results:
                        print("Found instances for key", key, ":", end=" ")
                        # The result is a short dataframe containing only the found rows.
                        # The actual indices need to be extracted from this, so extract all
                        # the indices in this dataframe and convert them to a list.
                        print(list(ind[ts_column].index[0:len(ind)]), "in target dataframe")
                    # Update the new dataframe that will be exported later with this
                    # list
                    dfResult.loc[i, key] = list(ind[ts_column].index[0:len(ind)])
                    dfResult.loc[i,"trial_index"] = i
                else:
                    # If the key-value pair is not a timestamp, just skip.
                    pass
            # Then move on to the next row.
            i += 1
            
    def rename_columns(self, dataframe, ignore, suffix="_ptrs"):
        # Renames all columns in the dataframe to include the suffix parameter
        for column in dataframe.columns:
            if column in ignore:
                pass
            else:
                dataframe.rename(columns = {column:column+suffix}, inplace = True)
    
        
# dconn = Dlink(client_fps=30, local_tz="US/Mountain")

# __TRIAL_PATH = "../example_data/InscopixData/Elsa/ElsaL2_Fri-Dec-09-2022_17-36-41_events.csv"
# __BONSA_PATH = "../example_data/InscopixData/Elsa/Bonsai_rat_tracking_2022-12-09T17_37_10.csv"
# __TRACE_PATH = "../example_data/InscopixData/Elsa/ElsaL2_MockCellTraces.csv"

# """ Import data 
#  Data is imported into pandas dataframes for processing. 
# """
# try:
#     print("Importing data...")
#     ### Extract events data ###
#     dfEvents = pd.read_csv(__TRIAL_PATH)
#     print("Trial event data imported!")
    
#     ### Extract behaviour tracking data ###
#     dfTrack = pd.read_csv(__BONSA_PATH)
#     print("Positional tracking data imported!")
    
#     ### Extract calcium imaging data ###
#     dfTrace = pd.read_csv(__TRACE_PATH, header=1)
#     print("Calcium trace data imported!")
# except Exception as error:
#     print(error, "One or more data files were not imported.")

# else:
#     ### Create new dataframe that will contain all combined data ###
#     dfTrialsToTrack = pd.DataFrame(columns=dconn.ts_data+["trial_index"])
#     dfTrialsToTrace = pd.DataFrame(columns=dconn.ts_data+["trial_index"])


# """ Parse timstamp data
#  Timestamps in both datasets need to be parsed. It is possible timestamps are
#  not timezone aware in one dataframe but are aware in the other, which impedes
#  comparisons between the two. In this section, I localise event timestamps
#  if they are timezone naive, and parse Bonsai timestamps to convert them from
#  having 7 microsecond digits to 6. This will overwrite the two dataframes so
#  I can work on them further, but the files will remain intact.
# """
# print("\nParsing timstamp data in trial event dataset, please wait...")
# try:
#     dconn.tsstrings_to_timestamp(dfEvents, ts_columns=dconn.ts_data, ts_format="%Y-%m-%dT%H:%M:%S.%f%z")
#     print("Trial event timestamps parsed successfully!")
    
#     dconn.parse_timestamps(dfTrack, ts_column="Timestamp", ts_format="%Y-%m-%dT%H:%M:%S.%f%z")
#     print("Bonsai timestamps parsed successfully!")

#     dconn.tsunix_to_timestamp(dfTrace, ts_column="Time(s)/Cell Status", ts_format="%Y-%m-%dT%H:%M:%S.%f%z")
#     print("Inscopix timestamps parsed successfully!")

# except Exception as error:
#     print(error, ". Could not parse timestamps in one or more files.")


# """ Calculate relative sampling rate
#  Take the average time delta between all adjacent datapoints. I prefer using
#  the relative sampling rate to find events because this is the actual rate
#  in the data, using this might make the results more exact, though it is
#  possible that is makes no difference as both this value and the absolute rate
#  end up being very similar.
# """
# print("\nCalculating relative sampling rate and average timedelta across all datapoints...")
# Bavg_delta, Brsrate = dconn.get_timedelta(dfTrack, column="Timestamp")
# print("Bonsai relative sampling rate:", Brsrate)
# print("Bonsai absolute sampling rate:", dconn.abs_s_rate)

# Iavg_delta, Irsrate = dconn.get_timedelta(dfTrace, column="Time(s)/Cell Status")
# print("Inscopix relative sampling rate:", Irsrate)

# """ Find trial events in dataframe 
#   Here I iterate through each trial in the events dataframe, then for each key
#   that I know contains timestamp data, I try to find the three Bonsai/Inscopix
#   datapoints that mostly closely match with each event's timestamp. Here I
#   sharpen my search from 2 times the relative sampling rate to only 1 times
#   that rate.
# """
# print("\nFinding trial events in Bonsai dataset...")
# dconn.divide_to_events(dfEvents, dfTrack, Bavg_delta, dfTrialsToTrack, ts_column="Timestamp", print_results=False)

# print("\nFinding trial events in Inscopix dataset...")
# dconn.divide_to_events(dfEvents, dfTrace, Iavg_delta, dfTrialsToTrace, ts_column="Time(s)/Cell Status", print_results=False)

# # Find timestamp data
# tss = dconn.find_time_data(dfEvents)
# print(tss)