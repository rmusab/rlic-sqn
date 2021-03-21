#!/usr/bin/python

import random, sys
sys.path.append('/usr/lib/sumo/tools')
import traci
import numpy as np
from ICStatistics import ICStatistics
from NeuralNetwork import NeuralNetwork

class Intersection(object):
	def __init__(self, id, edges, interphaseDuration, minPhaseDuration, maxPhaseDuration, signalPlan):
		self.id = id
		self.edges = edges
		self.interphaseDuration = interphaseDuration
		self.minPhaseDuration = minPhaseDuration
		self.maxPhaseDuration = maxPhaseDuration
		self.signalPlan = signalPlan
		self.cycleCount = 0
		
	def getIntersectionId(self):
		return self.id
		
	def getEdgeIds(self):
		return self.edges
		
	def getInterphaseDuration(self):
		return self.interphaseDuration
		
	def getMinPhaseDuration(self):
		return self.minPhaseDuration
		
	def getMaxPhaseDuration(self):
		return self.maxPhaseDuration
	
	def getSignalPlan(self):
		return self.signalPlan
	
	def getCycleLength(self):
		return self.interphaseDuration+self.signalPlan['NS']+self.signalPlan['WE']
	
	def setSignalPlan(self, signalPlan):
		self.signalPlan = signalPlan
	
	def getCycleCount(self):
		return self.cycleCount
		
	def incrementCycleCount(self):
		self.cycleCount += 1

gamma = 0.6
epsilon = 0.1
train_num = 1
iter_num = 1
reg_param = 0.03

# Dictionary of states: state-index pairs
# ============================================
stateDict = {}
stateComponents = ['EL', 'L', 'M', 'H', 'EH']
counter = 0
for i in stateComponents:
	for j in stateComponents:
		stateDict[i+j] = counter
		counter += 1
# ============================================

