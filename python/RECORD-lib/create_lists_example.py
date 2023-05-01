# -*- coding: utf-8 -*-
"""
Created on Fri Sep  9 16:13:48 2022

@author: Raquel Ibáñez Alcalá
"""
from record_lib import TRIALS

# How to use the TRIALS class:
# Initialize the class and call it "mytrials":
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
                                              T_intertrial=3,
                                              T_decision=1,
                                              T_feeding=6,
                                              trials=10,
                                              avail_lvls=[0,1,2,3],
                                              avail_fdrs=['a','b','c','d'],
                                              P_lvls=[0,0.33,0.33,0.34],
                                              P_fdrs=[0.25,0.25,0.25,0.25]                                         
                                              )

# This will simply show you the trial session details, or the "metadata" for
# this trial session. The dictionary object will be printed to the console.
print(myparameters)

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
tlist_fdrs , tlist_lvls = mytrials.create_trial_list(avail_fdrs=[1,2,3,4])

# Finally, we have our lists here. We can print them to the console to show
# them off, or pass them on to an actual trial. For an example on how to do
# this, see the "trail_example.py" script.
print(tlist_fdrs)
print(tlist_lvls)

# You can implement a wait that prints asterisks to the console to symbolise
# seconds. It's useful if you want to do this for a command line interface,
# but you can absolutely implement a different kind of delay. Simply give this
# "wait" method a whole number for the amount of seconds you want to wait and
# watch it go.
mytrials.wait(4)

# ############################################################################## 
# # Initialize all trial variables: 
# #    1. inter_trial_interval: The time to wait in-between trials, in seconds.
# #    2. decision_interval: The time to wait while rat is making a decision,
# #       in seconds.
# #    3. feeding_interval: The time to wait while rat is eating, in seconds.
# #    4. trials: Number of trials in session.
# #    5. levels: (List) Available cost levels, whole numbers only.
# #    6. feeders: (List) Available feeders, whole numbers only.
# #    7. lvl_probs: (List) Probability for each cost level to appear in a trial
# #       list, position-sensitive. Reads as: P[lvl0], P[lvl1], P[lvl2], P[lvl3].
# #    8. fdr_probs: (List) Probability for each feeder to appear in a trial
# #       list, position sensitive. Reads as: P[fdr1], P[fdr2], P[fdr3], P[fdr4].
# #       
# #    The sum of elements in lvl_probs must equal 1.
# #    The sum of elements in fdr_probs must also equal 1.
# #    
# #    Using this format to imitate the JSON format from an AJAX request as I
# #    might implement this script as API for a web interface.
# # 
# trialParams = {'inter_trial_interval': 5,
#                 'decision_interval'   : 5,
#                 'feeding_interval'    : 2,
#                 'trials'              : 4,
#                 'levels'              : [0, 1, 2, 3],
#                 'feeders'             : [1, 2, 3, 4],
#                 'lvl_probs'           : [0, 0.5, 0, 0.5],
#                 'fdr_probs'           : [0.25, 0.25, 0.25, 0.25]
#                 }
# # #
# # ############################################################################## 

# # Parse incoming trial parameters...
# inter_trial_interval = trialParams.get('inter_trial_interval')
# decision_interval = trialParams.get('decision_interval')
# feeding_interval = trialParams.get('feeding_interval')
# trials = trialParams.get('trials')
# lvls= trialParams.get('levels')
# feeders = trialParams.get('feeders')
# lvl_probs = trialParams.get('lvl_probs')
# fdr_probs = trialParams.get('fdr_probs')

# dist_lvls = []
# dist_fdrs = []

# # Multiply the probabilistic distribution list by the total number of trials
# # to find out how many aprearances of each level should be found in the trial
# # list...
# lvl_num = list(np.array(lvl_probs) * trials)
# print("I will first make a list of 'cost level' parameters that we'll use in your trials:")
# print("  Level 0 will appear", lvl_num[0], "times,")
# print("  Level 1 will appear", lvl_num[1], "times,")
# print("  Level 2 will appear", lvl_num[2], "times,")
# print("  And level 3 will appear", lvl_num[3], "times.\r\n...Just a moment!")

# for i in range(len(lvl_num)):
#     lvl_num[i] = int(lvl_num[i])
#     # Begin generating the levels in the trial list...
#     for _ in range(lvl_num[i]):
#         dist_lvls.append(lvls[i])

# print("Done! Here's the list of levels that I got, keep in mind that I will shuffle these numbers later:")
# print(dist_lvls)
# print("\r\n")
# # At this point you will have a list of n repetitions of each number
# # representation of every level in the list, however all numbers will be in
# # order; for example, if your probability distribution (lvl_probs) looked like
# # "[0, 0.25, 0.25, 0.25, 0.25]", meaning equal probabilities for every level
# # except for level 0, and you wish to generate 40 trials, then the dist_lvls
# # list will have 0 repetitions of the number 0, 10 repetitions of the number
# # 1, 10 repetitions of the number 2, and so on, like so:
# # [1,1,1,1,...1, 2,2,2,2,...,2, 3,3,3,3,...,3].

# # Repeat the process above for the list of feeders...
# fdr_num = list(np.array(fdr_probs) * trials)
# print("Next, I will make a list of 'feeder IDs' that we'll couple with those cost levels:")
# print(" Feeder 1 will appear", fdr_num[0], "times,")
# print(" Feeder 2 will appear", fdr_num[1], "times,")
# print(" Feeder 3 will appear", fdr_num[2], "times,")
# print(" And feeder 4 will appear", fdr_num[3], "times.\r\nLet me calculate that!")
# for i in range(len(fdr_num)):
#     fdr_num[i] = int(fdr_num[i])
#     # Begin generating the levels in the trial list...
#     for _ in range(fdr_num[i]):
#         dist_fdrs.append(feeders[i])

# print("And done! These are your feeders. Again, I'll shuffle these around later':")
# print(dist_fdrs)
# print("\r\n")



# # The lists now need to be shuffled to make the order of these numbers appear
# # as random as possible...
# print("Let's shuffle these now!")
# rand.shuffle(dist_fdrs)
# print("Feeders after shuffling:")
# print(dist_fdrs)
# rand.shuffle(dist_lvls)
# print("Levels after shuffling:")
# print(dist_lvls)

# answer = ""
# cont = 1
# while cont:
#     answer = input("Do you wish to continue with these lists? Or if you want to re-shuffle, just say 'r'. [y/n/r]\r\n")
#     if answer.lower().startswith("y"):
#         print("\r\nGreat! Continuing on to execution of", trials, "trials...\r\n")
#         cont = 0
#     elif answer.lower().startswith("r"):
#         rand.shuffle(dist_fdrs)
#         print("Feeders after re-shuffling:")
#         print(dist_fdrs)
#         rand.shuffle(dist_lvls)
#         print("Levels after re-shuffling:")
#         print(dist_lvls)
#     elif answer.lower().startswith("n"):
#         print("\r\nStopping script. See you later!\r\n")
#         sys.exit()