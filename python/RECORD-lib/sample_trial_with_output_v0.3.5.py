# -*- coding: utf-8 -*-
"""
Created on Tue Sep  6 13:26:59 2022
Last updated Fri 17 Feb, 2023
v0.3.4

@author: Raquel Ibáñez Alcalá

An example script to automate 4 trials using the RECORD system, its library
and manual user input to determine acceptance of the offer.
"""

import random as rand
import datetime
import pytz
from record_lib import RECORD
from record_lib import TRIALS
import sys
import csv
# Has a bug on Windows that makes it not close the stream, whatever that means.
# from playsound import playsound
# For playing sound.
import os
import subprocess

############################################################################## 
# Initialize all trial variables: 
#    1. inter_trial_interval: The time to wait in-between trials, in seconds.
#    2. decision_interval: The time to wait while rat is making a decision,
#       in seconds.
#    3. feeding_interval: The time to wait while rat is eating, in seconds.
#    4. trials: Number of trials in session.
#    5. levels: (List) Available cost levels, whole numbers only.
#    6. feeders: (List) Available feeders, whole numbers only.
#    7. lvl_probs: (List) Probability for each cost level to appear in a trial
#       list, position-sensitive. Reads as: P[lvl0], P[lvl1], P[lvl2], P[lvl3].
#    8. fdr_probs: (List) Probability for each feeder to appear in a trial
#       list, position sensitive. Reads as: P[fdr1], P[fdr2], P[fdr3], P[fdr4].
#    9. rewards: The reward identifier. Usually a percentage representing
#       concentration of the reward in water.
#    10. intensities: The intensity of the cost. If the cost is light, this
#       will likely be a value in lux.
#    11. subj_name: The name of the rat/mouse/vole/rodent subject that runs the
#       tasks.
#    12. filename: The name of the files to be output. Subcripts will be added
#       to this name as well as a timestamp in order to identify what file type
#       is output and when the session was run. This script will output two
#       files: A metadata file containing the parametres defined below, and an
#       events file with timestamps for events that happened during the session
#       
#    The sum of elements in lvl_probs must equal 1.
#    The sum of elements in fdr_probs must also equal 1.
#    
#    Using this format to imitate the JSON format from an AJAX request as I
#    might implement this script as API for a web interface.
#
# BE SURE TO NOT REMOVE QUOTATION MARKS WHEREVER YOU MAKE CHANGES!! 
trialParams = {
               # Time intervals, in seconds.
               'inter_trial_interval': 1,
               'decision_interval'   : 1,
               'feeding_interval'    : 1,
               # Number of trials
               'trials'              : 5,
               # Do not need to be changed
               'levels'              : [0, 1, 2, 3],
               'feeders'             : ['a', 'b', 'c', 'd'],
               # Probability of a COST level appearing in the trial list. Sum of all elements must equal 1.
               'lvl_probs'           : [0, 1, 0, 0],
               # Probability of a FEEDER appearing in the trial list. Sum of all elements must equal 1.
               'fdr_probs'           : [0.25, 0.25, 0.25, 0.25],
               # Sugar concentration in reward solution. If compound solution (for example sucrose + alcohol), include second solute concentration in parenthesis: X%(Y%). No spaces.
               'rewards'             : ["9%","5%","2%","0.5%"],
               # Reward volume delivered
               'reward_volume'       : "4ml",
               # Cost intensity, in lux. Include units, no spaces.                      
               'intensities'         : ["0lux","15lux","140lux","290lux"],
               # Subject's name, as defined in rat roster.                        
               'subj_name'           : "A4",
               # Specify the type of manipulation done. If regular behaviour trial: "Normal"; if alcohol trial: "Alcohol"; if oxy trial: "Oxycodone"; etc...
               'subj_health'         : "Normal",
               # Specify the subject weight, in grams. Include units, no spaces. If no weight is defined, write "Undefined"
               'subj_weight'         : "Undefined",
               # Specify the type of task done. For example L1, L2, L3, L1L2, L1L3, etc.
               'task_type'           : "L1",     
               # The root folder where all generated data is going to be saved to.
               'root_folder'         : "D:/BehaviourData/",
               # Timezone information for timestamping               
               'timezone'            : "US/Mountain", 
               # Physiological recording made/Technique used. For example: Calcium Imaging, Optogenetics, Electrophysiology, etc.
               'recording_type'      : "Calcium Imaging"
               ## End
               }
