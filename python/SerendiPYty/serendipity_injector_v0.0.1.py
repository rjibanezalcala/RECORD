# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 17:33:54 2023
Last updated 13-Feb-2023
v0.0.1

@author: Raquel J. Ibáñez Alcalá

Master script to be run when "injecting" Python trial (pytrial), Bonsai, and 
external system data (calcium trace, ephys, etc), along with their pointer
tables, into the Serendipity database.
This script is intended to be run as a placeholder for a proper graphical user
interface (GUI) and its goal is to do the job with minimal user input or
general involvement.
This script will take the contents of an adjacent folder,
parse them, possibly preprocess them (if the pointer table is not
available), and finally upload the data to a table in the Serendipity database.

"""
#%%
# Serendipity_lib
from serendipity_lib import Serendipity
# Tables for database
from serendipity_lib import Tables
# For linking datasets
from serendipity_lib import Dlink
# Data processing
import numpy as np
import pandas as pd
# SQL data upload
from sqlalchemy import create_engine
# Excel file export (for writing reference file)
import xlsxwriter as xlsx
# Date object handling
import datetime as dt
from datetime import datetime as dtt
import pytz
# System processes
import sys
import multiprocessing
import os
import glob
# Data parsing
import ast
#%%
###############################################################################
############################ Parameter Definitions ############################

# Unique ID for these files' session, will be built from metadata.
sessionid = ""

# Flags to indicate whether or not pointer files need to be created.
NEED_POINT = [False, False]

# Tables existing in database, datasets will be uploaded to their respective tables.
optogen_table = 'inscopix_table'
position_table = 'bonsai_table'
ephys_table = 'ephys_table'
trials_table = 'trial_table'
longreg_table = 'cellregistration_table'
subject_table = 'rattable'            # Existing table where all rat data is stored

query = ""
# Directory where files to be uploaded are contained.
WORKING_DIR = r"example_data/InscopixData/Bunny/3-31-23"

METADATA = None
TRIAL_EVENTS = None
POSITION_TRACK = None
CELL_TRACE = None
TRACE_EVENTS = None
PROPS = None
POSITION_PTRS = ""
TRACE_PTRS = ""

###############################################################################
############################## Object Definitions #############################

sdpty = Serendipity()
tcols = Tables()
dlink = Dlink(local_tz="US/Mountain")

###############################################################################
############################## Table Definitions ##############################

metadata_cols  =  tcols.housekeep\
                + tcols.rats\
                + tcols.session

trials_cols    =  tcols.tevents
                
optogen_cols   =  tcols.traces\
                + tcols.traevents
                              
position_cols  =  tcols.position

ephys_cols     =  tcols.ephys

appoptns = sdpty.parse_ini(section="injector")

###############################################################################
############################ Auto File Detection ##############################



# Detect metadata file
search_res = glob.glob(WORKING_DIR + appoptns.get('metadatawc'))
if len(search_res) == 1:
    METADATA = search_res[0]
# Detect trial events file
search_res = glob.glob(WORKING_DIR + appoptns.get('trialevwc'))
if len(search_res) == 1:
    TRIAL_EVENTS = search_res[0]
# Detect positional tracking file
search_res = glob.glob(WORKING_DIR + appoptns.get('positwc'))
if len(search_res) == 1:
    POSITION_TRACK = search_res[0]
# Detect cell trace file
search_res = glob.glob(WORKING_DIR + appoptns.get('celltrawc'))
if len(search_res) == 1:
    CELL_TRACE = search_res[0]
# Detect cell trace event file
search_res = glob.glob(WORKING_DIR + appoptns.get('cellevwc'))
if len(search_res) == 1:
    TRACE_EVENTS = search_res[0]
# Detect cell trace props file
search_res = glob.glob(WORKING_DIR + appoptns.get('celltrapropwc'))
if len(search_res) == 1:
    PROPS = search_res[0]
# Detect positional tracking pointers file 
search_res = glob.glob(WORKING_DIR + appoptns.get('positptrwc'))
if len(search_res) == 1:
    POSITION_PTRS = search_res[0]
# Detect cell trace pointers file
search_res = glob.glob(WORKING_DIR + appoptns.get('celltraptrwc'))
if len(search_res) == 1:
    TRACE_PTRS = search_res[0]

if not any([METADATA,TRIAL_EVENTS,POSITION_TRACK,CELL_TRACE,TRACE_EVENTS,PROPS]) is None:
    print("Some files were not found in the working directory, asking for user input.")
    file_list = os.listdir(WORKING_DIR)
    file_list_id = ['metadata (.txt)',
                    'trial events (.csv)',
                    'positional data (.csv)',
                    'cell trace data (.csv)',
                    'cell trace event data (.csv)',
                    'cell props data, enter 0 if file does not exist (.csv)']
    file_list = [f for f in file_list if os.path.isfile(WORKING_DIR+'/'+f)] #Filtering only the files.
    # print(*file_list, sep="\n")
    for f in range(len(file_list)):
        print(str(f+1)+". "+file_list[f])
    
    print("\nPlease select a file from the file list above that matches the following criteria by entering the file's list number:")
    for i,f in enumerate([METADATA,TRIAL_EVENTS,POSITION_TRACK,CELL_TRACE,TRACE_EVENTS,PROPS]):
        if f is None:
            file_index = input("\n"+file_list_id[i]+": ")
            if int(file_index) > 0:
                if i == 0: METADATA = WORKING_DIR +"/"+ file_list[int(file_index)-1]
                elif i == 1: TRIAL_EVENTS = WORKING_DIR +"/"+ file_list[int(file_index)-1]
                elif i == 2: POSITION_TRACK = WORKING_DIR +"/"+ file_list[int(file_index)-1]
                elif i == 3: CELL_TRACE = WORKING_DIR +"/"+ file_list[int(file_index)-1]
                elif i == 4: TRACE_EVENTS = WORKING_DIR +"/"+ file_list[int(file_index)-1]
                elif i == 5: PROPS = WORKING_DIR +"/"+ file_list[int(file_index)-1]
        else:
            pass    
        
###############################################################################
###############################################################################
#%%
""" #0 Check Database Connection
This section will check that the connection to the PostgreSQL database is
configured correctly. It will also check if the destination table exists.
This is done through a PostgresSQL query to the database. If the
table does not exist, an attempt will be made to create it.
"""
print("Checking database connection...")
if sdpty.connect():
    # Ask the database for version to check connection
    sdpty.get_version()
    print("\nDatabase connection was successful!")
    
else:
    print("\nConnection to database failed. Please check connection parameters.")
    sys.exit()


""" #1 Parse Incoming Files
This section attempts to read a folder and check if the necessary files are
present. This requires a standardised file naming convention. The files to
look for are AT LEAST the following:
    1. pytrial event table, produced by the RECORDpy trial scripts.
    2. Bonsai animal tracking table, produced by Bonsai running our animal
       tracking workflow.
    3. Cell trace data table, created by the an external post-processor
       (must contain timestamps in unix timestamp format).

