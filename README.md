

# 🛡️ Wallet Risk Model

A machine learning-based scoring system designed to assess the **risk level of Ethereum wallets** using on-chain activity and behavioral features.

---

## 📂 Repository Structure

| File/Folder               | Description                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| `wallet_risk_model.ipynb` | Jupyter notebook for data preprocessing, feature engineering, and training |
| `wallet_risk_model.py`    | Python script version of the modeling pipeline                             |
| `model.pkl`               | Trained ML model (e.g., XGBoost)                                           |
| `wallet_score.csv`        | Final output with wallet addresses and their predicted risk scores         |
| `shap_summary.png`        | SHAP explainability visualization                                          |
| `Wallet Activity Analysis.pdf` | PDF detailing data exploration & wallet activity patterns             |
| `Methodology Document.pdf`| Project methodology, assumptions, and scoring criteria                     |
| `summery.txt`             | Plaintext summary of results                                               |
| `README.md`               | Project overview and usage instructions                                    |

---

## 🚀 Features

- Stratified K-Fold Cross Validation
- Hyperparameter Tuning (GridSearchCV / Optuna)
- SHAP-based Explainability
- Wallet-level behavioral feature engineering
- Robust pipeline with saved model & reproducible outputs

---

## 📊 Model Overview

- **Model Used:** XGBoost /
- **Features:** Deposit frequency, volume, asset diversity, USD value, etc.
- **Target:** Risk classification or scoring of wallets
- **Evaluation Metrics:** AUC, F1-score, Precision/Recall

---

## 📈 Outputs

- `wallet_score.csv` — Risk score assigned to each wallet
- `shap_summary.png` — Visual explanation of top contributing features
- `model.pkl` — Serialized trained model for reuse

---

## 🛠️ How to Use

```bash
# Clone the repository
git clone https://github.com/Nikhils-G/wallet-risk-model.git

# Navigate to the folder
cd wallet-risk-model

# Run the notebook or script
jupyter notebook wallet_risk_model.ipynb
# or
python wallet_risk_model.py
````

---

## 📚 References

* Ethereum transaction dataset
* Compound V2 documentation
* SHAP: [https://github.com/slundberg/shap](https://github.com/slundberg/shap)

---

## 🧠 Author

**Nikhil Sukthe**
B.Tech in CSE (AI & DS) | Data Science & ML Enthusiast
Connect on [LinkedIn](https://www.linkedin.com/in/nikhil-sukthe)

---

## 📄 License

MIT License — feel free to use, adapt, and contribute.

```



