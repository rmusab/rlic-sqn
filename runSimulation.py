#!/usr/bin/python

import os, sys
import random	

import subprocess
sys.path.append('/usr/lib/sumo/tools')
import traci

from NNIntersection import NNIntersection

import io

def reportStatistics(outFileName, node):
	'''
	write states' indeces, performed actions, north-south halting cars, west-east halting cars, rewards to a file
	'''
	states = node.getStates()
	actions = node.getActions()
	rewards = node.rewards
	
	if not actions:
		actions = [0]*len(states)
		
	nsCars = [item[0] for item in states]
	weCars = [item[1] for item in states]
	with io.open(outFileName, 'w') as f:
		f.writelines(str(st) + u'\t' + str(ac) + u'\t' + str(ns)+ u'\t' + str(we) + u'\t' + str(re) + u'\n' for (st, ac, ns, we, re) in zip(node.convertStatesToStateIndeces(), actions, nsCars, weCars, rewards))

#======================= INIT TRACI =======================
PORT = 8873

if True:
	sumoBinary = "sumo"
else:
	sumoBinary = "sumo-gui"
"""
if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:	 
	sys.exit("please declare environment variable 'SUMO_HOME'")
"""

sumoProcess = subprocess.Popen([sumoBinary, "-c", "data/test.sumocfg", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)

traci.init(PORT)

#==================== INITIALIZATION =================

dt = 3000
actionList = [[0,0], [+dt,-dt], [-dt,+dt]]

# Define the constraints
mainPhaseDuration = 66000
minPhaseDuration = 12000
maxPhaseDuration = mainPhaseDuration - minPhaseDuration
interPhase = 24000

node0 = NNIntersection('0', {'NS':['D10','D30'], 'WE':['D40','D20']}, interPhase, minPhaseDuration, maxPhaseDuration, {'NS':24000, 'WE':42000}, actionList)

node0.setTrafficLightLogic()

#======================= RUN =======================
step = 0
#604800
while step < 100000:
	node0.trainIntersection(step)
	traci.simulationStep()
	step+=1
traci.close()

reportStatistics('output.txt', node0)
sumoProcess.wait()