class NNIntersection(Intersection):
	def __init__(self, id, edges, interphaseDuration, minPhaseDuration, maxPhaseDuration, signalPlan, listOfActions):
		Intersection.__init__(self, id, edges, interphaseDuration, minPhaseDuration, maxPhaseDuration, signalPlan)

                # Instantiate the ICStatistics class
                self.myStatistics = ICStatistics('')
                # Instantiate the NeuralNetwork class
                self.myNeuralNetwork = NeuralNetwork(2, 25, 3, reg_param, gamma, train_num)
                self.iterationsSoFar = 0
                
		self.prevState = {'NS':0, 'WE': 0}
		self.currentState = {'NS':0, 'WE': 0}	# new state
		self.currentAction = 0					# index of a new action (not the action itself)
		self.states = []						# states [[NS_1, WE_1], [NS_2, WE_2] ... ]
		self.actions = []						# indeces of performed actions
		self.EndOfRedPhases = {	'NS':signalPlan['NS'] + signalPlan['WE'] + interphaseDuration, 
								'WE': signalPlan['NS'] + int(0.5*interphaseDuration)
							  }	
		self.definedActionSet = listOfActions	# actions themselves
		self.rewards = []
	
	def getStates(self):
		return self.states
		
	def getActions(self):
		return self.actions
	
	def setEndOfRedPhases (self, timeMS):
		self.EndOfRedPhases['WE'] = timeMS + self.signalPlan['NS'] + int(0.5*self.interphaseDuration)
		self.EndOfRedPhases['NS'] = timeMS + self.signalPlan['NS'] + self.signalPlan['WE'] + self.interphaseDuration
		
	def getEndOfRedPhases(self):
		return self.EndOfRedPhases
	
	def updateStates(self):
		self.states.append([self.prevState['NS'], self.prevState['WE']])
		
	def setCurrentAction(self, action):
		self.actions.append(self.currentAction)
		self.currentAction = action
			
	def getStateIndex(self, state):
		'''
		The function returns an index corresponding to the state (number of halting vehicles in all defined directions) 
		'''
		global stateDict
		haltingCars = []
		
		if type(state)==type({}):
			haltingCars.append(state['NS'])
			haltingCars.append(state['WE'])
		else:
			haltingCars = state
			
		stateKey = ''
		for n in haltingCars:
			if n<=20:
				stateKey +='EL'
			elif n>20 and n<=40:
				stateKey +='L'
			elif n>40 and n<=70:
				stateKey += 'M'
			elif n>70 and n<=100:
				stateKey += 'H'
			elif n>100:
				stateKey += 'EH'
		
		return stateDict[stateKey]
	
	def convertStatesToStateIndeces(self):
		l = []
		for st in self.states:
			l.append(self.getStateIndex(st))
			
		return l
	
	def setTrafficLightLogic(self):
		'''
		It is assumed that the number of phases does not change and always equal to 8 for all controlled intersections. 
		The indexation starts from 0.
		'''
                
		gyrDef = traci._trafficlights.Logic('SP'+self.id,0,0,0,
			[
			traci._trafficlights.Phase(self.signalPlan['NS'], self.signalPlan['NS'], self.signalPlan['NS'], 'GGGgrrrrGGGgrrrr'),
			traci._trafficlights.Phase(3000, 3000, 3000, 'yyygrrrryyygrrrr'),
			traci._trafficlights.Phase(6000, 6000,6000, 'rrrGrrrrrrrGrrrr'),
			traci._trafficlights.Phase(3000, 3000, 3000, 'rrryrrrrrrryrrrr'),
			traci._trafficlights.Phase(self.signalPlan['WE'], self.signalPlan['WE'], self.signalPlan['WE'], 'rrrrGGGgrrrrGGGg'),
			traci._trafficlights.Phase(3000, 3000, 3000, 'rrrryyygrrrryyyg'),
			traci._trafficlights.Phase(6000, 6000, 6000, 'rrrrrrrGrrrrrrrG'),
			traci._trafficlights.Phase(3000, 3000, 3000, 'rrrrrrryrrrrrrry')
			]
		);
		
		traci.trafficlights.setCompleteRedYellowGreenDefinition(self.id, gyrDef)
		traci.trafficlights.setPhase(self.id,0)
		traci.trafficlights.setProgram(self.id, 'SP0')
		
		traci.trafficlights.setProgram(self.id, 'SP'+self.id)

	def chooseAction(self, currentState):
		global epsilon
		
		action = 0
		if (random.random() < epsilon):
			action = random.randint(0,len(self.definedActionSet)-1)
			print '\n\tAction:',action,'random\n'
		else:
                        sNS = self.myStatistics.carsMeanNormalize(currentState['NS'])
                        sWE = self.myStatistics.carsMeanNormalize(currentState['WE'])
                        s = np.array([sNS, sWE]).reshape(1, 2)
                        z3 = self.myNeuralNetwork.predict(s)
                        z3 = z3.tolist()[0]
			action = z3.index(max(z3))
                        print '\tz3 = [%0.3f, %0.3f, %0.3f]' % (z3[0], z3[1], z3[2])
                        print '\n\tAction:',action,' neural network\n'
			
		return action

        def checkAction(self, actionIndex):
                return self.signalPlan['NS']+self.definedActionSet[actionIndex][0]>=self.minPhaseDuration and self.signalPlan['NS']+self.definedActionSet[actionIndex][0]<=self.maxPhaseDuration and self.signalPlan['WE']+self.definedActionSet[actionIndex][1]>=self.minPhaseDuration and self.signalPlan['WE']+self.definedActionSet[actionIndex][1]<=self.maxPhaseDuration
		
	def neuralNetwork(self):
		# choose and perform action
		actionIndex = None
		isFeasibleAction = False
                prevActionIndex = self.currentAction
                
		while not isFeasibleAction:
			actionIndex = self.chooseAction(self.currentState)
			if self.checkAction(actionIndex):
				self.signalPlan['NS'] = self.signalPlan['NS']+self.definedActionSet[actionIndex][0]
				self.signalPlan['WE'] = self.signalPlan['WE']+self.definedActionSet[actionIndex][1]
				isFeasibleAction = True
			else:
                                """
                                # penalizing the neural network for taking an unfeasible action
                                s1 = [self.prevState['NS'], self.prevState['WE']]
                                self.myNeuralNetwork.penalize(s1, actionIndex)
                                print '\n\tNeural Network has been penalized\n'
                                """
                                # if the neural network predicted an unfeasible action, we will just choose a random action until it is feasible
                                while not isFeasibleAction:
                                        actionIndex = random.randint(0,len(self.definedActionSet)-1)
                                        if self.checkAction(actionIndex):
                                                self.signalPlan['NS'] = self.signalPlan['NS']+self.definedActionSet[actionIndex][0]
				                self.signalPlan['WE'] = self.signalPlan['WE']+self.definedActionSet[actionIndex][1]
                                                print '\n\tAction:',actionIndex,' random after unfeasible action\n'
                                                isFeasibleAction = True
		self.setCurrentAction(actionIndex)
		#prevActionIndex = self.actions[-1]
	        
		reward = abs(self.prevState['NS'] - self.prevState['WE']) - abs(self.currentState['NS'] - self.currentState['WE']) + self.prevState['NS'] + self.prevState['WE'] - (self.currentState['NS'] + self.currentState['WE'])
		print '\treward: ', reward
		self.rewards.append(reward)
		print '\tUpdated signal plan NS:', self.signalPlan['NS'], ' WE:',self.signalPlan['WE']
		
		# Add the current training example to the history
                s1 = [self.prevState['NS'], self.prevState['WE']]
                #s1 = self.getStateIndex(self.prevState)
                a = prevActionIndex
		s2 = [self.currentState['NS'], self.currentState['WE']]
                #s2 = self.getStateIndex(self.currentState)
		self.myStatistics.addItem(s1, a, s2, reward)
                
                self.iterationsSoFar += 1
                # Train the NN
                if self.iterationsSoFar == iter_num:
                        self.myNeuralNetwork.gradientDescent()
                        self.iterationsSoFar = 0
		
		self.setTrafficLightLogic()
		
	def trainIntersection(self, step):
		# detect the begining of the next cycle for an intersection
		if step==0:
			print "Cycle: ", self.getCycleCount(), "	 step: ", step
			print 'End of red:', self.getEndOfRedPhases(), '\n'
		
		# if end of WE red phase
		if 1000*step==(self.getEndOfRedPhases()['WE']):
			# get number of cars WE in direction
			vehicleNum = 0
			for edge in self.getEdgeIds()['WE']:
				vehicleNum += traci.edge.getLastStepHaltingNumber(edge)
			self.prevState['WE'] = self.currentState['WE']
			self.currentState['WE'] = vehicleNum
			print "\n\tEnd of the West-East red phase\n\tweCars = ", vehicleNum
			
		# if end of NS red phase
		if 1000*step==(self.getEndOfRedPhases()['NS']):
			# get number of cars NS in direction
			vehicleNum = 0
			for edge in self.getEdgeIds()['NS']:
				vehicleNum += traci.edge.getLastStepHaltingNumber(edge)
			self.prevState['NS'] = self.currentState['NS']
			self.currentState['NS'] = vehicleNum
			print "\n\tEnd of the North-South red phase\n\tnsCars = ", vehicleNum
			
			# append currentState to list of states
			self.updateStates()
		
			# Report the state change
			currentStateIndex = self.getStateIndex(self.currentState)
			prevStateIndex = self.getStateIndex(self.states[-1])
                        prevStateLabel = [label for label, index in stateDict.items() if index == prevStateIndex][0]
                        currentStateLabel = [label for label, index in stateDict.items() if index == currentStateIndex][0]
			print '\tStates:',prevStateLabel,'-->',currentStateLabel,'\n'
					
			# Neural Network: choose action, perform action, perform backpropagation
			self.neuralNetwork()
			
			# increment cycle count
			self.incrementCycleCount()
			
			self.setEndOfRedPhases(1000*step)
			print "\nCycle: ", self.getCycleCount(), "	 step: ", step
			print 'End of red:', self.getEndOfRedPhases()