#
############################################################################## 

mcu_com_port = "COM4"
TTL_ON       = False
# Parse incoming trial parameters...
inter_trial_interval = trialParams.get('inter_trial_interval')
decision_interval    = trialParams.get('decision_interval')
feeding_interval     = trialParams.get('feeding_interval')
trials               = trialParams.get('trials')
lvls                 = trialParams.get('levels')
feeders              = trialParams.get('feeders')
lvl_probs            = trialParams.get('lvl_probs')
fdr_probs            = trialParams.get('fdr_probs')
reward_conc          = trialParams.get('rewards')
cost_intensities     = trialParams.get('intensities')
subject_name         = trialParams.get('subj_name')
timezone             = pytz.timezone(trialParams.get('timezone', 'UTC'))
recording_type       = trialParams.get('recording_type')
health               = trialParams.get('subj_health')
weight               = trialParams.get('subj_weight')
reward_volume        = trialParams.get('reward_volume')
now                  = timezone.localize(datetime.datetime.now())
filename             = trialParams.get('root_folder')+trialParams.get('subj_name')+r"_"+trialParams.get('task_type')+r"_"+now.strftime('%a-%b-%d-%Y_%H-%M-%S')
print(now)
# Initialize the TRIALS class. Make a "mytrials" object that will contain
# information for your trials.
mytrials = TRIALS()

# Create session parameters and save them as "myparameters". This will create
# a "metadata" dictionary object with the following parameters:
#    1. Inter-trial interval (as T_intertrial): The time to wait in-between
#       trials, in seconds. Default 5.
#    2. Decision delay (as T_decision): The time to wait while rat is making a
#       decision, in seconds. Default 2.
#    3. Feeding delay (as T_feeding): The time to wait while rat is eating, in
#       seconds. Default 5.
#    4. Trials: Number of trials in session. Default 4.
#    5. Levels (as avail_lvls): (List) Available cost levels, list of whole
#       numbers only. Default [0,1,2,3]
#    6. Feeders (as avail_fdrs): (List) Available feeders, list of whole
#       numbers only. Default [1,2,3,4]
#    7. Probability of appearance for each level (as P_lvls): Probability
#       for each cost level to appear in a trial. List, position-sensitive.
#       Reads as: P[lvl0], P[lvl1], P[lvl2], P[lvl3]. Default [0.25,0.25,0.25,0.25]
#    8. Probability of appearance for each feeder (as P_fdrs): Probability for
#       each feeder to appear in a trial. List, position sensitive.
#       Reads as: P[fdr1], P[fdr2], P[fdr3], P[fdr4]. Default [0.25,0.25,0.25,0.25]
#
# Call the "create_trial_session" method by referencing "mytrials" first, then
# calling the method. You may overwrite the default parameters by specifying
# the parameter name (as defined in the list above). If no parameter is
# specified when you call this method, that parameter will default to its
# default value. Note that here we define "avail_fdrs" as a, b, c, and d, we'll
# adress this later.

myparameters = mytrials.create_trial_session(
                                             T_intertrial=inter_trial_interval,
                                             T_decision=decision_interval,
                                             T_feeding=feeding_interval,
                                             trials=trials,
                                             avail_lvls=lvls,
                                             cost_inten=cost_intensities,
                                             avail_fdrs=feeders,
                                             reward_lvls=reward_conc,
                                             P_lvls=lvl_probs,
                                             P_fdrs=fdr_probs,
                                             subj_name=subject_name,
                                             tz=timezone,
                                             rectype=recording_type,
                                             subj_health=health,
                                             subj_weight=weight,
                                             reward_volume=reward_volume
                                             )