Additionally, pointer information will be injected into the database. This
information is generated by running the above three files through the data
connector script, which is contained elsewhere in this project. If these files
are not rovided by the user, they will be generated by calling the
aforementioned script.
    a. pytrial events to positional animal tracking pointers
    b. pytrial events to cell trace data
    
The output of this section will be dataframes containing the information from
the above five files.

"""
#%%
# Import metadata...
try:
    print("\nImporting session metadata...", end="")
    file = open(METADATA,'r')
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
        if substring[0] in tcols.rats + tcols.housekeep + tcols.session:
            # Copy keys of interest (defined in tcols)
            metadata.update({substring[0]: substring[1]})
        else:
            # Skip keys that are not needed 
            pass
# Metadata compatibility section 2 for previous versions (pre-pyTrials version 0.3.3)
    metadata.setdefault('subjecthealth', 'Undefined')
    metadata.setdefault('subjectweight', 'Undefined')
    metadata.setdefault('recordingtype', 'Undefined')
    metadata.setdefault('notes', '')
# End compatibility section 1
# Create session id from metadata and add it
# 1. First letter of rat name
# 2. Rat ID no, from database
# 3. Recording type

# 3. Date and time of session as D%d%B%YT%H%M%S
# 4. Task type code (P2A, L1, L1L3, PAV, P1)
# 4. Genotype
# 5. Accute manipulation code (fd, sal, iso, pf, oxy, ghr#, alc#)
# 6. (optional, if 5 is oxy) Oxycodone manipulation code (NF, PF, GHR-S, GHR-ISO, GHR, GHR-2X, GHR-N)
    #sessionid = metadata.get('subjectid')[0] + str(metadata.get('subjectidnumber')) + 
    tasktype = ''
    accmanip = ''
    # Determine task type
    l = ast.literal_eval(metadata.get('costprobabilities'))
    # If subject health indicates an alcohol infusion task, indicate it with
    # 'P2A'
    if 'alcohol' in metadata.get('subjecthealth').lower():
        tasktype += 'P2A'
    else:
        # Go through list of cost probabilities and for every probability above 0,
        # indicate L0, L1, L2, or L3.
        for i in range(len(l)):
            if l[i] != 0:
                tasktype += 'L'+str(i)
    # If all probabilities are 0, making the string remain empty after the
    # process above, indicate pavlovian task
    if len(tasktype) == 0:
        str += 'PAV'
    metadata.update({'tasktypedone':tasktype})
                     
    # Determine the accute manipulation code
    if 'alcohol' in metadata.get('subjecthealth').lower():
        accmanip += 'alc'
    elif 'ghrelin' in metadata.get('subjecthealth').lower():
        accmanip += 'ghr'
    elif 'depr' in metadata.get('subjecthealth').lower():
        accmanip += 'fd'
    elif 'saline' in metadata.get('subjecthealth').lower():
        accmanip += 'sal'
    elif 'iso' in metadata.get('subjecthealth').lower():
        accmanip += 'iso'
    elif 'pre' in metadata.get('subjecthealth').lower():
        accmanip += 'pf'
    elif 'oxy' in metadata.get('subjecthealth').lower():
        accmanip += 'oxy'
    else:
        accmanip += 'nm'
    
    metadata.update({'accutemanipulation':accmanip})
    
except FileNotFoundError as error:
    print("failed!")
    print(error, "\nOne or more files were not found in folder. Please verify that files are in folder and comply with naming conventions.")
    sdpty.disconnect()
    sys.exit()
except IOError as error:
    print("failed!")
    print(error, "\nError: can\'t find file or read data")
    sdpty.disconnect()
    sys.exit()
else:
    print("success!")

## Query subject information from database
print("\nInformation for "+metadata.get('subjectid').lower()+" will be fetched from database via the following query:")
query = "SELECT * FROM "+ subject_table +" WHERE name='"+ metadata.get('subjectid').lower() +"';"
#query = "SELECT * FROM "+ subject_table +" WHERE name='"+ "jafar" +"';"
print(" ", query)
print("\nQuerying database...", end="")

try:
    subject_data = sdpty.query_database(query)
    if subject_data:
        print("success!")
        hit_length = len(subject_data)
        for item in subject_data:
            print(item)
        if hit_length > 1:
            print("Query for name/subjectid: '"+metadata.get('subjectid').lower()+"' returned "+hit_length+" hits.")
            print("  Defaulting to first result.")
        # Compare name in metadata vs name in database for sanity
        print("\nComparing name in metadata to name in database...", end="")
        if subject_data[0].get("name") == metadata.get("subjectid").lower():
            print("match!")
        else:
            print("mismatch!")
            raise Exception("[Query error 1] Subject name mismatch.\nPlease make sure that name in metadata '"+metadata.get("subjectid").lower()+"' is spelled correctly and matches name in database '"+subject_data[0].get("name")+"'.")
            print("\n\nExiting script.")
            sys.exit()
    else:
        print("failed!")
        raise Exception("[Query error 2] Query for name/subjectid: '"+metadata.get('subjectid').lower()+"' returned no hits.")
        # ASK TO MANUALLY ENTER INFORMATION
except Exception as e:
    print("  Query failed due to the following error:\n"+str(e))
    print("\nCannot continue with missing or mismatching subject information.\nExiting...")
    if sdpty.conn.closed == 0:
        sdpty.disconnect()
    sys.exit()

else:
    # If no errors are caught, copy this dictionary into metadata dictionary
    sessionid = metadata.get('subjectid').upper()\
                + str(subject_data[0].get('id'))\
                + dtt.strptime(metadata.get('sessionstart'), "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%y%m%dT%H%M%S")\
                + tasktype\
                + accmanip
    metadata.setdefault('sessionid', sessionid)
    print("\nGenerated session ID: " + sessionid)

    print("\nCopying queried subject information to dataframe...")
    for key in subject_data[0].keys():
        if key in tcols.rats:
            metadata.update({key: subject_data[0].get(key)})
        elif key == "id":
            metadata.update({"subjectidnumber": subject_data[0].get(key)})
        elif key == "name":
            metadata.update({"subjectid": subject_data[0].get(key)})
        else:
            print("  Key '"+key+"' skipped.")
    
    # Create dataframe based on the metadata.
    dfMetadata = pd.DataFrame([metadata], index=None)
    print("done!")
            
#%%
# Import main files...
try:
    print("\nImporting data from",r"'\files_for_upload'...")
    ### Extract events data ###
    print("  1. Trial events...", end="")
    dfEvents = pd.read_csv(TRIAL_EVENTS, skipinitialspace=True)
    if "reward_con" in dfEvents.columns:
        dfEvents = dfEvents.rename(columns={"reward_con":"reward_concentration"})
    dfEvents['extracolumn'] = "FFFFFFFFF"
    print("imported!")
    
    ### Extract behaviour tracking data ###
    print("  2. Positional data...", end="")
    dfTrack = pd.read_csv(POSITION_TRACK, skipinitialspace=True)
    print("imported!")
    
    ### Extract cell traces data ###
    print("  3. Cell trace data...", end="")
    # Find out how many columns exist in dataset
    with open(CELL_TRACE) as x:
        ncols = len(x.readline().split(','))
    # Import only the cell status and exclude the first column (timestamp)
    CellStatus = pd.read_csv(CELL_TRACE, usecols=range(1,ncols), skipinitialspace=True, skiprows=lambda x: x not in [0, 1]).to_dict('records')[0]
    # Import the actual trace data, but don't import the initial space before
    # the column names.
    dfTrace = pd.read_csv(CELL_TRACE, skipinitialspace=True, header=1)
    # Rename the first column to "Timestamp".
    dfTrace = dfTrace.rename(columns={"Time(s)/Cell Status":"Timestamp"})
    # Then rename all other columns to their respective cell name.
    i = 0
    for key in dfTrace.columns:
        if key != "Timestamp":
            dfTrace = dfTrace.rename(columns={key:list(CellStatus.keys())[i]})
            i += 1
    print("imported!")
    
    ### Extract cell event data ###
    print("  4. Cell trace events...", end="")
    dfTraev = pd.read_csv(TRACE_EVENTS, skipinitialspace=True)
    dfTraev = dfTraev.rename(columns={"Time (s)":"Timestamp"})
    print("imported!")
    
    ### Extract the props data as well, if it exists ###
    print("  5. Cell trace props...", end="")
    if PROPS is not None:
        dfProps = pd.read_csv(PROPS, skipinitialspace=True)
        print("imported!")
    else:
        dfProps = None
        print("not provided!")

except FileNotFoundError as error:
    print("failed!\n")
    print(error, "One or more files were not found in folder. Please verify that files are in folder and comply with naming conventions.")
    sdpty.disconnect()
    sys.exit()
except Exception as error:
    print("failed!\n")
    print(error)
    sdpty.disconnect()
    sys.exit()

else:
    # sys.exit()
    # If files exist and have been imported, parse the timestamps
    print("\nParsing timestamp data in imported datasets, please wait...")
    try:
        print("  1. Trial event timestamps...", end="")
        dlink.tsstrings_to_timestamp(dfEvents, ts_columns=dlink.ts_data, ts_format="%Y-%m-%dT%H:%M:%S.%f%z")
        print("parsed successfully!")
        
        print("  2. Positional timestamps...", end="")
        dlink.parse_timestamps(dfTrack, ts_column="Timestamp", ts_format="%Y-%m-%dT%H:%M:%S.%f%z")
        print("parsed successfully!")
       
        print("  3. Cell trace timestamps...", end="")
        dlink.tsunix_to_timestamp(dfTrace, ts_column="Timestamp", ts_format="%Y-%m-%dT%H:%M:%S.%f%z")
        print("parsed successfully!")
      
        print("  4. Cell trace event timestamps...", end="")
        dlink.tsunix_to_timestamp(dfTraev, ts_column="Timestamp", ts_format="%Y-%m-%dT%H:%M:%S.%f%z")
        print("parsed successfully!")
        
    except Exception as error:
        print("failed!\n")
        print(error, "\nCould not parse timestamps in one or more files.")
        sdpty.disconnect()
        sys.exit()

#%%
# Import data pointers, if available...
try:
    print("\nAttempting to import pointer data (1/2)...", end="")
    dfTrialsToTrack = pd.read_csv(POSITION_PTRS)
except FileNotFoundError as error:
    print("failed!\n")
    print(error, "Pointers for positional data were not found in folder.")
    print("\n  Pointer data between "+TRIAL_EVENTS+" and "+POSITION_TRACK+" will be created shortly.")
    NEED_POINT[0] = True
except Exception as error:
    print("failed!\n")
    print(error)
    sdpty.disconnect()
    sys.exit()
else:
    print("success!")
    
try:
    print("\nAttempting to import pointer data (2/2)...", end="")
    dfTrialsToTrace = pd.read_csv(TRACE_PTRS)
except FileNotFoundError as error:
    print("failed!\n")
    print(error, "Pointers for cell trace data were not found in folder.")
    print("\n  Pointer data between "+TRIAL_EVENTS+" and "+CELL_TRACE+" will be created shortly.")
    NEED_POINT[1] = True
except Exception as error:
    print("failed!\n")
    print(error)
    sdpty.disconnect()
    sys.exit()
else:
    print("success!")

""" # 1.5 Create pointer data if it does not exist
If no pointer data was found, this section will try to create it.

