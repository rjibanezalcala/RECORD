# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 14:40:02 2022

@author: Raquel Ibáñez Alcalá

Example script showing how to save and load trial lists for the
RECORD system.
"""

from record_lib import TRIALS

# Declare the TRIALS class.
mytrials = TRIALS()

# We'll start with creating two example lists, ordered so that we know that we
# can retreive the same lists after saving.
feeders_list = [1,2,3,4,1,2,3,4]
levels_list  = [0,1,2,3,0,1,2,3]

print("Created lists:")
print("Feeders:", feeders_list)
print("Levels:", levels_list)

# Save these lists. They will be saved in one file called whatever you pass to
# the third argument of the "save_list" method.
filename = "trial_list_example"
mytrials.save_list(feeders_list, levels_list, filename)

# At this point, you'll see a new file created in the same folder where this
# example script is contained. Add a path to the "filename" variable if you
# wish to save it elsewhere.

# Let's load that trial list, we just need to give the "load_list" method the
# name of the file you created with "save_list". Notice how we're calling
# this method. We need two containers to put the loaded lists into. The first
# has to be the container for the feeders list, and the second the one for the
# levels.
# We'll just overwrite the containers we defined above this time, but it is not
# recommended to do so in practice.
feeders_list, levels_list = mytrials.load_list(filename)

# Now you should have the same two lists that we defined at the beginning of
# this example in their respective containers! Use them as any other list
# object.
print("\r\nLoaded lists from file:")
print("Feeders:", feeders_list)
print("Levels:", levels_list)