# This will simply show you the trial session details, or the "metadata" for
# this trial session. The dictionary object will be printed to the console.
print(myparameters)
_LIST_LOADED = 1    # 1 means there was no list loaded
answer = ""
answer = input("\nDo you wish to import a previously saved trial list? [y/n]\n")
if answer.lower().startswith("y"):
    print("Please write the path to the trial list file you wish to import, including its extension.")
    trial_file = input("For example: D:\BehaviourData\example_list.csv\n")
    tlist_fdrs, tlist_lvls = mytrials.load_list(trial_file)
    _LIST_LOADED = 0
elif answer.lower().startswith("n"):
    print("\nNo trial list will be loaded.")

# Now that we have defined our parameters, we need to create a trial list. The
# "create-trial_list" method will do this for us and randomise the values so
# that cost/reward pairs don't appear sequentially. The method will create two
# lists; one for feeders which we'll call "tlist_fdrs", and one for levels
# called "tlist_lvls".
#
# Notice that we overwrote the "avail_fdrs" parameter again. You can do this
# for any parameter you want, but keep in mind that, unless you do some
# preprocessing on the trial list, the values in "avail_fdrs" and "avail_lvls"
# will be sent directly to the microcontroller, which can only read whole
# numbers for those parameters.
if _LIST_LOADED:
    tlist_fdrs , tlist_lvls = mytrials.create_trial_list(avail_fdrs=[1,2,3,4])

# Show both these lists:
print("\nFeeders:", tlist_fdrs)
print("Cost levels:", tlist_lvls)

# Ask the user whether or not they want to continue with the generated lists,
# or if they want to re-shuffle the lists.
answer = ""
cont = 1
while cont:
    answer = input("\nDo you wish to continue with these lists? Or if you want to re-shuffle, just say 'r'. [y/n/r]\r\n")
    if answer.lower().startswith("y"):
        print("\nGreat! Continuing on to execution of", trials, "trials...\r\n")
        cont = 0
    elif answer.lower().startswith("r"):
        rand.shuffle(tlist_fdrs)
        print("\nFeeders after re-shuffling:")
        print(tlist_fdrs)
        rand.shuffle(tlist_lvls)
        print("Cost levels after re-shuffling:")
        print(tlist_lvls)
    elif answer.lower().startswith("n"):
        print("\nStopping script. See you later!\n")
        sys.exit()
        
# Ask the user whether or not they want to save the generated lists.
answer = ""
answer = input("Do you wish to save the generated lists? [y/n]\n")
if answer.lower().startswith("y"):
    print("\nSaving lists...")
    trial_file = filename + "_trial_list"
    mytrials.save_list(tlist_fdrs,tlist_lvls,trial_file)
elif answer.lower().startswith("n"):
    print("\nTrial list will not be saved.")

# We want to log a lot of information for this session of trials, so let's
# create a few lists:
session_summary = []# List of dictionaries containing events and TSs for e/trial

# Initialize the RECORD class, we'll use this to call methods that will
# control the microcontroller in some way. We'll call this object "MCU".
MCU = RECORD()

# Define and initialize a serial communications session so we can start talking 
# to the microcontroller. We don't need to do anything before opening the
# communication channel to the microcontroller so we'll open it right away.
print("\nOpening serial port. Interrupt execution of all trials with keyboard interrupt (Ctrl + C)")
session = MCU.createSS(com_port=mcu_com_port)
session.open()      # Open the serial interface

# Timestamp when the session starts. We'll use this later.
session_start = timezone.localize(datetime.datetime.now())