"""
#%%
i = 0
while(NEED_POINT[0] or NEED_POINT[1]):
    timezone = pytz.timezone('US/Mountain')
    if NEED_POINT[0]:
        print("\nCreating positional data pointers, please wait...")
        dlink = Dlink(client_fps=30)
        # Create pointer data beween trial events and positional data.
            
        ### Create new dataframe that will contain all combined data ###
        dfTrialsToTrack = pd.DataFrame(columns=dlink.ts_data+["trial_index"])
    
        print("\n  Calculating relative sampling rate and average timedelta across all datapoints...")
        avg_delta, rsrate = dlink.get_timedelta(dfTrack, column="Timestamp")
        print("  Dataset relative sampling rate:", rsrate)
        print("  Dataset absolute sampling rate:", dlink.abs_s_rate)
    
        print("\n  Finding trial events in dataset...")
        dlink.divide_to_events(dfEvents, dfTrack, avg_delta, dfTrialsToTrack, ts_column="Timestamp", print_results=False)
        #dlink.rename_columns(dfTrialsToTrack, ignore=["trial_index"])
        dfTrialsToTrack.add_suffix('_ptrs')
        print("Done!")
        
        # Export the produced dataframe into a CSV file.
        print("\nCreating data file in", WORKING_DIR)
        now = timezone.localize(dtt.now())
        FILENAME = WORKING_DIR+'/'+metadata.get('subjectid')+"_TrialToBonsai_"+now.strftime('%a-%b-%d-%Y_%H-%M-%S_%z')+".csv"
        dfTrialsToTrack.to_csv(FILENAME, index=False)
        
        # Double check that file exists in directory, if so, clear the flag.
        print("  Verifying that file was exported successfully...", end="")
        if os.path.isfile(FILENAME):
            print("success!")
            POSITION_PTRS = FILENAME
            NEED_POINT[0] = False
        else:
            print("failed!")
            print("There was a problem creating file, please verify that path to file is correct.")
            print("\nExiting script...")
            sdpty.disconnect()
            sys.exit()
            
    if NEED_POINT[1]:
        print("\nCreating cell trace data pointers, please wait...")
        dlink = Dlink(client_fps=20)
        # Create pointer data beween trial events and cell trace data.
        
        ### Create new dataframe that will contain all combined data ###
        dfTrialsToTrace = pd.DataFrame(columns=dlink.ts_data+["trial_index"])
        
        print("\n  Calculating relative sampling rate and average timedelta across all datapoints...")
        avg_delta, rsrate = dlink.get_timedelta(dfTrace, column="Timestamp")
        print("  Dataset relative sampling rate:", rsrate)
        print("  Dataset absolute sampling rate:", dlink.abs_s_rate)
    
        print("\n  Finding trial events in Inscopix dataset...")
        dlink.divide_to_events(dfEvents, dfTrace, avg_delta, dfTrialsToTrace, ts_column="Timestamp", print_results=False)    
        #dlink.rename_columns(dfTrialsToTrace, ignore=["trial_index"])
        dfTrialsToTrace.add_suffix('_ptrs')
        print("Done!")
        
        # Export the produced dataframe into a CSV file.
        print("\nCreating data file in", WORKING_DIR)
        now = timezone.localize(dtt.now())
        FILENAME = WORKING_DIR+'/'+metadata.get('subjectid')+"_TrialToInscopix_"+now.strftime('%a-%b-%d-%Y_%H-%M-%S_%z')+".csv"
        dfTrialsToTrace.to_csv(FILENAME, index=False)
        
        # Double check that file exists in directory, if so, clear the flag.
        print("  Verifying that file was exported successfully...", end="")
        if os.path.isfile(FILENAME):
            print("success!")
            TRACE_PTRS = FILENAME
            NEED_POINT[1] = False
        else:
            print("There was a problem creating file, please verify that path to file is correct.")
            print("\nExiting script...")
            sdpty.disconnect()
            sys.exit()
            
    i += 1
    if i >= 4:
        print("Pointer data could not be created. This could be due to a data error in either dataset.")
        sys.exit()
# End loop

#%%
""" #2 Create Serendipity Data Table
Here, the dataframes from the section above are processed and formatted in
accordance to the table(s) contained in the Serendipity database. The dataframe
where the data will be stored must follow the same format as the database
table.
Each row in the table will contain the metadata for one trial, and data under 
the columns that correspond to position or cell trace data will be lists of
values from their corresponding datasets. These data must be divided into
trials to keep the general "1 trial per row" theme.

