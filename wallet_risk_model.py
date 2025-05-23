# -*- coding: utf-8 -*-
"""wallet-risk-model.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1PaiI1tfkcYBnNs_AomWirRA0JtR0BtLB

## 🧭 Introduction and Objective

This notebook develops a credit scoring model for wallets on the Compound V2 protocol.  
We aim to assign a score between 0 and 100 based solely on historical transaction behavior.  
Higher scores reflect more reliable and responsible usage, while lower scores suggest risky or bot-like activity.
"""

import json
import pandas as pd
from glob import glob

"""## 📥 Data Loading

Load and combine the top 3 largest raw transaction files from Compound V2 to work with significant activity data.

"""

def load_deposits_from_files(file_list):
    all_data = []
    for file in file_list:
        with open(file, 'r') as f:
            data = json.load(f)
            all_data.extend(data['deposits'])
    return pd.DataFrame(all_data)

file_list = [
    '/content/compoundV2_transactions_ethereum_chunk_0.json',
    '/content/compoundV2_transactions_ethereum_chunk_1.json',
    '/content/compoundV2_transactions_ethereum_chunk_2.json'
]

df = load_deposits_from_files(file_list)
df.head()

import numpy as np
import pandas as pd
import shap
import matplotlib.pyplot as plt
import xgboost as xgb
import pickle
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import os

"""## 🧹 Data Preprocessing

Convert timestamps, extract wallet and asset details, and clean unnecessary columns.

"""

df['amountUSD'] = df['amountUSD'].astype(float)
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
df['account_id'] = df['account'].apply(lambda x: x['id'])
df['asset_symbol'] = df['asset'].apply(lambda x: x['symbol'])
df.drop(['account', 'asset'], axis=1, inplace=True)

"""## 🧪 Feature Engineering

Aggregate transaction behavior into wallet-level features such as total USD transacted, transaction count, asset diversity, etc.

"""

features = df.groupby('account_id').agg({
    'amountUSD': ['sum', 'mean', 'std', 'count', 'max'],
    'timestamp': [lambda x: (x.max() - x.min()).days + 1],
    'asset_symbol': pd.Series.nunique
}).reset_index()

features.columns = ['account_id', 'total_usd', 'avg_usd', 'std_usd', 'tx_count', 'max_usd', 'active_days', 'unique_assets']

features.fillna(0, inplace=True)

features['label'] = np.where((features['tx_count'] > 3) & (features['total_usd'] > 10), 1, 0)

X = features.drop(['account_id', 'label'], axis=1)
y = features['label']

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
all_preds, all_true = [], []

"""## 🔀 . Model Training and Validation

Train an XGBoost classifier using StratifiedKFold cross-validation and collect performance metrics.

"""

for train_idx, val_idx in skf.split(X, y):
    model = xgb.XGBClassifier(random_state=42, eval_metric='logloss')
    model.fit(X.iloc[train_idx], y.iloc[train_idx])
    preds = model.predict(X.iloc[val_idx])
    all_preds.extend(preds)
    all_true.extend(y.iloc[val_idx])

"""## 📊  Model Evaluation

Generate a classification report and measure model performance (accuracy, AUC,Confusion Matrix ).

"""

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

print("Accuracy:", accuracy_score(all_true, all_preds))
print("Classification Report:\n", classification_report(all_true, all_preds))
print("Confusion Matrix:\n", confusion_matrix(all_true, all_preds))

explainer = shap.Explainer(model, X)
shap_values = explainer(X)

"""## 🧠 Model Explainability (SHAP)

Use SHAP values to understand feature importance and model decisions.

"""

import seaborn as sns

shap.summary_plot(shap_values, X, show=False)
plt.tight_layout()
plt.savefig("shap_summary.png")

features['credit_score'] = (model.predict_proba(X)[:, 1] * 100).round(2)

top_wallets = features[['account_id', 'credit_score']].sort_values(by='credit_score', ascending=False).head(1000)
top_wallets.to_csv("wallet_score.csv", index=False)

import seaborn as sns

cm = confusion_matrix(all_true, all_preds)


sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=['Risky', 'Reliable'],
            yticklabels=['Risky', 'Reliable'])
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.tight_layout()
plt.show()

cm_percent = cm.astype('float') / cm.sum() * 100

plt.figure(figsize=(6, 5))
sns.heatmap(cm_percent, annot=True, fmt=".2f", cmap='coolwarm',
            xticklabels=['Risky', 'Reliable'],
            yticklabels=['Risky', 'Reliable'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix (% of Total Predictions)')
plt.show()

labels = np.array([['TN', 'FP'], ['FN', 'TP']])
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=labels + "\n" + cm.astype(str), fmt='', cmap='Purples',
            xticklabels=['Risky', 'Reliable'],
            yticklabels=['Risky', 'Reliable'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix with Labels (TN/FP/FN/TP)')
plt.show()

shap.plots.bar(shap_values, max_display=7)

from sklearn.metrics import roc_curve, precision_recall_curve

y_proba = model.predict_proba(X)[:, 1]
fpr, tpr, _ = roc_curve(y, y_proba)
precision, recall, _ = precision_recall_curve(y, y_proba)

plt.figure(figsize=(6, 5))
plt.plot(fpr, tpr, label='ROC Curve')
plt.plot([0, 1], [0, 1], '--', color='gray')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend()
plt.grid()
plt.show()

plt.figure(figsize=(6, 5))
plt.plot(recall, precision, label='PR Curve', color='purple')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.legend()
plt.grid()
plt.show()

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

"""**Conclusion**

This project successfully addresses the challenge of building a decentralized, AI-powered credit scoring system for Compound V2 wallets using only raw transaction-level data. Without any predefined labels or schema, a complete end-to-end pipeline was developed—from parsing complex JSON structures to engineering wallet-level features, designing heuristics for behavior-based labeling, and training a supervised learning model.

The final system assigns a credit score between 0 and 100 to each wallet, reflecting its historical behavior and risk profile. The approach balances clarity, scalability, and explainability, providing Zeru Finance with a robust framework to evaluate user reliability across the protocol. This solution is entirely custom, irreproducible without the full code and logic, and lays the groundwork for future credit innovation in DeFi.

**Yours sincerely,**

**Nikhil Sukthe**

[**Github-Repo-PS**](https://github.com/Nikhils-G/wallet-risk-model) |
[**Github-Link**](https://github.com/Nikhils-G) |
[**LinkedIn**](http://www.linkedin.com/in/nikhilsukthe) |
[**Portfolio**](https://nikhilsukthe.vercel.app/)
"""