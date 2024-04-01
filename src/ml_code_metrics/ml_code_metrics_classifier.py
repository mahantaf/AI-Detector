import numpy as np
import pandas as pd
from itertools import combinations, permutations, product
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.ensemble import VotingClassifier, BaggingClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV, cross_validate
from sklearn.feature_selection import VarianceThreshold
from scipy.stats import uniform
import xgboost as xgb
import matplotlib.pyplot as plt
import pickle
from sklearn.base import clone
from tqdm import tqdm
import os


np.random.seed(42)


def data_preprocess(df, col_list):
    df = df.dropna(axis=1)
    y = df['actual label'].replace({'ai': 0, 'human': 1})
    try:
        df = df.drop(columns=['actual label'])
    except:
        pass
    df = df[col_list]
    X = df
    return X, y

def run(train_df, test_df, train_df_label, eclf, features_to_remove, col_list):
    col_list_new = [x for x in col_list if x not in features_to_remove]

    X_train_df, y_train = data_preprocess(train_df, col_list_new)
    X_test_df, y_test = data_preprocess(test_df, col_list_new)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train_df)
    X_test = scaler.transform(X_test_df)

    eclf_clone = clone(eclf)
    eclf_clone.fit(X_train, y_train)

    pred = eclf_clone.predict(X_test)
    acc = accuracy_score(y_test, pred)
    f1 = f1_score(y_test, pred)    

    return acc, f1, y_test, pred

def calculate_cohens_d(x,y):
    return (np.mean(x) - np.mean(y)) / np.sqrt((np.std(x, ddof=1) ** 2 + np.std(y, ddof=1) ** 2) / 2.0)


def generate_pairs_combinations(lst):
    pairs = list(product(lst, repeat=2))
    return pairs


file_list = [x[:-len('_final.csv')] for x in os.listdir('')]
seq = sorted(generate_pairs_combinations(file_list))

col_list = ['AvgCountLineCode',
 'SumCyclomatic',
 'keywords',
 'if_else_while_operators',
 'MaxNesting',
 'CountLineBlank',
 'CountDeclFunction',
 'CountLineCodeDecl']

acc_list, tpr_list, tnr_list, human_f1_list, ai_f1_list, f1_list = [], [], [], [], [], []


for tr, te in seq:
    tr_data, tr_model, tr_lang = tr.split('_')
    te_data, te_model, te_lang = te.split('_')
    
    print(f'Training: {tr}, Test: {te}')
    train_file_path = [x for x in os.listdir(f'') if 'train' in x][0]
    train_df = pd.read_csv(f''+train_file_path)

    val_file_path = [x for x in os.listdir(f'') if 'val' in x][0]
    val_df = pd.read_csv(f''+val_file_path)

    test_file_path = [x for x in os.listdir(f'') if 'test' in x][0]
    test_df = pd.read_csv(f''+test_file_path)
    
    # Set classifier
    clf = MLPClassifier()

    acc, f1, y_test, pred = run(train_df, test_df, tr, clf, [], col_list)
    acc = accuracy_score(y_test, pred)
    f1 = f1_score(y_test, pred)

    # Calculate F1-score for human predictions
    human_f1 = f1_score(y_test, pred, pos_label=1)
    
    # Calculate F1-score for AI predictions
    ai_f1 = f1_score(y_test, pred, pos_label=0)

    tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
    print(tn, fp, fn, tp)
    fpr = fp / (fp + tn)
    fnr = fn / (tp + fn)
    tpr = tp / (tp+fn)
    tnr = tn / (tn+fp)


    avg_f1 = (human_f1 + ai_f1)/2

    # print(human_f1, ai_f1)
    
    print(f'--> Accuracy: {round(acc, 4)} TPR: {round(tpr, 4)} TNR: {round(tnr, 4)} Human_F1: {round(human_f1, 4)} AI_F1: {round(ai_f1, 4)}')
    
    acc_list.append(acc)
    tpr_list.append(tpr)
    tnr_list.append(tnr)
    human_f1_list.append(human_f1)
    ai_f1_list.append(ai_f1)
    f1_list.append(avg_f1)


avg_acc = round(sum(acc_list)/len(acc_list), 4)
avg_tpr = round(sum(tpr_list)/len(tpr_list), 4)
avg_tnr = round(sum(tnr_list)/len(tnr_list), 4)
avg_human_f1 = round(sum(human_f1_list)/len(human_f1_list), 4)
avg_ai_f1 = round(sum(ai_f1_list)/len(ai_f1_list), 4)
avg_f1 = round(sum(f1_list)/len(f1_list), 4)

print(f'--> Accuracy: {avg_acc} TPR: {avg_tpr} TNR: {avg_tnr} Human_F1: {avg_human_f1} AI_F1: {avg_ai_f1} F1: {avg_f1}')
