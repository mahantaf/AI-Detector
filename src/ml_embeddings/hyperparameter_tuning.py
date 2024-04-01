from pycaret.classification import *
import os
import pandas as pd
import numpy as np
from collections import defaultdict
import xgboost as xgb
import lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.ensemble import VotingClassifier, BaggingClassifier, GradientBoostingClassifier
from pycaret.classification import * 
import pickle

tuned_model_list_datas = defaultdict()
i = 0

emb_types = ['ast_', 'combined_', 'code_']

for folder_name in os.listdir(''):
    print(folder_name)
    file_name = [x for x in os.listdir('') if 'train' in x][0]
    data = pd.read_csv('', index_col=0)
    for emb_type in emb_types:
        print(f'--> {emb_type}')

        filtered_data = data.loc[:, data.columns.str.startswith(emb_type)]
        filtered_data['actual label'] = data['actual label']
        print(filtered_data.shape)
        reg1 = setup(data = filtered_data, target = 'actual label', index=False, session_id=42)
        # Set models to tune
        model_list = [GradientBoostingClassifier()]
        tuned_model_list = []

        for model in model_list:
            tuned_model = tune_model(model)
            tuned_model_list.append(tuned_model)
            print(tuned_model, '\n')
        
        tuned_model_list_datas[folder_name+emb_type] = tuned_model_list
        i += 1


with open('', 'wb') as f:
    pickle.dump(tuned_model_list_datas, f)