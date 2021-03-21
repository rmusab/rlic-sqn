import numpy as np
import sys
from ICStatistics import ICStatistics

max_iter = 5
alpha = 0.001
penalty_num = 10
penalty_reward = -5

class NeuralNetwork(object):
  def __init__ (self, inLayerSize, hidLayerSize, outLayerSize, regParameter, gamma, trainNum):
    self.inLayerSize = inLayerSize
    self.hidLayerSize = hidLayerSize
    self.outLayerSize = outLayerSize
    self.regParameter = regParameter
    self.gamma = gamma
    self.trainNum = trainNum
    
    self.Theta1 = self.randWeights(inLayerSize, hidLayerSize)
    self.Theta2 = self.randWeights(hidLayerSize, outLayerSize)
    self.Grad1 = np.zeros((inLayerSize, hidLayerSize))
    self.Grad2 = np.zeros((hidLayerSize, outLayerSize))
    self.myStatistics = ICStatistics('')
    self.X1 = np.zeros((self.trainNum, self.inLayerSize))
    self.X2 = np.zeros((self.trainNum, self.inLayerSize))
    self.rewards = np.zeros(self.trainNum)
    self.trainBatch = []
    self.penaltyCount = 0
    self.pX = np.zeros((penalty_num, self.inLayerSize))
    self.pActions = np.zeros(penalty_num)
    
  def randWeights(self, lIn, lOut):
    epsilonInit = 0.12
    return np.random.randn(lOut, 1 + lIn) * 2 * epsilonInit - epsilonInit
    
  def sigmoid(self, z):
    return 1. / (1. + np.exp(-z))

  def sigmoidGradient(self, z):
    return self.sigmoid(z) * (1. - self.sigmoid(z))

  def relu(self, z):
    return z * (z > 0)

  def reluGradient(self, z):
    return 1 * (z > 0)

  def predict(self, X):
    m = X.shape[0]
    X = np.insert(X, 0, np.ones(m), axis=1)
    z2 = np.dot(self.Theta1, X.T).T
    a2 = self.relu(z2)
    a2 = np.insert(a2, 0, np.ones(m), axis=1)
    z3 = np.dot(self.Theta2, a2.T).T
    return z3
    
  def feedforward(self, X):
    m = X.shape[0]
    z2 = np.dot(self.Theta1, X.T).T
    a2 = self.relu(z2)
    a2 = np.insert(a2, 0, np.ones(m), axis=1)
    z3 = np.dot(self.Theta2, a2.T).T
    return (z2, a2, z3)
    
  def getTrainingData(self):
    self.trainBatch = self.myStatistics.getTrainingBatch(self.trainNum)
    self.X1 = np.zeros((self.trainNum, self.inLayerSize))
    self.X2 = np.zeros((self.trainNum, self.inLayerSize))
    self.rewards = np.zeros(self.trainNum)
    for i, item in enumerate(self.trainBatch):
        self.X1[i,0] = item['prev_state'][0]
        self.X1[i,1] = item['prev_state'][1]
        self.X2[i,0] = item['next_state'][0]
        self.X2[i,1] = item['next_state'][1]
        self.rewards[i] = item['reward']
    self.X1 = np.insert(self.X1, 0, np.ones(self.trainNum), axis=1)
    
  def backpropGradient(self, penalize=False):
    m = self.X1.shape[0]
    (z2, a2, z3) = self.feedforward(self.X1)    
    if not penalize:
      nextZ3 = self.predict(self.X2)
      targetQ = np.copy(z3)
      for i in range(m):
        maxNextQVal = np.amax(nextZ3[i,:])
        maxPrevQValIndex = np.argmax(z3[i,:])
        targetQ[i,maxPrevQValIndex] = self.rewards[i] + self.gamma * maxNextQVal
    else:
      targetQ = np.copy(z3)
      for i in range(m):
        targetQ[i,self.pActions[i]] += penalty_reward # substract a fixed negative reward
    
    z2 = np.insert(z2, 0, np.ones(m), axis=1)
    delta3 = z3 - targetQ
    delta2 = np.dot(self.Theta2.T, delta3.T).T * self.reluGradient(z2)
    delta2 = delta2[:, 1:]
    DELTA1 = np.dot(delta2.T, self.X1)
    DELTA2 = np.dot(delta3.T, a2)
    self.Grad1 = 1. / float(m) * DELTA1
    self.Grad2 = 1. / float(m) * DELTA2
    
    # Adding regularization to the gradient
    for i in range(self.Grad1.shape[0]):
        for j in range(1, self.Grad1.shape[1]):
            self.Grad1[i, j] += float(self.regParameter) / float(m) * self.Theta1[i, j]
    for i in range(self.Grad2.shape[0]):
        for j in range(1, self.Grad2.shape[1]):
            self.Grad2[i, j] += float(self.regParameter) / float(m) * self.Theta2[i, j]

  def gradientDescent(self):
    global max_iter

    self.getTrainingData()
    for i in range(max_iter):
      self.backpropGradient()
      self.Theta1 -= alpha * self.Grad1
      self.Theta2 -= alpha * self.Grad2

  def penalize(self, prevState, a):
    self.penaltyCount += 1
    self.pX[self.penaltyCount-1,0] = self.myStatistics.meanNormalize(prevState[0])
    self.pX[self.penaltyCount-1,1] = self.myStatistics.meanNormalize(prevState[1])
    self.pActions[self.penaltyCount-1] = a
    if self.penaltyCount == penalty_num:
      self.X1 = np.copy(self.pX)
      self.X1 = np.insert(self.X1, 0, np.ones(punish_num), axis=1)
      for i in range(max_iter):
        self.backpropGradient(True)
        self.Theta1 -= alpha * self.Grad1
        self.Theta2 -= alpha * self.Grad2
      self.penaltyCount = 0