"""
print("\nFitting cell trace data to new table, please wait...", end="")
# Take a row from dfTrace, excluding the timestamp, and convert it into
# dict, do the same with dfTraev at the same row index.
# Onto new dataframe, copy the Timestamp column from dfTrace, then at
# 'CellTraces', add the dictionary row from dfTrace, and at 'CellEvent'
# add the dict row from dfTraev. Finally, at 'CellStatus' add the
# dfCellStatus row as a dictionary.
dfCells = pd.DataFrame(columns=optogen_cols, index=range(len(dfTrace)))
dfCells["timestamp"] = dfTrace["Timestamp"]
dfCells["cellstatus"] = dfCells["cellstatus"].apply(lambda x: CellStatus.copy())
if dfProps is not None:
    dfCells["props"] = str(dfProps.to_dict('records'))
else:
    dfCells["props"] = "NoData"
#dfCells["props"] = dfProps.to_dict('list')
for i in range(len(dfCells)):
    dfCells["celltrace"][i] = dfTrace.loc[:, dfTrace.columns!='Timestamp'].iloc[i].to_dict()
    if len(dfTraev.columns) == 3:
        result = dfTraev.loc[(dfCells["timestamp"][i] == dfTraev["Timestamp"])].to_dict('index')
        if len(result) >= 1:
            for j in list(result.keys()):
                result[j].pop('Timestamp')
            dfCells["cellevent"].iloc[i] = str(result)
            
        else:
            dfCells["cellevent"].iloc[i] = "NoData"
    else:
        dfCells["cellevent"][i] = dfTraev.loc[:, dfTrace.columns!='Timestamp'].iloc[i].to_dict()
print("done!")

# Copy the metadata onto the position and cell trace 
print("\nCopying metadata to all data tables, please wait...")

print("  1. Joining metadata and trial event dataset...", end="")
dfPtrs = pd.DataFrame(columns=tcols.pointers[0:len(tcols.pointers)], index=range(len(dfEvents)))
for index in range(len(dfEvents)):
    # Create a new dataframe with the pointers inside a dictionary
    dfPtrs[tcols.pointers[0]][index] = dict(dfTrialsToTrack.iloc[index])
    dfPtrs[tcols.pointers[1]][index] = dict(dfTrialsToTrace.iloc[index])
dfEvents = pd.concat([dfEvents,\
                      dfPtrs],\
                      ignore_index=False, join='outer', axis=1)
dfEvents = pd.concat([dfEvents,\
                      dfMetadata.loc[dfMetadata.index.repeat(len(dfEvents))].reset_index(drop=True)],\
                      ignore_index=False, join='outer', axis=1)
dfEvents["localindex"] = dfEvents.index
print("done!")
    
print("  2. Joining metadata and cell trace dataset...", end="")
dfCells = pd.concat([dfCells,\
                     dfMetadata.loc[dfMetadata.index.repeat(len(dfCells))].reset_index(drop=True)],\
                     ignore_index=False, join='outer', axis=1)
dfCells["localindex"] = dfCells.index
print("done!")

print("  3. Joining metadata and position dataset...", end="")
dfTrack = pd.concat([dfTrack,\
                     dfMetadata.loc[dfMetadata.index.repeat(len(dfTrack))].reset_index(drop=True)],\
                     ignore_index=False, join='outer', axis=1)
dfTrack.columns = map(str.lower, dfTrack.columns)
dfTrack["localindex"] = dfTrack.index
print("done!")

# Validate all data
#%%
print("\nValidating data before uploading...")
upload_ok = {'trials':False, 'position':False, 'celltrace':False}

print("\n  Validating data keys in trials dataset")
dfstatus = [False,False]
i = 0
not_found = list()
errors = list(dfEvents.columns)
for key in metadata_cols + trials_cols + tcols.pointers:
    print("   "+str(i+1)+". "+key+"...", end="")   
    if key in dfEvents.columns and key in metadata_cols and dfEvents[key].count == len(dfEvents[key]):
        # Count non-null entries in metadata column, if all entries are not null, then data is good
        errors.pop(errors.index(key))
        print("OK")
    elif key in dfEvents.columns:
        print("OK")
        errors.pop(errors.index(key))
    elif key not in dfEvents.columns:
        print("Not found!")
        not_found.append(key)
    else:
        print("Error!")
    i += 1

if len(errors) > 0:
    print("\nThe following "+str(len(errors))+" data keys were found in the input data and are not part of the database table, or caused an error.", "Columns have been removed." if appoptns.get('droperrorcols').lower() in ["true", "1", "yes"] else "")
    print(errors)
    if appoptns.get('droperrorcols').lower() in ["true", "1", "yes"]:
        for key in errors:
            dfEvents = dfEvents.drop(key, axis=1)
        dfstatus[0] = True
else:
    dfstatus[0] = True
        
    
if len(not_found) > 0:
    print("\nThe following "+str(len(not_found))+" data keys were not found in the input data.", "Values were set to 'NotMeasured'." if appoptns.get('fillmissing').lower() in ["true", "1", "yes"] else "")
    print(not_found)
    if appoptns.get('fillmissing').lower() in ["true", "1", "yes"]:
        for key in not_found:
            if key in dlink.ts_data:
                dfEvents[key] = pd.NaT
            else:
                dfEvents[key] = "NotMeasured"
        dfstatus[1] = True
else:
    dfstatus[1] = True
            
upload_ok.update({'trials':np.bitwise_and.reduce(dfstatus)})
#%%
print("\n  Validating data keys in cell traces dataset")
dfstatus = [False,False]
i = 0
not_found = list()
errors = list(dfCells.columns)
for key in metadata_cols + optogen_cols:
    print("   "+str(i+1)+". "+key+"...", end="")   
    if key in dfCells.columns and key in metadata_cols and dfCells[key].count == len(dfCells[key]):
        # Count non-null entries in metadata column, if all entries are not null, then data is good
        errors.pop(errors.index(key))
        print("OK")
    elif key in dfCells.columns:
        print("OK")
        errors.pop(errors.index(key))
    elif key not in dfCells.columns:
        print("Not found!")
        not_found.append(key)
    else:
        print("Error!")
    i += 1

if len(errors) > 0:
    print("\nThe following "+str(len(errors))+" data keys were found in the input data and are not part of the database table, or caused an error.", "Columns have been removed." if appoptns.get('droperrorcols').lower() in ["true", "1", "yes"] else "")
    print(errors)
    if appoptns.get('droperrorcols').lower() in ["true", "1", "yes"]:
        for key in errors:
            dfCells = dfCells.drop(key, axis=1)
        dfstatus[0] = True
else:
    dfstatus[0] = True
        
    
if len(not_found) > 0:
    print("\nThe following "+str(len(not_found))+" data keys were not found in the input data.", "Values were set to 'NotMeasured'." if appoptns.get('fillmissing').lower() in ["true", "1", "yes"] else "")
    print(not_found)
    if appoptns.get('fillmissing').lower() in ["true", "1", "yes"]:
        for key in not_found:
            dfCells[key] = 'NotMeasured'
        dfstatus[1] = True
else:
    dfstatus[1] = True
            
upload_ok.update({'celltrace':np.bitwise_and.reduce(dfstatus)})
#%%
print("\n  Validating data keys in positional dataset")
dfstatus = [False,False]
i = 0
not_found = list()
errors = list(dfTrack.columns)
for key in metadata_cols + position_cols:
    print("   "+str(i+1)+". "+key+"...", end="")   
    if key in dfTrack.columns and key in metadata_cols and dfTrack[key].count == len(dfTrack[key]):
        # Count non-null entries in metadata column, if all entries are not null, then data is good
        errors.pop(errors.index(key))
        print("OK")
    elif key in dfTrack.columns:
        print("OK")
        errors.pop(errors.index(key))
    elif key not in dfTrack.columns:
        print("Not found!")
        not_found.append(key)
    else:
        print("Error!")
    i += 1

if len(errors) > 0:
    print("\nThe following "+str(len(errors))+" data keys were found in the input data and are not part of the database table, or caused an error.", "Columns have been removed." if appoptns.get('droperrorcols').lower() in ["true", "1", "yes"] else "")
    print(errors)
    if appoptns.get('droperrorcols').lower() in ["true", "1", "yes"]:
        for key in errors:
            dfTrack = dfTrack.drop(key, axis=1)
        
        dfstatus[0] = True
else:
    dfstatus[0] = True
        
    
if len(not_found) > 0:
    print("\nThe following "+str(len(not_found))+" data keys were not found in the input data.", "Values were set to 'NotMeasured'." if appoptns.get('fillmissing').lower() in ["true", "1", "yes"] else "")
    print(not_found)
    if appoptns.get('fillmissing').lower() in ["true", "1", "yes"]:
        for key in not_found:
            dfTrack[key] = 'NotMeasured'
        
        dfstatus[1] = True
else:
    dfstatus[1] = True

upload_ok.update({'position':np.bitwise_and.reduce(dfstatus)})

if appoptns.get('stringify').lower() in ["true", "1", "yes"]:
    print("\nStringifying data in tables, this could take a few moments...", end="")
    dfEvents = dfEvents.astype(str)
    dfTrack = dfTrack.astype(str)
    dfCells = dfCells.astype(str)
    print("done!")

#%%

""" #3 Upload data
A PostgreSQL query is constructed and sent to the database to upload the
table(s) created by the previous section.

