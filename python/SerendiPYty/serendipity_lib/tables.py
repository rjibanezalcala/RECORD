# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 16:35:48 2023
Last updated 
v0.0.0

@author: Raquel Ibáñez Alcalá

Table definitions for PostgreSQL database.

"""

class Tables:
    def __init__(self):
        self.rats = [
                'subjectid',
                'gender',
                'birthdate',
                'genotype',
                'cagenumber',
                'health',
                'cagemate',
                'subjectidnumber',
                'subjecthealth',
                'subjectweight',
                'notes',
                'tasktypedone',
                'accutemanipulation'
                ]
        
        self.session = [
                   'sessionstart',
                   'trials',
                   'costlevels',
                   'costprobabilities',
                   'rewardlevels',
                   'rewardprobabilities',
                   't_intertrial',
                   't_decision',
                   't_feeding',
                   'sessionduration',
                   'recordingtype',
                   'localindex'
                   ]
        
        self.tevents = [
                  # Trial timestamps and information
                  'trial_start',
                  'trial_end',
                  'trial_elapsed',
                  'trial_index',
                  'cost_level',
                  'cost_intensity',
                  'reward_concentration',
                  'reward_level',
                  'decision_made',
                  # Events
                  'play_tone',
                  'first_reset',
                  'mcu_timer_start',
                  'trial_start_cue',
                  'offer_presented',
                  'reward_delivery',
                  'last_reset',
                  'mcu_timer_stop',
                  'decision_ts',
                  'extsys_on',
                  'extsys_off',
                  # MCU responses and acknowledgements
                  'first_reset_resp',
                  'first_reset_ack',
                  'mcu_timer_start_resp',
                  'mcu_timer_start_ack',
                  'trial_start_cue_resp',
                  'trial_start_cue_ack',
                  'offer_presented_resp',
                  'offer_presented_ack',
                  'reward_delivery_resp',
                  'reward_delivery_ack',
                  'last_reset_resp',
                  'last_reset_ack',
                  'mcu_timer_stop_resp',
                  'mcu_timer_stop_ack',
                  'extsys_on_resp',
                  'extsys_on_ack',
                  'extsys_off_resp',
                  'extsys_off_ack'
                  ]
        
        # These can be considered as keys for a dictionary instead.
        self.position = [
                   'positionx',
                   'positiony',
                   'orientation',
                   'isindiag',
                   'isingrid',
                   'isinhori',
                   'isinradi',
                   'timestamp'
                   ]
        
        
        self.traces = [
                   'timestamp',
                   'celltrace',
                   'props'
                   ]
        
        # These can be considered as keys for a dictionary instead.
        self.traevents = [
                    'cellevent',
                    'cellstatus'
                   ]
        
        self.props = [
                    'name',
                    'snr',
                    'eventrate(hz)']
        
        self.dictdata = [
                   'positiondata',
                   'celltracedata',
                   'celleventdata'
                   ]
        
        self.pointers = [
                   'positionpointers',      # 2D array where each column is a set of pointers for each trial event.
                   'celltracepointers'      # 2D array where each column is a set of pointers for each trial event.
                  ]
        
        self.ephys = []
        
        self.housekeep = [
                   'sessionid'                 # Unique database id number generated by SQL database.
                   ]
        self.rectype_codes = {'calciumimaging':'CI', 'optogenetics':'OPG', 'electrophysiology':'EPH', 'behavior':'BEH', 'undefinied':'UDF'}
       # Task type code (P2A, L1, L1L3, PAV, P1)
        self.task_codes = {'alcohol':'P2A', '[0,1,0,0]':'L1', '[0,0.5,0,0.5]':'L1L3', '[0,0,0,0]':'PAV', '[0.25,0.25,0.25,0.25]':'P1'}
        self.mani_codes = {'fooddeprivation':'fd', 'saline':'sal', 'isoflurane':'iso', 'prefeeding':'pf', 'ghrelin':'ghr', 'alcohol':'alc'}
        self.submani_codes = {'fooddeprivation':'NF', 'saline':'GHR-S', 'isoflurene':'GHR-ISO', 'prefeeding': 'PF', 'ghrelin':'GHR', '2xghrelin':'GHR-2X', 'noinjection':'GHR-N'}