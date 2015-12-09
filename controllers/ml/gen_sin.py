#!/usr/bin/env python
from keras.models import Sequential, Graph
from keras.models import model_from_json
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import SGD
import numpy as np
import theano, sys

import numpy as np                                                                                                                
import pandas as pd

def fn(xt) :
  return np.sin(xt) #+ 2*np.cos(np.multiply(2.1, xt)) - 1.4*np.cos(3.4*np.sin(np.multiply(xt, xt)))

# xt = np.random.rand(10000, 1)
# xt = np.multiply(xt, 10)
# yt = fn(xt)
# 
# dx = pd.DataFrame(xt)
# dy = pd.DataFrame(yt)
# 
# dx.to_csv("/home/jhallard/linux/tinyML/testXX.csv")
# dy.to_csv("/home/jhallard/linux/tinyML/testYY.csv")

dx = pd.read_csv("/home/jhallard/linux/tinyML/testXX.csv")
dy = pd.read_csv("/home/jhallard/linux/tinyML/testYY.csv")
X = dx.values.copy()
np.random.shuffle(X)  # https://youtu.be/uyUXoap67N8
X = X[:, -1:]
print str(X)

Y = dy.values.copy()
np.random.shuffle(Y)
Y = Y[:, -1:]
print str(Y)

model = model_from_json("""{"layers": [{"b_constraint": null, "name": "Dense", "activity_regularizer": null, "W_constraint": null, "input_shape": [1], "init": "uniform", "activation": "linear", "input_dim": 1, "b_regularizer": null, "W_regularizer": null, "output_dim": 12}, {"b_constraint": null, "name": "Dense", "activity_regularizer": null, "W_constraint": null, "init": "uniform", "activation": "linear", "input_dim": null, "b_regularizer": null, "W_regularizer": null, "output_dim": 1}, {"beta": 0.1, "activation": "relu", "name": "Activation", "target": 0}], "loss": "mean_squared_error", "theano_mode": null, "name": "Sequential", "class_mode": "categorical", "optimizer": {"epsilon": 1e-06, "lr": 0.001, "name": "RMSprop", "rho": 0.9}}""") #Sequential()
model.add(Dense(output_dim=18, input_dim=1))
model.add(Activation('relu'))
model.add(Dense(output_dim=64, init='uniform', input_dim=15))
# model.add(Dropout(0.1))
model.add(Activation('relu'))
# model.add(Dropout(0.1))
model.add(Dense(1, init='uniform'))
model.compile(loss='mean_squared_error', optimizer='rmsprop')
model.fit(X, Y, nb_epoch=460, batch_size=360, validation_split=0.2)

