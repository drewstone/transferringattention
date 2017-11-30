import os
import argparse
import numpy as np
from sklearn.datasets import fetch_rcv1

import keras
from keras.models import Sequential, Model
from keras.layers import Dense

import preprocess
import networks
import callbacks
import plotting

# fix random seed for reproducibility
seed = 7
np.random.seed(seed)

def train_and_validate(model, data, validation_split=0.33, epochs=10):
    """
    Trains a model over specified amount of data with specified train/validation split
    """
    X, Y = data
    cbs = callbacks.get_callbacks(name="initial_training")
    history = model.fit(X, Y, validation_split=validation_split, batch_size=64, epochs=epochs, callbacks=cbs)

    return model, history, cbs

def transfer_and_repeat(model, intermediate, shallow, data, validation_split=0.33, epochs=10):
    """
    Trains a new shallower network using second split of data
    given a particular data split, stored in the data directory
    """
    X, Y = data

    # Save model weights to load into intermediate model
    intermediate = load_weights_by_name(model, intermediate)

    # Compute intermediate transformation from previous intermediate model over new data
    preds = intermediate.predict(X, batch_size=64)

    # Fit shallower model using predictions and labels of new data
    cbs = callbacks.get_callbacks(name="transfer_training")
    history = shallow.fit(preds, Y, validation_split=validation_split, batch_size=64, epochs=epochs, callbacks=cbs)
    
    return intermediate, shallow, history, cbs

def load_weights_by_name(model, transferred_model):
    save_model(model, 'temp_model')
    transferred_model.load_weights('models/temp_model.h5', by_name=True)
    return transferred_model

def get_data(split_type, amt):
    data = preprocess.get_data(split_type)

    first, second, indices = data
    X1, Y1 = first
    X2, Y2 = second
    fst, snd = indices

    return X1[:amt].todense(), Y1[:amt].todense(), X2[:amt].todense(), Y2[:amt].todense(), fst, snd

def save_model(model, name):
    if not os.path.exists('./models'):
        os.makedirs('./models')

    model.save('models/{}.h5'.format(name))