"""
# ### REMOVE LATER #####################
# # Create table or disconnect
# if sdpty.conn.closed == 0:
#     sdpty.disconnect()
# ######################################

# #### REMOVE LATER #############################################################
#     print("Checking database connection...")
#     if sdpty.connect(credentials='D:/Documents/Python Scripts/RECORD-snpity/RECORD-snpity/serendipity_lib/bin/config1.ini'):
#         # Ask the database for version to check connection
#         sdpty.get_version()
#         print("\nDatabase connection was successful!")
        
#     else:
#         print("\nConnection to database failed. Please check connection parameters.")
#         sys.exit()
    
#     appoptns = sdpty.parse_ini(filename='D:/Documents/Python Scripts/RECORD-snpity/RECORD-snpity/serendipity_lib/bin/config1.ini', section="injector")
# ###############################################################################
if appoptns.get('autoupload').lower() in ["true", "1", "yes"]:
    connstr = "postgresql://"\
            + sdpty.conn_params.get('user') + ":"\
            + sdpty.conn_params.get('password') + "@"\
            + sdpty.conn_params.get('host') + ":"\
            + sdpty.conn_params.get('port') + "/"\
            + sdpty.conn_params.get('database')
    engine = create_engine(connstr)
# %% Upload trial events
    if upload_ok.get('trials'):
        try:        
            print("\nAttempting to upload trial data to host...")
            if sdpty.exists(trials_table):
                # Check if data exists in table:
                query = "SELECT sessionstart FROM "+trials_table+" WHERE sessionid='"+metadata.get('sessionid')+"';"
                if sdpty.query_database(query) is not None:
                    if appoptns.get('ifdatasetexists').lower() == "ask":
                        userinput = input("\nData with session ID '"+metadata.get('sessionid')+"' already exists in table. Would you like to overwrite this data? (y/n)\n")
                        if userinput.lower().startswith("y"):
                            query = "DELETE FROM "+trials_table+" WHERE sessionid='"+metadata.get('sessionid')+"';"
                            if sdpty.execute_query(query):
                                # Convert df to sql table and upload, set up test_database to test this (done)
                                # converting data to sql
                                print("\nUploading data to database...", end="")
                                dfEvents.to_sql(trials_table, con=engine, if_exists='append')
                                print("done!")
                        else:
                            print("\nData will not be uploaded.")
                    elif appoptns.get('ifdatasetexists').lower() == "overwrite":
                        query = "DELETE FROM "+trials_table+" WHERE sessionid='"+metadata.get('sessionid')+"';"
                        if sdpty.execute_query(query):
                            print("\nUploading data to database...", end="")
                            dfEvents.to_sql(trials_table, con=engine, if_exists='append')
                            print("done!")
                    elif appoptns.get('ifdatasetexists').lower() == "fail":
                        print("\nData will not be uploaded.")
                else:
                    # Convert df to sql table and upload, set up test_database to test this (done)
                    # converting data to sql
                    print("\nUploading data to database...", end="")
                    dfEvents.to_sql(trials_table, con=engine, if_exists='append')
                    print("done!")
            elif appoptns.get('automktable').lower() in ["true", "1", "yes"]:
                # Create table or disconnect
                print("\nCreating table...")
                # drop table if it already exists
                sdpty.curr.execute('DROP TABLE if EXISTS '+trials_table+';')
                i = 0
                query = "CREATE TABLE "+trials_table+"("
                for item in dfEvents.columns:
                    start = ', ' if i != 0 else ' '
                    query += start+str(item)+" VARCHAR"
                    i += 1
                
                query += " );"
                
                print("  "+query)
                sdpty.curr.execute(query)
                sdpty.conn.commit()
                # converting data to sql
                print("\nUploading data to database...", end="")
                dfEvents.to_sql(trials_table, con=engine, if_exists='append')
                print("done!")
            else:
                print("\nData was not uploaded.")
        except Exception as error:
            print("failed!")
            print(error)
    else:
        print("\nTrials dataset contains errors and cannot be uploaded to the database.")

# %% Upload positional data
    if upload_ok.get('position'):
        try:
            print("\nAttempting to upload position data to host...")
            if sdpty.exists(position_table):
                # Check if data exists in table:
                query = "SELECT sessionstart FROM "+position_table+" WHERE sessionid='"+metadata.get('sessionid')+"';"
                if sdpty.query_database(query) is not None:
                    if appoptns.get('ifdatasetexists').lower() == "ask":
                        userinput = input("\nData with session ID '"+metadata.get('sessionid')+"' already exists in table. Would you like to overwrite this data? (y/n)\n")
                        if userinput.lower().startswith("y"):
                            query = "DELETE FROM "+position_table+" WHERE sessionid='"+metadata.get('sessionid')+"';"
                            if sdpty.execute_query(query):
                                # Convert df to sql table and upload, set up test_database to test this (done)
                                # converting data to sql
                                print("\nUploading data to database...", end="")
                                dfTrack.to_sql(position_table, con=engine, if_exists='append')
                                print("done!")
                        else:
                            print("\nData will not be uploaded.")
                    elif appoptns.get('ifdatasetexists').lower() == "overwrite":
                        query = "DELETE FROM "+position_table+" WHERE sessionid='"+metadata.get('sessionid')+"';"
                        if sdpty.execute_query(query):
                            print("\nUploading data to database...", end="")
                            dfTrack.to_sql(position_table, con=engine, if_exists='append')
                            print("done!")
                    elif appoptns.get('ifdatasetexists').lower() == "fail":
                        print("\nData will not be uploaded.")
                else:
                    # Convert df to sql table and upload, set up test_database to test this (done)
                    # converting data to sql
                    print("\nUploading data to database...", end="")
                    dfTrack.to_sql(position_table, con=engine, if_exists='append')
                    print("done!")
            elif appoptns.get('automktable').lower() in ["true", "1", "yes"]:
                # Create table or disconnect
                print("\nCreating table...")
                # drop table if it already exists
                #sdpty.curr.execute('DROP TABLE if EXISTS '+position_table+';')
                i = 0
                query = "CREATE TABLE "+position_table+"("
                for item in dfTrack.columns:
                    start = ', ' if i != 0 else ' '
                    query += start+str(item)+" VARCHAR"
                    i += 1
                
                query += " );"
                
                print("  "+query)
                sdpty.curr.execute(query)
                sdpty.conn.commit()
                # converting data to sql
                print("\nUploading data to database...", end="")
                dfTrack.to_sql(position_table, con=engine, if_exists='append')
                print("done!")
            else:
                print("\nData was not uploaded.")
        except Exception as error:
            print("failed!")
            print(error)
    else:
        print("\nPosition dataset contains errors and cannot be uploaded to the database.")

# %% Upload cell trace data
    if upload_ok.get('celltrace'):
        try:        
            print("\nAttempting to upload cell trace data to host...")
            if sdpty.exists(optogen_table):
                # Check if data exists in table:
                query = "SELECT sessionstart FROM "+optogen_table+" WHERE sessionid='"+metadata.get('sessionid')+"';"
                if sdpty.query_database(query) is not None:
                    if appoptns.get('ifdatasetexists').lower() == "ask":
                        userinput = input("\nData with session ID '"+metadata.get('sessionid')+"' already exists in table. Would you like to overwrite this data? (y/n)\n")
                        if userinput.lower().startswith("y"):
                            query = "DELETE FROM "+optogen_table+" WHERE sessionid='"+metadata.get('sessionid')+"';"
                            if sdpty.execute_query(query):
                                # Convert df to sql table and upload, set up test_database to test this (done)
                                # converting data to sql
                                print("\nUploading data to database...", end="")
                                dfCells.to_sql(optogen_table, con=engine, if_exists='append')
                                print("done!")
                        else:
                            print("\nData will not be uploaded.")
                    elif appoptns.get('ifdatasetexists').lower() == "overwrite":
                        query = "DELETE FROM "+optogen_table+" WHERE sessionid='"+metadata.get('sessionid')+"';"
                        if sdpty.execute_query(query):
                            print("\nUploading data to database...", end="")
                            dfCells.to_sql(optogen_table, con=engine, if_exists='append')
                            print("done!")
                    elif appoptns.get('ifdatasetexists').lower() == "fail":
                        print("\nData will not be uploaded.")
                else:
                    # Convert df to sql table and upload, set up test_database to test this (done)
                    # converting data to sql
                    print("\nUploading data to database...", end="")
                    dfCells.to_sql(optogen_table, con=engine, if_exists='append')
                    print("done!")
            elif appoptns.get('automktable').lower() in ["true", "1", "yes"]:
                # Create table or disconnect
                print("\nCreating table...")
                # drop table if it already exists
                # sdpty.curr.execute('DROP TABLE if EXISTS '+optogen_table+';')
                i = 0
                query = "CREATE TABLE "+optogen_table+"("
                for item in dfCells.columns:
                    start = ', ' if i != 0 else ' '
                    query += start+str(item)+" VARCHAR"
                    i += 1
                
                query += " );"
                
                print("  "+query)
                sdpty.curr.execute(query)
                sdpty.conn.commit()
                # converting data to sql
                print("\nUploading data to database...", end="")
                dfCells.to_sql(optogen_table, con=engine, if_exists='append')
                print("done!")
            else:
                print("\nData was not uploaded.")
        except Exception as error:
            print("failed!")
            print(error)
    else:
        print("\nCell trace dataset contains errors and cannot be uploaded to the database.")
        
else:
    print("\nEntry 'autoupload' in .ini is set to 'False', '0', or 'No', no data was uploaded to database.")

""" #4 Cleanup
Close connection to database and clean up.
"""
# %%
# workbook = xlsx.Workbook('columns.xlsx')
# worksheet1 = workbook.add_worksheet('trial_table Columns')
# worksheet2 = workbook.add_worksheet('bonsai_table Columns')
# worksheet3 = workbook.add_worksheet('inscopix_table Columns')

# # Start from the first cell.
# # Rows and columns are zero indexed.
# row = 0
# column = 0

# header = ['Column Name', 'Column Type', 'Data Type', 'Meaning', 'Example']
# cell_format = workbook.add_format({'bold': True,})
# for item in header:
#     worksheet1.write(row, column, item, cell_format)
#     worksheet2.write(row, column, item, cell_format)
#     worksheet3.write(row, column, item, cell_format)
#     column += 1 

# content = dfEvents.columns

# row = 1
# column = 0
 
# # iterating through content list
# for item in content :
 
#     # write operation perform
#     worksheet1.write(row, column, item)
#     worksheet1.write(row, 4, dfEvents[item][1])
#     worksheet1.write(row, 2, str(type(dfEvents[item][1])))
#     if item in metadata_cols:
#         worksheet1.write(row, 1, 'metadata')
#     elif item in dlink.ts_data:
#         worksheet1.write(row, 1, 'data timestamp')
#     elif item in tcols.pointers:
#         worksheet1.write(row, 1, 'pointer to row')
#         worksheet1.write(row, 2, str(type(dfEvents[item][1]))+", dictionary")
#     else:
#         worksheet1.write(row, 1, 'data')
    
 
#     # incrementing the value of row by one
#     # with each iterations.
#     row += 1

# row = 1
# column = 0

# content = dfTrack.columns
 
# # iterating through content list
# for item in content :
 
#     # write operation perform
#     worksheet2.write(row, column, item)
#     worksheet2.write(row, 4, dfTrack[item][1])
#     worksheet2.write(row, 2, str(type(dfTrack[item][1])))
#     if item in metadata_cols:
#         worksheet2.write(row, 1, 'metadata')
#     elif item.lower() == "timestamp":
#         worksheet2.write(row, 1, 'data timestamp')
#     else:
#         worksheet2.write(row, 1, 'data')
 
#     # incrementing the value of row by one
#     # with each iterations.
#     row += 1

    
# row = 1
# column = 0


# content = dfCells.columns
 
# # iterating through content list
# for item in content :
 
#     # write operation perform
#     worksheet3.write(row, column, item)
#     worksheet3.write(row, 4, dfCells[item][1])
#     worksheet3.write(row, 2, str(type(dfCells[item][1])))
#     if item in metadata_cols:
#         worksheet3.write(row, 1, 'metadata')
#     elif item.lower() == "timestamp":
#         worksheet3.write(row, 1, 'data timestamp')
#     elif item.lower() == "celltrace" or item.lower() == "cellevent" or item.lower() == "cellstatus":
#         worksheet3.write(row, 2, str(type(dfCells[item][1]))+", dictionary")
#     else:
#         worksheet3.write(row, 1, 'data')
 
#     # incrementing the value of row by one
#     # with each iterations.
#     row += 1
# workbook.close()
#%%
# If connection is not closed, then close it.
if sdpty.conn.closed == 0:
    sdpty.disconnect()