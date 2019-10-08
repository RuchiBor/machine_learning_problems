import os
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn import metrics
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow import keras

# from imblearn.over_sampling import SMOTE
import models
import evaluation
import data_loader
from common.config_files.config import CGNConfigParser

def train_neural_network():

  train_df, orig_test_df, test_df = data_loader.read_csv()
  train_features, train_labels, test_features = data_loader.feature_filtering(
    train_df, orig_test_df, test_df)

  model = models.make_model(features=train_features)

  checkpoint_cb, tensorboard_cb = models.callbacks(
    model_name='nn_submission03_s_1_m1_f_2165.ckpt')
  EPOCHS = 1
  BATCH_SIZE = 32

  history = model.fit(train_features,
                      train_labels,
                      batch_size=BATCH_SIZE,
                      epochs=EPOCHS,
                      callbacks=[checkpoint_cb, tensorboard_cb]
                      #     validation_data=(val_features, val_labels)
                     )

  evaluation.evaluation(model, train_features, train_labels)
  evaluation.plot_metrices(EPOCHS, history, if_val=False)
  evaluation.plot_confusion_matrix(model, train_features, train_labels)
  evaluation.submission(model=model,
                        test_features=test_features,
                        orig_test_df=orig_test_df,
                        submission_name='nn_submission03_s_1_m1_f_2165.csv')

def train_lightgbm():
    train_df, orig_test_df, test_df = data_loader.read_csv()
    train_features, train_labels, test_features = data_loader.feature_filtering(
        train_df, orig_test_df, test_df)

    preds = np.zeros((len(test_df), 1))
    num_lgbm_ensemble = 17
    for i in range(num_lgbm_ensemble):
        print("training LGBC model {}".format(i))
        n_estimators = 900
        max_depth = 7
        learning_rate = 0.01
        random_state = i
        colsample_bytree = 0.1
        reg_lambda = 15
        reg_alpha = 10
        lgbc = models.make_model_lgbm(n_estimators, max_depth, learning_rate, i, colsample_bytree, reg_lambda, reg_alpha)
        lgbc.fit(train_features, train_labels)
        preds = preds + lgbc.predict_proba(test_features)[:, 1].reshape(-1, 1)
    preds = preds / num_lgbm_ensemble

    config_all = CGNConfigParser()
    config = config_all.get_sub_config('hdfc')
    model_path = config['model_path']

    submission_df = pd.DataFrame()
    sub_list = {'Col1': orig_test_df['Col1']}
    submission_df = pd.DataFrame(sub_list)
    submission_df['score'] = preds
    submission_df['Col2'] = 0
    submission_df.loc[submission_df['score'] > 0.28945, 'Col2'] = 1
    submission_df[['Col1', 'Col2']].to_csv(model_path + "submission_lgbm.csv", index=False)

    print("Values : ", submission_df['Col2'].value_counts())


if __name__ == "__main__":
  train_neural_network()
  train_lightgbm()