# Start repeating trials...
try:  
    for x in range(trials):
        # Define an ordered structure in which to contain data. Defining all
        # items here is not needed, it is only done for transparency, but not
        # doing so would change how we put information in the dictionary.        
        this_trial = {
                      # Trial timestamps and information
                      "trial_start"          : "Null",
                      "trial_end"            : "Null",
                      "trial_elapsed"        : "Null",
                      "trial_index"          : "Null",
                      "cost_level"           : "Null",
                      "cost_intensity"       : "Null",
                      "reward_concentration" : "Null",
                      "reward_level"         : "Null",
                      "decision_made"        : "Null",
                      # Events
                      "play_tone"       : "Null",
                      "first_reset"     : "Null",
                      "mcu_timer_start" : "Null",
                      "trial_start_cue" : "Null",
                      "offer_presented" : "Null",
                      "reward_delivery" : "Null",
                      "last_reset"      : "Null",
                      "mcu_timer_stop"  : "Null",
                      "decision_ts"     : "Null",
                      "extsys_on"       : "Null",
                      "extsys_off"      : "Null",
                      # MCU responses and acknowledgements
                      "first_reset_resp"     : "Null",
                      "first_reset_ack"      : "Null",
                      "mcu_timer_start_resp" : "Null",
                      "mcu_timer_start_ack"  : "Null",
                      "trial_start_cue_resp" : "Null",
                      "trial_start_cue_ack"  : "Null",
                      "offer_presented_resp" : "Null",
                      "offer_presented_ack"  : "Null",
                      "reward_delivery_resp" : "Null",
                      "reward_delivery_ack"  : "Null",
                      "last_reset_resp"      : "Null",
                      "last_reset_ack"       : "Null",
                      "mcu_timer_stop_resp"  : "Null",
                      "mcu_timer_stop_ack"   : "Null",
                      "extsys_on_resp"       : "Null",
                      "extsys_on_ack"        : "Null",
                      "extsys_off_resp"      : "Null",
                      "extsys_off_ack"       : "Null"
                      }
        
        print("\n######### Trial number", x+1, "out of", trials, "#########")
        ## Inter-trial interval
        print("\nStarting trial with inter-trial interval of", inter_trial_interval,"seconds...")
        mytrials.wait(inter_trial_interval)
        
        ## Send TTL out to start external system recording
        print("\nSending TTL to external system to start recording...")
        status, ts = MCU.output_ttl(enforce_delay=False)
        
        if status == 0: # Check if communication with MCU returned no problems.
            this_trial.update({"extsys_on": timezone.localize(ts).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
        resp, ts = MCU.fetch_response()
        this_trial.update({"extsys_on_resp": resp})
        this_trial.update({"extsys_on_ack" : timezone.localize(ts).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
        # (Optional) Display the microcontroller's response in the console.
        print("  ", resp)
        TTL_ON, _ = MCU.request_ttl_state()
        
        mytrials.wait(1)
        
        # Log the start of the trial and save it into one of our timestamp lists.
        trial_start = timezone.localize(datetime.datetime.now())
        this_trial.update({"trial_start": trial_start.strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
        
        ## Start microcontroller's internal trial timer
        print("\nStarting MCU timer...")
        status, ts = MCU.timer_start(enforce_delay=True)
       
        if status == 0: # Check if communication with MCU returned no problems.
            this_trial.update({"mcu_timer_start": timezone.localize(ts).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
        resp, ts = MCU.fetch_response()
        this_trial.update({"mcu_timer_start_resp": resp})
        this_trial.update({"mcu_timer_start_ack" : timezone.localize(ts).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
        # (Optional) Display the microcontroller's response in the console.
        print("  ", resp)
        
        # Perform first reset
        print("\nPerforming first reset before starting next trial...")
        status, ts = MCU.all_inactive(enforce_delay=False)
       
        if status == 0: # Check if communication with MCU returned no problems.
            this_trial.update({"first_reset": timezone.localize(ts).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
        resp, ts = MCU.fetch_response()
        this_trial.update({"first_reset_resp": resp})
        this_trial.update({"first_reset_ack" : timezone.localize(ts).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
        # (Optional) Display the microcontroller's response in the console.
        print("  ", resp)
        
        ## Indicate start of trial
        print("\nTurning indicator on to indicate ongoing trial...")
        status, ts = MCU.indicator_toggle(enforce_delay=False)
       
        if status == 0: # Check if communication with MCU returned no problems.
            this_trial.update({"trial_start_cue": timezone.localize(ts).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
        resp, ts = MCU.fetch_response(timeout=2)
        this_trial.update({"trial_start_cue_resp": resp})
        this_trial.update({"trial_start_cue_ack" : timezone.localize(ts).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
        # (Optional) Display the microcontroller's response in the console.
        print("  ", resp)
        
        # Play trial tone
        print("\n♪♪ Playing trial start tone ♪♪")
        # ts = timezone.localize(datetime.datetime.now())
        # audio_file = r"D:\Python\RECORDpy\trial_start_tone.wav"
        # with open(os.devnull, 'wb') as devnull:
        #     subprocess.check_call(["vlc", audio_file, "--play-and-exit"], stdout=devnull, stderr=subprocess.STDOUT)
        # this_trial.update({"play_tone": ts.strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
    
        # Cue rat to approach a random feeder with a random cost
        print("\nCueing on feeder",tlist_fdrs[x],"at level",tlist_lvls[x],"...")
        status, ts = MCU.feeder_light(tlist_fdrs[x],tlist_lvls[x], enforce_delay=False)
       
        if status == 0: # Check if communication with MCU returned no problems.
            this_trial.update({"offer_presented": timezone.localize(ts).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
        resp, ts = MCU.fetch_response()
        this_trial.update({"offer_presented_resp": resp})
        this_trial.update({"offer_presented_ack" : timezone.localize(ts).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
        # (Optional) Display the microcontroller's response in the console.
        print("  ", resp)
        
        ## Wait for rat to approach feeder, give it 5 seconds to do so...
        print("\nAllowing rat to make a decision for", decision_interval, "seconds...")
        mytrials.wait(decision_interval)
    
        ## React to rat's decision
        # THIS PART IS NOT AUTOMATED IN THIS EXAMPLE. If you have a way to automate
        # zone detection with rat tracking, please update this section appropriately.
        # Check if the rat is at the feeder...
        approach = input("\nDid the rat approach the offer? (delivers reward if yes) [y/n]\n")
        if approach.lower().startswith("y"):
            # Deliver reward if the rat did approach the offer.      
            this_trial.update({"decision_ts" : timezone.localize(datetime.datetime.now()).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
            status, ts = MCU.valve_activate(tlist_fdrs[x], enforce_delay=False)
           
            if status == 0: # Check if communication with MCU returned no problems.
                this_trial.update({"reward_delivery": timezone.localize(ts).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
            resp, ts = MCU.fetch_response()
            this_trial.update({"reward_delivery_resp": resp})
            this_trial.update({"reward_delivery_ack" : timezone.localize(ts).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
            # (Optional) Display the microcontroller's response in the console.
            print("  ", resp)
            
            # Wait until rat finishes eating (2 seconds)
            print("Waiting for rat to eat for", feeding_interval,"seconds...")
            mytrials.wait(feeding_interval)
        elif approach.lower().startswith("n"):
            this_trial.update({"decision_ts" : timezone.localize(datetime.datetime.now()).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
            # Do nothing if the rat did not approach the offer. You might want
            # to do something instead, put that code in here.
            # pass
        else:
            this_trial.update({"decision_ts" : timezone.localize(datetime.datetime.now()).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
            print("\nInput not recognized, defaulting to 'n'.")
            approach = "n"
        
        # Save the rat's decision into the decisions list.
        this_trial.update({"decision_made": approach})
    
        ## Record for 2 seconds for a post-trial baseline...
        print("\nRecording for 2 seconds before ending...")
        mytrials.wait(2)
        
        ## Reset microcontroller to its idle state
        print("\nPerforming last reset...")
        status, ts = MCU.all_inactive(enforce_delay=False)
       
        if status == 0: # Check if communication with MCU returned no problems.
            this_trial.update({"last_reset": timezone.localize(ts).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
        resp, ts = MCU.fetch_response()
        this_trial.update({"last_reset_resp": resp})
        this_trial.update({"last_reset_ack" : timezone.localize(ts).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
        # (Optional) Display the microcontroller's response in the console.
        print("  ", resp)
        
        ## ...then stop the microcontroller's timer and end the trial
        print("\nStopping MCU timer...")
        status, ts = MCU.timer_stop(enforce_delay=False)
       
        if status == 0: # Check if communication with MCU returned no problems.
            this_trial.update({"mcu_timer_stop": timezone.localize(ts).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
        resp, ts = MCU.fetch_response()
        this_trial.update({"mcu_timer_stop_resp": resp})
        this_trial.update({"mcu_timer_stop_ack" : timezone.localize(ts).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
        # (Optional) Display the microcontroller's response in the console.
        print("  ", resp)
                
        # Also log the end time of the trial.
        trial_end = timezone.localize(datetime.datetime.now())
        this_trial.update({"trial_end": trial_end.strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
        
        ## Send TTL out to stop external system from recording
        print("\nSending TTL to external system to stop recording...")
        status, ts = MCU.output_ttl(enforce_delay=False)
        
        if status == 0: # Check if communication with MCU returned no problems.
            this_trial.update({"extsys_off": timezone.localize(ts).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
        resp, ts = MCU.fetch_response()
        this_trial.update({"extsys_off_resp": resp})
        this_trial.update({"extsys_off_ack" : timezone.localize(ts).strftime("%Y-%m-%dT%H:%M:%S.%f%z")})
        # (Optional) Display the microcontroller's response in the console.
        print("  ", resp)
        TTL_ON, _ = MCU.request_ttl_state()
        
        # Save the rest of the trail data into structure
        trial_elapsed = trial_end - trial_start
        this_trial.update({"trial_elapsed"       : str(trial_elapsed)})
        this_trial.update({"trial_index"         : x+1})
        this_trial.update({"cost_level"          : tlist_lvls[x]})
        this_trial.update({"reward_level"        : tlist_fdrs[x]})
        this_trial.update({"cost_intensity"      : cost_intensities[tlist_lvls[x]]})
        this_trial.update({"reward_concentration": reward_conc[tlist_fdrs[x]-1]})
        
        # Save the generated trial data
        session_summary.append(this_trial)
        print("\n###########################################")
        print("\n                END TRIAL                  ")

except KeyboardInterrupt:
# Execute if user enters Ctrl+C.
    # If the user enters a keyboard interrupt, i.e. Ctrl+C, you have to do
    # some cleanup if you started a serial session.
    print("\n\n[KeyboardInterrupt detected!]")
    print("\nAttempting to export session data...")

except Exception as e:
# Exceute if an exception is caught. This is, if any type of error occurs at
# any time in the middle of the code in the "try:" clause, this will execute.
    print("\n\n[Exception detected!]:", e)
    print("\nAttempting to export session data...")

else:
# Exceute this if no exception is caught.        
    # When all trials have run, close the serial session so you can open it
    # later.
    print("\nTrials ended successfully, saving data...")
            
finally:
# Execute regardless of whether or not a exception was caught.
    # Export session data
    total_trials= len(session_summary)
    if total_trials != 0:
        
        # Just a function to show the user something while they wait. Simply prints
        # a progrss bar into the console.
        def progress_bar(current, total, bar_length=20):
            try:
                fraction = current / total
                arrow = int(fraction * bar_length - 1) * '-' + '>'
                padding = int(bar_length - len(arrow)) * ' '
                ending = '\n' if current == total else '\r'
                print(f'Progress: [{arrow}{padding}] {int(fraction*100)}%', end=ending)
            except Exception as error:
                print("[Progress bar could not be created for index",current,"out of",total,"]\n")
                print(error)
       
        try:
            # Log the end of all sessions.
            session_end = timezone.localize(datetime.datetime.now())
            
           ## Display the session summary.
            print("\n###########################################")
            print("Computing session summary...")
            # Session time:
            session_elapsed = session_end - session_start
            print('\nSession time:', session_elapsed)
            myparameters.update({'sessionduration': str(session_elapsed)})
            # All trial times:
            for i in range(total_trials):
                print("", str(i+1)+'.', session_summary[i]["trial_elapsed"], end=" ")
                print("using feeder", tlist_fdrs[i], "(", session_summary[i]["reward_concentration"], ")", end=" ")
                print("and level", tlist_lvls[i], "(", session_summary[i]["cost_intensity"], ")", end=" ")
                print("with decision", session_summary[i]["decision_made"])
               
           ### Write session summary to files
            # Session metadata to text file
            print("\nExporting session metadata...", end="")
            file = open(filename+"_metadata.txt","w")
            for key, value in myparameters.items(): 
                file.write('%s:%s\n' % (key, value))
            file.close()
            print("done!")
           
           ### Trial data to CSV file
            print("\nExporting session data to file, please wait...")
            # Create the CSV column headers, or desired field names to export. Here I
            # just take all the kets from the this_trial dictionary. I also sort them
            # alphabetically so stuff is easier to find.
            print("  Sorting data keys...")
            fieldnames= sorted(list(this_trial.keys()))
            
            # Start writing file
            print("  Writing trial data to file, this could take a few seconds...")
            with open(filename+"_events.csv", 'w', encoding='UTF8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()    # Write the column headers
                for _ in range(total_trials):
                    # Write each row individually. Yes this can be done with writerows
                    # but I want to do each row so I can use the progress bar. Slower?
                    # maybe, but at least the user will be able to see something
                    # happening.
                    writer.writerow(session_summary[_]) 
                    if (total_trials-1)>0: progress_bar(_, total_trials-1)
        except Exception as e:
            print("\nSomething went wrong during data export!")
            print("\n", e)
    else:
        print("\nNo session data to export.")

    # Attempt to turn the connected system off
    if TTL_ON:
        ## Send TTL out to stop external system from recording
        print("\nSending TTL to external system to stop recording before exiting...")
        status, _ = MCU.output_ttl(enforce_delay=False)
        resp, _ = MCU.fetch_response()
        print("  ", resp)
        print("Please ensure that external system is inactive.")
    
    # Reset MCU to idle state, clean up, and exit.
    # Stop the timer so it's not running forever.
    print("\nStopping MCU timer...")
    MCU.timer_stop()    
    resp, _ = MCU.fetch_response()
    print("  ", resp)
    
    # Reset the microcontroller to its idle state.
    print("\nResetting MCU to idle...")
    MCU.all_inactive()  
    resp, _ = MCU.fetch_response()
    print("  ", resp)
    
    # Make sure serial session is closed
    print("\nClosing serial session and exiting...")
    session.close()
    print("\n\nClosing Spyder is no longer required, but make sure to stop Bonsai!")
    sys.exit()


"""

Data output should contain a header where the session parameters are shown:
    1. inter_trial_interval
    2. decision_interval
    3. feeding_interval
    4. trials
    5. levels
    6. feeders
    7. lvl_probs
    8. fdr_probs
    9. * The trial list
    10. Whether the session was supervised (manual decision input from
        experimenter), or unsupervised (implementation of computer vision
        animal detection).

Each trial will output the following information:
    1. The start timestamp of the trial
    2. The end timestamp of the trial
    3. The trial duration (end - start)
    4. The trial number (index)
    5. Timestamp for each event:
        a. First microcontroller reset (all inactive)
        b. Microcontroller timer start
        c. Trial indicator light turn on (start of trial)
        d. Presentation of offer (activation of feeder lights)
        e. Decision made (user input)
        f. Reward delivery (activation of valve)
        g. Final reset (end of trial)
        h. Microcontroller timer stop
    6. The rat's decision during the trial
    7. * Cost level (0, 1, 2, or 3)
    8. * Cost intensity (lux)
    9. * Reward level (% concentration)

Also log events (as a separate file?):
    1. Timestamp of when a command was sent
    2. The command sent
    3. Timestamp of when the microcontroller acknowledged and responded
    4. The response message

* Calculate after session ends to minimize CPU execution time and load during
  trial.

"""