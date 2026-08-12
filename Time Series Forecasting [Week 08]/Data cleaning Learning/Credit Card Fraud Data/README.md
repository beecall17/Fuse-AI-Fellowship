# Credit Card Fraud Detection – Data Cleaning & Analysis

## 📌 Overview

This notebook performs a complete data cleaning and exploratory analysis on the **Kaggle Credit Card Fraud Detection** dataset.  
The goal is to demonstrate professional data‑cleaning practices: handling missing data (MCAR / MAR), testing imputation strategies, outlier detection (global vs. grouped IQR), and generating business‑oriented insights.

## 📊 Dataset

- **Source:** (https://github.com/nsethi31/Kaggle-Data-Credit-Card-Fraud-Detection/blob/master/creditcard.csv)  
- **Size:** 284,807 transactions, 31 features (30 anonymised PCA components + Time + Amount + Class)
- **Target:** `Class` – 0 = genuine, 1 = fraud (only 0.17% fraud – heavily imbalanced)

## 🧹 Cleaning & Analysis Steps

1. **Initial Inspection**  
   - Checked for missing values, data types, class distribution, and descriptive statistics.

2. **Introducing Artificial Missing Data**  
   - `Amount`: 3% of values set to `NaN` completely at random (MCAR).  
   - `Time`: 2% of fraud transactions set to `NaN` (MAR – missingness depends on Class).

3. **Imputation Strategies**  
   - **Global median imputation** – simple but creates a density spike (visualised).  
   - **Forward / backward fill** (after sorting by `Time`) – for demonstration; not recommended for non‑temporal data.  
   - **Missing indicator column** – retains the information that a value was missing.

4. **Outlier Detection**  
   - **Global IQR** on `Amount`.  
   - **Grouped IQR** by `Class` – captures more outliers because of class imbalance.  
   - Explanation of why grouped detection is superior here.

5. **GroupBy Business Insights**  
   - Mean, median, std, and 90th percentile of `Amount` per `Class`.  
   - Interpretation: fraud has higher mean but lower median → long‑tail distribution of large frauds.

6. **Visualisations**  
   - Histograms (log scale) of transaction amounts for each class.  
   - KDE plot comparing original vs imputed distributions.  
   - Boxplots of `Time` and `Amount` by `Class`.

## 📈 Key Findings

- Fraudulent transactions have a **higher mean amount** ($116 vs $88) but a **lower median** ($9 vs $22), indicating a few very high‑value frauds.
- Global IQR outlier detection flagged fewer outliers than class‑grouped IQR – grouping is essential for imbalanced targets.
- Median imputation creates an artificial spike in the distribution; forward‑fill is theoretically unsound for transaction data without natural ordering.

## 🛠️ Requirements

- Python 3.8+
- pandas, numpy, matplotlib, seaborn

Install dependencies:
```bash
pip install pandas numpy matplotlib seaborn
```
## 🚀 How to Run
Clone the repository.

Place the creditcard.csv file in the same folder as the notebook (or update the path).

Run the notebook cell‑by‑cell or use Run All.

## 📝 Future Improvements
1. Compare imputation methods on predictive model performance (e.g., logistic regression).

2. Use missingno library for missing data visualisation.

3. Apply winsorisation to outliers instead of just flagging them.