import pickle
import random

max_cars = 240

class ICStatistics(object):

    def __init__ (self, path):
        self.path = path
        """
        try:
            with open(path + 'history/history.pkl', 'r') as f:
                self.history = pickle.load(f)
	except IOError:
	    self.history = []
	    with open(path + 'history/history.pkl', 'w') as f:
	        pickle.dump(self.history, f)
        """
        # for now let us have a clear the history at every new simulation
        self.history = []
	with open(path + 'history/history.pkl', 'w') as f:
	    pickle.dump(self.history, f)
		
    def saveHistory(self):
	with open(self.path + 'history/history.pkl', 'w') as f:
            pickle.dump(self.history, f)

    def refreshHistory(self):
        with open(self.path + 'history/history.pkl', 'r') as f:
                self.history = pickle.load(f)
            
    def carsMeanNormalize(self, val):
        return ((val - (max_cars / 2.)) / max_cars) * 2

    def addItem(self, prevState, action, nextState, reward):
        newItem = {}
	newItem['prev_state'] = prevState
	newItem['action_id'] = action
        newItem['next_state'] = nextState
        newItem['reward'] = reward
        self.history.append(newItem)
	self.saveHistory()

    def getTrainingBatch(self, n):
        result = []
        self.refreshHistory()
        item = self.history[-1]
        item['prev_state'][0] = self.carsMeanNormalize(item['prev_state'][0])
        item['prev_state'][1] = self.carsMeanNormalize(item['prev_state'][1])
        item['next_state'][0] = self.carsMeanNormalize(item['next_state'][0])
        item['next_state'][1] = self.carsMeanNormalize(item['next_state'][1])
        result.append(item)
        """
        result = []
        for i in range(n):
            item = self.history[random.randint(0, self.featureParams[1]-1)]
            item['prev_state'][0] = self.carsMeanNormalize(item['prev_state'][0])
            item['prev_state'][1] = self.carsMeanNormalize(item['prev_state'][1])
            item['next_state'][0] = self.carsMeanNormalize(item['next_state'][0])
            item['next_state'][1] = self.carsMeanNormalize(item['next_state'][1])
            result.append(item)
        """
        return result
