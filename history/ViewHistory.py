#!/usr/bin/python

import pickle

with open('history.pkl', 'r') as f:
    history = pickle.load(f)

for item in history:
    print item
print "length = %d" % (len(history))
