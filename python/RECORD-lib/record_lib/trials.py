# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 14:02:51 2022
Last updated Mon Feb 6 2023
v0.3.2

@author: Raquel Ibáñez Alcalá
"""

import datetime
import pytz
import time
import numpy as np
import random as rand
import csv
from os.path import exists

class TRIALS:
    def __init__ (self):
        pass
    
    def create_trial_session(self, **kwargs):
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
        #       
        #    The sum of elements in lvl_probs must equal 1.
        #    The sum of elements in fdr_probs must also equal 1.
        #    
        #    Using this format to imitate the JSON format from an AJAX request as I
        #    might implement this script as API for a web interface.
        
        now = datetime.datetime.now()
        self.timezone     = kwargs.get('tz', 'UTC')
        self.T_intertrial = kwargs.get('T_intertrial',5)
        self.T_decision   = kwargs.get('T_decision',2)
        self.T_feeding    = kwargs.get('T_feeding',5)
        self.trials       = kwargs.get('trials',4)
        self.avail_lvls   = kwargs.get('avail_lvls',[0,1,2,3])
        self.cost_inten   = kwargs.get('cost_inten',["0", "unkn", "unkn", "unkn"])
        self.avail_fdrs   = kwargs.get('avail_fdrs',[1,2,3,4])
        self.reward_lvls  = kwargs.get('reward_lvls',["unkn", "unkn", "unkn", "unkn"])
        self.P_lvls       = kwargs.get('P_lvls',[0.25,0.25,0.25,0.25])
        self.P_fdrs       = kwargs.get('P_fdrs',[0.25,0.25,0.25,0.25])
        self.subj_name    = kwargs.get('subj_name','None')
        self.subj_health  = kwargs.get('subj_health','Undefined')  
        self.subj_weight  = kwargs.get('subj_weight','Undefined')  
        self.rew_volume   = kwargs.get('reward_volume', 'Undefined')
        self.created      = self.timezone.localize(now).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        self.rectype      = kwargs.get('rectype', 'Undefined')
        
        metadata = {'sessionstart'        : self.created,
                    'sessionduration'     : "",
                    'trials'              : self.trials,
                    'avail_lvls'          : self.avail_lvls,
                    'costlevels'          : self.cost_inten,
                    'costprobabilities'   : self.P_lvls,
                    'avail_reward'        : self.avail_fdrs,
                    'rewardlevels'        : self.reward_lvls,
                    'rewardprobabilities' : self.P_fdrs,
                    'rewardvolume'        : self.rew_volume,
                    't_intertrial'        : self.T_intertrial,
                    't_decision'          : self.T_decision,
                    't_feeding'           : self.T_feeding,
                    'subjectid'           : self.subj_name,
                    'subjecthealth'       : self.subj_health,
                    'subjectweight'       : self.subj_weight,
                    'recordingtype'       : self.rectype,
                    'notes'               : ""
                    }
        
        return metadata
    
    def create_trial_list(self, **kwargs):
        # Create a trial list based on the trial parameters created after
        # running the "create_trial_session". Accepts optional parameters
        # explicitly defined.        
        #  The following trial parameters can be manually passed:
        #    1. a list of integers of available cost levels.
        #    2. a list of floats with probabilities for each cost level, 
        #       position sensitive. P[L0], P[L1], P[L2], ..., P[Ln] = 1
        #    3. a list of integers of available feeders on the arena.
        #    4. a list of floats with probabilities for each feeder to appear, 
        #       position sensitive. P[F0], P[F1], P[F2], ..., P[Fn] = 1
        #
        # The lengths of all lists must match. Ideally, the parameters
        # dictionary should be created by the "create_trial_session" method in
        # this library, but parameters can also be inputted manually as long as
        # each parameter identifiers matches the one created by that method.
        #
        # Returns tuple of a list of feeders and a list of cost levels
        
        dist_lvls = []
        dist_fdrs = []
        
        # Parse incoming trial parameters...
        trials = kwargs.get('trials', self.trials)
        lvls= kwargs.get('avail_lvls', self .avail_lvls)
        feeders = kwargs.get('avail_fdrs', self.avail_fdrs)
        lvl_probs = kwargs.get('P_lvls', self.P_lvls)
        fdr_probs = kwargs.get('P_fdrs', self.P_fdrs)
        
        if np.sum(lvl_probs) != 1:
            print("Sum of cost level probabilities does not equal 1. Exiting.")
            return -1
        elif np.sum(fdr_probs) != 1:
            print("Sum of feeder probabilities does not equal 1. Exiting.")
            return -1
    
        # Multiply the probabilistic distribution list by the total number of trials
        # to find out how many aprearances of each level should be found in the trial
        # list...
        lvl_num = list(np.array(lvl_probs) * trials)
    
        for i in range(len(lvl_num)):
            lvl_num[i] = int(lvl_num[i])
            # Begin generating the levels in the trial list...
            for _ in range(lvl_num[i]):
                dist_lvls.append(lvls[i])
    
        # At this point you will have a list of n repetitions of each number
        # representation of every level in the list, however all numbers will be in
        # order; for example, if your probability distribution (lvl_probs) looked like
        # "[0, 0.25, 0.25, 0.25, 0.25]", meaning equal probabilities for every level
        # except for level 0, and you wish to generate 40 trials, then the dist_lvls
        # list will have 0 repetitions of the number 0, 10 repetitions of the number
        # 1, 10 repetitions of the number 2, and so on, like so:
        # [1,1,1,1,...1, 2,2,2,2,...,2, 3,3,3,3,...,3].
    
        # Repeat the process above for the list of feeders...
        fdr_num = list(np.array(fdr_probs) * trials)

        for i in range(len(fdr_num)):
            fdr_num[i] = int(fdr_num[i])
            # Begin generating the levels in the trial list...
            for _ in range(fdr_num[i]):
                dist_fdrs.append(feeders[i])
    
        # The lists now need to be shuffled to make the order of these numbers appear
        # as random as possible...
        rand.shuffle(dist_fdrs)
        rand.shuffle(dist_lvls)
        
        # Check that the lists are good to be shipped out...
        if len(dist_lvls) < trials:     # Check for shorter-than-needed lists
            while(len(dist_lvls) < trials):
            # Create numbers from the levels list using the probabilities
            # given by lvl_probs. This will generate an individual number with
            # probability P[Lvlx].
                rmn = np.random.choice(np.arange(lvls[0],(lvls[len(lvls)-1]+1)), p=lvl_probs)
                dist_lvls.append(rmn)
        elif len(dist_lvls) > trials:
            for i in range(trials - len(dist_lvls)):
            # Generate a random number with probability given by the lvl_probs
            # list and remove the first occurance of it. Repeat until the list
            # is of appropriate length.
                rmv = np.random.choice(np.arange(lvls[0],(lvls[len(lvls)-1]+1)), p=lvl_probs)
                dist_lvls.remove(rmv)
        
        if len(dist_fdrs) < trials:
            for i in range(trials - len(dist_fdrs)):
            # Create numbers from the levels list using the probabilities
            # given by fdr_probs. This will generate an individual number with
            # probability P[Fdrx].
                rmn = np.random.choice(np.arange(feeders[0],(feeders[len(feeders)-1]+1)), p=fdr_probs)
                dist_fdrs.append(rmn)
        elif len(dist_fdrs) > trials:
            for i in range(trials - len(dist_fdrs)):
            # Generate a random number with probability given by the fdr_probs
            # list and remove the first occurance of it. Repeat until the list
            # is of appropriate length.
                rmv = np.random.choice(np.arange(feeders[0],(feeders[len(feeders)-1]+1)), p=fdr_probs)
                dist_fdrs.remove(rmv)
        
        return dist_fdrs, dist_lvls
    
    def wait(self, interval):
        for i in range(interval):
            time.sleep(1)
            print('*', end="")
        return 0
    
    def save_list(self, fdr_list, lvl_list, filename):
        print("\nSaving the following trial list as comma-separated values file:")
        print("Feeders:", fdr_list)
        print("Levels:", lvl_list)
        
        rows = zip(fdr_list, lvl_list)
        
        fieldnames = ["feeder", "cost_level"]
        with open(filename+".csv", 'w', encoding='UTF8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(fieldnames)
            for row in rows:
                writer.writerow(row)
        return 0
    
    def load_list(self, trial_csv):
        filename = open(trial_csv+'.csv', 'r')
        
        # creating dictreader object
        file = csv.DictReader(filename)
         
        # creating empty lists
        feeders = []
        levels  = []
         
        # iterating over each row and append
        # values to empty list
        for col in file:
            feeders.append(col['feeder'])
            levels.append(col['cost_level'])
        
        feeders = list(map(int, feeders))
        levels = list(map(int, levels))
        
        return feeders, levels
    
    def zone_status(self, filepath,
                    roi='all',
                    return_last=False,
                    expect_zones=[1,2,3,4]):
        # Parse arguments
        try:
            if exists(filepath):
                pass
            else:
                raise InexistantFileError(filepath)
            if type(roi) is str:
                roi_index = 0
                if 'diag' in roi:
                    roi_index = 1
                elif 'grid' in roi:
                    roi_index = 2
                elif 'hori' in roi:
                    roi_index = 3
                elif 'radi' in roi:
                    roi_index = 4
                else:
                    raise InvalidROIError(roi)
            elif type(roi) is int and roi in expect_zones:
                roi_index = roi
            else:
                raise InvalidROIError(roi)
        except InvalidROIError as error:
            print("Invalid ROI Error: The input region of interest, '", error.value, "', is not defined in list of available feeders or is not a valid value.")
            return -1
        except InexistantFileError as fileerror:
            print("Invalid filepath, please check that the following path contains the Bonsai rat tracking file:'", fileerror.value, "'")
            return -1
        else:
            # Open the CSV file...
            filename = open(filepath, 'r')
            print("hewwooo")
            # Create dictreader object to read CSV file using the headers.
            file = csv.DictReader(filename)
             
            # Create empty lists to store the read values into depending on
            # what the region of interest (roi) is, then...
            # Use the dict reader object to iterate through every row in the CSV
            # file and create dictionary objects out of each. The key on each
            # dictionary will correspond to the header in the CSV file, which we
            # define in the "row['XXX']" segment.
            # At the same time, fetch and convert each dictionary entry to a string
            # (in case it isn't a string already), and convert it to a boolean
            # if that string matches any of the expected values.
            # Finally, append the resulting bollean to the empty lists defined
            # above.
            list_index = 0
            if roi_index == 1:
                IsInDIAG = []
                for row in file:
                    IsInDIAG.append(str(row['IsInDIAG']).lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh'])
                    list_index += 1
                if return_last:
                    return IsInDIAG[list_index-1]
                else:
                    return IsInDIAG
            elif roi_index == 2:
                IsInGRID = []
                for row in file:
                    IsInGRID.append(str(row['IsInGRID']).lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh'])
                    list_index += 1
                if return_last:
                    return IsInGRID[list_index-1]
                else:
                    return IsInGRID
            elif roi_index == 3:
                IsInHORI = []
                for row in file:
                    IsInHORI.append(str(row['IsInHORI']).lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh'])
                    list_index += 1
                if return_last:
                    return IsInHORI[list_index-1]
                else:
                    return IsInHORI
            elif roi_index == 4:
                IsInRADI = []
                for row in file:
                    IsInRADI.append(str(row['IsInRADI']).lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh'])
                    list_index += 1
                if return_last:
                    return IsInRADI[list_index-1]
                else:
                    return IsInRADI
            else:
                IsInDIAG = []
                IsInGRID = []
                IsInHORI = []
                IsInRADI = []
                for row in file:
                    IsInDIAG.append(str(row['IsInDIAG']).lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh'])
                    IsInGRID.append(str(row['IsInGRID']).lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh'])
                    IsInHORI.append(str(row['IsInHORI']).lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh'])
                    IsInRADI.append(str(row['IsInRADI']).lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh'])
                    list_index += 1  # Will give the length of the whole dataset
                if return_last:
                    return [IsInDIAG[list_index-1], IsInGRID[list_index-1], IsInHORI[list_index-1], IsInRADI[list_index-1]]
                else:
                    return [IsInDIAG, IsInGRID, IsInHORI, IsInRADI]
    
class InvalidROIError(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
    # Prints the error value
        return(repr(self.value))

class InexistantFileError(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
    # Prints the error value
        return(repr(self.value))